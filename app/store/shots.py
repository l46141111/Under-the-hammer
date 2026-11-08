# Play 商店截圖：手機直式 1080×1920（360×640、3 倍），所有對外連線都擋掉
import sys,asyncio,json,os
from playwright.async_api import async_playwright
URL='file:///home/claude/uth-work/check/v80t.html';OUT='/home/claude/uth-work/store/shots';os.makedirs(OUT,exist_ok=True)
SETUP="""if(dayOpen)closeDayCard();S.unl={travel:1,market:1,shop:1,events:1,east:1,abroad:1,jade:1};S.npcQ=[];S.npcMet={zhou:1,kun:1,you:1,lin:1};S.story.ch=9;S.star=3;S.money=86400;
 const mk=(id,q)=>({t:'spec',id,st:'ok',q:q||80,cert:'self',fake:false,comp:false,src:'dahan'});
 ['crab','elrathia','rosestone','sharktooth','ammonite','shell','deer','knightia','belem'].forEach((id,i)=>{if(SPEC[id])S.cases[i]=mk(id);});S.region='tw';S.day=6;S.wx='sun';S.wxHome='sun';
 S.npcQ=[];if(!E.npcModal.hidden){npcOpen=false;DLG.on=false;closeModal(E.npcModal);}renderAll();0"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        c=await b.new_context(viewport={'width':360,'height':640},device_scale_factor=3,is_mobile=True,has_touch=True)
        await c.route('**/*',lambda r:r.continue_() if r.request.url.startswith(('file:','data:','blob:')) else r.abort())
        pg=await c.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        EV=lambda code:pg.evaluate('__ev('+json.dumps(code)+')')
        await pg.goto(URL);await pg.wait_for_timeout(900);await EV(SETUP);await pg.wait_for_timeout(400)
        async def shot(name,wait=600,el=None):
            await pg.wait_for_timeout(wait);await pg.evaluate('window.scrollTo(0,0)')
            if el:await pg.evaluate(f"(()=>{{const e=document.querySelector('{el}');if(e){{const r=e.getBoundingClientRect();window.scrollTo(0,Math.max(0,r.top+scrollY-136));}}}})()")
            await pg.evaluate("document.getElementById('toasts')&&(document.getElementById('toasts').innerHTML='')")
            await pg.wait_for_timeout(150);await pg.screenshot(path=f'{OUT}/{name}.png');print('shot',name,el)
        # 1 野外岩壁
        await EV("setView('field');0");await shot('1-field',900,'#siteName')
        # 2 剖開：Wheeler 頁岩裡的三葉蟲
        await EV("CUE_TBL[3]=[['red',1]];playSplit({rk:'wheeler',tier:3,hid:'elrathia',rich:null});0");await pg.wait_for_timeout(2600);await shot('2-split-glow',0)
        await pg.wait_for_timeout(6500);await shot('3-split-reveal',0)
        await EV("if(!E.ov.hidden){ovBusy=false;E.ov.hidden=true;if(A)A.alive=false;}0")
        # 4 博物館展示廳
        await EV("""setView('museum');HALL.ppl=HALL.ppl.filter(p=>p.staff);['adult','kid','old','tourist','student','teacher'].forEach((k,i)=>{const q=hallSpawn(k);if(q){q.x=40+i*((HALL.W-60)/6);q.y=124+(i%3)*10;q.path=[];q.goal=null;q.st=i%2?'idle':'look';q.bub='done';q.todo=[];q.wait=99;q.dir=0;}});hallNpc('zhou');0""")
        await shot('4-museum',2500,'#hallCv')
        # 5 緬甸曼德勒的市場
        await EV("travel('mm',null);S.day=10;S.wx='sun';S.npcQ=[];if(!E.npcModal.hidden){npcOpen=false;DLG.on=false;closeModal(E.npcModal);}refreshMarket();setView('market');renderMarket();0")
        await shot('5-market',2600,'#marketW')
        print('errors',errs);await b.close()
asyncio.run(main())
