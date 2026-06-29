#!/usr/bin/env python3
# 수치 레퍼런스 → reference.html
# 모든 표는 tools/*.json(parts_data·parts_stats·tech_nodes·items_data)에서 산출(데이터 기반).
# 게임 상수만 docs/kb 기반 하드코딩 + 신뢰도 태그.
import json, html, os, re
from collections import defaultdict, Counter

ROOT = os.path.expanduser("~/sand-kr-guide")
def J(p): return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
PARTS = {p["slug"]: p for p in J("tools/parts_data.json")["parts"]}
# 블루프린트 카탈로그와 동일하게 트램플러 에디터 부품만 — 휴대 아이템·탄약·원자재·의류·소모품 제외.
NOT_PARTS = {
 "med-kit", "energy-bar", "smokeless-energy-bar", "treasure-shovel",
 "resource-fabric-scraps", "resource-threads", "resource-metal-t2", "resource-metal-t3",
 "old-jacket", "old-jacket-t2", "smoke-grenade", "rifle-musket", "shotgun-handmade",
 "c4-dynamite", "semi-automatic-pistol", "repeater-rifle", "grenade-contact",
 "pistol-ammo-high-velocity", "rifle-ammo-high-velocity", "shotgun",
 "shotgun-turret-ammo", "small-cannon-ammo",
}
PARTS = {s: p for s, p in PARTS.items() if s not in NOT_PARTS}
for _s, _p in PARTS.items():
    if _s == "sgow-universal-casemate": _p["cat"] = "대포·포"  # 밀폐 포실 → 대포·포
# parts_stats.json은 영문/한글 라벨을 혼용 — 영문으로 정규화(한글 라벨 부품 누락 방지)
LBL_ALIAS = {"적재 용량": "Weight Capacity", "무게": "Weight", "내구도": "Health", "치수": "Dimensions",
             "에너지 소비": "Energy Consumption", "에너지 용량": "Energy Capacity", "정격 출력": "Rated Power",
             "승무원 슬롯": "Crew Slots", "무게 보정": "Weight Compensation", "적재 슬롯": "Item Slots"}
PSTATS = {it["slug"]: {LBL_ALIAS.get(s["label"], s["label"]): s["value"] for s in it["stats"]}
          for it in J("tools/parts_stats.json")["items"]}
NODES = J("tools/tech_nodes.json")
_it = J("tools/items_data.json")
ITEMS = _it["items"] if isinstance(_it, dict) else _it
ITEM = {i["slug"]: i for i in ITEMS}
NAME = {**{s: p["name"] for s, p in PARTS.items()}, **{i["slug"]: i["name"] for i in ITEMS}}

def esc(s): return html.escape(str(s if s is not None else ""))
def num(v):
    m = re.match(r"^\s*([\d,]+(?:\.\d+)?)", str(v))
    return float(m.group(1).replace(",", "")) if m else None
def comma(n): return f"{int(n):,}" if n == int(n) else f"{n:,}"

MAT_KO = {
 "Crowns": "크라운", "Black Box": "블랙박스", "Alloy Steel": "합금강", "Weird Coral": "기이한 산호",
 "Coral Chunk": "산호 덩어리", "Mixtures": "혼합물", "Raw Aurogen Crystal": "원석 오로젠",
 "Fabric Scraps": "천 조각", "Gunpowder": "화약", "Threads": "실", "Scrap Metal": "고철",
 "Crystal": "크리스탈", "Ficus": "피커스", "Reinforced Leather Strips": "강화 가죽끈",
 "Scrapped Ammo": "폐탄약", "Coral Dust": "산호 가루", "Leviathan Skin": "리바이어던 가죽",
 "Metal Rods": "금속 봉", "District Officer's Portable Safe": "구역 담당관 금고", "Optic Lenses": "광학 렌즈",
 "Weapon Parts": "무기 부품", "Fabric": "직물", "Leviathan Meat": "리바이어던 고기",
 "High-Grade Gunpowder": "고급 화약", "Crate of 1889 Chardonnay": "1889 샤르도네 상자",
 "Canned Sea Deer XL": "바다사슴 통조림 XL", "Computing Module": "연산 모듈", "Pneumatic Parts": "공압 부품",
}
def mko(n): return MAT_KO.get(n, n)
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV"}

