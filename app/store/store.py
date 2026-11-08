# 上架素材：App 圖示（Play 512、Android 圖示用的前景／背景 1024）、啟動畫面 2732、Play 宣傳橫幅 1024×500
# 全部用遊戲自己的像素素材畫（三葉蟲 Elrathia 的 32 格圖、地質槌、Wheeler 頁岩的紋層），不用 AI 圖
import sys,asyncio,json,base64,io,os
from playwright.async_api import async_playwright
from PIL import Image,ImageDraw,ImageFont
OUT='/home/claude/uth-work/store';os.makedirs(OUT,exist_ok=True)
BG='#1E2930'
JS=r"""(()=>{
const N=64,c=cvs(N,N),x=c.getContext('2d');
const P=(i,j,col)=>{x.fillStyle=col;x.fillRect(i,j,1,1);};
// 頁岩石板：上面是剖開的層面（新鮮、淺一點），下面露出一點厚度，看得到紋層
const top=[[5,17],[10,12],[52,11],[59,16],[60,46],[55,50],[10,51],[4,47]];
const inPoly=(px,py,pts)=>{let o=false;for(let a=0,b=pts.length-1;a<pts.length;b=a++){const[xa,ya]=pts[a],[xb,yb]=pts[b];if((ya>py)!==(yb>py)&&px<(xb-xa)*(py-ya)/(yb-ya)+xa)o=!o;}return o;};
const base='#8E8A80',h=(i,j)=>hHash(i*31+j*7,j*13+i*3);
for(let j=0;j<N;j++)for(let i=0;i<N;i++){
  const inTop=inPoly(i+.5,j+.5,top),inSide=!inTop&&inPoly(i+.5,j-4.5,top)&&j>30;
  if(inTop){let col=shade(base,.1+(h(i,j)-.5)*.06);if(h(i,j)>.97)col=shade(base,.2);if(h(i,j)<.03)col=shade(base,-.1);P(i,j,col);}
  else if(inSide){const d=j-(j>46?44:44);const band=[-.12,-.2,-.08,-.24,-.14][(j+(i>>4))%5];P(i,j,shade(base,band-.06));}
}
// 外框
for(let j=0;j<N;j++)for(let i=0;i<N;i++){const me=inPoly(i+.5,j+.5,top)||(inPoly(i+.5,j-4.5,top)&&j>30);if(me)continue;
  const nb=[[1,0],[-1,0],[0,1],[0,-1]].some(([dx,dy])=>{const a=i+dx,b=j+dy;return inPoly(a+.5,b+.5,top)||(inPoly(a+.5,b-4.5,top)&&b>30);});if(nb)P(i,j,'#14100C');}
// 層面的亮邊
for(let i=6;i<59;i++){for(let j=10;j<25;j++){if(inPoly(i+.5,j+.5,top)&&!inPoly(i+.5,j-.5,top)){P(i,j,shade(base,.28));break;}}}
// 三葉蟲躺在層面上
const t=specArt('elrathia','#4A4642','#8C857A');x.drawImage(t,9,15,32,32);
// 地質槌靠在右上角（遊戲裡剖開岩塊用的那一支）
const save=A;A={hand:[30.6,30.6],hL:13};x.save();x.scale(2,2);drawHammer(x,-1.95);x.restore();A=save;
// 錘頭的外框
const id=x.getImageData(0,0,N,N).data,al=(i,j)=>i>=0&&j>=0&&i<N&&j<N&&id[(j*N+i)*4+3]>0;
const add=[];for(let j=0;j<N;j++)for(let i=0;i<N;i++)if(!al(i,j)&&[[1,0],[-1,0],[0,1],[0,-1]].some(([dx,dy])=>al(i+dx,j+dy)))add.push([i,j]);
add.forEach(([i,j])=>P(i,j,'#14100C'));
// 宣傳橫幅用的標本（32 格）
const ids=['elrathia','ammonite','crab','sharktooth','rosestone','knightia'].filter(k=>SPEC[k]);
const sp=ids.map(k=>{const d=SPEC[k];return[k,d.bg,specArt(d.g,d.fg,d.hi).toDataURL()];});
return JSON.stringify({icon:c.toDataURL(),sp});})()"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
        await pg.route('**/*',lambda r:r.continue_() if r.request.url.startswith(('file:','data:')) else r.abort())
        await pg.goto('file:///home/claude/uth-work/check/v80t.html');await pg.wait_for_timeout(800)
        o=json.loads(await pg.evaluate('__ev('+json.dumps(JS)+')'));await b.close()
    print('errors',errs)
    im=lambda u:Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGBA')
    art=im(o['icon']);art.save(f'{OUT}/icon-art-64.png')
    def onbg(size,scale,bg=BG):
        I=Image.new('RGBA',(size,size),bg);A=art.resize((64*scale,64*scale),Image.NEAREST);I.alpha_composite(A,((size-64*scale)//2,(size-64*scale)//2));return I
    onbg(512,8).save(f'{OUT}/play-icon-512.png')
    # Android 圖示：前景（透明，圖案在安全區內）、背景（純色）、舊式圖示
    fg=Image.new('RGBA',(1024,1024),(0,0,0,0));A=art.resize((832,832),Image.NEAREST);fg.alpha_composite(A,(96,96));fg.save(f'{OUT}/icon-foreground.png')
    Image.new('RGBA',(1024,1024),BG).save(f'{OUT}/icon-background.png')
    onbg(1024,14).save(f'{OUT}/icon-only.png')
    # 啟動畫面：深色底、中間是圖示和遊戲名稱
    F=ImageFont.truetype('/home/claude/uth-work/font/cubic/package/Cubic_11_1.100_R.ttf',132)
    sp=Image.new('RGBA',(2732,2732),BG);A=art.resize((64*12,64*12),Image.NEAREST);sp.alpha_composite(A,((2732-768)//2,(2732-768)//2-140))
    d=ImageDraw.Draw(sp);t='Under the Hammer';w=d.textlength(t,font=F);d.text(((2732-w)/2,(2732-768)//2-140+768+60),t,font=F,fill='#F2BE62')
    sp.save(f'{OUT}/splash.png');sp.save(f'{OUT}/splash-dark.png')
    # Play 宣傳橫幅 1024×500（不能有透明）
    W,H=1024,500;fgx=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(fgx)
    rgb=lambda c:tuple(int(c[i:i+2],16) for i in (1,3,5))
    layers=[('#C7A060',30),('#8D8272',28),('#7D7668',26),('#A08C6A',26)];y=H-sum(h for _,h in layers)
    d.rectangle([0,y-6,W,y],fill='#5E7E43')
    for col,h in layers:
        d.rectangle([0,y,W,y+h],fill=col)
        for xx in range(0,W,16):
            if (xx//16+y)%5==0:d.rectangle([xx,y+h//2,xx+5,y+h//2+3],fill=tuple(max(0,v-35) for v in rgb(col)))
        y+=h
    F1=ImageFont.truetype('/home/claude/uth-work/font/cubic/package/Cubic_11_1.100_R.ttf',66);F2=ImageFont.truetype('/home/claude/uth-work/font/cubic/package/Cubic_11_1.100_R.ttf',33)
    d.text((44,30),'Under the Hammer',font=F1,fill='#F2BE62');d.text((48,112),'像素風地質博物館經營遊戲',font=F2,fill='#E2E7E3')
    big=art.resize((256,256),Image.NEAREST);fgx.paste(big,(W-256-36,24),big)
    Z=3;x0=44;yy=196
    for k,(sid,bgc,u) in enumerate(o['sp'][:5]):
        s=im(u).resize((32*Z,32*Z),Image.NEAREST);ox=x0+k*(32*Z+22)
        d.rectangle([ox-6,yy-6,ox+32*Z+5,yy+32*Z+5],fill=bgc,outline='#2B2420',width=3);fgx.paste(s,(ox,yy),s)
    fgx.save(f'{OUT}/play-feature-1024x500.png')
    print('ok',[f for f in os.listdir(OUT)])
asyncio.run(main())
