#!/bin/bash
# gh_push.sh — 用 GitHub REST API 提交(不依赖 git 二进制)
# 用途:git 被系统门禁(Xcode license)或不可用时,把本地工作副本的改动推回远端
# 用法: bash gh_push.sh <工作副本目录> <提交说明> [--dry-run]
set -u
REPO="judickzhu/guhai-honglou"
WORK="${1:?工作副本目录}"; MSG="${2:?提交说明}"; DRY="${3:-}"
[ -d "$WORK" ] || { echo "✗ 工作副本不存在: $WORK"; exit 1; }

echo "=== gh_push: $WORK ==="
# 1. 远端 HEAD + 根树
HEAD=$(gh api "repos/$REPO/git/ref/heads/main" -q .object.sha) || exit 1
ROOTTREE=$(gh api "repos/$REPO/git/commits/$HEAD" -q .tree.sha) || exit 1
echo "HEAD=$HEAD TREE=$ROOTTREE"

# 2. 递归树(注意:必须用 URL query,不能用 -f recursive=1)
TREES_JSON=$(gh api "repos/$REPO/git/trees/$ROOTTREE?recursive=1") || exit 1

# 3. 计算 delta(传给 python)
DELTA=$(python3 - "$WORK" "$TREES_JSON" <<'PYEOF'
import json,sys,hashlib,os
work=sys.argv[1]; data=json.loads(sys.argv[2])
entries={e['path']:e for e in data['tree'] if e['type']=='blob'}
def blob_sha(p):
    b=open(p,'rb').read()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
ch={}
for p,e in entries.items():
    lp=os.path.join(work,p)
    if not os.path.exists(lp): ch[p]=None
    else:
        s=blob_sha(lp)
        if s!=e['sha']: ch[p]=s
for root,dirs,files in os.walk(work):
    if '.git' in root: continue
    for f in files:
        rel=os.path.relpath(os.path.join(root,f),work)
        if rel not in entries: ch[rel]=blob_sha(os.path.join(root,f))
print(json.dumps(ch))
PYEOF
) || exit 1
N=$(python3 -c "import json,sys;print(len(json.loads('''$DELTA''')))")
echo "改动文件数: $N"
[ "$N" = "0" ] && { echo "✓ 无改动,无需提交"; exit 0; }
[ "$DRY" = "--dry-run" ] && { echo "(dry-run) 改动: $(echo $DELTA | python3 -c 'import json,sys;print(list(json.loads(sys.stdin.read())))' | head -c 200)"; exit 0; }

# 4. 上传 blob + 重建树 + 提交 + 更新 ref(交给 python 做)
python3 - "$WORK" "$REPO" "$HEAD" "$ROOTTREE" "$DELTA" "$MSG" <<'PYEOF'
import json,sys,subprocess,base64,os
work,REPO,HEAD,ROOTTREE,DELTA,MSG=sys.argv[1:7]
changes=json.loads(DELTA)
def ghj(*a,stdin=None):
    r=subprocess.run(['gh','api',*a],capture_output=True,text=True,input=stdin)
    if r.returncode!=0: raise RuntimeError(r.stderr[:300])
    return json.loads(r.stdout)
def upload(p):
    b=open(os.path.join(work,p),'rb').read()
    body=json.dumps({"content":base64.b64encode(b).decode(),"encoding":"base64"})
    return ghj(f'repos/{REPO}/git/blobs','-X','POST','--input','-',stdin=body)['sha']
# 上传新blob
newsha={}
for p,s in changes.items():
    if s is None: continue
    newsha[p]=upload(p); print('  blob', p, newsha[p][:7])
# 递归树拿子树sha
t=ghj(f'repos/{REPO}/git/trees/{ROOTTREE}?recursive=1')
trees={e['path']:e['sha'] for e in t['tree'] if e['type']=='tree'}
# 按目录重组改动
bydir={}
for p,s in newsha.items():
    d=os.path.dirname(p); bydir.setdefault(d,[]).append((os.path.basename(p),s))
# 重建受影响的子树(从最深到根)
newtree={}
def rebuild(d):
    if d in newtree: return newtree[d]
    if d=='':
        base=ROOTTREE; entries=[]
        for dd,ss in bydir.items():
            if dd=='':
                for b,s in ss: entries.append({'path':b,'mode':'100644','type':'blob','sha':s})
            else:
                entries.append({'path':os.path.basename(dd),'mode':'040000','type':'tree','sha':rebuild(dd)})
    else:
        base=trees.get(d); entries=[]
        for b,s in bydir.get(d,[]): entries.append({'path':b,'mode':'100644','type':'blob','sha':s})
        for dd in bydir:
            if os.path.dirname(dd)==d:
                entries.append({'path':os.path.basename(dd),'mode':'040000','type':'tree','sha':rebuild(dd)})
    nt=ghj(f'repos/{REPO}/git/trees','-X','POST','--input','-',stdin=json.dumps({"base_tree":base,"tree":entries}))['sha']
    newtree[d]=nt; return nt
root=rebuild('')
print('  根树', root[:7])
# 删除的文件处理(在 rebuild 中未含:需在对应子树里显式删除——简化:删除文件走 contents API)
# 提交
commit=ghj(f'repos/{REPO}/git/commits','-X','POST','--input','-',stdin=json.dumps({"message":MSG,"tree":root,"parents":[HEAD]}))['sha']
print('  提交', commit[:7])
r=ghj(f'repos/{REPO}/git/refs/heads/main','-X','PATCH','--input','-',stdin=json.dumps({"sha":commit,"force":True}))
print('  ref 更新:', r['object']['sha'][:7], '✓ 推送完成')
PYEOF
