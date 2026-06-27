#!/usr/bin/env python3
# sand-help 아이템 123개 상세 데이터 → 한국어 아이템 도감 items.html
import json, html, os, re

ROOT = os.path.expanduser("~/sand-kr-guide")
SCRATCH = "/tmp/claude-1000/-home-shawnkim/accddb21-599c-4336-be46-bd6fd94b1a98/scratchpad"
data = json.load(open(os.path.join(ROOT, "tools/items_data.json")))["items"]
icons = json.load(open(os.path.join(ROOT, "tools/items_slugs.json")))["icons"]

CAT_KO = {"Weapons":"무기","Artillery":"포·대포","Resources":"자원","Attire":"의복·방어구",
          "Tools":"도구","Medical":"의료","Ammo":"탄약","Misc":"기타"}
CAT_ORDER = ["Weapons","Artillery","Ammo","Medical","Tools","Attire","Resources","Misc"]
CAT_COL = {"Weapons":"#c1572a","Artillery":"#e3a008","Ammo":"#d9a84c","Medical":"#8aae66",
           "Tools":"#6fa3bd","Attire":"#b07d8a","Resources":"#9a8358","Misc":"#7d6f56"}
STAT_KO = {"Range":"사거리","Reload":"재장전","Damage":"피해","Magazine":"탄창","Type":"종류",
  "Rate of Fire":"연사 속도","Fire Rate":"연사 속도","Accuracy":"명중률","Penetration":"관통",
  "Capacity":"용량","Weight":"무게","Energy":"에너지","Duration":"지속시간","Healing":"회복량",
  "Workbench tier":"작업대 티어","Workbench Tier":"작업대 티어","Sell Value":"판매가","Category":"카테고리",
  "Spread":"탄퍼짐","Magazine Size":"탄창","Caliber":"구경","Value":"가치","Slot":"슬롯","Ammo":"탄약",
  "Armor":"장갑","Fire rate":"연사 속도","Penetrates":"관통","Rarity":"희귀도","Regen":"재생","Splash Damage":"범위 피해",
  "Velocity":"탄속","Damage (Player)":"피해(플레이어)","Damage (Trampler)":"피해(트램플러)"}
VALUE_KO = {
  "Autocannon":"오토캐논","Carryable Object":"휴대품","Carryable Objects":"휴대품","Energetic":"에너지 무기",
  "Food":"식량","Grenade":"수류탄","Medical Supplies":"의료품","Money":"화폐","Raw Materials":"원자재",
  "Shotgun":"샷건","Single-Shot Rifle":"단발 라이플","Semi-Automatic Pistol":"반자동 권총","Pistol":"권총",
  "Revolver":"리볼버","Rifle":"라이플","Naval":"함포","Sniper":"저격","Rocket":"로켓","Valuables":"귀중품",
  "Common":"일반","Uncommon":"고급","Rare":"희귀","Noteworthy":"특별","Yes":"예","No":"아니오"}
MAT_KO = {"Scrap Metal":"고철","Metal Rods":"금속 막대","Weapon Parts":"무기 부품","Mechanical Parts":"기계 부품",
  "Fabric":"천","Fabric Scraps":"천 조각","Threads":"실","Gunpowder":"화약","High-Grade Gunpowder":"고급 화약",
  "Scrapped Ammo":"폐탄약","Optic Lenses":"광학 렌즈","Reinforced Leather Strips":"강화 가죽끈","Mixtures":"혼합물",
  "Coral Chunk":"산호 덩어리","Coral Dust":"산호 가루","Weird Coral":"기이한 산호","Crystal":"크리스탈","Ficus":"피커스",
  "Black Box":"블랙박스","Alloy Steel":"합금강","Leviathan Skin":"리바이어던 가죽","Leviathan Meat":"리바이어던 고기",
  "Raw Aurogen Crystal":"원석 오로젠","Computing Modules":"연산 모듈","Pneumatic Parts":"공압 부품","Medkit":"메드킷"}