# ---------- table helper ----------
def tbl(headers, rows, cls="ref", cap=""):
    h = "<tr>" + "".join(f'<th scope="col">{esc(x)}</th>' for x in headers) + "</tr>"
    body = ""
    for r in rows:
        body += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
    lbl = (cap or "데이터") + " 표 (가로 스크롤 가능)"
    return f'<div class="tw" tabindex="0" role="region" aria-label="{esc(lbl)}"><table class="{cls}">{h}{body}</table></div>'

REL = {  # 신뢰도 태그
 "데이터": ("데이터", "rd"), "검증": ("검증", "rv"), "언론": ("언론", "rp"),
 "커뮤니티": ("커뮤니티", "rc"), "AI": ("AI-SEO", "ra"),
}
def rel(t):
    lab, c = REL[t]
    return f'<span class="rel {c}">{lab}</span>'

# ===================== SECTIONS =====================
SEC = []  # (id, title, kicker, html)

# ---- A. 부품 스탯 범위 ----
STAT_KO = {"Dimensions": "치수", "Health": "내구도", "Weight": "무게", "Energy Consumption": "에너지 소모",
 "Weight Capacity": "적재 한도", "Item Slots": "적재 슬롯", "Magazine": "탄창", "Reload": "재장전",
 "Fire rate": "연사", "Velocity": "탄속", "Range": "사거리", "Energy Capacity": "에너지 용량",
 "Rated Power": "정격 출력", "Crew Slots": "승무원 슬롯", "Weight Compensation": "무게 보정", "Armor": "장갑"}
agg = defaultdict(list)
for sl in PARTS:  # 트램플러 부품(93)만 — 휴대무기/탄약 스탯은 각 전용 섹션에
    for lab, val in PSTATS.get(sl, {}).items():
        n = num(val)
        if n is not None and lab in STAT_KO:
            agg[STAT_KO[lab]].append((n, val, NAME.get(sl, sl)))
rng_order = ["적재 한도", "무게", "내구도", "에너지 소모", "정격 출력", "에너지 용량", "무게 보정",
             "승무원 슬롯", "적재 슬롯", "장갑", "사거리", "탄창", "재장전"]
rows = []
for k in rng_order:
    if k in agg:
        vs = sorted(agg[k])
        lo, hi = vs[0], vs[-1]
        if lo[0] == hi[0]:
            rng_txt, ext = esc(lo[1]), f'<span class="dim">{len(vs)}종 전부 동일</span>'
        else:
            rng_txt = f"{esc(lo[1])} ~ {esc(hi[1])}"
            ext = f'<span class="dim">{esc(lo[2])} → {esc(hi[2])}</span>'
        rows.append([f"<b>{esc(k)}</b>", rng_txt, ext])
SEC.append(("range", "부품 스탯 범위", "트램플러 부품 전체에서 각 스탯의 최소~최대.",
            tbl(["스탯", "범위", "최소 → 최대 부품"], rows) +
            f'<p class="cap">{rel("데이터")} sand-help 에디터 수치. 개별 부품 값은 <a href="blueprints.html">블루프린트</a> 모달의 스탯 바·비교표 참조.</p>'))

# ---- B. 섀시 ----
def tier_of(nm):
    for k, t in [("Small", "소형"), ("Middling", "중형"), ("Great", "대형"), ("Royal", "왕급")]:
        if k in nm: return t
    return "—"
ch = [(num(PSTATS.get(sl, {}).get("Weight Capacity")), p["name"], PSTATS.get(sl, {}).get("Dimensions", "—"))
      for sl, p in PARTS.items() if p["cat"] == "섀시"]
ch = [c for c in ch if c[0]]
ch.sort()
crows = [[f"<b>{tier_of(n)}</b>", esc(n), f'<span class="big">{comma(cap)}</span>', esc(dim)] for cap, n, dim in ch]
SEC.append(("chassis", "섀시 — 적재 한도(무게 예산)", "트램플러가 실을 수 있는 총무게 = 이 한도.",
            tbl(["티어", "섀시", "적재 한도", "치수"], crows) +
            f'<p class="cap">{rel("데이터")} 큰 섀시일수록 한도↑(더 얹음)지만 자체가 무겁고 속도·기동↓.</p>'))

