"""Moonwake: original pixel scenery, sprite animation and verified CGB tile bytes.

Sprite, font and foreground assets are authored at native resolution. The
original generated scenery paintings are production inputs, reduced and palette
fitted once. Final previews decode exact ROM-ready pixels, with no display
smoothing or dithering.
The generated key visual is a mood/composition reference, never an unqualified
hardware screenshot. Each 8x8 background tile selects a real 4-color RGB555
palette. Patterns share reflections; scenery never touches reserved tile slots.
"""
from pathlib import Path
import hashlib, json, math, random, re
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/native'; SOURCE=ROOT/'assets/source'
OUT.mkdir(parents=True,exist_ok=True); SOURCE.mkdir(parents=True,exist_ok=True)
PALETTES=[
 [['49375d','a36785','e3a692','ffd5a6'],['a36785','e3a692','ffe6bb','fff2d6'],['31364f','496773','86aa91','d0dba7'],['31364f','77506e','b67b7c','f6b998'],['252d51','3b466b','64768f','a5b4b2'],['49375d','b97780','e7b491','ffeac6']],
 [['163c54','35787c','73b4ac','bfe1c6'],['35787c','73b4ac','bfe1c6','edf0cd'],['173e50','286d69','58a588','a9d7a2'],['24354f','557b77','abbd96','eee1b1'],['162d4d','29556b','4b8f98','8ed5ca'],['3c495e','908293','d2b8b4','fce1c4']],
 [['34264e','685777','a48b9f','e0b4b0'],['685777','a48b9f','e0b4b0','f5dbbf'],['242d4b','494b65','8d8392','c9c0ba'],['30294a','796276','c39175','f7ce91'],['222848','3f456c','747294','b3a5bd'],['34264e','797b97','bacad0','e3eee2']],
 [['182847','294e6b','4f8494','8db5b8'],['294e6b','4f8494','b2d7d4','edf3d4'],['17243f','305574','5998a7','bddcda'],['1c2b47','426375','839995','e1d6b5'],['111f3b','263a60','42628c','7ca2b4'],['294e6b','669ca9','b2d7d4','f6f1d5']],
 [['281c3b','67314e','ad3d39','e78444'],['963432','d45a31','eda150','ffe5a1'],['221d38','353453','675170','ae7990'],['3b233d','8d3c4c','cf7152','f5bd78'],['161d36','2d2946','514261','927282'],['67314e','b65c42','efab5a','ffedba']],
 [['142850','254d82','5d96bf','b0d6e7'],['637dac','a6b2d2','e2d9bd','fff2cf'],['1a3158','446998','9db7d0','eceada'],['32416b','867a97','c8b996','fff0ba'],['111e3d','20375b','385981','7896b3'],['1d3b68','587d99','b6d7d7','f4f1d5']],
 [['242751','504b85','8a96b0','c5dcca'],['375b65','5fa19c','9bcead','e7ead0'],['172c41','315c63','669c8e','c3d6a6'],['52456e','956d9d','d599ae','ffe5cd'],['111f35','253c4e','3b6971','74a5a5'],['294f59','779878','c5c0ad','ffe8d0']],
 [['604759','a57383','d9a894','ffdbab'],['ac7e88','d4af99','efd4ac','fff0ca'],['3c354e','6d5d70','a89192','d7c6b2'],['493746','97776c','d4b08c','ffe1a2'],['24263f','45415d','73627a','ad8c9a'],['48565c','82978c','bfc6a4','ffedc1']],
]
TERRAIN=[['292d49','825666','c1947c','f6dfa9'],['153f46','34766e','86b996','f0edc7'],['27253f','886965','c39978','ffe5a5'],['142d48','3d7385','8bb3bf','f2f1d1'],['291e3b','944638','d48a50','ffe1a1'],['1d3257','7583a9','c2c4ce','fff0c9'],['183a45','466a69','8ab499','fff0cd'],['372b49','937565','d0b895','fff1c8']]
UI=['172443','fff0cf','db866d','6a8895']
SPRITE=[['000000','25213f','fff0cc','ed735c'],['000000','25213f','d19a73','ffe2a0'],['000000','282345','b59bbe','fff0cc'],['000000','173b4c','66c8aa','e9f6cc'],['000000','44314b','e1aa6b','fff0c7'],['000000','172a45','8acecd','f8f3d6'],['000000','702f53','ef795f','ffc99b'],['000000','18243f','6fb5c5','e2f2d6']]