def esc(s): return html.escape(str(s or ""))
def ko_cat(c): return CAT_KO.get(c, c or "기타")
def ko_stat(l): return STAT_KO.get(l, l)
def ko_mat(m): return MAT_KO.get(m, m)
def ko_val(v):
    v = str(v or "")
    if v in VALUE_KO: return VALUE_KO[v]
    v = re.sub(r'\bCrowns?\b', '크라운', v)
    v = v.replace('delay', '지연')
    return v
OBT_TERMS = [
 ("Suspicious Pile of Sand","수상한 모래 더미"),("Valuables Safe","귀중품 금고"),("Medical Cabinet","의료 보관함"),
 ("Weapon Crate","무기 상자"),("Food Crate","식량 상자"),("Crate of Shells","포탄 상자"),
 ("Ironclad Loot Box","아이언클래드 전리품 상자"),("District Officer's Portable Safe","구역 담당관 금고"),
 ("Crate of 1889 Chardonnay","1889 샤르도네 상자"),("Canned Sea Deer XL","바다사슴 통조림 XL"),
 ("Dreadnought crates","드레드노트 상자"),("Very Rare","매우 희귀"),("drop rate","드롭률"),
 ("Purchasable via","구매 —"),("Purchase with","구매 —"),("Purchase","구매"),
 ("Unlocked by","해금 —"),("Unlocked via","해금 —"),("after unlocking","해금 후"),
 ("tech unlock","테크 해금"),("technology","테크"),("tech","테크"),
 ("Crowns","크라운"),("Crown","크라운"),("Crafted","제작"),("Loot","전리품"),("Buy","구매"),
 ("Scrapped Ammo","폐탄약"),("Leviathan Skin","리바이어던 가죽"),("produces","생산"),
 ("Armament","병기 공방"),("Utility","유틸리티"),("Workbench","작업대"),("Tier","티어"),
]
def ko_obt(s):
    s = str(s or "")
    for en, ko in OBT_TERMS: s = s.replace(en, ko)
    return s
def icon_of(it):
    ic = icons.get(it["slug"])
    return "assets/tech_icons/" + ic.rsplit("/",1)[-1] if ic else ""

for it in data:
    it["_icon"] = icon_of(it)
    it["_catko"] = ko_cat(it.get("category"))

# group by category
from collections import defaultdict, Counter
G = defaultdict(list)
for it in data: G[it.get("category","Misc")].append(it)
def cat_key(c): return CAT_ORDER.index(c) if c in CAT_ORDER else 99

# DETAIL map for modal (index -> full)
DETAIL = []
for it in data:
    DETAIL.append({
        "name": it.get("name",""), "cat": it["_catko"], "col": CAT_COL.get(it.get("category"),"#d9a84c"),
        "icon": it["_icon"], "desc": it.get("description_ko","") or it.get("description_en",""),
        "stats": [[ko_stat(s["label"]), ko_val(s["value"])] for s in it.get("stats",[])],
        "recipe": [[ko_mat(r["item"]), r["amount"]] for r in it.get("recipe",[])],
        "workbench": ko_obt(it.get("workbench","")), "sell": ko_val(it.get("sellValue","")),
        "obtained": [ko_obt(o) for o in it.get("obtainedFrom",[])],
        "usedIn": [ko_obt(u) for u in it.get("usedIn",[])], "ammo": it.get("compatibleAmmo",[]),
    })
slug2idx = {it["slug"]: i for i,it in enumerate(data)}

def card(it, idx):
    snip = (it.get("description_ko") or it.get("description_en") or "")[:46]
    col = CAT_COL.get(it.get("category"),"#d9a84c")
    key = (it.get("name","")+" "+it["_catko"]+" "+(it.get("description_ko") or "")).lower()
    return (f'<button class="it" data-i="{idx}" data-cat="{esc(it.get("category","Misc"))}" data-s="{esc(key)}" style="--col:{col}">'
            f'<img class="it-ic" src="{esc(it["_icon"])}" alt="" loading="lazy" decoding="async">'
            f'<span class="it-body"><span class="it-n">{esc(it.get("name",""))}</span>'
            f'<span class="it-c">{esc(it["_catko"])}</span>'
            f'<span class="it-d">{esc(snip)}</span></span></button>')