# ---- C. 동력 ----
pw = []
for sl, p in PARTS.items():
    if p["cat"] != "동력": continue
    d = PSTATS.get(sl, {})
    pw.append([esc(p["name"]),
               esc(d.get("Rated Power", "—")), esc(d.get("Energy Capacity", "—")),
               esc(d.get("Weight Compensation", "—")), esc(d.get("Energy Consumption", "—")),
               esc(d.get("Weight", "—"))])
_rw = sorted(n for n in (num(PSTATS.get(sl, {}).get("Weight")) for sl, p in PARTS.items()
             if p["cat"] == "동력" and "Reactor" in p["name"]) if n)
_rwr = f"{comma(_rw[0])}~{comma(_rw[-1])}" if _rw else "—"
SEC.append(("power", "동력 — 리액터 / 엔진", "리액터=출력·연료, 엔진=무게 보정으로 기동 회복.",
            tbl(["부품", "정격 출력", "에너지 용량", "무게 보정", "에너지 소모", "무게"], pw) +
            f'<p class="cap">{rel("데이터")} 리액터는 무겁다({_rwr}). 엔진은 무게를 상쇄(보정)하지만 에너지를 더 먹는다.</p>'))

# ---- D. 대포 킷 + 포탄 ----
kit = []
for i in ITEMS:  # 거치 캐논 킷 12종(parts_data엔 8종뿐 — Rusty 80mm·익스페리멘털 T4 누락)
    if i.get("category") == "Artillery" and i.get("stats"):
        d = {s["label"]: s["value"] for s in i["stats"]}
        kit.append((i["name"], d.get("Fire rate", "—"), d.get("Velocity", "—"), d.get("Reload", "—")))
def cal(n):
    m = re.search(r"(\d+ mm)", n); return m.group(1) if m else "—"
QORD = {"Rusty": 0, "Worn": 1, "Pristine": 2, "Experimental": 3}
def qual(n):
    for k, v in QORD.items():
        if k in n: return v
    return 9
kit.sort(key=lambda x: (cal(x[0]), qual(x[0]), x[0]))  # 구경 내 품질 오름차순(캡션 진행과 일치)
krows = [[esc(n), esc(fr), esc(v), esc(rl)] for n, fr, v, rl in kit]
# 포탄(ammo) 피해
shells = []
CANNON_T = {"Autocannon", "Naval", "Rocket"}  # 거치 대포·중화기 탄종
for i in ITEMS:
    if not i.get("stats"): continue
    d = {s["label"]: s["value"] for s in i["stats"]}
    t = d.get("Type")
    if not (t in CANNON_T or (t == "Shotgun" and re.search(r"\d+ mm", i["name"]))): continue
    shells.append([esc(i["name"]), esc(d.get("Damage", "—")), esc(d.get("Damage (Trampler)", "—")),
                   esc(d.get("Splash Damage", "—")), esc(d.get("Range", "—"))])
SEC.append(("cannon", "대포 — 킷(발사) + 포탄(피해)", "킷이 연사·탄속·재장전을, 포탄이 피해를 정한다.",
            "<h3>거치 캐논 킷 (12종)</h3>" + tbl(["킷", "연사", "탄속", "재장전"], krows) +
            "<h3>포탄·로켓 — 피해</h3>" + tbl(["탄종", "피해", "피해(트램플러)", "범위 피해", "사거리"], shells) +
            f'<p class="cap">{rel("데이터")} 품질 Rusty→Worn→Pristine이 오르면 연사·재장전 개선(Experimental T4: Railgun 탄속 2000 m/s 등). 오토캐논=고연사 근거리, 함포=저연사 고탄속 장거리. 트램플러 피해는 데이터상 40mm Shell(150)만 명시되고 나머지는 일반 피해.</p>'))

# ---- E. 휴대 무기 · 탄약 ----
wk = []
for i in ITEMS:
    if i.get("category") == "Weapons" and i.get("stats"):
        d = {s["label"]: s["value"] for s in i["stats"]}
        if any(k in d for k in ("Magazine", "Reload", "Type")):
            wk.append([esc(i["name"]), esc(d.get("Type", "—")), esc(d.get("Magazine", "—")),
                       esc(d.get("Reload", "—")), esc(d.get("Range", "—"))])
