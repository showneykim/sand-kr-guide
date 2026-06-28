#!/usr/bin/env python3
# 트램플러 내부 설계 부품(구획) 115종 → 인터랙티브 블루프린트 카탈로그 blueprints.html
import json, html, os

ROOT = os.path.expanduser("~/sand-kr-guide")
P = json.load(open(os.path.join(ROOT, "tools/parts_data.json")))["parts"]

CAT_ORDER = ["섀시","동력","조향","대포·포","무기·공성","장갑","화물·보관","승무원·생활","구조·이동","도구·유틸","기타"]
CAT_COL = {"섀시":"#4493f8","동력":"#d9a84c","조향":"#6fa3bd","대포·포":"#c1572a","무기·공성":"#cf6a4a",
           "장갑":"#9a8358","화물·보관":"#e3a008","승무원·생활":"#8aae66","구조·이동":"#b07d8a","도구·유틸":"#6fb24a","기타":"#7d6f56"}

def esc(s): return html.escape(str(s or ""))
from collections import Counter, defaultdict
G = defaultdict(list)
for p in P: G[p["cat"]].append(p)

# DETAIL for modal
DETAIL = []
for p in P:
    DETAIL.append({
        "name": p["name"], "cat": p["cat"], "col": CAT_COL.get(p["cat"], "#d9a84c"),
        "icon": "assets/tech_icons/" + p["icon"], "desc": p["desc"],
        "fac": p["faction"], "tier": p["tier"], "crowns": p["crowns"],
        "mats": p["mats"], "node": p["node"],
    })

def card(p, i):
    snip = (p["desc"] or "")[:44]
    col = CAT_COL.get(p["cat"], "#d9a84c")
    key = (p["name"] + " " + p["cat"] + " " + (p["desc"] or "") + " " + p["node"]).lower()
    return (f'<button class="it" data-i="{i}" data-cat="{esc(p["cat"])}" data-s="{esc(key)}" style="--col:{col}">'
            f'<img class="it-ic" src="assets/tech_icons/{esc(p["icon"])}" alt="" loading="lazy" decoding="async">'
            f'<span class="it-body"><span class="it-n">{esc(p["name"])}</span>'
            f'<span class="it-c">{esc(p["cat"])} · T{esc(p["tier"])}</span>'
            f'<span class="it-d">{esc(snip)}</span></span></button>')

cards_html = "\n".join(card(p, i) for i, p in enumerate(P))
fbtns = '<button class="fbtn active" data-f="all" aria-pressed="true">전체</button>' + "".join(
    f'<button class="fbtn" data-f="{esc(c)}" aria-pressed="false" style="--col:{CAT_COL[c]}">{esc(c)}</button>'
    for c in CAT_ORDER if G.get(c))
total = len(P)
DETAIL_JSON = json.dumps(DETAIL, ensure_ascii=False)

