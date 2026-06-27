#!/usr/bin/env python3
# sand-help.com/tech RSC 플라이트 데이터(게임 사실: 노드·비용·재료·선행조건) → 한국어 tech.html
import json, html, re, os

ROOT = os.path.expanduser("~/sand-kr-guide")
SCRATCH = "/tmp/claude-1000/-home-shawnkim/accddb21-599c-4336-be46-bd6fd94b1a98/scratchpad"
nodes = json.load(open(os.path.join(ROOT, "tools/tech_nodes.json")))
DESCP = os.path.join(ROOT, "tools/tech_desc_ko.json")
DESC = json.load(open(DESCP)) if os.path.exists(DESCP) else {}  # slug -> 한국어 설명

FAC = {  # faction slug -> (ko, color, role)
 "godlewski": ("고들레프스키 원정대", "#4493f8", "트램플러의 뼈대와 심장 — 섀시·동력(리액터/엔진/로드)·승무원실·생활·유틸리티"),
 "landwehr":  ("K.K. 란트베어", "#6fb24a", "방어와 백병 화력 — 조타·장갑·개인무기·포실·공성 장비·개량탄"),
 "kaiser":    ("카이저의 친구들", "#e3a008", "대포 화력과 적재 — 캐논/오토캐논/샷건캐논·화물 보관·갑판·섀시 변형"),
}
FAC_ORDER = ["godlewski", "landwehr", "kaiser"]
ROMAN = {1:"I",2:"II",3:"III",4:"IV"}

BASE_KO = {
 "Stairs":"계단","Framed Stairs":"프레임 계단","Crew Room":"승무원실","Captain's Cabin":"선장실",
 "Small Chassis":"소형 섀시","Middling Chassis":"중형 섀시","Great Chassis":"대형 섀시","Royal Chassis":"왕급 섀시",
 "Motor-Reactor":"모터-리액터","Energy Rod":"에너지 로드","Smokeless Energy Rod":"무연 에너지 로드",
 "Small Engine":"소형 엔진","Medium Engine":"중형 엔진","MedKit":"메드킷","Shovel":"삽",
 "Wooden Corridor":"목재 복도","Metal Corridor":"금속 복도","Crafting Materials":"제작 재료","Smoke Grenade":"연막탄",
 "Framed Steering":"프레임 조타","Steering":"조타","Large Open Steering":"대형 개방 조타","Large Framed Steering":"대형 프레임 조타",
 "Small Armament Workshop":"소형 병기 공방","Large Armament Workshop":"대형 병기 공방",
 "Artillery Decks":"포 갑판","Framed Artillery Deck":"프레임 포 갑판","Armored Artillery Decks":"장갑 포 갑판",
 "Framed Armored Artillery Deck":"프레임 장갑 포 갑판","Armored Artillery Compartment":"장갑 포실","Enclosed Artillery Compartment":"밀폐 포실",
 "Wooden Vestibule":"목재 진입구","Armored Vestibule":"장갑 진입구",
 "Weapons":"무기(연구)","Armor":"장갑(연구)","Armor Plate":"장갑판","Improved Ammo":"개량탄",
 "Time Bomb":"시한폭탄","Battering Ram":"충각","Embrasure":"총안","Grenade":"수류탄",
 "Wooden Decks":"목재 갑판","Armored Deck":"장갑 갑판","Balconies":"발코니","Armored Balconies":"장갑 발코니",
 "Cargo Deck":"화물 갑판","Cargo Hold":"화물 적재고","Cargo Bay":"화물칸","Cargo Compartment":"화물 구획",
 "Shotgun Cannon":"샷건 캐논","Auto Cannon":"오토캐논","Autocannon":"오토캐논","Cannon":"캐논","Resources":"자원(연구)",
}
SUFFIX_KO = {"multiple":"여러 종","L-Shape":"L자형","Parallel":"평행형","U-Shape":"U자형","Hole":"구멍","Trench":"참호"}
MAT_KO = {
 "Crowns":"크라운","Black Box":"블랙박스","Alloy Steel":"합금강","Weird Coral":"기이한 산호","Coral Chunk":"산호 덩어리",
 "Mixtures":"혼합물","Raw Aurogen Crystal":"원석 오로젠","Fabric Scraps":"천 조각","Gunpowder":"화약","Threads":"실",
 "Crate of 1889 Chardonnay":"1889 샤르도네 상자","Canned Sea Deer XL":"바다사슴 통조림 XL","Scrap Metal":"고철",
 "Crystal":"크리스탈","Ficus":"피커스","Reinforced Leather Strips":"강화 가죽끈","Scrapped Ammo":"폐탄약",
 "Coral Dust":"산호 가루","Leviathan Skin":"리바이어던 가죽","Metal Rods":"금속 막대",
 "District Officer's Portable Safe":"지구 관리관 금고","Optic Lenses":"광학 렌즈","Weapon Parts":"무기 부품",
 "Fabric":"천","Leviathan Meat":"리바이어던 고기","High-Grade Gunpowder":"고급 화약",
}