def rgb(s):return tuple(int(s[i:i+2],16) for i in (0,2,4))
def pal555(rows):
 p=np.round(np.array([[rgb(c) for c in row] for row in rows],dtype=float)*31/255).astype(np.uint16)
 return (p[:,:,0]|p[:,:,1]<<5|p[:,:,2]<<10).flatten(),(p*255//31).astype(np.uint8)
def pack(a):
 out=[]
 for row in a:
  out.extend([sum((int(v)&1)<<(7-x) for x,v in enumerate(row)),sum(((int(v)>>1)&1)<<(7-x) for x,v in enumerate(row))])
 return bytes(out)
def unpack(raw):
 return np.array([[(raw[2*y]>>(7-x)&1)|((raw[2*y+1]>>(7-x)&1)<<1) for x in range(8)] for y in range(8)],dtype=np.uint8)
def arr(name,v,typ='uint8_t'):
 v=list(np.array(v).flatten());return 'const '+typ+' '+name+'['+str(len(v))+'] = {\n'+'\n'.join('    '+','.join(str(int(x)) for x in v[i:i+24])+',' for i in range(0,len(v),24))+'\n};\n'

class C:
 def __init__(self,b,w=256):
  self.b=b; self.w=w; self.p=[[rgb(c) for c in row] for row in PALETTES[b]]
  self.im=Image.new('RGB',(w,144),self.p[0][2]);self.d=ImageDraw.Draw(self.im);self.r=random.Random(1937+b)
 def col(self,p,i):return self.p[p][i]
 def rect(self,r,p,i):self.d.rectangle(r,fill=self.col(p,i))
 def poly(self,r,p,i):self.d.polygon(r,fill=self.col(p,i))
 def line(self,r,p,i,width=1):self.d.line(r,fill=self.col(p,i),width=width)
 def oval(self,r,p,i):self.d.ellipse(r,fill=self.col(p,i))
 def dot(self,x,y,p,i):self.d.point((x,y),fill=self.col(p,i))
 def moon(self,x,y,r,p=1):
  self.oval((x-r,y-r,x+r,y+r),p,2)
  self.oval((x-r+3,y-r+1,x+r-3,y+r-4),p,3)
  # Large stepped lunar maria, few highlights, deliberately clustered.
  for xx,yy,rx,ry in [(-8,1,4,2),(5,-8,3,2),(9,5,2,1),(-3,10,3,1)]:
   if r>15:self.oval((x+xx-rx,y+yy-ry,x+xx+rx,y+yy+ry),p,2)
 def cloud(self,x,y,w,p=1,i=1):
  self.poly([(x,y+7),(x+3,y+3),(x+w//5,y+3),(x+w//4,y),(x+w//2,y),(x+w//2+3,y+2),(x+w-9,y+2),(x+w-5,y+5),(x+w,y+5),(x+w,y+9),(x,y+9)],p,i)
  self.line([(x+5,y+7),(x+w-4,y+7)],p,max(0,i-1))
 def stars(self,n=26,p=5):
  for j in range(n):
   x=self.r.randrange(8,self.w-8);y=self.r.randrange(9,75)
   self.dot(x,y,p,2 if j%4 else 3)
   if j%9==0:self.line([(x-2,y),(x+2,y)],p,3);self.line([(x,y-2),(x,y+2)],p,3)
 def mountain(self,y,p,i,seed):
  r=random.Random(seed);pts=[(0,y)]
  for x in range(8,self.w-7,8):pts.append((x,y-r.randrange(3,14)))
  self.poly(pts+[(self.w,y),(self.w,144),(0,144)],p,i)
 def sea(self,y,p=4):
  self.rect((0,y,self.w-1,143),p,0)
  for yy in range(y+3,144,8):
   for xx in range(0,self.w,32):
    self.line([(xx+(yy//8%2)*8,yy),(xx+13+(yy//8%2)*8,yy)],p,1)
    self.line([(xx+19,yy+4),(xx+25,yy+4)],p,2 if yy<110 else 1)
 def pagoda(self,x,y,w=26,h=43,p=3):
  self.rect((x+4,y-h+11,x+w-5,y),p,0)
  self.rect((x+7,y-h+14,x+w-8,y-3),p,1)
  for yy in range(y-h+16,y-5,13):
   for xx in range(x+9,x+w-8,6):
    self.rect((xx,yy,xx+2,yy+6),p,3)
    self.dot(xx,yy+6,p,2)
  # Upturned corners, joined eave rhythm. Broad roof forms at small scale.
  for yy,ww in [(y-h+10,w),(y-h+27,w+4),(y-3,w+8)]:
   cx=x+w//2;l=cx-ww//2;r=cx+ww//2
   self.poly([(l-2,yy-3),(l+3,yy),(cx-4,yy-6),(cx+4,yy-6),(r-3,yy),(r+2,yy-3),(r,yy+3),(l,yy+3)],p,0)
   self.line([(l,yy+1),(r,yy+1)],p,2)
   self.line([(cx-5,yy-5),(cx+5,yy-5)],p,2)
  self.line([(x+w//2,y-h+4),(x+w//2,y-h)],p,0)
 def island(self,x,y,w,h,p=2):
  self.poly([(x,y),(x+w,y),(x+w-5,y+5),(x+w-8,y+h-2),(x+w//2+3,y+h),(x+6,y+h-5),(x+3,y+5)],p,0)
  self.line([(x,y),(x+w,y)],p,2,2)
  self.poly([(x+5,y+4),(x+w-5,y+4),(x+w-10,y+h-6),(x+w//2+3,y+h-3),(x+w//2,y+10)],p,1)
  self.line([(x+w-7,y+6),(x+w-11,y+h-7)],p,2)
 def bird(self,x,y,p=1):self.line([(x-3,y-1),(x,y+1),(x+3,y-1)],p,3)
 def lantern(self,x,y,p=2):
  self.line([(x,y-5),(x,y)],p,0);self.rect((x-3,y,x+3,y+7),p,0);self.rect((x-2,y+1,x+2,y+5),p,3);self.line([(x,y+7),(x,y+10)],p,2)
 def seam(self):
  # Matching mirrored8pxboundary cells share both palette and tile pattern.
  # The finaldecodedfirstandlastcolumns match exactly, not merely the source.
  a=np.array(self.im);a[:,-8:]=a[:,:8][:,::-1]
  self.im=Image.fromarray(a);self.d=ImageDraw.Draw(self.im)

def harbor():
 c=C(0);c.rect((0,0,255,38),0,1);c.rect((0,39,255,73),0,2);c.rect((0,74,255,93),0,3)
 c.moon(150,43,24)
 for x,y,w in [(6,29,60),(76,16,44),(179,35,63),(13,69,53),(207,67,43)]:c.cloud(x,y,w,1,1)
 c.mountain(92,3,1,9);c.sea(99)
 # Two architecturally different silhouettes and a hanging causeway.
 c.island(23,105,59,35);c.pagoda(37,104,30,56)
 c.island(184,109,50,30);c.pagoda(195,108,26,42)
 c.line([(79,105),(97,102),(115,104)],3,0,2);c.line([(80,101),(98,98),(115,100)],3,2)
 for xx in range(80,116,8):c.line([(xx,101),(xx,106)],3,0)
 c.lantern(76,67);c.lantern(230,80)
 # Reflect the moon in grouped ribbons, never noisy checkerboard dithering.
 for yy,ww in [(103,17),(111,27),(119,11),(127,23)]:
  c.line([(150-ww//2,yy),(150+ww//2,yy)],4,3);c.line([(150-ww//2+3,yy+1),(150+ww//2-3,yy+1)],4,2)
 for x,y in [(107,49),(90,59),(173,70),(238,53)]:c.bird(x,y)
 c.seam();return c

def lotus():
 c=C(1);c.rect((0,0,255,24),0,0);c.rect((0,25,255,60),0,1);c.rect((0,61,255,104),0,2)
 for x,y,w in [(8,15,66),(99,8,62),(185,22,59)]:c.cloud(x,y,w,1,1)
 c.moon(193,50,18,1);c.mountain(101,2,1,52);c.sea(110)
 # A sleeping giant lotus, seven long pointed overlapping pearl-jade petals.
 petals=[[(126,108),(84,88),(75,58),(90,62),(115,82)],[(128,106),(99,72),(103,38),(116,55),(132,87)],[(130,105),(121,71),(134,27),(146,62),(140,93)],[(136,108),(149,73),(171,42),(174,63),(157,98)],[(136,111),(167,88),(196,72),(191,94),(168,109)]]
 for j,pts in enumerate(petals):
  c.poly(pts,2,0);c.poly([(x+1,y+1) for x,y in pts],2,2);c.line(pts[:3],2,3)
  c.line([(132,108),pts[2]],2,1)
 c.oval((103,105,176,119),2,1);c.line([(105,109),(131,107),(173,109)],2,3)
 c.poly([(135,110),(144,115),(157,115),(162,112),(161,119),(137,118)],2,0)
 # Water terraces and sparse bamboo are distant, visibly below platforms.
 c.island(15,121,43,20);c.pagoda(26,120,23,29)
 c.island(209,124,30,17);c.lantern(225,95,2)
 for xx,hh in [(17,39),(23,51),(233,50),(241,34)]:
  c.line([(xx,101),(xx,101-hh)],2,0,2)
  for yy in range(101-hh+8,100,12):
   c.line([(xx-1,yy),(xx+2,yy)],2,2)
   c.poly([(xx,yy-2),(xx-7,yy-8),(xx-6,yy-3)],2,1)
   c.poly([(xx,yy+2),(xx+8,yy-2),(xx+5,yy+4)],2,2)
 for xx,yy in [(54,38),(71,56),(187,30),(209,61),(85,15),(180,88)]:
  c.line([(xx,yy),(xx-3,yy+7)],1,2)
 c.seam();return c

def gear(c,x,y,r,p=3):
 pts=[]
 for j in range(64):
  a=j*math.pi/32;rr=r if j%4 in(1,2) else r-4;pts.append((int(x+math.cos(a)*rr),int(y+math.sin(a)*rr)))
 c.poly(pts,p,0);c.oval((x-r+6,y-r+6,x+r-6,y+r-6),p,2);c.oval((x-r+10,y-r+10,x+r-10,y+r-10),p,0)
 for j in range(8):
  a=j*math.pi/4;c.line([(x,y),(int(x+math.cos(a)*(r-9)),int(y+math.sin(a)*(r-9)))],p,1,3)
 c.oval((x-5,y-5,x+5,y+5),p,3);c.oval((x-2,y-2,x+2,y+2),p,0)

def engines():
 c=C(2);c.rect((0,0,255,26),0,0);c.rect((0,27,255,64),0,1);c.rect((0,65,255,107),0,2)
 c.stars(21);c.cloud(8,53,45,1,1);c.cloud(190,35,50,1,1)
 c.mountain(113,2,1,88);c.sea(120)
 # A monumental celestial clock. The dial is clean, lower-detail negative space.
 x,y,r=144,69,44
 c.oval((x-r-3,y-r-3,x+r+3,y+r+3),3,0);c.oval((x-r,y-r,x+r,y+r),3,2);c.oval((x-r+3,y-r+3,x+r-3,y+r-3),3,3);c.oval((x-r+5,y-r+5,x+r-5,y+r-5),3,0);c.oval((x-r+8,y-r+8,x+r-8,y+r-8),3,1)
 for j in range(12):
  a=j*math.pi/6;c.line([(int(x+math.sin(a)*32),int(y-math.cos(a)*32)),(int(x+math.sin(a)*36),int(y-math.cos(a)*36))],3,3,2 if j%3==0 else 1)
 c.line([(144,69),(130,50)],3,3,3);c.line([(144,69),(167,57)],3,3,2);c.oval((140,65,148,73),3,0);c.oval((142,67,146,71),3,3)
 # Orbit route is a fine architectural hairline with pearl nodes.
 c.line([(77,40),(92,21),(135,13),(182,26),(206,61),(206,94)],5,2)
 for xx,yy in [(92,21),(182,26),(206,61)]:c.oval((xx-3,yy-3,xx+3,yy+3),5,3);c.dot(xx,yy,5,1)
 gear(c,57,107,27);gear(c,215,111,22);gear(c,91,121,15)
 # Suspended cable fixtures add purpose and depth to the machine.
 for xx,yy in [(41,59),(224,47)]:
  c.line([(xx,0),(xx,yy)],2,0);c.lantern(xx,yy,3)
 c.seam();return c

def whale(c,x=18,y=54,scale=1.0):
 def pts(seq):return [(int(x+a*scale),int(y+b*scale)) for a,b in seq]
 # Original elegant sky whale: sweeping manta-like flukes and a smiling eye.
 body=[(0,14),(12,23),(36,29),(70,11),(102,3),(137,0),(174,7),(202,20),(205,28),(190,42),(155,51),(114,53),(84,49),(55,37),(29,34),(20,36),(10,30)]
 c.poly(pts(body),2,0)
 upper=[(25,26),(70,11),(102,3),(137,0),(174,7),(202,20),(200,24),(173,20),(141,16),(110,19),(80,28),(50,32)]
 c.poly(pts(upper),2,2)
 c.line(pts([(61,20),(103,5),(137,2),(173,9),(199,21)]),2,3)
 belly=[(65,36),(94,39),(128,38),(161,31),(189,29),(199,25),(191,38),(155,48),(115,50),(86,46)]
 c.poly(pts(belly),2,1)
 # Baleen grooves curve with the belly, keeping large color clusters intact.
 for j in range(5):c.line(pts([(118+j*13,38-j),(120+j*12,47-j)]),2,2)
 c.poly(pts([(20,30),(8,11),(4,-7),(22,4),(32,18),(36,29)]),2,1)
 c.line(pts([(6,-5),(16,8),(26,19)]),2,2)
 c.poly(pts([(30,29),(5,45),(-3,48),(7,32),(21,27)]),2,2)
 c.poly(pts([(98,34),(81,58),(63,67),(71,47),(83,33)]),2,0);c.line(pts([(83,36),(72,51),(65,63)]),2,2)
 ex,ey=pts([(181,25)])[0];c.dot(ex,ey,2,0);c.dot(ex+1,ey-1,2,3)
 c.line(pts([(185,34),(191,32)]),2,3)
 # Water spout is a little star-shaped dream, never a photographic texture.
 sx,sy=pts([(158,3)])[0];c.line([(sx,sy),(sx-3,sy-6),(sx-5,sy-10)],1,2);c.line([(sx-3,sy-6),(sx+2,sy-11)],1,3)

def moonwhale():
 c=C(3);c.rect((0,0,255,53),0,0);c.rect((0,54,255,93),0,1);c.rect((0,94,255,143),4,0)
 c.stars(48);c.moon(154,42,28);c.cloud(12,82,54,0,1);c.cloud(183,93,56,0,1)
 whale(c,21,58)
 c.sea(131)
 # Stair-step comet sweeps echo the hero's scarf shape, subtly.
 c.line([(15,34),(31,23),(52,17),(79,17)],5,1);c.line([(15,36),(32,26),(52,19)],5,2)
 for xx,yy in [(33,113),(66,127),(234,109)]:c.lantern(xx,yy,5)
 c.seam();return c

# Original narrow caps, marble top edges, riveted cloudstone understructure.
TERRAIN_ROWS=[
 ['00000333','00003222','00032111','00321111','03211111','32111111','21111111','21111111'],
 ['33333333','22222222','11111111','21111112','12111121','11122111','11111111','11111111'],
 ['33300000','22230000','11123000','11112300','11111230','11111123','11111112','11111112'],
 ['11111111','11211111','11121110','11111100','21111000','00111112','00011121','10001111'],
 ['11111111','11111111','11111111','21111112','22211222','02222220','00022000','00000000'],
 ['00000000','00333300','03222230','32222223','11111111','00000000','00000000','00000000'],
 ['33333333','22222222','11111111','01333310','00311300','01300310','00311300','01300310'],
 ['33333333','22212222','11101111','11001101','11110011','11111111','11011111','11101111'],
 ['33000333','21000122','01000111','00000101','00011011','00001111','00011111','00000111'],
 ['00333000','03222300','03232300','00323000','00023000','00023000','00023000','00023000'],
 ['00333000','03222300','32232223','11222111','00111000','00111000','01111100','11111110'],
 ['00000000','00000000','02222200','22222222','11111111','00111100','11111111','11111111'],
 ['00030000','00333000','03323300','00333000','00030000','00000000','00000000','00000000'],
 ['00000003','00000032','00000321','00003211','03332111','32222111','11111111','11111111'],
 ['00033000','00322300','03211230','32111123','22222222','11111111','11111111','11111111'],
 ['30000000','23000000','12300000','11230000','11123330','11122223','11111111','11111111']]
HERO=[
# Eyes and ears always retain a one-pixel silhouette and the red scarf.
['0000000100100000','0000001211210000','0000001211210000','0000001211210000','0000001222210000','0000012222221000','0000122222122100','0000122222222130','0033312222222100','0333331333331000','0033312222210000','0000122222210000','0000122222221000','0000012222210000','0000012212210000','0000111101111000'],
['0000000010010000','0000000121121000','0000000121121000','0000000121121000','0000000122221000','0000001222222100','0000012222212210','0000012222222213','0033331222222100','0333333133333100','0033331222221000','0000012222210000','0000122222221000','0000122222222100','0001221100122210','0001111000011110'],
['0000000100100000','0000001211210000','0000001211210000','0000001211210000','0000001222210000','0000012222221000','0000122222122100','0000122222222130','0033312222222100','0333331333331000','0033312222210000','0000122222210000','0000122222221000','0000012222222100','0000001221001210','0000001111001110'],
['0000001000100000','0000012101210000','0000012211210000','0000001222210000','0000012222221000','0000122222122100','0000122222222130','0033312222222100','0333331333331000','0033312222221100','0000122222222210','0000122222221210','0000012222211100','0000012222210000','0000012111210000','0000011101110000'],
['0000000000000000','0000011111000000','0000122222111100','0000122222222210','0000012222222210','0000122222212210','3333122222222213','3333312222222100','0333331333331000','0033312222221100','0000122222222210','0001222222221210','0001222212211100','0000111111110000','0000000000000000','0000000000000000'],
['0000000100100000','0000001211210000','0000001222210000','0000012222221000','0000122221222100','0000122212122100','0000122222222130','0000112222221100','0033331333310000','0333312222221000','0033122222222100','0000122222222210','0000012222222100','0000001222211000','0000001211210000','0000011101110000']]

# Hand-designed small silhouettes; no scaled illustrations in native sprite VRAM.
BEETLE=['0000000000000000','0000000330000000','0000013333100000','0000132222310000','0001322222231000','0013222232223100','0013222332223100','0132222332222310','1322222332222231','1322222332222231','1322222332222231','0111111111111110','0011211111121000','0011000000011000','0111000000011100','0000000000000000']
OWL=[['00000000','01000010','01211210','01222210','01211210','01233210','12222221','12122121','01222210','00122100','00122100','00011000','00033000','00300300','00000000','00000000'],['00000000','00000000','01000010','01211210','01222210','11211211','22233222','12222221','01222210','00122100','00122100','00011000','00033000','00300300','00000000','00000000']]
LANTERN=['00010000','00131000','01111100','01232100','12333210','12323210','12333210','12323210','12333210','01232100','01111100','00031000','00031000','00121000','00010000','00000000']
SEAL=['00000000','00033000','00122300','01332230','13223223','13233223','13222223','13233223','13223223','01332230','00122300','00033000','00000000','00000000','00000000','00000000']
CHECKPOINT=['00110000','01221000','12332100','01221000','00110000','00110000','00133330','00132310','00133100','00110000','00110000','00110000','00110000','01111000','12222100','11111100']
GOAL=['0000013333100000','0000132222310000','0001323332231000','0013231113323100','0132310001322310','1323100000132231','1322100000132231','1322100000132231','1322100000132231','1322100000132231','1322100000132231','1322100000132231','1322100000132231','1322100000132231','1323333333332231','0111111111111110']
TRAIL=['00000000','00000000','00000003','00000033','00000323','00003223','00032223','00322223','03222223','00322223','00032223','00003223','00000323','00000033','00000003','00000000']
SPARK=['00000000','00000000','00030000','00030000','03033030','00322300','03322330','00322300','03033030','00030000','00030000','00000000','00000000','00000000','00000000','00000000']
HEART=['00000000','01101100','13313310','13232310','13222310','01323100','00131000','00010000']+['00000000']*8
SPRING=['00000000']*3+['13333331','12222221','11111111','00133100','00311300','00133100','00311300','00133100','00311300','00133100','01111110','12222221','11111111']
PROJECTILE=['00000000','00000000','00033000','00122300','01233230','12333323','12333323','01233230','00122300','00033000','00000000','00000000','00000000','00000000','00000000','00000000']
MOVER=['33333333','32222223','11111111','12111121','11211211','11122111','01111110','00111100']+['00000000']*8
JELLY=[
 ['00000000','00111100','01233210','12333321','12322321','12333321','12222221','01111110','00122100','01211210','01211210','00100100','00100100','00011000','00000000','00000000'],
 ['00000000','00000000','00111100','01233210','12333321','12322321','12333321','12222221','01111110','01211210','12100121','01000010','01000010','00000000','00000000','00000000']]

def expansion_boss_images():
 """Original native silhouettes. Index3 is supplied by unchanged v1 whale art."""
 images=[]
 # Rainbell Warden: a suspended shrine-bell with a tiered rain crown and
 # scalloped ivy cloak. Its clapper and curled arms read apart from the body.
 im=Image.new('L',(32,32));d=ImageDraw.Draw(im)
 d.polygon([(16,0),(19,4),(24,4),(26,8),(30,10),(28,13),(25,12),(24,18),(28,24),(25,27),(19,27),(18,30),(14,30),(13,27),(6,27),(3,24),(7,18),(7,12),(3,13),(1,10),(6,8),(8,4),(13,4)],fill=1)
 d.polygon([(16,2),(18,6),(22,6),(24,9),(8,9),(10,6),(14,6)],fill=2)
 d.line([(6,10),(25,10)],fill=3)
 d.polygon([(10,12),(21,12),(22,18),(25,23),(23,25),(8,25),(6,23),(9,18)],fill=2)
 d.line([(9,13),(10,18),(7,23),(24,23)],fill=3)
 d.line([(12,15),(12,18)],fill=1);d.line([(19,15),(19,18)],fill=1)
 d.point((11,14),fill=3);d.point((18,14),fill=3)
 d.polygon([(13,21),(18,21),(17,24),(14,24)],fill=1)
 d.line([(16,27),(16,28)],fill=3)
 for x in (3,28):
  d.polygon([(x,15),(x+2,18),(x+1,21),(x-1,19)],fill=3)
 images.append(np.array(im))
 # Comet Manta: pointed swept wings, pearl forehead, forked trailing tail.
 im=Image.new('L',(32,32));d=ImageDraw.Draw(im)
 d.polygon([(0,3),(7,7),(12,11),(14,7),(16,5),(18,7),(20,11),(26,7),(31,3),(30,13),(26,19),(21,21),(18,19),(17,25),(21,31),(16,28),(12,31),(15,24),(13,19),(9,21),(4,18),(1,12)],fill=1)
 d.polygon([(2,6),(8,10),(12,14),(15,8),(17,8),(20,14),(27,9),(29,6),(28,13),(24,17),(21,18),(18,16),(16,20),(13,16),(9,18),(5,15)],fill=2)
 d.line([(3,7),(8,11),(12,16)],fill=3);d.line([(28,7),(24,11),(20,16)],fill=3)
 d.polygon([(16,9),(19,13),(16,17),(13,13)],fill=3)
 d.point((16,13),fill=2);d.point((13,17),fill=1);d.point((19,17),fill=1)
 d.line([(16,22),(16,26),(19,29)],fill=2)
 images.append(np.array(im))
 # Prism Sentinel: tall faceted core with detached orbit brackets and jewel
 # antennae. Angular silhouette opposes the Warden and Manta curves.
 im=Image.new('L',(32,32));d=ImageDraw.Draw(im)
 d.polygon([(16,1),(25,9),(23,22),(16,30),(8,22),(6,9)],fill=1)
 d.polygon([(16,3),(22,10),(20,21),(16,26),(11,21),(9,10)],fill=2)
 d.polygon([(16,5),(20,11),(16,17),(12,11)],fill=3)
 d.polygon([(16,17),(19,21),(16,25),(13,21)],fill=1)
 d.line([(16,6),(16,14)],fill=2)
 d.line([(10,10),(13,16),(11,20)],fill=3)
 d.line([(22,10),(19,16),(21,20)],fill=1)
 for pts in [[(3,5),(5,7),(4,12),(2,13),(2,20),(5,24),(4,27),(0,22),(0,12)],[(28,5),(26,7),(27,12),(29,13),(29,20),(26,24),(27,27),(31,22),(31,12)]]:
  d.polygon(pts,fill=1);d.line(pts[1:4],fill=3)
 d.polygon([(3,0),(5,2),(3,4),(1,2)],fill=3);d.polygon([(28,0),(30,2),(28,4),(26,2)],fill=3)
 images.append(np.array(im))
 return images

def pack_sprite(a):
 return b''.join(pack(a[y:y+8,x:x+8]) for x in range(0,a.shape[1],8) for y in range(0,a.shape[0],8))

def sprites():
 patterns=np.zeros((96,8,8),dtype=np.uint8);gallery=[]
 def add(rows,start,p,name):
  a=np.array([[int(c) for c in row] for row in rows],dtype=np.uint8);n=start
  for x in range(0,a.shape[1],8):
   for y in range(0,a.shape[0],8):patterns[n]=a[y:y+8,x:x+8];n+=1
  gallery.append((a,p,name));return n
 for n,h in enumerate(HERO):assert add(h,n*4,0,'KIP '+str(n))==n*4+4
 add(BEETLE,24,1,'BRASS BEETLE');add(OWL[0],28,2,'OWLET');add(OWL[1],30,2,'OWLET FLAP')
 for data,n,p,name in [(LANTERN,32,3,'LANTERN'),(SEAL,34,4,'MOON SEAL'),(CHECKPOINT,36,5,'BEACON'),(GOAL,38,5,'SKY GATE'),(TRAIL,42,6,'SCARF WAKE'),(SPARK,44,4,'SPARK'),(HEART,46,0,'HEART'),(SPRING,48,4,'SPRING'),(PROJECTILE,80,7,'MOONFIRE')]:add(data,n,p,name)
 thorn=['00000000','00010000','00131000','00132100','01032110','13132321','01322310','00122310','00012310','00122310','01322310','13132321','01111110','12333321','12322321','01111110']
 add(thorn,50,1,'COMET THORN')
 add(MOVER,52,5,'MOVING CLOUDSTONE')
 add(JELLY[0],54,2,'PEARL JELLY');add(JELLY[1],56,2,'PEARL JELLY PULSE')
 # Boss is a side-profile sleeping engine-whale, matching the sky sea fantasy.
 # A pearlribbedbelly, curvedfin and twin sweepingflukes fit32x32native pixels.
 im=Image.new('L',(32,32));d=ImageDraw.Draw(im)
 d.polygon([(2,2),(5,4),(8,10),(13,9),(19,6),(25,7),(30,10),(31,14),(31,18),(28,22),(23,25),(17,27),(12,25),(8,22),(6,16),(2,14),(0,17),(0,12),(3,10),(1,6)],fill=1)
 d.polygon([(3,3),(5,5),(7,12),(12,11),(19,8),(25,9),(29,11),(30,15),(29,18),(26,22),(22,24),(17,25),(12,23),(9,20),(7,15),(4,13),(2,14),(3,12),(5,11)],fill=2)
 d.line([(9,12),(17,9),(23,9),(28,11)],fill=3)
 d.polygon([(11,20),(16,21),(23,19),(30,16),(28,21),(24,24),(18,26),(13,24)],fill=3)
 for x in(15,18,21,24):d.line([(x,21),(x+1,24 if x<21 else 22)],fill=2)
 d.polygon([(15,18),(18,19),(16,25),(11,31),(10,31),(12,25)],fill=1)
 d.line([(16,20),(14,26),(11,29)],fill=2)
 d.point((27,13),fill=1);d.point((28,12),fill=3)
 d.line([(27,18),(29,17)],fill=1)
 # A luminous "dream knot" jewel marks it as a magical clockwork creature.
 d.polygon([(20,10),(23,13),(20,16),(17,13)],fill=1);d.polygon([(20,11),(22,13),(20,15),(18,13)],fill=3);d.point((20,13),fill=2)
 boss=np.array(im);add([''.join(str(i) for i in row) for row in boss],64,7,'DREAM-KNOT WHALE')
 boss_images=expansion_boss_images()+[boss]
 for a,name in zip(boss_images[:3],['RAINBELL WARDEN','COMET MANTA','PRISM SENTINEL']):gallery.append((a,7,name))
 vals,display=pal555(SPRITE)
 sheet=Image.new('RGBA',(240,math.ceil(len(gallery)/6)*40),(0,0,0,0))
 for n,(a,p,name) in enumerate(gallery):
  rgba=np.concatenate([display[p][a],np.where(a[:,:,None]>0,255,0).astype(np.uint8)],axis=2)
  sheet.paste(Image.fromarray(rgba),(n%6*40,n//6*40))
 sheet.save(OUT/'sprites.png');sheet.resize((sheet.width*6,sheet.height*6),Image.Resampling.NEAREST).save(OUT/'sprites-6x.png')
 # These sheets decode the actual packed 2bpp boss blocks, not the drawing
 # arrays, and preserve transparency at color0 for hardware matching.
 boss_raw=[pack_sprite(a) for a in boss_images];boss_sheet=Image.new('RGBA',(128,32),(0,0,0,0))
 for n,raw in enumerate(boss_raw):
  a=np.zeros((32,32),dtype=np.uint8)
  for x in range(4):
   for y in range(4):a[y*8:y*8+8,x*8:x*8+8]=unpack(raw[(x*4+y)*16:(x*4+y+1)*16])
  rgba=np.concatenate([display[7][a],np.where(a[:,:,None]>0,255,0).astype(np.uint8)],axis=2);boss_sheet.paste(Image.fromarray(rgba),(n*32,0))
 boss_sheet.save(OUT/'bosses.png');boss_sheet.resize((1024,256),Image.Resampling.NEAREST).save(OUT/'bosses-8x.png')
 return b''.join(pack(t) for t in patterns),vals,boss_raw

def font():
 # Compatible proven ASCII32..95 font retains the familiar readable tiny labels.
 data=bytearray((SOURCE/'font-base.bin').read_bytes())
 assert len(data)==1024,'The local ASCII font foundation must contain1024 bytes.'
 # HUD'scustomglyphs32..95: * moonseal/health, $ collectible star.
 glyphs={'*':[0,20,28,62,28,20,0,0], '$':[8,28,62,127,62,28,8,0], '+':[0,8,8,62,8,8,0,0], '-':[0,0,0,62,0,0,0,0], '>':[32,16,8,4,8,16,32,0], '?':[28,34,2,4,8,0,8,0], '=':[0,0,62,0,62,0,0,0], '<':[4,8,16,32,16,8,4,0], ',':[0,0,0,0,8,8,16,0]}
 for ch,rows in glyphs.items():
  at=(ord(ch)-32)*16
  for y,b in enumerate(rows):data[at+y*2]=b;data[at+y*2+1]=0
 for at in range(0,1024,16):data[at:at+16]=bytes([0,0])+data[at:at+14]
 return bytes(data)

def validate_font(data):
 # Actual UI/dialogue literals plus dynamic HUD symbols must have real pixels.
 # Lowercase filename includes are not displayed and are omitted.
 used=set('0123456789*$')
 for file in ('ui.c','levels.c','game.c','main.c'):
  path=ROOT/'src'/file
  if not path.exists():continue
  for literal in re.findall(r'"([^"\n]*)"',path.read_text()):
   if literal==literal.upper() and not any(c in literal for c in ('\\','%')):
    used.update(literal)
 missing=[]
 for ch in sorted(used):
  if ch==' ':continue
  if not 32<=ord(ch)<=95 or not any(data[(ord(ch)-32)*16:(ord(ch)-31)*16]):missing.append(ch)
 assert not missing,'Blank displayed glyphs: '+repr(missing)
 assert all(data[i]==data[i+1]==0 for i in range(0,1024,16))
 return ''.join(sorted(used))

def title():
 c=C(3,160);c.rect((0,0,159,143),0,0);c.stars(30);c.moon(93,56,22);whale(c,7,57,.69)
 c.sea(109)
 painted=SOURCE/'world_3-painted.png'
 if painted.exists():
  pic=Image.open(painted).convert('RGB').resize((160,90),Image.Resampling.BOX)
  c.im.paste(pic,(0,23));c.d=ImageDraw.Draw(c.im);c.painted=True;c.sea(110)
 # Original title lettering: generous counters, tailored diagonal notches.
 letters={
 'M':['1100011','1110111','1111111','1101011','1100011','1100011','1100011','1100011','1100011'],
 'O':['0111110','1100011','1100011','1100011','1100011','1100011','1100011','1100011','0111110'],
 'N':['1100011','1110011','1110011','1101011','1101011','1100111','1100111','1100011','1100011'],
 'W':['1100011','1100011','1100011','1100011','1101011','1101011','1111111','1110111','0100010'],
 'A':['0011100','0110110','1100011','1100011','1100011','1111111','1100011','1100011','1100011'],
 'K':['1100011','1100110','1101100','1111000','1111000','1101100','1100110','1100011','1100011'],
 'E':['1111111','1100000','1100000','1100000','1111100','1100000','1100000','1100000','1111111']}
 word='MOONWAKE';x0=8
 for n,ch in enumerate(word):
  for y,row in enumerate(letters[ch]):
   for x,bit in enumerate(row):
    if bit=='1':
     xx=x0+n*18+x*2;yy=13+y*2
     c.rect((xx+1,yy+1,xx+2,yy+2),0,1);c.rect((xx,yy,xx+1,yy+1),1,3)
 c.line([(13,36),(66,36)],5,2);c.line([(94,36),(147,36)],5,2)
 c.line([(80,33),(80,39)],5,3);c.line([(77,36),(83,36)],5,3)
 # The title's calm lower quarter is intentionally left to the menu.
 return c

def fitted_scenery(image, initial):
 # Fit palette groups to the actual painting while keeping four colors per tile.
 # This prevents blocky color bands caused by forcing every mist shade through
 # a generic global palette, and preserves handcrafted local color clusters.
 h,w=image.shape[:2]
 tiles=image.reshape(h//8,8,w//8,8,3).transpose(0,2,1,3,4).reshape(-1,64,3)
 ps=initial.astype(np.float32).copy()
 def centers(pts,start):
  cs=start.copy()
  for _ in range(10):
   labels=((pts[:,None]-cs[None])**2).sum(2).argmin(1)
   nxt=np.array([pts[labels==i].mean(0) if np.any(labels==i) else cs[i] for i in range(4)])
   if abs(nxt-cs).max()<.3:break
   cs=nxt
  return cs
 for _ in range(6):
  costs=np.array([((tiles[:,:,None,:]-p[None,None,:,:])**2).sum(3).min(2).mean(1) for p in ps])
  groups=costs.argmin(0)
  for p in range(6):
   pts=tiles[groups==p].reshape(-1,3)
   if len(pts):ps[p]=centers(pts,ps[p])
 q=np.round(ps*31/255).clip(0,31).astype(np.uint16)
 for p in range(6):q[p]=q[p][np.argsort(q[p]@np.array([.2126,.7152,.0722]))]
 values=(q[:,:,0]|q[:,:,1]<<5|q[:,:,2]<<10).flatten()
 return values,(q*255//31).astype(np.uint8)

def convert(c,name,bank):
 image=np.array(c.im,dtype=np.float32);h,w=image.shape[:2];rows=PALETTES[c.b]+[TERRAIN[c.b],UI]
 vals,display=pal555(rows)
 if getattr(c,'painted',False):
  fitted,pd=fitted_scenery(image,display[:6]);vals[:24]=fitted;display[:6]=pd
 ps=display[:6].astype(np.float32)
 patterns=[];lookup={};indices=[];pals=[];flips=[]
 for y in range(0,h,8):
  for x in range(0,w,8):
   tile=image[y:y+8,x:x+8]
   distances=((tile[None,:,:,None,:]-ps[:,None,None,:,:])**2).sum(4)
   p=int(distances.min(3).sum((1,2)).argmin());a=distances[p].argmin(2).astype(np.uint8)
   # Canonical reflections share silhouettes and cloud/wave textures.
   variants=[(pack(a),0),(pack(a[:,::-1]),32),(pack(a[::-1]),64),(pack(a[::-1,::-1]),96)]
   raw,f=min(variants,key=lambda k:k[0])
   if raw not in lookup:lookup[raw]=len(patterns);patterns.append(unpack(raw))
   indices.append(lookup[raw]);pals.append(p);flips.append(f)
 original=len(patterns);merges=[]
 # A reflection-symmetric boundary pattern can lose that symmetry when it is
 # merged into an asymmetric pattern. Preserve expansion edge patterns so the
 # horizontal wrap remains pixel-exact after the304-pattern reduction.
 protected={indices[j] for j in range(len(indices)) if j%(w//8) in(0,w//8-1) or j//(w//8)>=14} if c.b>=4 else set()
 # Low-error matching only needed if more than304patterns; never move colors
 # across palettes. Every native preview below decodes final ROM-ready bytes.
 while len(patterns)>304:
  a=np.array(patterns,dtype=np.int16).reshape(len(patterns),64)
  diff=(a*a).sum(1)[:,None]+(a*a).sum(1)[None,:]-2*a@a.T;np.fill_diagonal(diff,100000)
  for drop in protected:diff[:drop,drop]=100000;diff[drop,:drop]=100000
  keep,drop=sorted(np.unravel_index(diff.argmin(),diff.shape));cost=int(diff[keep,drop])
  merges.append(dict(drop=int(drop),keep=int(keep),cost=cost));patterns.pop(drop)
  indices=[keep if i==drop else i-1 if i>drop else i for i in indices]
  protected={i-1 if i>drop else i for i in protected}
 preview=np.zeros((h,w,3),dtype=np.uint8);maps=[];attrs=[]
 for j,(i,p,f) in enumerate(zip(indices,pals,flips)):
  maps.append(i+112 if i<144 else i-144+96);attrs.append(p|f|(8 if i>=144 else 0))
  a=patterns[i];a=a[:,::-1] if f&32 else a;a=a[::-1] if f&64 else a
  yy,xx=divmod(j,w//8);preview[yy*8:yy*8+8,xx*8:xx*8+8]=display[p][a]
 n0=min(144,len(patterns));n1=max(0,len(patterns)-144);raw=[list(pack(a)) for a in patterns]
 text=f'#pragma bank {bank}\n#include <stdint.h>\n'
 text+=arr(name+'_tiles0',raw[:n0])+arr(name+'_tiles1',raw[n0:] or [[0]*16])+arr(name+'_map',maps)+arr(name+'_attr',attrs)+arr(name+'_pal',vals,'uint16_t')
 path=ROOT/'src'/('title_art.c' if name=='title' else name+'.c');path.write_text(text)
 c.im.save(SOURCE/(name+'-pixels.png'));im=Image.fromarray(preview);im.save(OUT/(name+'.png'));im.resize((w*4,h*4),Image.Resampling.NEAREST).save(OUT/(name+'-4x.png'))
 return dict(name=name,bank=bank,n0=n0,n1=n1,unique_tiles=len(patterns),original_unique=original,merges=merges,palettes=8,size=[w,h],pattern_flips=True)

def terrain_variants():
 # The same collision indices across eight separate material vocabularies.
 # Bright continuous top edges stay readable over every scenery palette.
 variants=[[list(rows) for rows in TERRAIN_ROWS] for _ in range(8)]
 tops=[
 ['33333333','22222222','11211121','12111211','21112111','11121112','11211121','11111111'],
 ['33333333','22222222','11221122','22112211','11111111','12111121','11122111','11111111'],
 ['33333333','22222222','11111111','22211222','21111112','21111112','22211222','11111111'],
 ['33333333','22222222','11111111','11122111','11211211','12111121','11111111','11111111'],
 ['33333333','22222222','11111111','21121121','12212211','11111111','11211211','11111111'],
 ['33333333','22222222','11111111','11222211','12111121','21111112','11222211','11111111'],
 ['33333333','22222222','11111111','21112111','12111211','11211121','11121112','11111111'],
 ['33333333','22222222','11111111','22222222','11111111','22222222','11111111','11111111']]
 fill=[
 ['11111111','01111110','20111102','12011021','11200211','11111111','11121111','11111111'],
 ['21111211','12112111','11121121','01111100','00111110','01110111','12111121','11121111'],
 ['11111111','01222210','01211210','01211210','01222210','01111110','11011011','10000001'],
 ['11111111','11111211','11122111','11211111','12111111','11111111','00111100','00011000'],
 ['11111111','01222210','12111121','21122112','11111111','01111110','00122100','00011000'],
 ['11111111','21111112','12111121','11211211','11122111','01122110','00122100','00011000'],
 ['11111111','12111121','11211211','11122111','01122110','00122100','01211210','00100100'],
 ['11111111','22222222','11111111','22222222','11111111','02222220','00111100','00011000']]
 for b in range(8):variants[b][1]=tops[b];variants[b][3]=fill[b]
 return variants

def main():
 names=['SAFFRON HARBOR','JADE MONSOON','VIOLET ENGINES','MOONWHALE','EMBER FESTIVAL','PEARL OBSERVATORY','AURORA ORCHARD','DAWN ARCHIVE']
 meta=[]
 for b in range(8):
  c=[harbor,lotus,engines,moonwhale][b]() if b<4 else C(b)
  painted=SOURCE/('world_'+str(b)+'-painted.png')
  if b==0:painted=SOURCE/'saffron-harbor-painted.png'
  if b>=4:assert painted.exists(),'Missing original expansion painting: '+str(painted)
  if painted.exists():
   c.im=Image.open(painted).convert('RGB').resize((256,144),Image.Resampling.BOX);c.d=ImageDraw.Draw(c.im);c.painted=True
   # Quietwateruses intentional horizontalpixel ribbons and frees tilebudget
   # for the landmarks, instead of noisy downsampled surface texture.
   if b in(1,2,3):c.sea([0,111,105,113][b])
   if b>=4:c.sea([112,110,112,113][b-4])
   c.seam()
  meta.append(convert(c,'world_'+str(b),8+b))
 mt=convert(title(),'title',2)
 spr,spal,boss_raw=sprites();terrain=b''.join(pack([[int(c) for c in r] for r in rows]) for rows in TERRAIN_ROWS)
 variants=terrain_variants();terrain_world=b''.join(pack([[int(c) for c in row] for row in rows]) for vs in variants for rows in vs)
 terrain_sheet=Image.new('RGB',(128,64))
 for b in range(8):
  _,tp=pal555([TERRAIN[b]])
  for n,rows in enumerate(variants[b]):
   a=np.array([[int(c) for c in r] for r in rows],dtype=np.uint8);terrain_sheet.paste(Image.fromarray(tp[0][a]),(n*8,b*8))
 terrain_sheet.resize((768,384),Image.Resampling.NEAREST).save(OUT/'terrain-6x.png')
 text='#pragma bank 1\n#include "art.h"\n'
 for prefix in ['world_'+str(b) for b in range(8)]+['title']:
  for key in ['tiles0','tiles1','map','attr']:text+=f'extern const uint8_t {prefix}_{key}[];\n'
  text+=f'extern const uint16_t {prefix}_pal[];\n'
 text+=arr('font_tiles',list(font()))+arr('terrain_tiles',list(terrain))+arr('terrain_world_tiles',list(terrain_world))+arr('sprite_tiles',list(spr))+arr('sprite_palettes',spal,'uint16_t')
 text+='const unsigned char boss_tiles[4][256] = {\n'
 for raw in boss_raw:
  text+='  {\n'+'\n'.join('    '+','.join(str(x) for x in raw[i:i+24])+',' for i in range(0,256,24))+'\n  },\n'
 text+='};\n'
 text+='const ArtDef art_worlds[8] = {\n'
 for m in meta:
  p=m['name'];text+=f'    {{{m["bank"]},{m["n0"]},{m["n1"]},{p}_tiles0,{p}_tiles1,{p}_map,{p}_attr,{p}_pal}},\n'
 text+='};\n';p=mt['name'];text+=f'const ArtDef art_title = {{{mt["bank"]},{mt["n0"]},{mt["n1"]},{p}_tiles0,{p}_tiles1,{p}_map,{p}_attr,{p}_pal}};\n'
 (ROOT/'src/art_data.c').write_text(text)
 (ROOT/'src/art.h').write_text('''#ifndef MOONWAKE_ART_H
#define MOONWAKE_ART_H
#include <stdint.h>
typedef struct {uint8_t bank,n0,n1;const uint8_t *tiles0,*tiles1,*map,*attr;const uint16_t *pal;} ArtDef;
extern const ArtDef art_worlds[8];
extern const ArtDef art_title;
extern const uint8_t font_tiles[1024],terrain_tiles[256],sprite_tiles[1536];
extern const uint8_t terrain_world_tiles[2048];
extern const unsigned char boss_tiles[4][256];
extern const uint16_t sprite_palettes[32];
#define ART_BANK_FIRST 8
#endif
''')
 (OUT/'manifest.json').write_text(json.dumps(meta+[mt],indent=2)+'\n')
 # Entire panorama plus a real160x144native viewport, including readable hero.
 board=Image.new('RGB',(880,2640),(17,25,43));d=ImageDraw.Draw(board)
 for b,m in enumerate(meta):
  y=18+b*322;d.text((20,y),f'{b+1:02d}  {names[b]}',fill=(255,233,192))
  im=Image.open(OUT/(m['name']+'.png'))
  board.paste(im.resize((512,288),Image.Resampling.NEAREST),(20,y+23))
  preview=im.crop((48,0,208,144));td=ImageDraw.Draw(preview);_,tp=pal555([TERRAIN[b]])
  for xx in range(0,160,8):
   for yy,n in [(128,1),(136,3)]:
    tile=np.array([[int(c) for c in row] for row in variants[b][n]],dtype=np.uint8);preview.paste(Image.fromarray(tp[0][tile]),(xx,yy))
  hero=np.array([[int(c) for c in row] for row in HERO[0]],dtype=np.uint8);_,sp=pal555(SPRITE)
  rgba=np.concatenate([sp[0][hero],np.where(hero[:,:,None]>0,255,0).astype(np.uint8)],axis=2);hi=Image.fromarray(rgba);preview.paste(hi,(48,112),hi)
  preview.save(OUT/(m['name']+'-gameplay-mock.png'))
  board.paste(preview.resize((320,288),Image.Resampling.NEAREST),(552,y+23))
 board.save(OUT/'contact-sheet.png')
 validate(meta+[mt]);print(json.dumps([{k:m[k] for k in ('name','bank','n0','n1','unique_tiles','original_unique')} for m in meta+[mt]],indent=2))

def validate(meta):
 # Verify every pixel by decoding bytes in generated C files, rather than trusting
 # the source paintings or the packer's working arrays.
 for m in meta:
  path=ROOT/'src'/('title_art.c' if m['name']=='title' else m['name']+'.c');text=path.read_text()
  def read(n):return np.array([int(i) for i in re.findall(r'\d+',re.search(r'\b'+n+r'\[\d+\] = \{(.*?)\};',text,re.S).group(1))])
  name=m['name'];maps=read(name+'_map');attrs=read(name+'_attr');v=read(name+'_pal');patterns=list(read(name+'_tiles0').reshape(-1,16))+list(read(name+'_tiles1').reshape(-1,16));w,h=m['size']
  assert len(v)==32 and all(0<=q<=32767 for q in v),'RGB555 palettes: '+name
  assert m['bank']==(2 if name=='title' else 8+int(name.split('_')[1]))
  assert len(maps)==w*h//64 and len(attrs)==len(maps);assert m['n0']<=144 and m['n1']<=160
  ps=np.array([[(q&31)*255//31,((q>>5)&31)*255//31,((q>>10)&31)*255//31] for q in v],dtype=np.uint8).reshape(8,4,3)
  output=np.zeros((h,w,3),dtype=np.uint8)
  for j,(t,attr) in enumerate(zip(maps,attrs)):
   assert attr&7<6 and not attr&128
   i=t-96+m['n0'] if attr&8 else t-112
   assert 0<=i<m['unique_tiles'];a=unpack(patterns[i]);a=a[:,::-1] if attr&32 else a;a=a[::-1] if attr&64 else a
   yy,xx=divmod(j,w//8);output[yy*8:yy*8+8,xx*8:xx*8+8]=ps[attr&7][a]
  assert np.array_equal(output,np.array(Image.open(OUT/(name+'.png')))),name
  if name.startswith('world_'):assert np.array_equal(output[:,0],output[:,-1]),'Wrap seam: '+name
 data=(ROOT/'src/art_data.c').read_text()
 def shared(name):
  raw=re.search(r'\b'+name+r'(?:\[\d+\])+ = \{(.*?)\};',data,re.S).group(1)
  return [int(i) for i in re.findall(r'\d+',raw)]
 for name,length in [('font_tiles',1024),('terrain_tiles',256),('terrain_world_tiles',2048),('sprite_tiles',1536),('sprite_palettes',32)]:
  v=shared(name);assert len(v)==length,name
  if name=='font_tiles':assert all(v[i]==0 and v[i+1]==0 for i in range(0,1024,16))
  if name=='sprite_palettes':assert all(0<=i<=32767 for i in v)
 assert len(font())==1024
 validate_font(font())
 # Exact decode of each native boss block, including column-major placement.
 bosses=np.array(shared('boss_tiles'),dtype=np.uint8).reshape(4,256)
 spr=bytes(shared('sprite_tiles'));assert bytes(bosses[3])==spr[64*16:80*16],'Dreamwhale slot preservation'
 for raw,a in zip(bosses[:3],expansion_boss_images()):assert bytes(raw)==pack_sprite(a)
 assert len({bytes(raw) for raw in bosses})==4,'Every boss needs its own silhouette'
 _,sp=pal555(SPRITE);boss_image=np.zeros((32,128,4),dtype=np.uint8)
 for b,raw in enumerate(bosses):
  for x in range(4):
   for y in range(4):
    a=unpack(raw[(x*4+y)*16:(x*4+y+1)*16]);boss_image[y*8:y*8+8,b*32+x*8:b*32+x*8+8,:3]=sp[7][a]
    boss_image[y*8:y*8+8,b*32+x*8:b*32+x*8+8,3]=np.where(a>0,255,0)
 assert np.array_equal(boss_image,np.array(Image.open(OUT/'bosses.png'))),'Boss byte preview'
 # New material blocks and actors must occupy exactly their contracted slots.
 terrain=bytes(shared('terrain_world_tiles'));variants=terrain_variants()
 assert len({terrain[b*256:(b+1)*256] for b in range(8)})==8
 terrain_image=np.zeros((64,128,3),dtype=np.uint8)
 for b,vs in enumerate(variants):
  _,tp=pal555([TERRAIN[b]])
  for n,rows in enumerate(vs):
   raw=terrain[b*256+n*16:b*256+(n+1)*16];a=unpack(raw)
   assert bytes(raw)==pack(np.array([[int(c) for c in row] for row in rows]))
   terrain_image[b*8:b*8+8,n*8:n*8+8]=tp[0][a]
 assert np.array_equal(np.array(Image.open(OUT/'terrain-6x.png')),np.repeat(np.repeat(terrain_image,6,axis=0),6,axis=1))
 for rows,start in [(MOVER,52),(JELLY[0],54),(JELLY[1],56)]:
  a=np.array([[int(c) for c in row] for row in rows],dtype=np.uint8)
  assert spr[start*16:(start+2)*16]==pack_sprite(a)
 # Immutable hashes captured from the original released C source make accidental
 # changes to the four old panoramas, title, fonts and original sprites visible.
 preserved=json.loads((SOURCE/'native-preservation.json').read_text())
 checks={'font_tiles':bytes(shared('font_tiles')),'terrain_original_four':terrain[:1024],'sprite_0_51':spr[:52*16],'sprite_58_95':spr[58*16:],'dreamwhale':bytes(bosses[3])}
 for name,raw in checks.items():assert hashlib.sha256(raw).hexdigest()==preserved[name],'Changed original art: '+name
 for name,digest in preserved['world_sources'].items():assert hashlib.sha256((ROOT/'src'/(name+'.c')).read_bytes()).hexdigest()==digest,'Changed original scene: '+name
 print('Validated: eight exact C-array panoramas, wrap seams, reserved VRAM slots, four colors per tile, RGB555 palettes, four native bosses, eight materials, new actor slots, unchanged original art.')

if __name__=='__main__':main()
