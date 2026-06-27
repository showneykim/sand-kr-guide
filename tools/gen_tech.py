#!/usr/bin/env python3
# sand-help.com/tech 에서 파싱한 게임 테크트리 데이터(사실) → 한국어 tech.html 생성
import json, html, re, os

ROOT = os.path.expanduser("~/sand-kr-guide")
nodes = json.load(open("/tmp/claude-1000/-home-shawnkim/accddb21-599c-4336-be46-bd6fd94b1a98/scratchpad/nodes.json"))

FAC = {  # color -> (en, ko, accent, role)
 '#4493f8': ("Godlewski's Expedition", "고들레프스키 원정대", "#4493f8",
             "트램플러의 뼈대와 심장 — 섀시·동력(리액터/엔진/로드)·승무원실·생활·유틸리티"),
 '#6fb24a': ("K.K. Landwehr", "K.K. 란트베어", "#6fb24a",
             "방어와 백병 화력 — 조타·장갑·개인무기·포실·공성 장비·개량탄"),
 '#e3a008': ("Kaiser's Friends", "카이저의 친구들", "#e3a008",
             "대포 화력과 적재 — 캐논/오토캐논/샷건캐논·화물 보관·갑판·섀시 변형"),
}
FAC_ORDER = ['#4493f8', '#6fb24a', '#e3a008']

# 티어 경계 (Tier 라벨 left: I=216,II=972,III=1728,IV=2484, 폭 748)
def tier_of(left):
    if left < 965: return 1
    if left < 1721: return 2
    if left < 2477: return 3
    return 4

BASE_KO = {
 "Stairs":"계단","Framed Stairs":"프레임 계단","Crew Room":"승무원실","Captain's Cabin":"선장실",
 "Small Chassis":"소형 섀시","Middling Chassis":"중형 섀시","Great Chassis":"대형 섀시","Royal Chassis":"왕급 섀시",
 "Motor-Reactor":"모터-리액터","Energy Rod":"에너지 로드","Smokeless Energy Rod":"무연 에너지 로드",
 "Small Engine":"소형 엔진","Medium Engine":"중형 엔진","MedKit":"구급킷","Shovel":"삽",
 "Wooden Corridor":"목재 복도","Metal Corridor":"금속 복도","Crafting Materials":"제작 재료","Smoke Grenade":"연막탄",
 "Framed Steering":"프레임 조타","Steering":"조타","Large Open Steering":"대형 개방 조타","Large Framed Steering":"대형 프레임 조타",
 "Small Armament Workshop":"소형 병기 공방","Large Armament Workshop":"대형 병기 공방",
 "Artillery Decks":"포 갑판","Framed Artillery Deck":"프레임 포 갑판","Armored Artillery Decks":"장갑 포 갑판",
 "Framed Armored Artillery Deck":"프레임 장갑 포 갑판","Armored Artillery Compartment":"장갑 포실","Enclosed Artillery Compartment":"밀폐 포실",
 "Wooden Vestibule":"목재 현관","Armored Vestibule":"장갑 현관",
 "Weapons":"무기(연구)","Armor":"장갑(연구)","Armor Plate":"장갑판","Improved Ammo":"개량탄",
 "Time Bomb":"시한폭탄","Battering Ram":"충각","Embrasure":"총안","Grenade":"수류탄",
 "Wooden Decks":"목재 갑판","Armored Deck":"장갑 갑판","Balconies":"발코니","Armored Balconies":"장갑 발코니",
 "Cargo Deck":"화물 갑판","Cargo Hold":"화물 적재고","Cargo Bay":"화물칸","Cargo Compartment":"화물 구획",
 "Shotgun Cannon":"샷건 캐논","Auto Cannon":"오토캐논","Autocannon":"오토캐논","Cannon":"캐논","Resources":"자원(연구)",
}
SUFFIX_KO = {"multiple":"여러 종","L-Shape":"L자형","Parallel":"평행형","U-Shape":"U자형","Hole":"구멍","Trench":"참호"}

def ko_name(en):
    m = re.match(r'^(.*?)\s*\((.+)\)\s*$', en)
    base, suf = (m.group(1), m.group(2)) if m else (en, None)
    ko = BASE_KO.get(base, base)
    if suf:
        suf_ko = SUFFIX_KO.get(suf, suf)
        ko += f" ({suf_ko})"
    return ko

