#!/usr/bin/env python3
import os, struct, zlib, hashlib

def generate():
    W, H = 1024, 1024
    all_raw = []
    for y in range(H):
        line = [0]
        for x in range(W):
            if y < 400:
                t = y / 400.0
                r, g, b = int(60+60*t), int(120+80*t), int(255-30*t)
            elif y < 600:
                t = (y-400)/200.0
                if t < 0.5:
                    r, g, b = int(120+135*(t*2)), int(200-80*(t*2)), int(225-175*(t*2))
                else:
                    t2 = (t-0.5)*2
                    r, g, b = 255, int(120+80*t2), int(50+100*t2)
            else:
                t = (y-600)/424.0
                n = ((x*31+y*17)%23)-11
                r, g, b = min(255,max(0,int(34+40*t)+n)), min(255,max(0,int(120+80*t)+n)), min(255,max(0,int(34+20*t)+n))
            dx, dy = x-512, y-320
            d = (dx*dx+dy*dy)**0.5
            if d < 80:
                t = d/80; r, g, b = 255, int(230-50*t), int(50+100*t)
            elif d < 180:
                t = (d-80)/100.0; a = int((dx*360/max(d,1))%360); ray = 1 if (a+22)%45<15 else 0; gl = 1-t
                r, g, b = int(255*gl), int((200+55*ray)*gl), int((50+100*ray)*gl)
            else:
                d2 = (dx*dx+(y-650)**2)**0.5
                for ri,(cr,cg,cb) in enumerate([(255,0,0),(255,127,0),(255,255,0),(0,200,0),(0,100,255),(75,0,130),(148,0,211)]):
                    if 275+ri*12 <= d2 <= 285+ri*12 and y<580:
                        af=(y-650)/max(abs(x-512),1)
                        if abs(af)>0 or (x<512 and y<650): r,g,b=cr,cg,cb; break
                for cx,cy,rx,ry in [(200,150,80,50),(750,120,100,60),(450,100,60,40)]:
                    cd=((x-cx)**2/(rx**2)+(y-cy)**2/(ry**2))
                    if cd<1.0: w=int(255*(1-cd*0.3)); r,g,b=w,w,min(255,w+5)
                for bx,by,br,color in [(300,450,30,(255,100,50)),(700,400,25,(100,150,255)),(550,500,20,(255,50,200))]:
                    bd=((x-bx)**2+(y-by)**2)**0.5
                    if bd<br:
                        ang=int(((x-bx)*180/max(bd,1))%360)
                        if abs(ang)<40 or abs(ang-180)<40 or abs(ang+180)<40:
                            wn=((x*7+y*11)%30)-11
                            r,g,b=min(255,max(0,color[0]+wn)),min(255,max(0,color[1]+wn)),min(255,max(0,color[2]+wn))
                        else:
                            r,g,b=min(255,color[0]+80),min(255,color[1]+80),min(255,color[2]+80)
                for fx,fy,fr,color in [(100,700,25,(255,100,150)),(250,750,20,(255,200,50)),(400,680,22,(200,100,255)),(600,720,18,(255,150,50)),(750,690,24,(255,80,80)),(850,760,20,(100,255,200)),(500,780,19,(255,255,100)),(180,820,21,(255,120,200)),(700,800,23,(150,200,255)),(950,730,17,(255,180,100))]:
                    fd=((x-fx)**2+(y-fy)**2)**0.5
                    if abs(x-fx)<3 and fy<y<fy+30: r,g,b=34,140,34
                    elif 8<fd<fr+8:
                        pa=int(((x-fx)*360/max(fd,1))%360)
                        if pa%45<25: r,g,b=color
                    if fd<6: r,g,b=255,230,50
                for sx2,sy2 in [(80,80),(920,60),(150,500),(870,480),(350,100),(650,80),(500,550),(100,900),(900,900),(512,200)]:
                    sd=((x-sx2)**2+(y-sy2)**2)**0.5
                    if sd<4: r,g,b=255,255,min(255,200+int(55*(sd/4)))
            line.append(r); line.append(g); line.append(b)
        all_raw.append(bytes([0])+bytes(line))
    return b''.join(all_raw)

def make_png(raw):
    comp = zlib.compress(raw, 6)
    def chunk(ct, d):
        c=ct+d; cr=struct.pack('>I',zlib.crc32(c)&0xFFFFFFFF)
        return struct.pack('>I',len(d))+c+cr
    sig=b'\x89PNG\r\n\x1a\n'
    return sig+chunk(b'IHDR',struct.pack('>IIBBBBB',1024,1024,8,2,0,0,0))+chunk(b'IDAT',comp)+chunk(b'IEND',b'')

od = os.environ.get('MAKEFUN_OUTPUT_DIR', '/tmp/test_out')
os.makedirs(od, exist_ok=True)
raw = generate()
png = make_png(raw)
p = os.path.join(od, 'entry.png')
with open(p, 'wb') as f: f.write(png)
h = hashlib.sha256(png).hexdigest()
print(f"Wrote {len(png)} bytes to {p}")
print(f"SHA256: {h}")
