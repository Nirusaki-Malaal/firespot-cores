#!/usr/bin/env python3
"""Two original CC0-1.0 Game Boy collect-the-checkpoint games. No third-party assets."""
from pathlib import Path
import json

FONT={
'A':['01110','10001','10001','11111','10001','10001','10001'],
'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'G':['01111','10000','10000','10111','10001','10001','01110'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['11111','00100','00100','00100','00100','00100','11111'],
'J':['00111','00010','00010','00010','00010','10010','01100'],
'K':['10001','10010','10100','11000','10100','10010','10001'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],
'N':['10001','11001','10101','10011','10001','10001','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'Q':['01110','10001','10001','10001','10101','10010','01101'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'V':['10001','10001','10001','10001','10001','01010','00100'],
'W':['10001','10001','10001','10101','10101','10101','01010'],
'X':['10001','10001','01010','00100','01010','10001','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],
'Z':['11111','00001','00010','00100','01000','10000','11111'],
'0':['01110','10001','10011','10101','11001','10001','01110'],
'1':['00100','01100','00100','00100','00100','00100','01110'],
'2':['01110','10001','00001','00010','00100','01000','11111'],
'3':['11110','00001','00001','01110','00001','00001','11110'],
'4':['00010','00110','01010','10010','11111','00010','00010'],
'5':['11111','10000','10000','11110','00001','00001','11110'],
'6':['01110','10000','10000','11110','10001','10001','01110'],
'7':['11111','00001','00010','00100','01000','01000','01000'],
'8':['01110','10001','10001','01110','10001','10001','01110'],
'9':['01110','10001','10001','01111','00001','00001','01110'],
}
class Asm:
 def __init__(self):self.code=bytearray();self.labels={};self.fix=[]
 def e(self,*v):self.code.extend(v)
 def label(self,n):self.labels[n]=0x150+len(self.code)
 def addr(self,op,n):self.e(op,0,0);self.fix.append((len(self.code)-2,n))
 def reg(self,r,v):self.e(0x3E,v,0xE0,r)
 def put(self,addr,v):self.e(0x3E,v,0xEA,addr&255,addr>>8)
 def load(self,addr):self.e(0xFA,addr&255,addr>>8)
 def store(self,addr):self.e(0xEA,addr&255,addr>>8)
 def finish(self):
  for off,n in self.fix:self.code[off:off+2]=self.labels[n].to_bytes(2,'little')
  return self.code

def game(title,speed,battery=False):
 chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';ids={c:16+i for i,c in enumerate(chars)}
 tiles=bytearray(16)  # blank
 for rows in [[0x3C,0x7E,0xFF,0xDB,0xDB,0xFF,0x7E,0x3C],[0x18,0x3C,0x7E,0xFF,0xFF,0x7E,0x3C,0x18],[0,0,0,0x10,0,0,0,0]]:
  for r in rows:tiles.extend([r,r])
 tiles.extend(bytes(16*(16-4)))
 for c in chars:
  for r in FONT[c]+['00000']:
   b=int(r,2)<<2;tiles.extend([b,b])
 bg=bytearray(1024)
 def text(row,col,s):
  for i,c in enumerate(s):bg[row*32+col+i]=ids.get(c,0)
 text(0,1,title);text(2,1,'POINTS');text(2,9,'0');text(16,1,'DPAD MOVE');text(17,1,'A OR SELECT TO BEEP')
 for y in range(4,15):
  for x in range(1,19):
   if (x+y*(2 if speed==2 else 1))%5==0:bg[y*32+x]=3
 a=Asm();a.e(0xF3,0x31,0xFE,0xFF)
 a.label('wait0');a.e(0xF0,0x44,0xFE,144);a.addr(0xDA,'wait0');a.reg(0x40,0)
 def copy(src,dst,count,n):
  a.addr(0x11,src);a.e(0x21,dst&255,dst>>8,0x01,count&255,count>>8)
  a.label(n);a.e(0x1A,0x22,0x13,0x0B,0x78,0xB1);a.addr(0xC2,n)
 copy('tiles',0x8000,len(tiles),'copytiles');copy('bg',0x9800,1024,'copybg')
 a.e(0x21,0,0xFE,0x06,160)
 a.label('clearOAM');a.e(0xAF,0x22,0x05);a.addr(0xC2,'clearOAM')
 for addr,val in [(0xFE00,80),(0xFE01,40),(0xFE02,1),(0xFE04,120),(0xFE05,136),(0xFE06,2),(0xC000,0)]:a.put(addr,val)
 if battery:
  a.put(0,0x0A);a.load(0xA000);a.e(0xFE,10);a.addr(0xDA,'batteryvalid');a.e(0xAF)
  a.label('batteryvalid');a.store(0xC000);a.e(0xC6,ids['0']);a.store(0x9849)
 a.reg(0x47,0xE4);a.reg(0x48,0xE4);a.reg(0x42,0);a.reg(0x43,0)
 a.reg(0x26,0x80);a.reg(0x24,0x77);a.reg(0x25,0x11);a.reg(0x40,0x93)
 a.label('frame');a.e(0xF0,0x44,0xFE,144);a.addr(0xDA,'frame')
 a.reg(0,0x20);a.e(0xF0,0,0xF0,0,0x4F)
 # Limit movement to the visible playfield.
 for bit,addr,bound,positive,n in [(0,0xFE01,152,True,'right'),(1,0xFE01,16,False,'left'),(2,0xFE00,48,False,'up'),(3,0xFE00,128,True,'down')]:
  a.e(0xCB,0x41+8*bit);a.addr(0xC2,n)
  a.load(addr);a.e(0xFE,bound);a.addr(0xD2 if positive else 0xDA,n)
  if not positive:a.addr(0xCA,n)
  a.e(*([0x3C if positive else 0x3D]*speed));a.store(addr);a.label(n)
 # Exact positions are reachable: all coordinates are even for the faster game.
 a.load(0xFE01);a.e(0x47);a.load(0xFE05);a.e(0xB8);a.addr(0xC2,'nogoal')
 a.load(0xFE00);a.e(0x47);a.load(0xFE04);a.e(0xB8);a.addr(0xC2,'nogoal')
 a.load(0xC000);a.e(0x3C,0xFE,10);a.addr(0xDA,'scoreok');a.e(0xAF)
 a.label('scoreok');a.store(0xC000)
 if battery:a.store(0xA000)
 a.e(0xC6,ids['0']);a.store(0x9849)
 a.load(0xC000);a.e(0xE6,3,0x87,0x5F,0x16,0);a.addr(0x21,'goals');a.e(0x19,0x2A);a.store(0xFE04);a.e(0x7E);a.store(0xFE05)
 a.addr(0xCD,'beep')
 a.label('nogoal');a.reg(0,0x10);a.e(0xF0,0,0xF0,0,0xE6,3,0xFE,3);a.addr(0xCA,'silent');a.addr(0xCD,'beep')
 a.label('silent');a.reg(0,0x30)
 a.label('end');a.e(0xF0,0x44,0xFE,144);a.addr(0xD2,'end');a.addr(0xC3,'frame')
 a.label('beep');a.reg(0x11,0x80);a.reg(0x12,0xA1);a.reg(0x13,0x80);a.reg(0x14,0x87);a.e(0xC9)
 a.label('goals');a.e(120,136,48,24,120,24,48,136)
 a.label('tiles');a.code.extend(tiles);a.label('bg');a.code.extend(bg)
 rom=bytearray(32768);rom[0x100:0x104]=bytes([0,0xC3,0x50,1]);name=title.encode()[:15];rom[0x134:0x134+len(name)]=name
 rom[0x150:0x150+len(a.code)]=a.finish()
 if battery:rom[0x147]=3;rom[0x149]=2
 check=0
 for x in rom[0x134:0x14D]:check=(check-x-1)&255
 rom[0x14D]=check;rom[0x14E:0x150]=(sum(rom)&65535).to_bytes(2,'big')
 return rom

if __name__=='__main__':
 out=Path(__file__).resolve().parents[1]/'app/src/main/assets/starter';out.mkdir(parents=True,exist_ok=True)
 items=[]
 for file,title,romtitle,speed,desc in [
 ('orbit-collector.gb','Orbit Collector','ORBIT COLLECTOR',1,'An original pocket arcade game. Move the round explorer onto each diamond checkpoint to score. D-pad moves; Select or A makes a tone. Pause with Menu.'),
 ('pocket-courier.gb','Pocket Courier','POCKET COURIER',2,'A faster original checkpoint course. Deliver your marker to the diamond and keep collecting points. D-pad moves; Select or A makes a tone. Pause with Menu.')]:
  (out/file).write_bytes(game(romtitle,speed));items.append(dict(file=file,title=title,description=desc))
 (out/'games.json').write_text(json.dumps(items,indent=2)+'\n')
 (out/'LICENSE.txt').write_text('FireSpot starter games and their generator are original work dedicated to the public domain under CC0-1.0. No commercial ROM or proprietary BIOS is included. https://creativecommons.org/publicdomain/zero/1.0/\n')
 print('Generated two original Game Boy games')
