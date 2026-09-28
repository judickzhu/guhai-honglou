#!/usr/bin/env python3
# sync_push.py —— 可靠同步推送（GitHub API + 推送後全站雜湊比對）
# 用法: python3 tools/sync_push.py ["commit message"]
# 為何需要：本機 git push 走唔通（HTTPS/SSH 被網絡擋），改用 GitHub Git Data API；
#           但 API 推送可能靜默失敗（部分檔案未上）——故推送後必須全站比對。
import subprocess, json, base64, hashlib, os, sys, time

REPO = 'judickzhu/guhai-honglou'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def gh(args, inp=None, tries=8):
    for k in range(tries):
        cmd = ['gh', 'api'] + args
        if inp is not None:
            cmd += ['--input', '-']
            r = subprocess.run(cmd, input=json.dumps(inp), capture_output=True, text=True)
        else:
            r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
        time.sleep(2 + 2 * k)
    raise RuntimeError('gh api 失敗: %s :: %s' % (args[-1], r.stderr[:200]))

def blob_sha(path):
    data = open(path, 'rb').read()
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()

def remote_blobs():
    t = gh(['repos/%s/git/trees/main?recursive=1' % REPO])
    return {e['path']: e['sha'] for e in t.get('tree', []) if e['type'] == 'blob'}

def tracked_files():
    out = subprocess.run(['git', '-c', 'core.quotepath=false', 'ls-files'],
                         capture_output=True, text=True, cwd=ROOT).stdout
    return [f for f in out.split('\n') if f.strip()]

def diff_local_remote(remote):
    stale, missing = [], []
    for f in tracked_files():
        p = os.path.join(ROOT, f)
        if not os.path.exists(p): continue
        if f not in remote: missing.append(f)
        elif blob_sha(p) != remote[f]: stale.append(f)
    return stale, missing

def main():
    msg = sys.argv[1] if len(sys.argv) > 1 else '同步更新(GitHub API)'
    os.chdir(ROOT)
    print('=== ① 比對遠端 vs 本地 ===')
    remote = remote_blobs()
    stale, missing = diff_local_remote(remote)
    todo = stale + missing
    print('  遠端檔案: %d / 本地有異: %d 過期 + %d 缺 = %d' % (len(remote), len(stale), len(missing), len(todo)))
    if not todo:
        print('  ✓ 已經完全一致，無需推送')
        return
    print('=== ② 推送 %d 個檔案（API，帶重試） ===' % len(todo))
    base = gh(['repos/%s/git/ref/heads/main' % REPO])['object']['sha']
    tree_sha = gh(['repos/%s/git/commits/%s' % (REPO, base)])['tree']['sha']
    entries = []
    for i, f in enumerate(todo, 1):
        blob = gh(['-X', 'POST', 'repos/%s/git/blobs' % REPO],
                  {'content': base64.b64encode(open(f, 'rb').read()).decode(), 'encoding': 'base64'})
        entries.append({'path': f, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
        if i % 20 == 0: print('  ...%d/%d' % (i, len(todo)), flush=True)
    newtree = gh(['-X', 'POST', 'repos/%s/git/trees' % REPO], {'base_tree': tree_sha, 'tree': entries})
    newcommit = gh(['-X', 'POST', 'repos/%s/git/commits' % REPO],
                   {'message': msg, 'tree': newtree['sha'], 'parents': [base]})
    gh(['-X', 'PATCH', 'repos/%s/git/refs/heads/main' % REPO], {'sha': newcommit['sha']})
    print('  推送 commit: %s' % newcommit['sha'][:8])
    print('=== ③ 推送後全站複核 ===')
    time.sleep(3)
    remote2 = remote_blobs()
    stale2, missing2 = diff_local_remote(remote2)
    left = stale2 + missing2
    if left:
        print('  ✗ 仍有 %d 個未同步:' % len(left))
        for f in left[:10]: print('    -', f)
        sys.exit(1)
    print('  ✓ 遠端 = 本地 完全一致（%d 個檔案）' % len(remote2))

if __name__ == '__main__':
    main()