def category(en):
    s = en
    checks = [
        ("대포·포", r"Cannon|Artillery"),
        ("화물·자원", r"Cargo|Resources|Crafting Materials"),
        ("동력", r"Reactor|Engine|Energy Rod"),
        ("조타", r"Steering"),
        ("섀시", r"Chassis"),
        ("도구", r"Shovel|Smoke"),
        ("무기·공성", r"Weapons|Ammo|Armament|Grenade|Time Bomb|Battering|Embrasure"),
        ("장갑", r"Armor"),
        ("승무원·생활", r"Crew|Captain|MedKit"),
        ("구조·이동", r"Stairs|Corridor|Deck|Balcon|Vestibule"),
    ]
    for ko, pat in checks:
        if re.search(pat, s, re.I): return ko
    return "기타"

# enrich
for n in nodes:
    n['tier'] = tier_of(n['left'])
    n['ko'] = ko_name(n['name'])
    n['cat'] = category(n['name'])

# group
from collections import defaultdict, Counter
G = defaultdict(lambda: defaultdict(list))
for n in nodes:
    G[n['fac']][n['tier']].append(n)

ROMAN = {1:"I",2:"II",3:"III",4:"IV"}

def esc(s): return html.escape(str(s))

# ---- build node cards ----
def node_card(n):
    return (f'<div class="tn" data-s="{esc((n["ko"]+" "+n["name"]+" "+n["cat"]).lower())}" data-fac="{n["fac"]}">'
            f'<div class="tn-h"><span class="tn-ko">{esc(n["ko"])}</span>'
            f'<span class="tn-cost">{n["cost"]:,}</span></div>'
            f'<div class="tn-m"><span class="tn-en">{esc(n["name"])}</span>'
            f'<span class="tn-cat">{esc(n["cat"])}</span></div></div>')

sections = []
for fac in FAC_ORDER:
    en, ko, col, role = FAC[fac]
    cnt = sum(len(v) for v in G[fac].values())
    cols = []
    for t in (1,2,3,4):
        items = sorted(G[fac][t], key=lambda x: x['cost'])
        cards = "\n".join(node_card(n) for n in items)
        cols.append(
            f'<div class="tier"><div class="tier-h"><span class="rom">{ROMAN[t]}</span>Tier {t}'
            f'<span class="tcount">{len(items)}</span></div>{cards}</div>')
    sections.append(
        f'<section class="fac" data-fac="{fac}" style="--col:{col}">'
        f'<div class="fac-h"><span class="dot"></span><h2>{esc(ko)} <span class="fac-en">{esc(en)}</span>'
        f'<span class="fac-n">{cnt}</span></h2><p class="fac-role">{esc(role)}</p></div>'
        f'<div class="tiers">{"".join(cols)}</div></section>')

# faction filter buttons
fbtns = '<button class="fbtn active" data-f="all">전체</button>' + "".join(
    f'<button class="fbtn" data-f="{f}" style="--col:{FAC[f][2]}">{esc(FAC[f][1])}</button>' for f in FAC_ORDER)

