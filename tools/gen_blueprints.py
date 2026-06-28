#!/usr/bin/env python3
# 트램플러 내부 설계 부품(구획) 115종 → 인터랙티브 블루프린트 카탈로그 blueprints.html
import json, html, os

ROOT = os.path.expanduser("~/sand-kr-guide")
P = json.load(open(os.path.join(ROOT, "tools/parts_data.json")))["parts"]

import re as _re
_SP = os.path.join(ROOT, "tools/parts_stats.json")
STATS = {x["slug"]: x["stats"] for x in (json.load(open(_SP))["items"] if os.path.exists(_SP) else [])}
STAT_KO = {
 "Dimensions":"치수","치수":"치수","Health":"내구도","내구도":"내구도","Weight":"무게","무게":"무게",
 "Energy Consumption":"에너지 소모","에너지 소비":"에너지 소모","Weight Capacity":"적재 한도","적재 용량":"적재 한도",
 "Item Slots":"적재 슬롯","Magazine":"탄창","Reload":"재장전","Fire rate":"연사 속도","Velocity":"탄속",
 "Penetrates":"관통","Range":"사거리","Type":"종류","Energy Capacity":"에너지 용량","에너지 용량":"에너지 용량",
 "Rated Power":"정격 출력","정격 출력":"정격 출력","Crew Slots":"승무원 슬롯","승무원 슬롯":"승무원 슬롯",
 "Damage":"피해","Damage (Trampler)":"피해(트램플러)","Damage (Player)":"피해(플레이어)","Splash Damage":"범위 피해",
 "Weight Compensation":"무게 보정","Armor":"장갑","Regen":"재생",
}
SVAL_KO = {"Yes":"예","No":"아니오","Shotgun":"샷건","Single-Shot Rifle":"단발 라이플","Semi-Automatic Pistol":"반자동 권총",
 "Pistol":"권총","Rifle":"라이플","Revolver":"리볼버","Autocannon":"오토캐논","Naval":"함포","Sniper":"저격"}
BAR = {"내구도","무게","에너지 소모","적재 한도","에너지 용량","적재 슬롯","정격 출력","피해","무게 보정","장갑","범위 피해","피해(트램플러)","피해(플레이어)"}
def _num(v):
    m = _re.match(r'^\s*([\d,]+(?:\.\d+)?)', str(v))
    return float(m.group(1).replace(',','')) if m else None
import collections as _co
def _norm(slug):
    r=[]
    for s in STATS.get(slug, []):
        lab = STAT_KO.get(s["label"], s["label"])
        val = SVAL_KO.get(s["value"], str(s["value"]).replace("delay", "지연"))
        r.append((lab, val, _num(s["value"]) if lab in BAR else None))
    return r
_MAX = {}; _CNT = _co.Counter()
for _sl in STATS:
    for lab, val, n in _norm(_sl):
        if n is not None:
            _MAX[lab] = max(_MAX.get(lab, 0), n); _CNT[lab] += 1
def stat_rows(slug):
    out=[]
    for lab, val, n in _norm(slug):
        pct = round(n/_MAX[lab]*100) if (n is not None and _CNT[lab] >= 3 and _MAX.get(lab,0) > 0) else 0
        out.append([lab, val, pct])
    return out

CAT_ORDER = ["섀시","동력","조향","대포·포","무기·공성","장갑","화물·보관","승무원·생활","구조·이동","도구·유틸","기타"]
CAT_COL = {"섀시":"#4493f8","동력":"#d9a84c","조향":"#6fa3bd","대포·포":"#c1572a","무기·공성":"#cf6a4a",
           "장갑":"#9a8358","화물·보관":"#e3a008","승무원·생활":"#8aae66","구조·이동":"#b07d8a","도구·유틸":"#6fb24a","기타":"#7d6f56"}
# 비교 컬럼: 카테고리별로 데이터에 실제 존재하는 스탯 상위 3개(치수는 후순위)
_catlab = _co.defaultdict(_co.Counter)
for _p in P:
    for _lab, _val, _pct in stat_rows(_p["slug"]):
        _catlab[_p["cat"]][_lab] += 1