def ko_name(en):
    m = re.match(r'^(.*?)\s*\((.+)\)\s*$', en)
    base, suf = (m.group(1), m.group(2)) if m else (en, None)
    ko = BASE_KO.get(base, base)
    if suf: ko += f" ({SUFFIX_KO.get(suf, suf)})"
    return ko

def category(en):
    for ko, pat in [("대포·포",r"Cannon|Artillery"),("화물·자원",r"Cargo|Resources|Crafting Materials"),
        ("동력",r"Reactor|Engine|Energy Rod"),("조타",r"Steering"),("섀시",r"Chassis"),("도구",r"Shovel|Smoke"),
        ("무기·공성",r"Weapons|Ammo|Armament|Grenade|Time Bomb|Battering|Embrasure"),("장갑",r"Armor"),
        ("승무원·생활",r"Crew|Captain|MedKit"),("구조·이동",r"Stairs|Corridor|Deck|Balcon|Vestibule")]:
        if re.search(pat, en, re.I): return ko
    return "기타"

def icon_base(path): return path.rsplit("/",1)[-1] if path else ""

# enrich
slug2 = {}
for n in nodes:
    n["ko"] = ko_name(n["name"])
    n["cat"] = category(n["name"])
    n["facko"] = FAC[n["faction"]][0]
    n["col"] = FAC[n["faction"]][1]
    slug2[n["slug"]] = n

def esc(s): return html.escape(str(s))

# TECH detail map for tooltip
TECH = {}
for n in nodes:
    mats = [[MAT_KO.get(c["name"], c["name"]), c["amount"], icon_base(c.get("icon",""))]
            for c in n.get("costs", []) if c["name"] != "Crowns"]
    pre = [slug2[p]["ko"] for p in n.get("prereqs", []) if p in slug2]
    TECH[n["slug"]] = {
        "ko": n["ko"], "en": n["name"], "fac": n["facko"], "col": n["col"],
        "tier": ROMAN[n["tier"]], "cat": n["cat"], "crowns": n["crowns"],
        "mats": mats, "pre": pre,
        "unlocks": [[u.get("name",""), icon_base(u.get("icon","")), DESC.get(u.get("slug",""),"")]
                    for u in (n.get("unlocks") or [])],
    }

# group
from collections import defaultdict, Counter
G = defaultdict(lambda: defaultdict(list))
for n in nodes: G[n["faction"]][n["tier"]].append(n)

def node_card(n):
    key = (n["ko"]+" "+n["name"]+" "+n["name"].replace(" ","")+" "+n["cat"]).lower()
    ico = "assets/tech_icons/" + icon_base(n.get("glyphIcon"))
    return (f'<div class="tn" data-s="{esc(key)}" data-fac="{n["faction"]}" data-slug="{esc(n["slug"])}" tabindex="0">'
            f'<img class="tn-ico" src="{esc(ico)}" alt="" loading="lazy" decoding="async">'
            f'<div class="tn-body">'
            f'<span class="tn-ko">{esc(n["ko"])}</span>'
            f'<span class="tn-en" title="{esc(n["name"])}">{esc(n["name"])}</span>'
            f'<span class="tn-foot">'
            f'<span class="tn-cost"><img class="coin" src="assets/tech_icons/icon_item_coinCrown.png" alt="">{n["crowns"]:,}<span class="sr-only"> 크라운</span></span>'
            f'<span class="tn-cat">{esc(n["cat"])}</span></span>'
            f'</div></div>')