total = len(nodes)
HTML = f'''<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>테크트리 (한국어) — 샌드: 레이더스 오브 소피</title>
<meta name="description" content="SAND: Raiders of Sophie 테크트리 한국어 — 3팩션·4티어·{total}개 노드를 검색·열람">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#13100b;--bg2:#1a150e;--panel:#221a10;--edge:#392b1a;--edge2:#4f3a21;--ink:#e9dfcd;--muted:#ab9a7c;--faint:#7d6f56;--brass:#d9a84c;--brass-d:#a9772a}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:"Pretendard","Malgun Gothic",sans-serif;font-size:16px;line-height:1.6;
 background-image:radial-gradient(1100px 460px at 82% -8%,rgba(217,168,76,.07),transparent 60%)}}
a{{color:var(--brass);text-decoration:none}}a:hover{{text-decoration:underline}}
.topbar{{position:sticky;top:0;z-index:50;backdrop-filter:blur(9px);background:rgba(15,11,7,.86);border-bottom:1px solid var(--edge)}}
.topbar .in{{max-width:1180px;margin:0 auto;padding:11px 22px;display:flex;gap:14px;align-items:center}}
.brand{{font-family:"Oswald";font-weight:700;letter-spacing:.2em;color:var(--brass);font-size:17px}}
.tabs{{margin-left:auto;display:flex;gap:6px}}
.tabs a{{font-size:13px;color:var(--muted);padding:6px 13px;border:1px solid var(--edge2);border-radius:6px}}
.tabs a.on{{color:var(--bg);background:var(--brass);border-color:var(--brass);font-weight:600}}
.tabs a:hover{{text-decoration:none;color:var(--brass)}}
.tabs a.on:hover{{color:var(--bg)}}
header.h{{max-width:1180px;margin:0 auto;padding:30px 22px 8px}}
header.h h1{{font-family:"Oswald";font-weight:700;letter-spacing:.04em;font-size:clamp(24px,4vw,34px);margin:0;color:#fff}}
header.h .sub{{color:var(--muted);margin:8px 0 0;font-size:15px;max-width:760px}}
header.h .sub b{{color:var(--brass)}}
.howto{{max-width:1180px;margin:16px auto 0;padding:0 22px}}
.howto .box{{background:linear-gradient(180deg,var(--panel),var(--bg2));border:1px solid var(--edge);border-left:3px solid var(--brass);border-radius:8px;padding:13px 18px;font-size:14px;color:var(--muted)}}
.howto .box b{{color:var(--brass)}}
.ctrl{{position:sticky;top:51px;z-index:40;background:rgba(15,11,7,.92);backdrop-filter:blur(6px);border-bottom:1px solid var(--edge);margin-top:18px}}
.ctrl .in{{max-width:1180px;margin:0 auto;padding:12px 22px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}}
#q{{flex:1;min-width:180px;background:#0d0a06;border:1px solid var(--edge2);color:var(--ink);border-radius:7px;padding:9px 13px;font-size:14px;font-family:inherit}}
#q:focus{{outline:none;border-color:var(--brass)}}
.fbtns{{display:flex;gap:6px;flex-wrap:wrap}}
.fbtn{{font-family:inherit;font-size:12.5px;color:var(--muted);background:transparent;border:1px solid var(--edge2);border-radius:999px;padding:6px 12px;cursor:pointer}}
.fbtn[data-f]:not([data-f=all]){{border-color:color-mix(in srgb,var(--col) 55%,var(--edge2))}}
.fbtn.active{{color:#fff;background:color-mix(in srgb,var(--col,#d9a84c) 26%,transparent);border-color:var(--col,var(--brass))}}
#count{{font-size:12.5px;color:var(--faint);margin-left:auto;white-space:nowrap}}
main{{max-width:1180px;margin:0 auto;padding:6px 22px 80px}}
.fac{{margin:30px 0 0}}
.fac-h{{display:flex;flex-direction:column;gap:2px;padding:12px 0 10px;border-bottom:1px solid var(--edge);position:relative}}
.fac-h h2{{font-family:"Oswald";font-weight:600;font-size:20px;margin:0;color:var(--col);display:flex;align-items:center;gap:10px;letter-spacing:.02em}}
.fac-h .dot{{position:absolute;left:-22px;top:18px;width:9px;height:9px;border-radius:50%;background:var(--col);box-shadow:0 0 10px var(--col)}}
.fac-en{{font-family:"Oswald";color:var(--faint);font-size:13px;font-weight:500;letter-spacing:.03em}}
.fac-n{{font-size:12px;color:var(--bg);background:var(--col);border-radius:999px;padding:1px 9px;font-weight:700}}
.fac-role{{margin:2px 0 0;font-size:13.5px;color:var(--muted)}}
.tiers{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:14px}}
@media(max-width:880px){{.tiers{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:520px){{.tiers{{grid-template-columns:1fr}}}}
.tier-h{{font-family:"Oswald";font-size:12.5px;letter-spacing:.06em;color:var(--muted);text-transform:uppercase;
 display:flex;align-items:center;gap:7px;padding:0 2px 8px;border-bottom:1px dashed var(--edge2);margin-bottom:9px}}
.tier-h .rom{{display:inline-flex;min-width:1.6em;height:1.6em;align-items:center;justify-content:center;background:#0d0a06;border:1px solid var(--col);color:var(--col);border-radius:5px;font-weight:700;font-size:.85em}}
.tier-h .tcount{{margin-left:auto;color:var(--faint);font-weight:500}}
.tn{{background:linear-gradient(180deg,var(--panel),var(--bg2));border:1px solid var(--edge);border-left:3px solid var(--col);
 border-radius:7px;padding:8px 11px;margin:0 0 8px}}
.tn-h{{display:flex;align-items:baseline;gap:8px}}
.tn-ko{{font-weight:600;color:var(--ink);font-size:14px;flex:1}}
.tn-cost{{font-family:"Oswald";color:var(--brass);font-size:13px;font-weight:600;white-space:nowrap}}
.tn-cost::before{{content:"◈ ";color:var(--brass-d);font-size:.85em}}
.tn-m{{display:flex;align-items:center;gap:8px;margin-top:2px}}
.tn-en{{font-family:"Oswald";color:var(--faint);font-size:11px;flex:1;letter-spacing:.02em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.tn-cat{{font-size:10.5px;color:var(--muted);background:#0d0a06;border:1px solid var(--edge2);border-radius:4px;padding:1px 6px;white-space:nowrap}}
.tn.hide,.tier.hide,.fac.hide{{display:none}}
.empty{{color:var(--faint);font-size:12px;padding:6px 2px}}
footer{{border-top:1px solid var(--edge);background:var(--bg2)}}
footer .in{{max-width:1180px;margin:0 auto;padding:22px 22px 44px;color:var(--faint);font-size:12px;line-height:1.65}}
footer b{{color:var(--muted)}}footer a{{color:var(--muted)}}
</style></head>
<body>
<div class="topbar"><div class="in">
  <span class="brand">SAND</span>
  <div class="tabs"><a href="index.html">입문 가이드</a><a class="on" href="tech.html">테크트리</a></div>
</div></div>

<header class="h">
  <h1>테크트리 <span style="color:var(--brass)">한국어</span></h1>
  <p class="sub">연구로 새 트램플러 부품을 해금한다. <b>3개 팩션 · 4개 티어 · {total}개 노드</b>를 한국어로 검색·열람하세요. 영어 UI에서 길을 잃지 않도록.</p>
</header>
<div class="howto"><div class="box">
  <b>읽는 법.</b> 노드를 <b>해금</b>하면 그 부품의 <b>레시피(설계도)만</b> 열립니다 — 실제로 에디터에서 만들 땐 <b>재료가 또</b> 듭니다. 비용 <b>◈는 크라운(Crowns)</b>. 상위 티어는 크라운 외에 희귀 재료(Crystal·Ficus·Black Box 등)도 필요합니다(상세 재료는 <a href="https://github.com/showneykim/sand-kr-guide/blob/main/docs/kb/02_%ED%85%8C%ED%81%AC%ED%8A%B8%EB%A6%AC_%ED%8C%A9%EC%85%98.md">지식베이스</a> 참고).
</div></div>

<div class="ctrl"><div class="in">
  <input id="q" type="search" placeholder="검색 — 한글/영문 부품명, 카테고리 (예: 캐논, 섀시, reactor)" autocomplete="off">
  <div class="fbtns">{fbtns}</div>
  <span id="count"></span>
</div></div>

<main id="tree">
{''.join(sections)}
</main>

<footer><div class="in">
  <p><b>데이터 출처.</b> 테크트리의 노드·비용·구조는 게임 인게임 데이터이며, 커뮤니티 팬 데이터베이스 <a href="https://sand-help.com/tech" target="_blank" rel="noopener">sand-help.com</a>(비공식)을 참조해 교차확인했습니다. 본 페이지는 그 데이터를 <b>한국어로 재구성한 독자 제작물</b>로, sand-help의 코드·디자인을 복제하지 않았습니다. 핵심 비용은 본 가이드 지식베이스의 검증값과 일치함을 확인했습니다.</p>
  <p>비공식 팬 가이드 · 얼리액세스(2026-06-22) 기준이라 수치·명칭은 패치로 바뀔 수 있습니다 — 인게임 확인 권장. 게임의 모든 권리는 Hologryph·TowerHaus·tinyBuild에 있습니다.</p>
</div></footer>

<script>
(function(){{
  var nodes=[].slice.call(document.querySelectorAll('.tn'));
  var tiers=[].slice.call(document.querySelectorAll('.tier'));
  var facs=[].slice.call(document.querySelectorAll('.fac'));
  var q=document.getElementById('q'),count=document.getElementById('count');
  var fsel='all';
  function apply(){{
    var term=q.value.trim().toLowerCase();var shown=0;
    nodes.forEach(function(n){{
      var ok=(fsel==='all'||n.dataset.fac===fsel)&&(!term||n.dataset.s.indexOf(term)>=0);
      n.classList.toggle('hide',!ok); if(ok)shown++;
    }});
    tiers.forEach(function(t){{var any=t.querySelector('.tn:not(.hide)');t.classList.toggle('hide',!any);}});
    facs.forEach(function(f){{var any=f.querySelector('.tn:not(.hide)');f.classList.toggle('hide',!any);}});
    count.textContent=shown+' / {total} 노드';
  }}
  q.addEventListener('input',apply);
  [].slice.call(document.querySelectorAll('.fbtn')).forEach(function(b){{
    b.addEventListener('click',function(){{
      document.querySelectorAll('.fbtn').forEach(function(x){{x.classList.remove('active');}});
      b.classList.add('active');fsel=b.dataset.f;apply();
    }});
  }});
  apply();
}})();
</script>
</body></html>'''

open(os.path.join(ROOT,"tech.html"),"w",encoding="utf-8").write(HTML)
print("wrote tech.html", len(HTML),"bytes ;", total,"nodes")
print("팩션별:", {FAC[f][1]:sum(len(v) for v in G[f].values()) for f in FAC_ORDER})
print("카테고리:", dict(Counter(n['cat'] for n in nodes)))
# sanity: print a few KO names
for n in nodes[:6]: print("  ",n['tier'],n['ko'],"/",n['name'],n['cost'])