CMP = {}
for _c in CAT_ORDER:
    _cands = [l for l, _ in _catlab[_c].most_common()]
    _cands.sort(key=lambda l: (l == "치수", -_catlab[_c][l]))
    CMP[_c] = _cands[:3] or ["내구도", "무게"]
NODE_KO = {
 "Stairs":"계단","Framed Stairs":"프레임 계단","Crew Room":"승무원실","Captain's Cabin":"선장실",
 "Small Chassis":"소형 섀시","Middling Chassis":"중형 섀시","Great Chassis":"대형 섀시","Royal Chassis":"왕급 섀시",
 "Motor-Reactor":"모터-리액터","Energy Rod":"에너지 로드","Smokeless Energy Rod":"무연 에너지 로드",
 "Small Engine":"소형 엔진","Medium Engine":"중형 엔진","MedKit":"메드킷","Shovel":"삽",
 "Wooden Corridor":"목재 복도","Metal Corridor":"금속 복도","Crafting Materials":"제작 재료","Smoke Grenade":"연막탄",
 "Framed Steering":"프레임 조타","Steering":"조타","Large Open Steering":"대형 개방 조타","Large Framed Steering":"대형 프레임 조타",
 "Small Armament Workshop":"소형 병기 공방","Large Armament Workshop":"대형 병기 공방","Artillery Decks":"포 갑판",
 "Framed Artillery Deck":"프레임 포 갑판","Armored Artillery Decks":"장갑 포 갑판","Framed Armored Artillery Deck":"프레임 장갑 포 갑판",
 "Armored Artillery Compartment":"장갑 포실","Enclosed Artillery Compartment":"밀폐 포실","Wooden Vestibule":"목재 진입구","Armored Vestibule":"장갑 진입구",
 "Weapons":"무기","Armor":"장갑","Armor Plate":"장갑판","Improved Ammo":"개량탄","Time Bomb":"시한폭탄","Battering Ram":"충각","Embrasure":"총안","Grenade":"수류탄",
 "Wooden Decks":"목재 갑판","Armored Deck":"장갑 갑판","Balconies":"발코니","Armored Balconies":"장갑 발코니",
 "Cargo Deck":"화물 갑판","Cargo Hold":"화물 적재고","Cargo Bay":"화물칸","Cargo Compartment":"화물 구획",
 "Shotgun Cannon":"샷건 캐논","Auto Cannon":"오토캐논","Autocannon":"오토캐논","Cannon":"캐논","Resources":"자원"}
def ko_node(n):
    m = _re.match(r'^(.*?)\s*\((.+)\)\s*$', str(n))
    base, suf = (m.group(1), m.group(2)) if m else (n, None)
    ko = NODE_KO.get(base, base)
    return ko + (f" ({suf})" if suf else "")

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
        "mats": p["mats"], "node": ko_node(p["node"]), "stats": stat_rows(p["slug"]),
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
fbtns = (f'<button class="fcat active" data-f="all" aria-pressed="true" style="--col:#d9a84c"><span class="dot"></span>전체<span class="n">{len(P)}</span></button>' + "".join(
    f'<button class="fcat" data-f="{esc(c)}" aria-pressed="false" style="--col:{CAT_COL[c]}"><span class="dot"></span>{esc(c)}<span class="n">{len(G[c])}</span></button>'
    for c in CAT_ORDER if G.get(c)))