sections = []
for fac in FAC_ORDER:
    ko, col, role = FAC[fac]
    cnt = sum(len(v) for v in G[fac].values())
    cols = []
    for t in (1,2,3,4):
        items = sorted(G[fac][t], key=lambda x: x["crowns"])
        cards = "\n".join(node_card(n) for n in items)
        cols.append(f'<div class="tier"><div class="tier-h"><span class="rom">{ROMAN[t]}</span>Tier {t}'
                    f'<span class="tcount">{len(items)}</span></div>{cards}</div>')
    sections.append(
        f'<section class="fac" data-fac="{fac}" style="--col:{col}">'
        f'<div class="fac-h"><span class="dot"></span><h2>{esc(ko)} <span class="fac-en">{esc(fac.upper())}</span>'
        f'<span class="fac-n">{cnt}</span></h2><p class="fac-role">{esc(role)}</p></div>'
        f'<div class="tiers">{"".join(cols)}</div></section>')

fbtns = '<button class="fbtn active" data-f="all" aria-pressed="true">전체</button>' + "".join(
    f'<button class="fbtn" data-f="{f}" aria-pressed="false" style="--col:{FAC[f][1]}">{esc(FAC[f][0])}</button>' for f in FAC_ORDER)

total = len(nodes)
TECH_JSON = json.dumps(TECH, ensure_ascii=False)

