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
  }).catch(function(){});
})();