total = len(P)
DETAIL_JSON = json.dumps(DETAIL, ensure_ascii=False)
CMP_JSON = json.dumps(CMP, ensure_ascii=False)

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
@media(max-width:560px){{.topbar .in{{padding:9px 12px;gap:8px;flex-wrap:wrap}}.brand{{font-size:15px}}.tabs a{{padding:5px 9px;font-size:12px}}.ctrl{{position:static}}}}
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
main{{max-width:1180px;margin:0 auto;padding:16px 22px 80px;display:grid;grid-template-columns:204px 1fr;gap:20px;align-items:start}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:11px}}
.sidebar{{position:sticky;top:128px;align-self:start}}
.sb-h{{font-family:"Oswald",sans-serif;font-size:11px;letter-spacing:.08em;color:var(--faint);text-transform:uppercase;padding:0 11px 8px}}
.sidebar-in{{display:flex;flex-direction:column;gap:3px}}
.fcat{{display:flex;align-items:center;gap:9px;width:100%;text-align:left;font-family:inherit;font-size:13.5px;color:var(--muted);background:transparent;border:1px solid transparent;border-radius:7px;padding:8px 11px;cursor:pointer}}
.fcat:hover{{color:var(--ink);background:rgba(255,255,255,.025)}}
.fcat .dot{{width:9px;height:9px;border-radius:50%;background:var(--col,var(--brass));flex:none;box-shadow:0 0 6px var(--col,transparent)}}
.fcat .n{{margin-left:auto;font-size:11px;color:var(--faint);font-family:"Oswald",sans-serif}}
.fcat.active{{color:#fff;background:color-mix(in srgb,var(--col,#d9a84c) 16%,transparent);border-color:color-mix(in srgb,var(--col,#d9a84c) 45%,var(--edge2))}}
.fcat.active .n{{color:var(--ink)}}
@media(max-width:760px){{main{{grid-template-columns:1fr;gap:12px}}.sidebar{{position:static;top:auto}}.sb-h{{display:none}}.sidebar-in{{flex-direction:row;flex-wrap:wrap;gap:6px}}.fcat{{width:auto;padding:6px 11px;border:1px solid var(--edge2);border-radius:999px;font-size:12.5px}}.fcat .n{{margin-left:5px;color:var(--faint)}}}}
.it{{display:flex;gap:10px;align-items:center;text-align:left;font-family:inherit;cursor:pointer;
 background:linear-gradient(180deg,#241b11,#191309);border:1px solid var(--edge);border-left:3px solid var(--col);
 border-radius:8px;padding:8px 10px;transition:transform .08s,border-color .12s,box-shadow .12s;color:var(--ink)}}
.it:hover,.it:focus{{transform:translateY(-1px);box-shadow:0 6px 18px rgba(0,0,0,.35);outline:none;border-color:color-mix(in srgb,var(--col) 50%,var(--edge))}}
.it-ic{{width:46px;height:46px;flex:none;object-fit:contain;padding:2px;border:1px solid var(--edge2);border-radius:7px;
 background:linear-gradient(rgba(217,168,76,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(217,168,76,.05) 1px,transparent 1px),radial-gradient(circle at 50% 36%,rgba(255,255,255,.06),transparent 70%),#0d0a06;background-size:8px 8px,8px 8px,auto,auto}}
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
#mod .m-ic{{width:64px;height:64px;flex:none;object-fit:contain;padding:4px;border:1px solid var(--edge2);border-radius:9px;background:linear-gradient(rgba(217,168,76,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(217,168,76,.05) 1px,transparent 1px),radial-gradient(circle at 50% 36%,rgba(255,255,255,.07),transparent 70%),#0d0a06;background-size:9px 9px,9px 9px,auto,auto}}
#mod .m-tt{{flex:1;min-width:0}}#mod .m-n{{font-weight:700;font-size:16.5px;color:#fff;line-height:1.25}}
#mod .m-c{{font-size:12px;color:var(--col,#d9a84c);font-weight:600;margin-top:2px}}
#mod .m-x{{flex:none;background:transparent;border:1px solid var(--edge2);color:var(--muted);border-radius:7px;width:32px;height:32px;font-size:17px;cursor:pointer}}#mod .m-x:hover{{color:var(--brass);border-color:var(--brass)}}
#mod .m-b{{padding:14px 20px 22px}}
#mod .m-desc{{font-size:14px;color:var(--ink);line-height:1.65;margin:0 0 14px}}
#mod .sec{{font-family:"Oswald",sans-serif;font-size:11px;letter-spacing:.06em;color:var(--faint);text-transform:uppercase;margin:16px 0 6px;border-bottom:1px solid var(--edge);padding-bottom:4px}}
#mod .row{{display:flex;justify-content:space-between;gap:10px;font-size:13.5px;padding:4px 0;border-bottom:1px solid var(--edge)}}
#mod .row:last-child{{border-bottom:0}}#mod .row .k{{color:var(--muted)}}#mod .row .v{{color:var(--ink);font-weight:600;font-family:"Oswald",sans-serif}}
#mod .chips{{display:flex;flex-wrap:wrap;gap:6px}}
#mod .chip{{font-size:12px;color:var(--ink);background:#0d0a06;border:1px solid var(--edge2);border-radius:6px;padding:3px 9px}}#mod .chip b{{color:var(--brass);font-family:"Oswald",sans-serif}}
#mod .strow{{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px;padding:6px 0;border-bottom:1px solid var(--edge)}}
#mod .strow:last-child{{border-bottom:0}}
#mod .strow .sk{{color:var(--muted);font-size:13px;flex:1}}
#mod .strow .sv{{font-family:"Oswald",sans-serif;color:#fff;font-weight:600;font-size:14px}}
#mod .strow .bar{{flex-basis:100%;height:5px;background:#0d0a06;border:1px solid var(--edge2);border-radius:3px;overflow:hidden;margin-top:1px}}
#mod .strow .bar i{{display:block;height:100%;background:linear-gradient(90deg,var(--brass-d),var(--brass))}}
#mod .mchip{{display:inline-flex;align-items:center;gap:5px;font-size:12px;color:var(--ink);background:#0d0a06;border:1px solid var(--edge2);border-radius:6px;padding:3px 9px 3px 5px}}
#mod .mchip img{{width:17px;height:17px;object-fit:contain}}#mod .mchip b{{color:var(--brass);font-family:"Oswald",sans-serif;margin-left:1px}}
#mod .cost{{display:inline-flex;align-items:center;gap:6px;font-family:"Oswald",sans-serif;color:var(--brass);font-weight:700;font-size:15px}}#mod .cost img{{width:18px;height:18px;object-fit:contain}}
#mod .cmpw{{max-height:262px;overflow:auto;border:1px solid var(--edge);border-radius:7px}}
#mod table.cmp{{border-collapse:collapse;width:100%;font-size:12px;min-width:0}}
#mod .cmp th{{position:sticky;top:0;z-index:1;background:#2a2110;color:var(--brass);font-family:"Oswald",sans-serif;font-weight:600;font-size:10px;letter-spacing:.03em;padding:6px 9px;text-align:right;white-space:nowrap}}
#mod .cmp th:first-child{{text-align:left}}
#mod .cmp td{{padding:6px 9px;border-top:1px solid var(--edge);text-align:right;color:var(--ink);font-family:"Oswald",sans-serif;white-space:nowrap}}
#mod .cmp td:first-child{{text-align:left;font-family:"Pretendard",sans-serif;color:var(--muted);max-width:168px;overflow:hidden;text-overflow:ellipsis}}
#mod .cmp tr[data-i]{{cursor:pointer}}#mod .cmp tr[data-i]:hover td{{background:rgba(217,168,76,.07)}}
#mod .cmp tr.cur td{{background:rgba(217,168,76,.16)}}#mod .cmp tr.cur td:first-child{{color:#fff;font-weight:600}}
#mod .cmp td.win{{color:var(--brass);font-weight:600}}
#mod .cmp tr[tabindex]:focus{{outline:2px solid var(--brass);outline-offset:-2px}}
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
  <span id="count"></span>
</div></div>

<main>
  <aside class="sidebar"><div class="sb-h">부품 분류</div><div class="sidebar-in">{fbtns}</div></aside>
  <div class="grid" id="grid">
{cards_html}
  </div>
</main>

<div id="ov" role="dialog" aria-modal="true"><div id="mod"></div></div>

<footer><div class="in">
  <p><b>데이터 출처.</b> 부품 이름·설명·해금 비용·재료는 게임 인게임 데이터이며, 커뮤니티 팬 데이터베이스 <a href="https://sand-help.com" target="_blank" rel="noopener">sand-help.com</a>(비공식)에서 가져와 한국어로 재구성했습니다. 부품 아이콘은 게임 내 에셋이며, sand-help의 코드·디자인은 복제하지 않았습니다.</p>
  <p>비공식 팬 가이드 · 얼리액세스(2026-06-22) 기준이라 수치·명칭은 패치로 바뀔 수 있습니다 — 인게임 확인 권장. 모든 권리는 Hologryph·TowerHaus·tinyBuild에 있습니다.</p>
</div></footer>

<script>
var PARTS={DETAIL_JSON};
var CMP={CMP_JSON};
(function(){{
  var cards=[].slice.call(document.querySelectorAll('.it'));
  var q=document.getElementById('q'),count=document.getElementById('count'),grid=document.getElementById('grid'),fsel='all';
  var emptyEl=document.createElement('p');emptyEl.className='empty';emptyEl.setAttribute('role','status');
  emptyEl.textContent='검색 결과가 없습니다.';emptyEl.style.display='none';emptyEl.style.gridColumn='1/-1';grid.appendChild(emptyEl);
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
  [].slice.call(document.querySelectorAll('.fcat')).forEach(function(b){{
    b.addEventListener('click',function(){{
      document.querySelectorAll('.fcat').forEach(function(x){{x.classList.remove('active');x.setAttribute('aria-pressed','false');}});
      b.classList.add('active');b.setAttribute('aria-pressed','true');fsel=b.dataset.f;apply();
    }});
  }});
  apply();
  var ov=document.getElementById('ov'),mod=document.getElementById('mod'),_prev=null;
  function esc(s){{return String(s==null?'':s).replace(/[&<>]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c];}});}}
  function chips(arr){{return '<div class="chips">'+arr.map(function(r){{return '<span class="mchip"><img src="assets/tech_icons/'+esc(r[2])+'" alt="">'+esc(r[0])+' <b>×'+esc(r[1])+'</b></span>';}}).join('')+'</div>';}}
  function statRows(arr){{return arr.map(function(s){{var bar=s[2]>0?'<span class="bar"><i style="width:'+s[2]+'%"></i></span>':'';return '<div class="strow"><span class="sk">'+esc(s[0])+'</span><span class="sv">'+esc(s[1])+'</span>'+bar+'</div>';}}).join('');}}
  function valOf(g,lab){{for(var i=0;i<g.stats.length;i++){{if(g.stats[i][0]===lab)return g.stats[i][1];}}return '—';}}
  function numOf(g,lab){{var v=valOf(g,lab);var m=String(v).match(/[0-9.,]+/);return m?parseFloat(m[0].replace(/,/g,'')):-1;}}
  function compareTable(ci){{
    var d=PARTS[ci],cat=d.cat,cols=CMP[cat]||['내구도','무게'],grp=[];
    for(var i=0;i<PARTS.length;i++){{if(PARTS[i].cat===cat&&cols.some(function(c){{return valOf(PARTS[i],c)!=='—';}}))grp.push(i);}}
    if(grp.length<2||grp.indexOf(ci)<0)return '';
    grp.sort(function(a,b){{return numOf(PARTS[b],cols[0])-numOf(PARTS[a],cols[0]);}});
    var mx={{}};cols.forEach(function(c){{var m=-Infinity;grp.forEach(function(gi){{var n=numOf(PARTS[gi],c);if(n>m)m=n;}});mx[c]=m;}});
    var hd='<tr><th>부품</th>'+cols.map(function(c){{return '<th>'+esc(c)+'</th>';}}).join('')+'</tr>';
    var rows=grp.map(function(gi){{var g=PARTS[gi];return '<tr data-i="'+gi+'" tabindex="0" role="button"'+(gi===ci?' class="cur"':'')+'><td>'+esc(g.name)+'</td>'+cols.map(function(c){{var n=numOf(g,c),w=(n>0&&n===mx[c])?' class="win"':'';return '<td'+w+'>'+esc(valOf(g,c))+'</td>';}}).join('')+'</tr>';}}).join('');
    return '<div class="sec">비교 · 같은 분류 ('+grp.length+'개)</div><div class="cmpw"><table class="cmp">'+hd+rows+'</table></div>';
  }}
  function open(i){{
    var d=PARTS[i]; if(!d)return; if(!ov.classList.contains('on'))_prev=document.activeElement;
    mod.style.setProperty('--col',d.col);
    var h='<div class="m-h"><img class="m-ic" src="'+esc(d.icon)+'" alt=""><div class="m-tt"><div class="m-n" id="mtitle">'+esc(d.name)+'</div><div class="m-c">'+esc(d.cat)+'</div></div><button class="m-x" aria-label="닫기">×</button></div><div class="m-b">';
    if(d.desc) h+='<p class="m-desc">'+esc(d.desc)+'</p>';
    if(d.stats&&d.stats.length){{ h+='<div class="sec">스탯</div>'+statRows(d.stats); }}
    h+='<div class="sec">해금</div>';
    h+='<div class="row"><span class="k">연구</span><span class="v">'+esc(d.fac)+' · '+esc(d.node)+' · T'+esc(d.tier)+'</span></div>';
    h+='<div class="row"><span class="k">비용</span><span class="cost"><img src="assets/tech_icons/icon_item_coinCrown.png" alt="">'+esc(d.crowns.toLocaleString('en-US'))+'</span></div>';
    if(d.mats&&d.mats.length){{ h+='<div class="sec">추가 재료</div>'+chips(d.mats); }}
    h+=compareTable(i);
    h+='</div>';
    mod.innerHTML=h; ov.classList.add('on'); mod.setAttribute('aria-labelledby','mtitle');
    mod.querySelector('.m-x').addEventListener('click',close);
    [].slice.call(mod.querySelectorAll('.cmp tr[data-i]')).forEach(function(tr){{var go=function(){{open(+tr.dataset.i);}};tr.addEventListener('click',go);tr.addEventListener('keydown',function(e){{if(e.key==='Enter'||e.key===' '){{e.preventDefault();go();}}}});}});
    mod.scrollTop=0; mod.querySelector('.m-x').focus();
  }}
  function close(){{ ov.classList.remove('on'); if(_prev&&_prev.focus)_prev.focus(); }}
  cards.forEach(function(c){{ c.addEventListener('click',function(){{ open(+c.dataset.i); }}); }});
  ov.addEventListener('click',function(e){{ if(e.target===ov)close(); }});
  document.addEventListener('keydown',function(e){{ if(e.key==='Escape')close(); }});
  ov.addEventListener('keydown',function(e){{
    if(e.key!=='Tab'||!ov.classList.contains('on'))return;
    var f=[].slice.call(mod.querySelectorAll('button,[tabindex="0"]')).filter(function(el){{return el.offsetParent!==null;}});
    if(!f.length)return; var a=f[0],b=f[f.length-1];
    if(e.shiftKey&&document.activeElement===a){{b.focus();e.preventDefault();}}
    else if(!e.shiftKey&&document.activeElement===b){{a.focus();e.preventDefault();}}
  }});
}})();
</script>
</body></html>'''
HTML = HTML.replace('{DETAIL_JSON}', DETAIL_JSON)
HTML = HTML.replace('{CMP_JSON}', json.dumps(CMP, ensure_ascii=False))
HTML = HTML.replace('font-family:"Oswald"', 'font-family:"Oswald",sans-serif')
open(os.path.join(ROOT, "blueprints.html"), "w", encoding="utf-8").write(HTML)
print("wrote blueprints.html", len(HTML), "bytes ;", total, "parts")
print("카테고리:", dict(Counter(p["cat"] for p in P)))