cards = []
for i,it in enumerate(data):
    cards.append(card(it, i))
cards_html = "\n".join(cards)

fbtns = '<button class="fbtn active" data-f="all" aria-pressed="true">전체</button>' + "".join(
    f'<button class="fbtn" data-f="{c}" aria-pressed="false" style="--col:{CAT_COL[c]}">{esc(CAT_KO[c])}</button>'
    for c in CAT_ORDER if G.get(c))

total = len(data)
DETAIL_JSON = json.dumps(DETAIL, ensure_ascii=False)

HTML = f'''<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>아이템 도감 (한국어) — 샌드: 레이더스 오브 소피</title>
<meta name="description" content="SAND: Raiders of Sophie 아이템 도감 한국어 — {total}개 아이템의 설명·스탯·제작·획득처">
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
@media(max-width:520px){{.topbar .in{{padding:9px 12px;gap:8px;flex-wrap:wrap}}.brand{{font-size:15px}}.tabs a{{padding:5px 9px;font-size:12px}}}}
header.h{{max-width:1180px;margin:0 auto;padding:30px 22px 8px}}
header.h h1{{font-family:"Oswald",sans-serif;font-weight:700;letter-spacing:.04em;font-size:clamp(24px,4vw,34px);margin:0;color:#fff}}
header.h .sub{{color:var(--muted);margin:8px 0 0;font-size:15px;max-width:780px}}
header.h .sub b{{color:var(--brass)}}
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
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(225px,1fr));gap:11px}}
.it{{display:flex;gap:10px;align-items:center;text-align:left;font-family:inherit;cursor:pointer;
 background:linear-gradient(180deg,#241b11,#191309);border:1px solid var(--edge);border-left:3px solid var(--col);
 border-radius:8px;padding:8px 10px;transition:transform .08s,border-color .12s,box-shadow .12s;color:var(--ink)}}
.it:hover,.it:focus{{transform:translateY(-1px);box-shadow:0 6px 18px rgba(0,0,0,.35);outline:none;border-color:color-mix(in srgb,var(--col) 50%,var(--edge))}}
.it-ic{{width:46px;height:46px;flex:none;object-fit:contain;padding:2px;border:1px solid var(--edge2);border-radius:7px;
 background:radial-gradient(circle at 50% 36%,rgba(255,255,255,.07),transparent 70%),#0d0a06}}
.it-body{{min-width:0;display:flex;flex-direction:column}}
.it-n{{font-weight:600;font-size:13px;line-height:1.2;color:var(--ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.it-c{{font-size:10.5px;color:var(--col);font-weight:600;margin-top:1px}}
.it-d{{font-size:11px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:2px}}
.it.hide{{display:none}}
.empty{{color:var(--faint);font-size:13px;padding:24px 2px}}
/* modal */
#ov{{position:fixed;inset:0;z-index:100;background:rgba(8,6,4,.78);backdrop-filter:blur(3px);display:none;align-items:center;justify-content:center;padding:20px}}
#ov.on{{display:flex}}
#mod{{max-width:540px;width:100%;max-height:88vh;overflow:auto;background:linear-gradient(180deg,#251c12,#15100b);
 border:1px solid var(--edge2);border-left:4px solid var(--col,#d9a84c);border-radius:12px;box-shadow:0 30px 80px rgba(0,0,0,.6)}}
#mod .m-h{{display:flex;gap:13px;align-items:center;padding:18px 20px 12px;position:sticky;top:0;background:linear-gradient(180deg,#251c12,#241b11);border-bottom:1px solid var(--edge)}}
#mod .m-ic{{width:64px;height:64px;flex:none;object-fit:contain;padding:4px;border:1px solid var(--edge2);border-radius:9px;background:radial-gradient(circle at 50% 36%,rgba(255,255,255,.08),transparent 70%),#0d0a06}}
#mod .m-tt{{flex:1;min-width:0}}
#mod .m-n{{font-weight:700;font-size:17px;color:#fff;line-height:1.25}}
#mod .m-c{{font-size:12px;color:var(--col,#d9a84c);font-weight:600;margin-top:2px}}
#mod .m-x{{flex:none;background:transparent;border:1px solid var(--edge2);color:var(--muted);border-radius:7px;width:32px;height:32px;font-size:17px;cursor:pointer}}
#mod .m-x:hover{{color:var(--brass);border-color:var(--brass)}}
#mod .m-b{{padding:14px 20px 22px}}
#mod .m-desc{{font-size:14px;color:var(--ink);line-height:1.65;margin:0 0 14px}}
#mod .sec{{font-family:"Oswald",sans-serif;font-size:11px;letter-spacing:.06em;color:var(--faint);text-transform:uppercase;margin:16px 0 6px;border-bottom:1px solid var(--edge);padding-bottom:4px}}
#mod .row{{display:flex;justify-content:space-between;gap:10px;font-size:13.5px;padding:3px 0;border-bottom:1px dashed rgba(79,58,33,.5)}}
#mod .row:last-child{{border-bottom:0}}
#mod .row .k{{color:var(--muted)}}#mod .row .v{{color:var(--ink);font-weight:600;font-family:"Oswald",sans-serif}}
#mod .chips{{display:flex;flex-wrap:wrap;gap:6px}}
#mod .chip{{font-size:12px;color:var(--ink);background:#0d0a06;border:1px solid var(--edge2);border-radius:6px;padding:3px 9px}}
#mod .chip b{{color:var(--brass);font-family:"Oswald",sans-serif}}
footer{{border-top:1px solid var(--edge);background:var(--bg2)}}
footer .in{{max-width:1180px;margin:0 auto;padding:22px 22px 44px;color:var(--muted);font-size:12px;line-height:1.65}}
footer b{{color:var(--muted)}}footer a{{color:var(--muted)}}
</style></head>
<body>
<div class="topbar"><div class="in">
  <span class="brand">SAND</span>
  <div class="tabs"><a href="index.html">입문 가이드</a><a href="tech.html">테크트리</a><a class="on" href="items.html">아이템 도감</a></div>
</div></div>

<header class="h">
  <h1>아이템 도감 <span style="color:var(--brass)">한국어</span></h1>
  <p class="sub"><b>{total}개 아이템</b>의 한국어 설명·스탯·제작 레시피·획득처·판매가. 카드를 <b>클릭하면 상세</b>가 열립니다. 무기·포·탄약·자원·도구·의료·의복까지.</p>
</header>

<div class="ctrl"><div class="in">
  <input id="q" type="search" aria-label="아이템 검색" placeholder="검색 — 이름·카테고리·설명 (예: 라이플, 산호, reactor)" autocomplete="off">
  <div class="fbtns">{fbtns}</div>
  <span id="count"></span>
</div></div>

<main><div class="grid" id="grid">
{cards_html}
</div></main>

<div id="ov" role="dialog" aria-modal="true"><div id="mod"></div></div>

<footer><div class="in">
  <p><b>데이터 출처.</b> 아이템 이름·설명·스탯·제작·획득처는 게임 인게임 데이터이며, 커뮤니티 팬 데이터베이스 <a href="https://sand-help.com" target="_blank" rel="noopener">sand-help.com</a>(비공식)에서 가져와 한국어로 재구성했습니다. 아이템 아이콘은 게임 내 에셋입니다. sand-help의 코드·디자인은 복제하지 않았습니다.</p>
  <p>비공식 팬 가이드 · 얼리액세스(2026-06-22) 기준이라 수치·명칭은 패치로 바뀔 수 있습니다 — 인게임 확인 권장. 게임의 모든 권리는 Hologryph·TowerHaus·tinyBuild에 있습니다.</p>
</div></footer>

<script>
var ITEMS={DETAIL_JSON};
(function(){{
  var cards=[].slice.call(document.querySelectorAll('.it'));
  var q=document.getElementById('q'),count=document.getElementById('count'),grid=document.getElementById('grid');
  var fsel='all';
  var emptyEl=document.createElement('p');emptyEl.className='empty';emptyEl.setAttribute('role','status');
  emptyEl.textContent='검색 결과가 없습니다.';emptyEl.style.display='none';grid.parentNode.appendChild(emptyEl);
  function apply(){{
    var term=q.value.trim().toLowerCase(),shown=0;
    cards.forEach(function(c){{
      var ok=(fsel==='all'||c.dataset.cat===fsel)&&(!term||c.dataset.s.indexOf(term)>=0);
      c.classList.toggle('hide',!ok); if(ok)shown++;
    }});
    emptyEl.style.display=shown?'none':'block';
    count.textContent=shown+' / '+cards.length+' 아이템';
  }}
  q.addEventListener('input',apply);
  [].slice.call(document.querySelectorAll('.fbtn')).forEach(function(b){{
    b.addEventListener('click',function(){{
      document.querySelectorAll('.fbtn').forEach(function(x){{x.classList.remove('active');x.setAttribute('aria-pressed','false');}});
      b.classList.add('active');b.setAttribute('aria-pressed','true');fsel=b.dataset.f;apply();
    }});
  }});
  apply();
  // modal
  var ov=document.getElementById('ov'),mod=document.getElementById('mod'),_prev=null;
  function esc(s){{return String(s==null?'':s).replace(/[&<>]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c];}});}}
  function rows(arr){{return arr.map(function(r){{return '<div class="row"><span class="k">'+esc(r[0])+'</span><span class="v">'+esc(r[1])+'</span></div>';}}).join('');}}
  function chips(arr){{return '<div class="chips">'+arr.map(function(x){{return '<span class="chip">'+esc(x)+'</span>';}}).join('')+'</div>';}}
  function recipe(arr){{return '<div class="chips">'+arr.map(function(r){{return '<span class="chip">'+esc(r[0])+' <b>×'+esc(r[1])+'</b></span>';}}).join('')+'</div>';}}
  function open(i){{
    var d=ITEMS[i]; if(!d)return;
    _prev=document.activeElement;
    mod.style.setProperty('--col',d.col);
    var h='<div class="m-h"><img class="m-ic" src="'+esc(d.icon)+'" alt=""><div class="m-tt"><div class="m-n">'+esc(d.name)+'</div><div class="m-c">'+esc(d.cat)+'</div></div><button class="m-x" aria-label="닫기">×</button></div><div class="m-b">';
    if(d.desc) h+='<p class="m-desc">'+esc(d.desc)+'</p>';
    if(d.stats&&d.stats.length) h+='<div class="sec">스탯</div>'+rows(d.stats);
    if(d.sell) h+='<div class="sec">판매가</div><div class="row"><span class="k">판매가</span><span class="v">'+esc(d.sell)+'</span></div>';
    if(d.recipe&&d.recipe.length){{ h+='<div class="sec">제작'+(d.workbench?' · '+esc(d.workbench):'')+'</div>'+recipe(d.recipe); }}
    if(d.obtained&&d.obtained.length) h+='<div class="sec">획득처</div>'+chips(d.obtained);
    if(d.ammo&&d.ammo.length) h+='<div class="sec">호환 탄약</div>'+chips(d.ammo);
    if(d.usedIn&&d.usedIn.length) h+='<div class="sec">사용처</div>'+chips(d.usedIn);
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
open(os.path.join(ROOT, "items.html"), "w", encoding="utf-8").write(HTML)
print("wrote items.html", len(HTML), "bytes ;", total, "items")
print("카테고리:", dict(Counter(it.get("category","Misc") for it in data)))
print("설명보유:", sum(1 for it in data if it.get("description_ko")), "/ 제작보유:", sum(1 for it in data if it.get("recipe")))