am = []
INF_T = {"Pistol", "Rifle", "Sniper", "Energetic"}  # 보병 구경(캐논 포탄·로켓은 대포 섹션)
for i in ITEMS:
    if i.get("category") == "Ammo" and i.get("stats"):
        d = {s["label"]: s["value"] for s in i["stats"]}
        t = d.get("Type")
        if not (t in INF_T or (t == "Shotgun" and not re.search(r"\d+ mm", i["name"]))): continue
        am.append([esc(i["name"]), esc(d.get("Type", "—")), esc(d.get("Damage", "—")),
                   esc(d.get("Damage (Trampler)", "—")), esc(d.get("Range", "—"))])
SEC.append(("weapons", "휴대 무기 · 탄약", "보병 화기와 탄약. 트램플러 피해는 포탄/거치포가 담당.",
            "<h3>휴대 무기</h3>" + tbl(["무기", "종류", "탄창", "재장전", "사거리"], wk) +
            "<h3>탄약</h3>" + tbl(["탄약", "종류", "피해", "피해(트램플러)", "사거리"], am) +
            f'<p class="cap">{rel("데이터")} 보병 탄약(권총·소총·산탄·저격)은 트램플러 장갑엔 거의 무력(트램플러 피해 0) — 트램플러 격침은 거치 캐논·포탄으로. 대(對)리액터 셀은 리액터 전용 예외.</p>'))

# ---- F. 방어구 ----
ar = []
for i in ITEMS:
    if i.get("category") == "Attire" and i.get("stats"):
        d = {s["label"]: s["value"] for s in i["stats"]}
        if "Armor" in d:
            ar.append((num(d.get("Armor")) or 0, [esc(i["name"]), f'<span class="big">{esc(d.get("Armor"))}</span>', esc(d.get("Regen", "—"))]))
ar.sort()
SEC.append(("armor", "방어구 (보병)", "캐릭터 착용 장갑 — 트램플러 장갑판과 별개.",
            tbl(["방어구", "장갑", "재생"], [r for _, r in ar]) +
            f'<p class="cap">{rel("데이터")} 재생은 피격 후 일정 지연 뒤 초당 회복.</p>'))

# ---- G. 승무원 · 화물 ----
crew = sorted([(num(PSTATS.get(sl, {}).get("Crew Slots")) or 0, p["name"]) for sl, p in PARTS.items()
               if p["cat"] == "승무원·생활" and PSTATS.get(sl, {}).get("Crew Slots")])
cargo = sorted([(num(PSTATS.get(sl, {}).get("Item Slots")) or 0, p["name"]) for sl, p in PARTS.items()
                if p["cat"] == "화물·보관" and PSTATS.get(sl, {}).get("Item Slots")])
cc = ("<h3>승무원 슬롯</h3>" +
      tbl(["객실", "승무원"], [[esc(n), f'<span class="big">{int(s)}</span>'] for s, n in crew]) +
      "<h3>화물 슬롯</h3>" +
      tbl(["화물칸", "적재 슬롯"], [[esc(n), f'<span class="big">{int(s)}</span>'] for s, n in cargo]))
SEC.append(("crew", "승무원 · 화물 용량", "크루룸과 화물칸의 수용량.",
            cc + f'<p class="cap">{rel("데이터")} 크루 정원은 최대 6인 {rel("언론")}. 화물은 선반·화물칸에 정리해야 추출 시 회수.</p>'))

