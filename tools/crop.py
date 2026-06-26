from PIL import Image
import os
SRC=os.path.expanduser("~/sand-kr/screenshots-source")
OUT=os.path.expanduser("~/sand-kr-guide/assets/img")
os.makedirs(OUT,exist_ok=True)
# (file, cropbox left,top,right,bottom in 5120x1440 space, outname, maxwidth)
jobs=[
 ("20260626172903_1.jpg",(1300,150,2050,1430),"crop_region.png",900),    # 서버 리전 목록 + 일부 행성
 ("20260626172903_1.jpg",(2050,80,3700,1300),"crop_hero.png",1500),       # SAND 행성 로고 (히어로)
 ("20260626182446_1.jpg",(1740,250,3450,1240),"crop_mode.png",1500),      # 모드선택 + RIVALS
 ("20260626182449_1.jpg",(1280,40,3780,1340),"crop_overview.png",1700),   # 출격준비 OVERVIEW 패널들
 ("20260626182449_1.jpg",(1180,120,2400,1300),"crop_character.png",1100), # 캐릭터+격납고
 ("20260626173319_1.jpg",(1900,180,3680,1180),"crop_combat.png",1600),    # COMBAT MANUAL 트램플러 도식
 ("20260626173313_1.jpg",(2950,360,3520,1080),"crop_editor_req.png",700), # 에디터 Requirements
 ("20260626173322_1.jpg",(1560,230,3520,1180),"crop_evac.png",1600),      # EVACUATION 카드들
 ("20260626173321_1.jpg",(1820,360,3520,1120),"crop_storm.png",1500),     # STORM DIVE 카드
]
for f,box,name,mw in jobs:
    p=os.path.join(SRC,f)
    if not os.path.exists(p):
        print("MISS",f); continue
    im=Image.open(p).crop(box)
    if im.width>mw:
        im=im.resize((mw,int(im.height*mw/im.width)),Image.LANCZOS)
    im.save(os.path.join(OUT,name))
    print(name, im.size)
