/* 紅樓解讀 · 交互：檢索 / 字號 / 夜間模式 */
var PREFIX = (typeof PREFIX !== "undefined") ? PREFIX : "";

function setSize(s) { document.body.setAttribute("data-size", s); localStorage.setItem("hl_size", s); }
function toggleTheme() {
  var cur = document.documentElement.getAttribute("data-theme");
  var nxt = (cur === "dark") ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", nxt);
  localStorage.setItem("hl_theme", nxt);
  document.getElementById("themeBtn").textContent = (nxt === "dark") ? "☀" : "◐";
}
function applyPrefs() {
  var s = localStorage.getItem("hl_size"); if (s) setSize(s);
  var t = localStorage.getItem("hl_theme");
  if (t === "dark") { document.documentElement.setAttribute("data-theme", "dark");
    var b = document.getElementById("themeBtn"); if (b) b.textContent = "☀"; }
}
function searchSite() {
  var q = (document.getElementById("q").value || "").trim();
  var box = document.getElementById("sr");
  if (!q) { box.classList.add("hidden"); box.innerHTML = ""; return; }
  var data = (typeof window.SEARCH_DATA !== "undefined") ? window.SEARCH_DATA : [];
  var hits = data.filter(function (e) {
    return (e.title + " " + e.text).indexOf(q) > -1;
  }).slice(0, 12);
  var html = "";
  if (!hits.length) html = '<div class="dim" style="padding:6px 10px">無結果：「' + q + '」</div>';
  else hits.forEach(function (e) {
    html += '<a href="' + PREFIX + e.url + '">' + e.title + '</a>';
  });
  box.innerHTML = html;
  box.classList.remove("hidden");
}
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") { var b = document.getElementById("sr"); if (b) b.classList.add("hidden"); }
});
applyPrefs();

/* 瀏覽統計：填充頁尾迷你統計（stats.json 由 GitHub Actions 每日更新；缺失時靜默） */
(function(){
  var p = (typeof PREFIX !== "undefined") ? PREFIX : "";
  fetch(p + "stats.json").then(function(r){ return r.ok ? r.json() : null; }).then(function(d){
    if (!d) return;
    function s(id, v){ var e = document.getElementById(id); if (e) e.textContent = v; }
    s("ftV", d.views_total); s("ftU", d.views_uniques);
    s("ftT", (d.updated_at || "").slice(0, 10));
    s("ftVis", d.cumulative_visitors);
  }).catch(function(){});
})();

/* 頁面訪問統計（不蒜子）：在頁尾注入即時「總瀏覽／訪客／本頁」。
   與上面的 stats.json（GitHub 倉庫頁 Traffic·不含頁面訪問）互補。 */
(function(){
  try {
    if (document.getElementById("busuanzi_value_site_pv")) return;
    var line = document.createElement("p");
    line.className = "foot-pagevisit";
    line.innerHTML = "本站頁面訪問（即時·不蒜子）：總瀏覽 <span id=\"busuanzi_value_site_pv\">—</span>"
      + " · 訪客 <span id=\"busuanzi_value_site_uv\">—</span>"
      + " · 本頁 <span id=\"busuanzi_value_page_pv\">—</span>";
    var f = document.querySelector("footer");
    (f || document.body).appendChild(line);
    var sc = document.createElement("script");
    sc.async = true;
    sc.src = "https://busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js";
    document.body.appendChild(sc);
  } catch (e) {}
})();