# ---- H. 테크 비용 ----
byt = defaultdict(list)
for n in NODES: byt[n["tier"]].append(n["crowns"])
trows = []
for t in (1, 2, 3, 4):
    v = sorted(byt[t])
    trows.append([f"Tier {ROMAN[t]}", f"{comma(min(v))} ~ {comma(max(v))}", comma(v[len(v) // 2]), str(len(v))])
FAC = {"godlewski": "고들레프스키", "landwehr": "란트베어", "kaiser": "카이저"}
fc = defaultdict(int)
for n in NODES: fc[n["faction"]] += n["crowns"]
total = sum(fc.values())
frows = [[esc(FAC[f]), f'<span class="big">{comma(c)}</span>'] for f, c in fc.items()]
frows.append(["<b>전 진영 합계</b>", f'<b class="big">{comma(total)}</b>'])
SEC.append(("tech", "테크트리 — 크라운 비용", "노드 해금에 드는 크라운(재료 별도).",
            "<h3>티어별 비용</h3>" + tbl(["티어", "크라운 범위", "중앙값", "노드 수"], trows) +
            "<h3>진영별 전체 해금</h3>" + tbl(["진영", "총 크라운"], frows) +
            f'<p class="cap">{rel("데이터")} 전 테크 완성 ≈ {comma(total)} 크라운 + 아래 재료. 인게임 비용과 교차확인.</p>'))

# ---- I. 재료 게이트 ----
matamt = defaultdict(list)
for n in NODES:
    for c in n.get("costs", []):
        if c["name"] != "Crowns": matamt[c["name"]].append(c["amount"])
gate = sorted(matamt.items(), key=lambda x: -sum(x[1]))
GATE_HI = {"Black Box", "Alloy Steel", "Raw Aurogen Crystal", "District Officer's Portable Safe",
           "Crate of 1889 Chardonnay", "Ficus", "Canned Sea Deer XL", "Crystal"}
grows = []
for m, amts in gate:
    hi = m in GATE_HI
    nm = f'<b>{esc(mko(m))}</b>' if hi else esc(mko(m))
    grows.append([nm, str(len(amts)), comma(sum(amts)), str(max(amts)), "희귀 게이트" if hi else ""])
SEC.append(("mats", "테크 재료 게이트", "각 재료가 몇 개 노드에서·총 얼마나 필요한지.",
            tbl(["재료", "요구 노드", "총량", "단건 최대", ""], grows) +
            f'<p class="cap">{rel("데이터")} <b>블랙박스(18노드)·합금강(17노드)·원석 오로젠</b>이 중후반 핵심 게이트. 희귀재일수록 적은 양을 후반에 요구.</p>'))

# ---- J. 판매가 ----
buckets = defaultdict(list)
for i in ITEMS:
    sv = num(i.get("sellValue"))
    if sv: buckets[int(sv)].append(i["name"])
srows = []
for price in sorted(buckets, reverse=True):
    names = buckets[price]
    sample = ", ".join(names[:6]) + (f" 외 {len(names) - 6}종" if len(names) > 6 else "")
    srows.append([f'<span class="big">{comma(price)}</span>', str(len(names)), f'<span class="dim">{esc(sample)}</span>'])
SEC.append(("sell", "판매가 (크라운)", "상점 판매 단가별 분포.",
            tbl(["판매가", "종수", "예시"], srows) +
            f'<p class="cap">{rel("데이터")} 최고가 500. 흔한 자원·기본 탄약은 1 — 팔 가치 거의 없음. 블랙박스는 테크 완성 전 비축({rel("언론")} 개당 ~500).</p>'))

# ---- K. 제작 레시피 ----
def rfmt(r): return " · ".join(f"{esc(mko(m.get('item')))}×{esc(m.get('amount'))}" for m in r)
pick = []
def add_rec(pred, head):
    rows = []
    for i in ITEMS:
        if i.get("recipe") and pred(i):
            rows.append([esc(i["name"]), rfmt(i["recipe"]), esc(i.get("workbench") or "—")])
    return f"<h3>{head}</h3>" + tbl(["결과물", "재료", "작업대"], rows) if rows else ""
rec_html = (
    add_rec(lambda i: "Shell" in i["name"], "대포 포탄") +
    add_rec(lambda i: i.get("category") == "Ammo" and "Shell" not in i["name"], "휴대 탄약") +
    add_rec(lambda i: i.get("category") in ("Misc", "Resources") and i.get("recipe"), "정제 · 상위 자원")
)
SEC.append(("recipe", "제작 레시피 (핵심)", "탄약·정제재의 인풋. 무기 등 전체는 도감 모달 참조.",
            rec_html +
            f'<p class="cap">{rel("데이터")} <b>블랙박스 ← 연산 모듈×10</b>, 직물 ← 천 조각×5·실×15. 전체 레시피는 <a href="items.html">아이템 도감</a> 모달.</p>'))

# ---- L. 게임 상수 ----
const_rows = [
 ["적 리액터 파괴", "구경에 따라 ~6~10발", rel("AI")],
 ["에너지 로드 1개 주행", "~10~12분 (신규 5개 시작)", rel("언론")],
 ["추출 — 호출 후", "초록 연기 90초 + 구조 케이블 ~60초", rel("언론") + rel("커뮤니티")],
 ["Amplifier 지속", "~1분", rel("AI")],
 ["블랙박스", "개당 ~500 크라운 · 함선당 1개", rel("언론")],
 ["라디오 비콘 박스", "~2,000 크라운 (시간 내 추출)", rel("AI")],
 ["기계 부품 구매", "1개 = 2크라운", rel("AI")],
 ["크루 정원", "최대 6인", rel("언론")],
 ["적 트램플러 공격 순서", "다리 → 대포 → 조향 → 리액터", rel("언론")],
]
SEC.append(("const", "게임 상수 (미검증 · 인게임 확인 권장)", "구조 데이터가 아닌 커뮤니티/매체 수치 — EA라 변동.",
            tbl(["항목", "수치", "신뢰도"], const_rows) +
            f'<p class="cap">{rel("AI")} 표기는 단일 AI-SEO 출처라 특히 주의. 자세한 교차검증은 <a href="https://github.com/showneykim/sand-kr-guide/tree/main/docs/kb">지식베이스</a>의 _검증.md.</p>'))

# ===================== ASSEMBLE =====================
navchips = "".join(f'<a href="#{sid}">{esc(title)}</a>' for sid, title, _, _ in SEC)
sections_html = ""
for sid, title, kicker, body in SEC:
    sections_html += (f'<section id="{sid}" class="sec">'
                      f'<h2>{esc(title)}</h2><p class="kicker">{esc(kicker)}</p>{body}</section>')

FAV = ("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2032%2032'%3E"
       "%3Crect%20width='32'%20height='32'%20rx='6'%20fill='%2313100b'/%3E%3Ctext%20x='16'%20y='23'%20"
       "font-size='21'%20font-weight='700'%20fill='%23d9a84c'%20text-anchor='middle'%20font-family='sans-serif'%3ES%3C/text%3E%3C/svg%3E")

CSS = """
:root{--bg:#13100b;--bg2:#1a150e;--panel:#221a10;--edge:#392b1a;--edge2:#4f3a21;--ink:#e9dfcd;--muted:#ab9a7c;--faint:#9a8966;--brass:#d9a84c;--brass-d:#a9772a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Pretendard","Malgun Gothic","Apple SD Gothic Neo",system-ui,sans-serif;font-size:16px;line-height:1.6;background-image:radial-gradient(1100px 460px at 82% -8%,rgba(217,168,76,.07),transparent 60%)}
a{color:var(--brass);text-decoration:none}a:hover{text-decoration:underline}
html{scroll-behavior:smooth}
.topbar{position:sticky;top:0;z-index:50;backdrop-filter:blur(9px);background:rgba(15,11,7,.86);border-bottom:1px solid var(--edge)}
.topbar .in{max-width:1180px;margin:0 auto;padding:11px 22px;display:flex;gap:14px;align-items:center}
.brand{font-family:"Oswald",sans-serif;font-weight:700;letter-spacing:.2em;color:var(--brass);font-size:17px}
.tabs{margin-left:auto;display:flex;gap:6px;flex-wrap:wrap}
.tabs a{font-size:13px;color:var(--muted);padding:6px 13px;border:1px solid var(--edge2);border-radius:6px}
.tabs a.on{color:var(--bg);background:var(--brass);border-color:var(--brass);font-weight:600}
.tabs a:hover{text-decoration:none;color:var(--brass)}.tabs a.on:hover{color:var(--bg)}
@media(max-width:560px){.topbar .in{padding:9px 12px;gap:8px;flex-wrap:wrap}.brand{font-size:15px}.tabs{flex-basis:100%;margin-left:0}.tabs a{padding:5px 9px;font-size:12px}.secnav .in{flex-wrap:nowrap;overflow-x:auto}.secnav a{flex:none}}
header.h{max-width:1180px;margin:0 auto;padding:30px 22px 6px}
header.h h1{font-family:"Oswald",sans-serif;font-weight:700;letter-spacing:.04em;font-size:clamp(24px,4vw,34px);margin:0;color:#fff}
header.h .sub{color:var(--muted);margin:8px 0 0;font-size:15px;max-width:820px}
header.h .sub b{color:var(--brass)}
.secnav{position:sticky;top:55px;z-index:40;background:rgba(15,11,7,.92);backdrop-filter:blur(6px);border-bottom:1px solid var(--edge);margin-top:16px}
.secnav .in{max-width:1180px;margin:0 auto;padding:10px 22px;display:flex;gap:6px;flex-wrap:wrap}
.secnav a{font-size:12px;color:var(--muted);padding:5px 10px;border:1px solid var(--edge2);border-radius:999px;white-space:nowrap}
.secnav a:hover{color:var(--brass);text-decoration:none;border-color:color-mix(in srgb,var(--brass) 50%,var(--edge2))}
main{max-width:1180px;margin:0 auto;padding:8px 22px 80px}
.sec{padding:30px 0 6px;scroll-margin-top:104px;border-top:1px solid var(--edge)}
.sec:first-child{border-top:0}
.sec h2{font-family:"Oswald",sans-serif;font-weight:600;font-size:21px;margin:0;color:var(--brass);letter-spacing:.02em}
.sec h3{font-family:"Oswald",sans-serif;font-weight:500;font-size:13.5px;letter-spacing:.04em;color:var(--muted);text-transform:uppercase;margin:20px 0 8px}
.kicker{color:var(--muted);font-size:14px;margin:4px 0 14px}
.tw{overflow-x:auto;border:1px solid var(--edge);border-radius:9px;background:linear-gradient(180deg,var(--panel),var(--bg2))}
.tw:focus{outline:2px solid var(--brass);outline-offset:2px}.tw:focus:not(:focus-visible){outline:none}
table.ref{width:100%;border-collapse:collapse;font-size:13.5px;min-width:440px}
table.ref th{text-align:left;font-family:"Oswald",sans-serif;font-weight:600;font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--faint);padding:10px 13px;border-bottom:1px solid var(--edge2);white-space:nowrap}
table.ref td{padding:9px 13px;border-bottom:1px solid var(--edge);vertical-align:top}
table.ref tr:last-child td{border-bottom:0}
table.ref tr:hover td{background:rgba(217,168,76,.045)}
table.ref .big{font-family:"Oswald",sans-serif;font-weight:700;color:var(--brass);font-size:15px}
table.ref .dim{color:var(--muted);font-size:12.5px}
table.ref b{color:#e0cfa6}
.cap{font-size:12.5px;color:var(--muted);margin:11px 2px 0;line-height:1.6}
.cap b{color:#d6c4a0}
.rel{display:inline-block;font-family:"Oswald",sans-serif;font-size:9.5px;font-weight:600;letter-spacing:.04em;padding:1px 6px;border-radius:4px;margin:0 2px 0 0;vertical-align:middle;border:1px solid}
.rel.rd{color:#8aae66;border-color:#3f5a30;background:rgba(138,174,102,.1)}
.rel.rv{color:#6fb24a;border-color:#3f5a30;background:rgba(111,178,74,.1)}
.rel.rp{color:#5a9bd4;border-color:#2f4a63;background:rgba(90,155,212,.1)}
.rel.rc{color:var(--brass);border-color:var(--brass-d);background:rgba(217,168,76,.1)}
.rel.ra{color:#cf6a4a;border-color:#6a2f1f;background:rgba(207,106,74,.1)}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--muted);margin:14px 0 0;padding:12px 16px;border:1px solid var(--edge);border-radius:8px;background:var(--bg2)}
footer{border-top:1px solid var(--edge);background:var(--bg2);margin-top:40px}
footer .in{max-width:1180px;margin:0 auto;padding:22px 22px 44px;color:var(--muted);font-size:12px;line-height:1.65}
footer a{color:var(--muted)}
"""

LEGEND = ('<div class="legend"><b style="color:var(--ink)">신뢰도</b>'
          + rel("데이터") + "JSON 데이터(에디터 수치) · "
          + rel("언론") + "매체 · " + rel("커뮤니티") + "플레이어 · "
          + rel("AI") + "AI-SEO 위키(미검증, 주의)</div>")

HTML = """<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>수치 레퍼런스 (한국어) — 샌드: 레이더스 오브 소피</title>
<meta name="description" content="SAND: Raiders of Sophie 수치 레퍼런스 한국어 — 부품 스탯·테크 비용·재료 게이트·판매가·제작 레시피·게임 상수.">
<meta name="theme-color" content="#13100b">
<meta property="og:type" content="website"><meta property="og:site_name" content="SAND 한국어 가이드">
<meta property="og:title" content="수치 레퍼런스 (한국어) — 샌드: 레이더스 오브 소피">
<meta property="og:description" content="부품 스탯·테크 비용·재료·판매가·레시피·게임 상수를 한곳에.">
<meta property="og:image" content="https://showneykim.github.io/sand-kr-guide/assets/img/crop_hero.webp">
<meta property="og:url" content="https://showneykim.github.io/sand-kr-guide/reference.html">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="__FAV__">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&display=swap" rel="stylesheet">
<style>__CSS__</style></head>
<body>
<div class="topbar"><div class="in">
  <a class="brand" href="index.html" style="text-decoration:none" aria-label="홈 — 입문 가이드">SAND</a>
  <nav class="tabs" aria-label="주요"><a href="index.html">입문 가이드</a><a href="tech.html">테크트리</a><a href="items.html">아이템 도감</a><a href="blueprints.html">블루프린트</a><a class="on" aria-current="page" href="reference.html">수치</a></nav>
</div></div>

<header class="h">
  <h1>수치 <span style="color:var(--brass)">레퍼런스</span></h1>
  <p class="sub">부품 스탯·테크 비용·재료 게이트·판매가·제작 레시피·게임 상수를 한곳에. <b>대부분 게임 데이터에서 직접 산출</b>했고, 구조 데이터가 없는 항목만 커뮤니티/매체 수치를 <b>신뢰도 표시</b>와 함께 실었습니다. 얼리액세스라 패치로 바뀔 수 있으니 인게임 확인을 권장합니다.</p>
  __LEGEND__
</header>

<div class="secnav"><div class="in">__NAV__</div></div>

<main>
__SECTIONS__
</main>

<footer><div class="in">
  <p><b style="color:var(--muted)">데이터 출처.</b> 부품 스탯·테크 비용·재료·판매가·레시피는 게임 인게임 데이터이며 커뮤니티 팬 DB <a href="https://sand-help.com" target="_blank" rel="noopener">sand-help.com</a>(비공식)에서 가져와 한국어로 재구성했습니다. 게임 상수(전투·연료·추출)는 매체·커뮤니티·AI-SEO 출처라 신뢰도가 낮고 EA라 변동됩니다 — 표의 신뢰도 태그와 <a href="https://github.com/showneykim/sand-kr-guide/tree/main/docs/kb">지식베이스</a>의 _검증.md를 함께 보세요.</p>
  <p>비공식 팬 가이드 · 얼리액세스(2026-06-22) 기준. 모든 권리는 Hologryph·TowerHaus·tinyBuild에 있습니다.</p>
</div></footer>
</body></html>"""

HTML = (HTML.replace("__CSS__", CSS).replace("__FAV__", FAV).replace("__LEGEND__", LEGEND)
        .replace("__NAV__", navchips).replace("__SECTIONS__", sections_html))
open(os.path.join(ROOT, "reference.html"), "w", encoding="utf-8").write(HTML)
print("wrote reference.html", len(HTML), "bytes ;", len(SEC), "sections")
print("섹션:", [s[0] for s in SEC])
print("테크 총비용:", comma(total), "| 섀시", len(ch), "| 동력", len(pw), "| 캐논킷", len(kit), "| 포탄", len(shells),
      "| 휴대무기", len(wk), "| 탄약", len(am), "| 방어구", len(ar), "| 판매가버킷", len(srows), "| 재료", len(grows))