HTML = f'''<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>테크트리 (한국어) — 샌드: 레이더스 오브 소피</title>
<meta name="description" content="SAND: Raiders of Sophie 테크트리 한국어 — 3진영·4티어·{total}개 노드. 호버하면 재료·선행연구 표시">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#13100b;--bg2:#1a150e;--panel:#221a10;--edge:#392b1a;--edge2:#4f3a21;--ink:#e9dfcd;--muted:#ab9a7c;--faint:#7d6f56;--brass:#d9a84c;--brass-d:#a9772a}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:"Pretendard","Malgun Gothic",sans-serif;font-size:16px;line-height:1.6;
 background-image:radial-gradient(1100px 460px at 82% -8%,rgba(217,168,76,.07),transparent 60%)}}
a{{color:var(--brass);text-decoration:none}}a:hover{{text-decoration:underline}}
.sr-only{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}
.topbar{{position:sticky;top:0;z-index:50;backdrop-filter:blur(9px);background:rgba(15,11,7,.86);border-bottom:1px solid var(--edge)}}
.topbar .in{{max-width:1180px;margin:0 auto;padding:11px 22px;display:flex;gap:14px;align-items:center}}
.brand{{font-family:"Oswald",sans-serif;font-weight:700;letter-spacing:.2em;color:var(--brass);font-size:17px}}
.tabs{{margin-left:auto;display:flex;gap:6px}}
.tabs a{{font-size:13px;color:var(--muted);padding:6px 13px;border:1px solid var(--edge2);border-radius:6px}}
.tabs a.on{{color:var(--bg);background:var(--brass);border-color:var(--brass);font-weight:600}}
.tabs a:hover{{text-decoration:none;color:var(--brass)}}.tabs a.on:hover{{color:var(--bg)}}
header.h{{max-width:1180px;margin:0 auto;padding:30px 22px 8px}}
header.h h1{{font-family:"Oswald",sans-serif;font-weight:700;letter-spacing:.04em;font-size:clamp(24px,4vw,34px);margin:0;color:#fff}}
header.h .sub{{color:var(--muted);margin:8px 0 0;font-size:15px;max-width:780px}}
header.h .sub b{{color:var(--brass)}}
.howto{{max-width:1180px;margin:16px auto 0;padding:0 22px}}
.howto .box{{background:linear-gradient(180deg,var(--panel),var(--bg2));border:1px solid var(--edge);border-left:3px solid var(--brass);border-radius:8px;padding:13px 18px;font-size:14px;color:var(--muted)}}
.howto .box b{{color:var(--brass)}}
.ctrl{{position:sticky;top:56px;z-index:40;background:rgba(15,11,7,.92);backdrop-filter:blur(6px);border-bottom:1px solid var(--edge);margin-top:18px}}
.ctrl .in{{max-width:1180px;margin:0 auto;padding:12px 22px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}}
#q{{flex:1;min-width:180px;background:#0d0a06;border:1px solid var(--edge2);color:var(--ink);border-radius:7px;padding:9px 13px;font-size:14px;font-family:inherit}}
#q:focus{{outline:none;border-color:var(--brass)}}
.fbtns{{display:flex;gap:6px;flex-wrap:wrap}}
.fbtn{{font-family:inherit;font-size:12.5px;color:var(--muted);background:transparent;border:1px solid var(--edge2);border-radius:999px;padding:6px 12px;cursor:pointer}}
.fbtn[data-f]:not([data-f=all]){{border-color:var(--edge2);border-color:color-mix(in srgb,var(--col) 55%,var(--edge2))}}
.fbtn.active{{color:#fff;border-color:var(--col,var(--brass));background:rgba(217,168,76,.22);background:color-mix(in srgb,var(--col,#d9a84c) 26%,transparent)}}
#count{{font-size:12.5px;color:var(--faint);margin-left:auto;white-space:nowrap}}
main{{max-width:1180px;margin:0 auto;padding:6px 22px 80px}}
.fac{{margin:30px 0 0}}
.fac-h{{display:flex;flex-direction:column;gap:2px;padding:12px 0 10px;border-bottom:1px solid var(--edge);position:relative}}
.fac-h h2{{font-family:"Oswald",sans-serif;font-weight:600;font-size:20px;margin:0;color:var(--col);display:flex;align-items:center;gap:10px;letter-spacing:.02em}}
.fac-h .dot{{position:absolute;left:-22px;top:18px;width:9px;height:9px;border-radius:50%;background:var(--col);box-shadow:0 0 10px var(--col)}}
.fac-en{{font-family:"Oswald",sans-serif;color:var(--faint);font-size:13px;font-weight:500;letter-spacing:.08em}}
.fac-n{{font-size:12px;color:var(--bg);background:var(--col);border-radius:999px;padding:1px 9px;font-weight:700}}
.fac-role{{margin:2px 0 0;font-size:13.5px;color:var(--muted)}}
.tiers{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:14px}}
@media(max-width:880px){{.tiers{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:520px){{.tiers{{grid-template-columns:1fr}}}}
.tier-h{{font-family:"Oswald",sans-serif;font-size:12.5px;letter-spacing:.06em;color:var(--muted);text-transform:uppercase;
 display:flex;align-items:center;gap:7px;padding:0 2px 8px;border-bottom:1px dashed var(--edge2);margin-bottom:9px}}
.tier-h .rom{{display:inline-flex;min-width:1.6em;height:1.6em;align-items:center;justify-content:center;background:#0d0a06;border:1px solid var(--col);color:var(--col);border-radius:5px;font-weight:700;font-size:.85em}}
.tier-h .tcount{{margin-left:auto;color:var(--faint);font-weight:500}}
.tn{{display:flex;gap:10px;align-items:center;background:linear-gradient(180deg,#241b11,#191309);border:1px solid var(--edge);
 border-left:3px solid var(--col);border-radius:8px;padding:7px 9px;margin:0 0 8px;cursor:help;transition:transform .08s ease,border-color .12s,box-shadow .12s}}
.tn:hover,.tn:focus{{transform:translateY(-1px);box-shadow:0 6px 18px rgba(0,0,0,.35);outline:none;border-color:color-mix(in srgb,var(--col) 45%,var(--edge))}}
.tn-ico{{width:54px;height:54px;flex:none;object-fit:contain;padding:3px;border:1px solid var(--edge2);border-radius:7px;
 background:radial-gradient(circle at 50% 36%,rgba(255,255,255,.07),transparent 70%),#0d0a06}}
.tn-body{{flex:1;min-width:0}}
.tn-ko{{display:block;font-weight:600;color:var(--ink);font-size:13.5px;line-height:1.25}}
.tn-en{{display:block;font-family:"Oswald",sans-serif;color:var(--muted);font-size:10.5px;letter-spacing:.02em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:1px}}
.tn-foot{{display:flex;align-items:center;gap:8px;margin-top:4px}}
.tn-cost{{display:inline-flex;align-items:center;gap:4px;font-family:"Oswald",sans-serif;color:var(--brass);font-size:12.5px;font-weight:600;white-space:nowrap}}
.tn-cost .coin{{width:15px;height:15px;object-fit:contain}}
.tn-cat{{font-size:10px;color:var(--muted);background:#0d0a06;border:1px solid var(--edge2);border-radius:4px;padding:1px 6px;white-space:nowrap;margin-left:auto}}
.tn.hide,.tier.hide,.fac.hide{{display:none}}
.empty{{color:var(--faint);font-size:13px;padding:20px 2px}}
/* tooltip */
#tip{{position:fixed;z-index:100;max-width:300px;min-width:210px;display:none;pointer-events:none;
 background:linear-gradient(180deg,#251c12,#140f09);border:1px solid var(--edge2);border-left:3px solid var(--col,#d9a84c);
 border-radius:9px;padding:12px 14px;box-shadow:0 18px 50px rgba(0,0,0,.62);font-size:13px;color:var(--ink)}}
#tip.on{{display:block}}
#tip .t-h{{display:flex;align-items:baseline;gap:7px;flex-wrap:wrap}}
#tip .t-ko{{font-weight:700;font-size:15px}}
#tip .t-en{{font-family:"Oswald",sans-serif;color:var(--muted);font-size:11px;letter-spacing:.02em}}
#tip .t-meta{{color:var(--muted);font-size:11.5px;margin:3px 0 2px}}
#tip .t-meta b{{color:var(--col,#d9a84c)}}
#tip .t-sec{{font-family:"Oswald",sans-serif;font-size:10px;letter-spacing:.06em;color:var(--faint);text-transform:uppercase;margin:9px 0 4px}}
#tip .m{{display:flex;align-items:center;gap:7px;margin:3px 0;font-size:12.5px}}
#tip .m img{{width:19px;height:19px;object-fit:contain;flex:none}}
#tip .m .amt{{margin-left:auto;font-family:"Oswald",sans-serif;color:var(--brass);font-weight:600}}
#tip .m.crown .amt{{color:#e7c87a}}
#tip .t-pre{{font-size:12px;color:var(--muted);line-height:1.5}}
#tip .u{{display:flex;gap:7px;margin:5px 0}}
#tip .u img{{width:28px;height:28px;object-fit:contain;flex:none;border:1px solid var(--edge2);border-radius:5px;background:#0d0a06;padding:2px}}
#tip .u-n{{font-weight:600;color:var(--ink);font-size:12px;line-height:1.3}}
#tip .u-d{{color:var(--muted);font-size:11px;line-height:1.45;margin-top:1px}}
#tip .t-note{{margin-top:9px;padding-top:8px;border-top:1px solid var(--edge);font-size:10.5px;color:var(--faint);line-height:1.5}}
footer{{border-top:1px solid var(--edge);background:var(--bg2)}}
footer .in{{max-width:1180px;margin:0 auto;padding:22px 22px 44px;color:var(--faint);font-size:12px;line-height:1.65}}
footer b{{color:var(--muted)}}footer a{{color:var(--muted)}}
</style></head>
<body>
<div class="topbar"><div class="in">
  <span class="brand">SAND</span>
  <div class="tabs"><a href="index.html">입문 가이드</a><a class="on" href="tech.html">테크트리</a><a href="items.html">아이템 도감</a></div>
</div></div>

<header class="h">
  <h1>테크트리 <span style="color:var(--brass)">한국어</span></h1>
  <p class="sub">연구로 새 트램플러 부품을 해금합니다. <b>3개 진영 · 4개 티어 · {total}개 노드</b>를 한국어로 검색·열람하세요. <b>노드에 마우스를 올리면(또는 탭하면) 재료·선행연구</b>가 나옵니다.</p>
</header>
<div class="howto"><div class="box">
  <b>읽는 법.</b> 노드를 <b>해금</b>하면 그 부품의 <b>레시피(설계도)만</b> 열립니다 — 실제로 에디터에서 만들 땐 <b>재료가 또</b> 듭니다. 비용의 <b>동전은 크라운(Crowns)</b>. <b>노드에 호버/탭</b>하면 필요한 재료와 선행연구가 표시됩니다(상세 표는 <a href="https://github.com/showneykim/sand-kr-guide/blob/main/docs/kb/02_%ED%85%8C%ED%81%AC%ED%8A%B8%EB%A6%AC_%ED%8C%A9%EC%85%98.md">지식베이스</a>).
</div></div>

<div class="ctrl"><div class="in">
  <input id="q" type="search" aria-label="부품 이름·카테고리 검색" placeholder="검색 — 한글/영문 부품명, 카테고리 (예: 캐논, 섀시, reactor)" autocomplete="off">
  <div class="fbtns">{fbtns}</div>
  <span id="count"></span>
</div></div>

<main id="tree">
{''.join(sections)}
</main>

<div id="tip" role="tooltip" aria-hidden="true"></div>

<footer><div class="in">
  <p><b>데이터 출처.</b> 테크트리의 노드·비용·재료·선행조건은 게임 인게임 데이터이며, 커뮤니티 팬 데이터베이스 <a href="https://sand-help.com/tech" target="_blank" rel="noopener">sand-help.com</a>(비공식)에서 가져와 교차확인했습니다. 노드·재료 아이콘은 게임 내 에셋입니다. 본 페이지는 이 데이터를 <b>한국어로 재구성한 독자 제작물</b>로, sand-help의 코드·디자인 자체는 복제하지 않았습니다. 핵심 비용은 본 가이드 지식베이스의 검증값과 일치함을 확인했습니다.</p>
  <p>비공식 팬 가이드 · 얼리액세스(2026-06-22) 기준이라 수치·명칭은 패치로 바뀔 수 있습니다 — 인게임 확인 권장. 게임의 모든 권리는 Hologryph·TowerHaus·tinyBuild에 있습니다.</p>
</div></footer>

<script>
var TECH={TECH_JSON};
(function(){{
  var nodes=[].slice.call(document.querySelectorAll('.tn'));
  var tiers=[].slice.call(document.querySelectorAll('.tier'));
  var facs=[].slice.call(document.querySelectorAll('.fac'));
  var q=document.getElementById('q'),count=document.getElementById('count');
  var fsel='all';
  var emptyEl=document.createElement('p');emptyEl.className='empty';emptyEl.setAttribute('role','status');
  emptyEl.textContent='검색 결과가 없습니다.';emptyEl.style.display='none';
  document.getElementById('tree').appendChild(emptyEl);
  function apply(){{
    var term=q.value.trim().toLowerCase();var shown=0;
    nodes.forEach(function(n){{
      var ok=(fsel==='all'||n.dataset.fac===fsel)&&(!term||n.dataset.s.indexOf(term)>=0);
      n.classList.toggle('hide',!ok); if(ok)shown++;
    }});
    tiers.forEach(function(t){{t.classList.toggle('hide',!t.querySelector('.tn:not(.hide)'));}});
    facs.forEach(function(f){{f.classList.toggle('hide',!f.querySelector('.tn:not(.hide)'));}});
    emptyEl.style.display=shown?'none':'block';
    count.textContent=shown+' / '+nodes.length+' 노드';
  }}
  q.addEventListener('input',apply);
  [].slice.call(document.querySelectorAll('.fbtn')).forEach(function(b){{
    b.addEventListener('click',function(){{
      document.querySelectorAll('.fbtn').forEach(function(x){{x.classList.remove('active');x.setAttribute('aria-pressed','false');}});
      b.classList.add('active');b.setAttribute('aria-pressed','true');fsel=b.dataset.f;apply();
    }});
  }});
  apply();

  // ---- 호버 툴팁: 재료·선행연구 ----
  var tip=document.getElementById('tip'),pinned=null;
  function esc(s){{return String(s).replace(/[&<>]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c];}});}}
  function fmt(n){{return n.toLocaleString('en-US');}}
  function build(d){{
    var mats=d.mats.map(function(m){{return '<div class="m"><img src="assets/tech_icons/'+esc(m[2])+'" alt="">'+esc(m[0])+'<span class="amt">×'+fmt(m[1])+'</span></div>';}}).join('');
    var pre=d.pre.length?('<div class="t-sec">선행 연구</div><div class="t-pre">'+d.pre.map(esc).join(' · ')+'</div>'):'';
    var unl=(d.unlocks&&d.unlocks.length)?('<div class="t-sec">해금 아이템</div>'+d.unlocks.map(function(u){{return '<div class="u"><img src="assets/tech_icons/'+esc(u[1])+'" alt=""><div><div class="u-n">'+esc(u[0])+'</div>'+(u[2]?'<div class="u-d">'+esc(u[2])+'</div>':'')+'</div></div>';}}).join('')):'';
    return '<div class="t-h"><span class="t-ko">'+esc(d.ko)+'</span><span class="t-en">'+esc(d.en)+'</span></div>'
      +'<div class="t-meta"><b>'+esc(d.fac)+'</b> · Tier '+esc(d.tier)+' · '+esc(d.cat)+'</div>'
      +unl
      +'<div class="t-sec">해금 비용</div>'
      +'<div class="m crown"><img src="assets/tech_icons/icon_item_coinCrown.png" alt="">크라운<span class="amt">'+fmt(d.crowns)+'</span></div>'
      +mats+pre
      +'<div class="t-note">해금 = 레시피만 열림. 제작 시 재료가 또 듭니다. (EA — 변동 가능)</div>';
  }}
  function place(card){{
    var r=card.getBoundingClientRect(),tw=tip.offsetWidth,th=tip.offsetHeight,m=10;
    var x=r.right+m; if(x+tw>window.innerWidth-8)x=r.left-tw-m; if(x<8)x=8;
    var y=r.top; if(y+th>window.innerHeight-8)y=window.innerHeight-th-8; if(y<8)y=8;
    tip.style.left=x+'px';tip.style.top=y+'px';
  }}
  function show(card){{
    var d=TECH[card.dataset.slug]; if(!d)return;
    tip.style.setProperty('--col',d.col); tip.innerHTML=build(d);
    tip.classList.add('on'); tip.setAttribute('aria-hidden','false'); place(card);
  }}
  function hide(){{ if(pinned)return; tip.classList.remove('on'); tip.setAttribute('aria-hidden','true'); }}
  nodes.forEach(function(c){{
    c.addEventListener('pointerenter',function(){{ if(!pinned) show(c); }});
    c.addEventListener('pointerleave',hide);
    c.addEventListener('focus',function(){{ show(c); }});
    c.addEventListener('blur',hide);
    c.addEventListener('click',function(e){{ e.stopPropagation(); if(pinned===c){{pinned=null;hide();}} else {{pinned=c;show(c);}} }});
  }});
  document.addEventListener('click',function(){{ if(pinned){{pinned=null;tip.classList.remove('on');}} }});
  document.addEventListener('keydown',function(e){{ if(e.key==='Escape'){{pinned=null;tip.classList.remove('on');}} }});
  window.addEventListener('scroll',function(){{ if(pinned)place(pinned); }},{{passive:true}});
}})();
</script>
</body></html>'''

HTML = HTML.replace('{TECH_JSON}', TECH_JSON)
HTML = HTML.replace('font-family:"Oswald"', 'font-family:"Oswald",sans-serif')
open(os.path.join(ROOT, "tech.html"), "w", encoding="utf-8").write(HTML)
print("wrote tech.html", len(HTML), "bytes ;", total, "nodes")
print("진영:", {FAC[f][0]: sum(len(v) for v in G[f].values()) for f in FAC_ORDER})
print("티어:", dict(Counter(n["tier"] for n in nodes)))
print("재료 있는 노드:", sum(1 for n in nodes if TECH[n["slug"]]["mats"]), "/ prereq 있는:", sum(1 for n in nodes if TECH[n["slug"]]["pre"]))