HTML = f'''<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>블루프린트 — 부품 카탈로그 (한국어) · 샌드: 레이더스 오브 소피</title>
<meta name="description" content="SAND: Raiders of Sophie 트램플러 부품(구획) {total}종 — 초기부터 테크 해금까지, 설명·해금 비용·재료">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#13100b;--bg2:#1a150e;--panel:#221a10;--edge:#392b1a;--edge2:#4f3a21;--ink:#e9dfcd;--muted:#ab9a7c;--faint:#7d6f56;--brass:#d9a84c;--brass-d:#a9772a}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:"Pretendard","Malgun Gothic","Apple SD Gothic Neo",system-ui,sans-serif;font-size:16px;line-height:1.6;
 background-image:radial-gradient(1100px 460px at 82% -8%,rgba(217,168,76,.07),transparent 60%)}}
a{{color:var(--brass);text-decoration:none}}a:hover{{text-decoration:underline}}
.sr-only{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}}
.topbar{{position:sticky;top:0;z-index:50;backdrop-filter:blur(9px);background:rgba(15,11,7,.86);border-bottom:1px solid var(--edge)}}
.topbar .in{{max-width:1180px;margin:0 auto;padding:11px 22px;display:flex;gap:14px;align-items:center}}
.brand{{font-family:"Oswald",sans-serif;font-weight:700;letter-spacing:.2em;color:var(--brass);font-size:17px}}
.tabs{{margin-left:auto;display:flex;gap:6px;flex-wrap:wrap}}
.tabs a{{font-size:13px;color:var(--muted);padding:6px 13px;border:1px solid var(--edge2);border-radius:6px}}
.tabs a.on{{color:var(--bg);background:var(--brass);border-color:var(--brass);font-weight:600}}
.tabs a:hover{{text-decoration:none;color:var(--brass)}}.tabs a.on:hover{{color:var(--bg)}}
@media(max-width:560px){{.topbar .in{{padding:9px 12px;gap:8px;flex-wrap:wrap}}.brand{{font-size:15px}}.tabs a{{padding:5px 9px;font-size:12px}}}}
header.h{{max-width:1180px;margin:0 auto;padding:28px 22px 6px}}
header.h h1{{font-family:"Oswald",sans-serif;font-weight:700;letter-spacing:.04em;font-size:clamp(23px,4vw,32px);margin:0;color:#fff}}
header.h .sub{{color:var(--muted);margin:8px 0 0;font-size:15px;max-width:820px}}
header.h .sub b{{color:var(--brass)}}
.intro{{max-width:1180px;margin:14px auto 0;padding:0 22px}}
figure{{margin:0;background:#0c0906;border:1px solid var(--edge2);border-radius:8px;overflow:hidden}}
figure img{{display:block;width:100%;height:auto;cursor:zoom-in}}
figcaption{{padding:10px 15px;font-size:12.5px;color:var(--muted);border-top:1px solid var(--edge);background:var(--bg2)}}
figcaption b{{color:#c9b58e}}
details.guide{{margin:14px 0 0;background:linear-gradient(180deg,var(--panel),var(--bg2));border:1px solid var(--edge);border-radius:8px;padding:4px 16px}}
details.guide summary{{cursor:pointer;font-family:"Oswald",sans-serif;color:var(--brass);font-size:14px;letter-spacing:.03em;padding:9px 0}}
details.guide .gb{{font-size:13.5px;color:var(--muted);line-height:1.6;padding:4px 0 12px}}
details.guide .gb b{{color:#d6c4a0}}details.guide .gb code{{font-family:"Oswald",monospace;background:#0d0a06;border:1px solid var(--edge2);color:var(--brass);padding:0 5px;border-radius:4px;font-size:.86em}}
.ctrl{{position:sticky;top:56px;z-index:40;background:rgba(15,11,7,.92);backdrop-filter:blur(6px);border-bottom:1px solid var(--edge);margin-top:16px}}
.ctrl .in{{max-width:1180px;margin:0 auto;padding:12px 22px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}}
#q{{flex:1;min-width:180px;background:#0d0a06;border:1px solid var(--edge2);color:var(--ink);border-radius:7px;padding:9px 13px;font-size:14px;font-family:inherit}}
#q:focus{{outline:none;border-color:var(--brass)}}
.fbtns{{display:flex;gap:6px;flex-wrap:wrap}}
.fbtn{{font-family:inherit;font-size:12.5px;color:var(--muted);background:transparent;border:1px solid var(--edge2);border-radius:999px;padding:6px 12px;cursor:pointer}}
.fbtn[data-f]:not([data-f=all]){{border-color:var(--edge2);border-color:color-mix(in srgb,var(--col) 55%,var(--edge2))}}
.fbtn.active{{color:#fff;border-color:var(--col,var(--brass));background:rgba(217,168,76,.22);background:color-mix(in srgb,var(--col,#d9a84c) 26%,transparent)}}
#count{{font-size:12.5px;color:var(--muted);margin-left:auto;white-space:nowrap}}
main{{max-width:1180px;margin:0 auto;padding:16px 22px 80px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(232px,1fr));gap:11px}}
.it{{display:flex;gap:10px;align-items:center;text-align:left;font-family:inherit;cursor:pointer;
 background:linear-gradient(180deg,#241b11,#191309);border:1px solid var(--edge);border-left:3px solid var(--col);
 border-radius:8px;padding:8px 10px;transition:transform .08s,border-color .12s,box-shadow .12s;color:var(--ink)}}
.it:hover,.it:focus{{transform:translateY(-1px);box-shadow:0 6px 18px rgba(0,0,0,.35);outline:none;border-color:color-mix(in srgb,var(--col) 50%,var(--edge))}}
.it-ic{{width:46px;height:46px;flex:none;object-fit:contain;padding:2px;border:1px solid var(--edge2);border-radius:7px;
 background:radial-gradient(circle at 50% 36%,rgba(255,255,255,.07),transparent 70%),#0d0a06}}
.it-body{{min-width:0;display:flex;flex-direction:column}}
.it-n{{font-weight:600;font-size:12.5px;line-height:1.2;color:var(--ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.it-c{{font-size:10.5px;color:var(--col);font-weight:600;margin-top:1px}}
.it-d{{font-size:11px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:2px}}
.it.hide{{display:none}}
.empty{{color:var(--faint);font-size:13px;padding:24px 2px}}
#ov{{position:fixed;inset:0;z-index:100;background:rgba(8,6,4,.78);backdrop-filter:blur(3px);display:none;align-items:center;justify-content:center;padding:20px}}
#ov.on{{display:flex}}
#mod{{max-width:540px;width:100%;max-height:88vh;overflow:auto;background:linear-gradient(180deg,#251c12,#15100b);
 border:1px solid var(--edge2);border-left:4px solid var(--col,#d9a84c);border-radius:12px;box-shadow:0 30px 80px rgba(0,0,0,.6)}}
#mod .m-h{{display:flex;gap:13px;align-items:center;padding:18px 20px 12px;position:sticky;top:0;background:linear-gradient(180deg,#251c12,#241b11);border-bottom:1px solid var(--edge)}}
#mod .m-ic{{width:64px;height:64px;flex:none;object-fit:contain;padding:4px;border:1px solid var(--edge2);border-radius:9px;background:radial-gradient(circle at 50% 36%,rgba(255,255,255,.08),transparent 70%),#0d0a06}}
#mod .m-tt{{flex:1;min-width:0}}#mod .m-n{{font-weight:700;font-size:16.5px;color:#fff;line-height:1.25}}
#mod .m-c{{font-size:12px;color:var(--col,#d9a84c);font-weight:600;margin-top:2px}}
#mod .m-x{{flex:none;background:transparent;border:1px solid var(--edge2);color:var(--muted);border-radius:7px;width:32px;height:32px;font-size:17px;cursor:pointer}}#mod .m-x:hover{{color:var(--brass);border-color:var(--brass)}}
#mod .m-b{{padding:14px 20px 22px}}
#mod .m-desc{{font-size:14px;color:var(--ink);line-height:1.65;margin:0 0 14px}}
#mod .sec{{font-family:"Oswald",sans-serif;font-size:11px;letter-spacing:.06em;color:var(--faint);text-transform:uppercase;margin:16px 0 6px;border-bottom:1px solid var(--edge);padding-bottom:4px}}
#mod .row{{display:flex;justify-content:space-between;gap:10px;font-size:13.5px;padding:3px 0;border-bottom:1px dashed rgba(79,58,33,.5)}}
#mod .row:last-child{{border-bottom:0}}#mod .row .k{{color:var(--muted)}}#mod .row .v{{color:var(--ink);font-weight:600;font-family:"Oswald",sans-serif}}
#mod .chips{{display:flex;flex-wrap:wrap;gap:6px}}
#mod .chip{{font-size:12px;color:var(--ink);background:#0d0a06;border:1px solid var(--edge2);border-radius:6px;padding:3px 9px}}#mod .chip b{{color:var(--brass);font-family:"Oswald",sans-serif}}
footer{{border-top:1px solid var(--edge);background:var(--bg2)}}
footer .in{{max-width:1180px;margin:0 auto;padding:22px 22px 44px;color:var(--muted);font-size:12px;line-height:1.65}}footer b{{color:var(--muted)}}footer a{{color:var(--muted)}}
</style></head>
<body>
<div class="topbar"><div class="in">
  <span class="brand">SAND</span>
  <div class="tabs"><a href="index.html">입문 가이드</a><a href="tech.html">테크트리</a><a href="items.html">아이템 도감</a><a class="on" href="blueprints.html">블루프린트</a></div>
</div></div>

<header class="h">
  <h1>블루프린트 <span style="color:var(--brass)">부품 카탈로그</span></h1>
  <p class="sub">트램플러 에디터에 배치하는 <b>내부 설계 부품(구획) {total}종</b> — 초기 부품부터 테크트리 해금까지 전부. 카드를 <b>클릭하면 설명·해금 비용·재료</b>가 열립니다.</p>
</header>

<div class="intro">
  <figure>
    <img src="assets/img/bp_editor.png" alt="트램플러 에디터">
    <figcaption><b>트램플러 에디터.</b> 좌측 라이브러리(<span style="color:var(--brass)">아래 카탈로그</span>)에서 부품을 골라 섀시 위에 조립합니다. 우측 스탯·우하단 검증(STRUCTURE/OVERHANG/REACHABILITY/UTILITY)이 모두 충족돼야 출격.</figcaption>
  </figure>
  <details class="guide"><summary>에디터·검증 규칙 빠르게 보기</summary>
    <div class="gb">
      <b>필수 5종</b>: 섀시 · 조향 · 모터-리액터 · 선장실 · 입구(+크루룸). · <b>스탯</b>: 기동성 / 에너지효율 / 무게(현재/한도) / 안정성 / 최고속도 / Crew·Cannons·Cargo·Engines.<br>
      <b>검증</b> — <b>STRUCTURE</b> 모든 칸 연결·지지 · <b>OVERHANG</b> 돌출은 프레임으로 받치기 · <b>REACHABILITY</b> 입구→복도로 모든 칸 도달 · <b>UTILITY</b> 필요 유틸 칸 충족. <br>
      <b>조작키</b> — <code>Tab</code> 라이브러리 · <code>R</code>/<code>F</code> 층 · <code>G</code> 윗층 숨김 · <code>T</code> 문 편집 · <code>Q</code>/<code>E</code> 카메라. · 무게↑ = 기동성↓, 솔로는 과적 금지. 좋은 설계는 블루프린트로 저장(계정 공유).
    </div>
  </details>
</div>

<div class="ctrl"><div class="in">
  <input id="q" type="search" aria-label="부품 검색" placeholder="검색 — 부품명·카테고리·설명 (예: 섀시, 캐논, reactor)" autocomplete="off">
  <div class="fbtns">{fbtns}</div>
  <span id="count"></span>
</div></div>

<main><div class="grid" id="grid">
{cards_html}
</div></main>

<div id="ov" role="dialog" aria-modal="true"><div id="mod"></div></div>

<footer><div class="in">
  <p><b>데이터 출처.</b> 부품 이름·설명·해금 비용·재료는 게임 인게임 데이터이며, 커뮤니티 팬 데이터베이스 <a href="https://sand-help.com" target="_blank" rel="noopener">sand-help.com</a>(비공식)에서 가져와 한국어로 재구성했습니다. 부품 아이콘은 게임 내 에셋이며, sand-help의 코드·디자인은 복제하지 않았습니다.</p>
  <p>비공식 팬 가이드 · 얼리액세스(2026-06-22) 기준이라 수치·명칭은 패치로 바뀔 수 있습니다 — 인게임 확인 권장. 모든 권리는 Hologryph·TowerHaus·tinyBuild에 있습니다.</p>
</div></footer>

<script>
var PARTS={DETAIL_JSON};
(function(){{
  var cards=[].slice.call(document.querySelectorAll('.it'));
  var q=document.getElementById('q'),count=document.getElementById('count'),grid=document.getElementById('grid'),fsel='all';
  var emptyEl=document.createElement('p');emptyEl.className='empty';emptyEl.setAttribute('role','status');
  emptyEl.textContent='검색 결과가 없습니다.';emptyEl.style.display='none';grid.parentNode.appendChild(emptyEl);
  function apply(){{
    var term=q.value.trim().toLowerCase(),shown=0;
    cards.forEach(function(c){{
      var ok=(fsel==='all'||c.dataset.cat===fsel)&&(!term||c.dataset.s.indexOf(term)>=0);
      c.classList.toggle('hide',!ok); if(ok)shown++;
    }});
    emptyEl.style.display=shown?'none':'block';
    count.textContent=shown+' / '+cards.length+' 부품';
  }}
  q.addEventListener('input',apply);
  [].slice.call(document.querySelectorAll('.fbtn')).forEach(function(b){{
    b.addEventListener('click',function(){{
      document.querySelectorAll('.fbtn').forEach(function(x){{x.classList.remove('active');x.setAttribute('aria-pressed','false');}});
      b.classList.add('active');b.setAttribute('aria-pressed','true');fsel=b.dataset.f;apply();
    }});
  }});
  apply();
  var ov=document.getElementById('ov'),mod=document.getElementById('mod'),_prev=null;
  function esc(s){{return String(s==null?'':s).replace(/[&<>]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c];}});}}
  function chips(arr){{return '<div class="chips">'+arr.map(function(r){{return '<span class="chip">'+esc(r[0])+' <b>×'+esc(r[1])+'</b></span>';}}).join('')+'</div>';}}
  function open(i){{
    var d=PARTS[i]; if(!d)return; _prev=document.activeElement;
    mod.style.setProperty('--col',d.col);
    var h='<div class="m-h"><img class="m-ic" src="'+esc(d.icon)+'" alt=""><div class="m-tt"><div class="m-n">'+esc(d.name)+'</div><div class="m-c">'+esc(d.cat)+'</div></div><button class="m-x" aria-label="닫기">×</button></div><div class="m-b">';
    if(d.desc) h+='<p class="m-desc">'+esc(d.desc)+'</p>';
    h+='<div class="sec">해금 정보</div>';
    h+='<div class="row"><span class="k">연구 진영</span><span class="v">'+esc(d.fac)+'</span></div>';
    h+='<div class="row"><span class="k">연구 노드</span><span class="v">'+esc(d.node)+' · T'+esc(d.tier)+'</span></div>';
    h+='<div class="row"><span class="k">해금 비용</span><span class="v">'+esc(d.crowns.toLocaleString('en-US'))+' 크라운</span></div>';
    if(d.mats&&d.mats.length){{ h+='<div class="sec">추가 재료</div>'+chips(d.mats); }}
    h+='</div>';
    mod.innerHTML=h; ov.classList.add('on');
    mod.querySelector('.m-x').addEventListener('click',close);
    mod.scrollTop=0; mod.querySelector('.m-x').focus();
  }}
  function close(){{ ov.classList.remove('on'); if(_prev&&_prev.focus)_prev.focus(); }}
  cards.forEach(function(c){{ c.addEventListener('click',function(){{ open(+c.dataset.i); }}); }});
  ov.addEventListener('click',function(e){{ if(e.target===ov)close(); }});
  document.addEventListener('keydown',function(e){{ if(e.key==='Escape')close(); }});
}})();
</script>
</body></html>'''
HTML = HTML.replace('{DETAIL_JSON}', DETAIL_JSON)
HTML = HTML.replace('font-family:"Oswald"', 'font-family:"Oswald",sans-serif')
open(os.path.join(ROOT, "blueprints.html"), "w", encoding="utf-8").write(HTML)
print("wrote blueprints.html", len(HTML), "bytes ;", total, "parts")
print("카테고리:", dict(Counter(p["cat"] for p in P)))
