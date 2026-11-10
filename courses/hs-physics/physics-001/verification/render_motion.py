"""Physics-driven, antialiased teaching GIFs + matching controllable MP4 and PDF frames."""
from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont
import math,json,subprocess,sys
import numpy as np
import motion_models as M
R=Path(__file__).resolve().parent.parent/'animations';W,H=960,560;AA=2;FPS=10
for sub in ['gifs','video','posters','plates','qa']:(R/sub).mkdir(exist_ok=True)
B='#205b82';T='#107b79';A='#b67b2b';RED='#b04b42';INK='#223b49';GRAY='#93a4ab';LIGHT='#dde6e7';BG='#fbfcfa';PURPLE='#77649b'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
@lru_cache(maxsize=100)
def font(n,bold=False):return ImageFont.truetype(BOLD if bold else FONT,int(n*AA),index=2)
def ff(v,n=2):return f'{0 if abs(v)<.5*10**(-n) else v:.{n}f}'
class C:
 def __init__(self,title,sub):
  self.im=Image.new('RGB',(W*AA,H*AA),BG);self.d=ImageDraw.Draw(self.im);self.text(28,18,title,25,INK,True);self.text(28,56,sub,14 if font(14).getlength(sub)<680*AA else 12,GRAY);self.line([(25,84),(935,84)],LIGHT,1);self.line([(25,429),(935,429)],LIGHT,1)
 def line(self,pts,c=GRAY,w=2,dash=False):
  if dash:
   for a,b in zip(pts,pts[1:]):
    dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
    for z in np.arange(0,length,11):
     q=min(z+6,length);self.d.line([(AA*(a[0]+dx*z/length),AA*(a[1]+dy*z/length)),(AA*(a[0]+dx*q/length),AA*(a[1]+dy*q/length))],fill=c,width=max(1,int(w*AA)))
  else:self.d.line([(AA*x,AA*y) for x,y in pts],fill=c,width=max(1,int(w*AA)),joint='curve')
 def text(self,x,y,s,n=18,c=INK,b=False,anchor=None):self.d.text((x*AA,y*AA),str(s),font=font(n,b),fill=c,anchor=anchor)
 def wrap(self,x,y,s,n=14,c=GRAY,width=900):
  line='';yy=y
  for ch in s:
   if font(n).getlength(line+ch)>width*AA:self.text(x,yy,line,n,c);line=ch;yy+=n+4
   else:line+=ch
  if line:self.text(x,yy,line,n,c)
 def circle(self,x,y,r,c=B,fill=None,w=2):self.d.ellipse(((x-r)*AA,(y-r)*AA,(x+r)*AA,(y+r)*AA),fill=fill,outline=c,width=max(1,int(w*AA)))
 def rect(self,x,y,w,h,fill='#e7eff3',c=B,lw=2):self.d.rectangle((x*AA,y*AA,(x+w)*AA,(y+h)*AA),fill=fill,outline=c,width=max(1,int(lw*AA)))
 def poly(self,pts,fill,c=None,w=2):
  pts=[(x*AA,y*AA) for x,y in pts];self.d.polygon(pts,fill=fill)
  if c:self.d.line(pts+[pts[0]],fill=c,width=int(w*AA))
 def arrow(self,x,y,dx,dy,c=B,label=None,n=17):
  L=math.hypot(dx,dy)
  if L<.5:return
  angle=math.atan2(dy,dx);self.line([(x,y),(x+dx,y+dy)],c,3);hs=min(10,L*.45)
  self.poly([(x+dx,y+dy),(x+dx-hs*math.cos(angle-.45),y+dy-hs*math.sin(angle-.45)),(x+dx-hs*math.cos(angle+.45),y+dy-hs*math.sin(angle+.45))],c)
  if label:self.text(x+dx+7 if dx>=0 else x+dx-font(n).getlength(label)/AA-7,y+dy-12,label,n,c)
 def spring(self,x0,y,x1,amp=8):
  pts=[(x0,y),(x0+8,y)];N=14
  for i in range(N+1):pts.append((x0+8+(x1-x0-16)*i/N,y+(0 if i in [0,N] else amp*(-1 if i%2 else 1))))
  pts.append((x1,y));self.line(pts,GRAY,2)
 def block(self,x,y,angle=0,w=36,h=24,c=B,fill='#dceaf0'):
  pts=[]
  for xx,yy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]:pts.append((x+xx*math.cos(angle)-yy*math.sin(angle),y+xx*math.sin(angle)+yy*math.cos(angle)))
  self.poly(pts,fill,c)
 def car(self,x,y,c=B):
  self.poly([(x,y-18),(x+10,y-40),(x+43,y-40),(x+59,y-18),(x+76,y-13),(x+76,y+4),(x,y+4)],'#e0ebf1',c)
  self.line([(x+14,y-35),(x+40,y-35),(x+51,y-19),(x+8,y-19)],c,1)
  for xx in [x+16,x+61]:self.circle(xx,y+4,9,INK,'#fff');self.circle(xx,y+4,3,GRAY,GRAY)
 def person(self,x,y,scale=1,wings=False):
  self.circle(x,y-17*scale,6*scale,INK,'#e9cba9');self.line([(x,y-10*scale),(x,y+12*scale)],INK,3)
  self.line([(x,y-3*scale),(x-16*scale,y+5*scale)],INK,3);self.line([(x,y-3*scale),(x+16*scale,y+5*scale)],INK,3)
  self.line([(x,y+12*scale),(x-10*scale,y+30*scale)],INK,3);self.line([(x,y+12*scale),(x+10*scale,y+30*scale)],INK,3)
  if wings:self.poly([(x,y-8*scale),(x-25*scale,y+10*scale),(x-8*scale,y+22*scale),(x+8*scale,y+22*scale),(x+25*scale,y+10*scale)],'#cce4df',T)
 def footer(self,phase,metrics,note,clock=None,hold=False):
  if clock is not None:self.text(735,56,'t = '+ff(clock,3)+' s'+('｜暂停观察' if hold else ''),15,T)
  elif hold:self.text(765,56,'暂停观察',15,T)
  self.wrap(28,440,phase,20,INK,width=900);self.text(28,476,metrics,17,B);self.wrap(28,514,note,13,GRAY,width=900)
 def image(self):return self.im.resize((W,H),Image.Resampling.LANCZOS)
def graph(c,x,y,w,h,xmax,ymax,xlabel,ylabel):
 c.line([(x,y-h),(x,y),(x+w,y)],GRAY,1);c.text(x,y-h-27,ylabel,15);c.text(x+w-80,y+12,xlabel,14,GRAY)
 return lambda t:x+w*t/xmax,lambda v:y-h*v/ymax

def scene01(t,hold=False):
 c=C('01｜雨滴下落：速度越大，阻力越大','背景情境示例；本题计算只需比较单位');vt=10;v=vt*(1-math.exp(-t));s=vt*(t-1+math.exp(-t));y=125+230*s/(vt*(4-1+math.exp(-4)));c.line([(180,115),(180,410)],LIGHT,2,True)
 c.poly([(180,y-14),(170,y+2),(171,y+12),(180,y+17),(189,y+12),(190,y+2)],'#6fabc8',B)
 c.arrow(250,y,0,55,RED,'重力不变');c.arrow(165,y,0,-55*v/vt,T,'阻力随v增大')
 c.text(500,155,'重力向下，阻力向上',23);c.text(500,205,'开始：重力 > 阻力',20);c.text(500,250,'后来：两者越来越接近',20,T);c.rect(510,325,250,15,'#eef1ee',LIGHT);c.rect(510,325,250*v/vt,15,T,T)
 p='雨滴仍向下加速，但加速度逐渐减小' if t<3 else '逐渐接近终极速度；本段不表示已经精确达到'
 c.footer(p,'速度 / 示例终速度 = '+ff(v/vt,3),'示例采用线性阻力模型；时间和场景参数为演示设定，不是原题数据。',t,hold);return c,p

def scene02(t,hold=False):
 k=min(3,int(t));u=min(1,t-k) if t<4 else 1.;names=['A 火箭受控回收','B 从水平飞行的飞机离开','C 翼装稳定滑翔','D 蹦极绳尚未绷紧'];c=C('02｜四种下落，逐一检查条件',names[k]+'｜四个独立场景，切换不代表连续运动')
 if k==0:
  y=130+215*(2*u-u*u);x=360;c.line([(240,360),(480,360)],GRAY,4);c.line([(240,360),(240,390),(480,390),(480,360)],GRAY,3)
  c.rect(x-18,y-57,36,72,'#e7eef2',B);c.poly([(x-18,y-57),(x,y-82),(x+18,y-57)],'#e7eef2',B);c.poly([(x-14,y+16),(x,y+45),(x+14,y+16)],'#ecc38c',A)
  c.arrow(x-45,y-20,0,-84,T,'推力');c.arrow(x+45,y-20,0,60,RED,'重力');c.text(590,195,'向下运动，但正在受控减速',21);c.text(590,240,'除重力外还有推力',21,T);p='回收减速段示意：不能只因“正在下落”就当作自由落体'
 elif k==1:
  c.line([(170,145),(730,145)],LIGHT,1,True);px=240+300*u;c.poly([(px-55,145),(px+55,145),(px+75,151),(px+35,157),(px-55,157),(px-70,140)],'#dceaf0',B);c.line([(px,135),(px+20,167)],B,4)
  x=240+300*u;y=168+150*u*u;c.person(x,y,.85);c.arrow(x+25,y-5,60,0,B,'保留水平速度');c.line([(240+300*z,168+150*z*z) for z in np.linspace(0,u,40)],GRAY,1,True);c.text(570,330,'刚离机时，相对地面并非静止',20);p='这里忽略空气作用，只突出离机时仍有水平初速度'
 elif k==2:
  c.poly([(180,110),(250,110),(250,390),(180,390)],'#e5e8df',GRAY);x=290+290*u;y=165+110*u;c.person(x,y,1.2,True);c.arrow(x-43,y,0,-60,T,'空气合力');c.arrow(x+43,y,0,60,RED,'重力');c.arrow(x+5,y+43,55,21,B,'速度');c.text(650,140,'稳定滑翔示意',21);c.text(650,188,'空气作用不能忽略',19,T);p='翼装靠空气作用滑翔；图示只展示一个稳定滑翔阶段'
 else:
  ax,ay=380,115;y=145+195*u*u;c.line([(230,100),(450,100)],GRAY,7);d=y-ay;slack=55*math.sqrt(max(0,1-u*u));pts=[(ax+slack*math.sin(2*math.pi*z),ay+d*z) for z in np.linspace(0,1,80)];c.line(pts,A,3);c.person(ax,y,1);c.arrow(ax+65,y,0,60,RED,'重力');c.text(590,155,'由静止开始',23);c.text(590,205,'绳松弛：没有绳拉力',21,T);c.text(590,255,'忽略空气作用：仅受重力',20);p='演示到绳刚绷直为止；此后的弹性拉伸属于另一阶段'
 c.footer(p,'本段只比较运动情境，不给出原题未提供的定量参数。','判据：相对地面初速度为零；运动阶段只受重力或其他力可忽略。',None,hold);return c,p

def scene03(t,hold=False):
 z=M.pendulum(t);th=z['theta'];px,py=400,120;L=220;x=px+L*math.sin(th);y=py+L*math.cos(th);c=C('03｜摆球端点：速度为零，合力通常不为零','实线是真实力；端点虚线用于解释重力分解')
 c.line([(px-50,py-12),(px+50,py-12)],GRAY,6);c.line([(px,py),(x,y)],GRAY,3);c.line([(px,py),(px,py+L)],LIGHT,1,True);c.circle(x,y,12,B,'#d9e9ef');c.arrow(x,y,-7*z['T']*math.sin(th),-7*z['T']*math.cos(th),B,'T');c.arrow(x,y,0,70,RED,'mg')
 if abs(z['omega'])<.05:
  c.line([(x,y),(x+70*math.cos(th)*math.sin(th),y+70*math.cos(th)**2)],A,2,True);c.text(600,310,'虚线分力不另算真实力',18,A)
 for th0 in [-M.TH,M.TH]:c.circle(px+L*math.sin(th0),py+L*math.cos(th0),5,GRAY,None,1)
 if abs(z['omega'])<.08:
  c.text(620,155,'端点：瞬时速度为零',21);c.text(620,202,'重力仍有沿切线的分量',19,T);c.text(620,250,'因此会开始摆回',21,T)
 else:
  c.text(620,155,'此刻在摆动中，速度不为零',20);c.text(620,202,'最低点需要向上的向心合力' if abs(th)<.1 else '速率与速度方向都在改变',18,T);c.text(620,250,'真实受力：重力与拉力',20)

 p='接近端点：速度很小，仍有切向加速度' if abs(z['omega'])<.08 else '运动中：速度与拉力都随位置变化'
 c.footer(p,'摆角 = '+ff(math.degrees(th),1)+'°　｜　速率 = '+ff(z['v'])+' m/s','演示取绳长1m、g=10m/s²、初始摆角35°；采用完整单摆运动关系。',t,hold);return c,p

def scene04(t,hold=False):
 c=C('04｜物块匀速上斜面','高度、斜面路程、各力做功分别看');theta=math.pi/6;s=t;x=180+90*s*math.cos(theta);y=380-90*s*math.sin(theta);c.poly([(180,380),(180+360*math.cos(theta),200),(180+360*math.cos(theta),380)],'#edf1ec',GRAY)
 for tt in [0,1,2,3,4]:c.circle(180+90*tt*math.cos(theta),380-90*tt*math.sin(theta),3,LIGHT,LIGHT)
 c.block(x,y-13,-theta,w=42,h=26);cx=x-6;cy=y-12;c.arrow(cx,cy,60*math.cos(theta),-60*math.sin(theta),B,'F');c.arrow(cx,cy,-30*math.cos(theta),30*math.sin(theta),A,'f');c.arrow(cx,cy,-52*math.sin(theta),-52*math.cos(theta),T,'N');c.arrow(cx,cy,0,60,RED,'mg')
 c.line([(520,380),(520,200)],GRAY,1,True);c.text(530,280,'h = 2m',18);c.text(215,398,'沿斜面全程 4m',17)
 c.text(655,145,'各力累积做功',22);c.text(655,195,'外力：'+ff(10*s,1)+' J',21,B);c.text(655,240,'重力：'+ff(-5*s,1)+' J',21,RED);c.text(655,285,'摩擦：'+ff(-5*s,1)+' J',21,A);c.text(655,335,'总功：0 J',21,T)
 p='相等时间内走过相等路程：物块匀速上滑';c.footer(p,'F=10N　f=5N　mg=10N　N=5√3N','本题的匀速条件已给出。演示额外取上滑速率1m/s，仅用于安排播放时间。',t,hold);return c,p

def scene05(t,hold=False):
 c=C('05｜甲在乙上滑动，乙留在桌面原处','上接触面：滑动摩擦；下接触面：静摩擦');x=190+90*(.5*t+.5*t*t);c.rect(110,320,495,14,'#dfe5e5',GRAY);c.line([(145,334),(145,410)],GRAY,5);c.line([(565,334),(565,410)],GRAY,5);c.rect(125,295,460,25,'#e2ebe6',T);c.rect(x,253,100,42,'#dceaf0',B);c.text(x+37,257,'甲',23,B,True);c.text(520,294,'乙',20,T,True)
 c.line([(125,295),(585,295)],A,3);c.line([(125,320),(585,320)],T,3);c.arrow(x+100,270,65,0,B,'F');c.arrow(x+40,289,-45,0,A,'甲受摩擦');c.arrow(420,304,45,0,A);c.arrow(420,326,-45,0,T)
 c.text(660,130,'分别圈出研究对象',23);c.text(660,184,'甲：4个真实力',21,B);c.text(660,230,'乙：5个真实力',21,T);c.text(660,284,'乙上方摩擦向右',19,A);c.text(660,326,'桌面对乙摩擦向左',19,T)
 p='甲向右滑动；乙与桌面保持相对静止';c.footer(p,'甲的运动仅选一种允许的加速情形演示；并未认定原题甲匀速。','示意箭头标方向，不作力大小的比较；完整受力分析见本题正文。',t,hold);return c,p

def scene06(t,hold=False):
 c=C('06｜卫星匀速绕行：速度沿切线，引力指向地心','示例取h=R；一般题目关系是h=R/n');cx,cy=380,255;R0=75;r=150;phi=2*math.pi*t;x=cx+r*math.cos(phi);y=cy+r*math.sin(phi);c.circle(cx,cy,r,GRAY,None,2);c.circle(cx,cy,R0,T,'#dcebea');c.text(cx-28,cy-15,'地球',22,T);c.circle(x,y,8,B,B);c.arrow(x,y,-60*math.sin(phi),60*math.cos(phi),B,'v');c.arrow(x,y,-52*math.cos(phi),-52*math.sin(phi),RED,'引力')
 c.line([(cx,cy),(cx+r,cy)],GRAY,1,True);c.line([(cx,cy+36),(cx+R0,cy+36)],T,3);c.text(cx+22,cy+44,'R',18,T);c.line([(cx+R0,cy+36),(cx+r,cy+36)],A,3);c.text(cx+105,cy+44,'h',18,A)
 c.text(650,155,'r = R + h',28,B);c.text(650,212,'引力公式用r',23);c.text(650,264,'速率不变',22);c.text(650,306,'速度方向一直改变',21,T)
 p='卫星始终受到指向地心的引力，沿圆轨道匀速运行';c.footer(p,'已完成 '+ff(t*100,0)+'% 的一圈','按圆轨道演示；箭头只说明方向，周期与真实地球大小不按屏幕时间、尺寸换算。',None,hold);return c,p

def scene07(t,hold=False):
 c=C('07｜定滑轮连接体：甲前进，乙下降','按原图可辨分数取乙质量3m/2；配图为依据题干重绘');s=3*t*t;dx=90*s;xa=190+dx;yb=265+dx;c.line([(100,220),(580,220)],GRAY,4);c.block(xa,197,w=52,h=46);c.text(xa-12,183,'甲',20,B,True)
 c.circle(610,219,22,GRAY,None,2);c.line([(xa+26,197),(610,197)],B,2);ang=np.linspace(-math.pi/2,0,40);c.line([(610+22*math.cos(a),219+22*math.sin(a)) for a in ang],B,2);c.line([(632,219),(632,yb-22)],B,2);c.block(632,yb,w=48,h=44,c=A,fill='#efe5d4');c.text(620,yb-15,'乙',20,A,True)
 c.arrow(xa,197,30,0,B,'T');c.arrow(632,yb,0,-30,B,'T');c.arrow(632,yb,0,75,RED,'乙的重力')
 # Equal displacement strips make the string constraint visible.
 c.line([(190,278),(xa,278)],T,4);c.line([(745,265),(745,yb)],T,4);c.text(230,295,'甲位移：'+ff(s,3)+'m',18,T);c.text(765,305,'乙下降同样距离',17,T);c.text(100,120,'甲质量m；水平面光滑',20);c.text(725,155,'两侧T相同',21,B)
 p='两块加速度大小相同，运动方向不同';c.footer(p,'a = 3g/5 = 6m/s²　｜　T = 3mg/5（演示取m=1kg）','只突出沿运动方向的力；图像分母下沿与原配图的裁切说明保留在正文。',t,hold);return c,p

def scene08(t,hold=False):
 c=C('08｜球拐了直角，踢前踢后速率相同','短时踢击用折点示意；不规定接触过程中每个瞬间的速率');hit=1.5
 if t<hit:x=225+150*t;y=235;dx,dy=55,0;phase='踢前：球由b向a运动'
 else:x=450;y=235+150*(t-hit);dx,dy=0,55;phase='踢后：球由a向c运动'
 c.line([(225,235),(450,235),(450,385)],GRAY,2,True);c.circle(x,y,12,B,'#e7eff1');c.arrow(x,y,dx,dy,B,'v');c.text(205,205,'b',22);c.text(463,210,'a',22);c.text(463,365,'c',22)
 ox,oy=700,215;c.arrow(ox,oy,95,0,B,'初动量');c.arrow(ox,oy,0,95,T,'末动量');c.arrow(ox+95,oy,-95,95,A,'动量差');c.text(660,130,'把两个动量从同一点画出',18);c.text(650,365,'动量改变，始末动能相同',20,T)
 c.footer(phase,'初末速度箭头等长　｜　净功0　｜　冲量大小√2mv','图示仅约束始末速率相等；动量变化要比较矢量，不能直接把两个速率相减。',t,hold);return c,phase

def scene09(t,hold=False):
 stage=min(2,int(t/2));tt=t-stage*2 if t<6 else 2.;rat=[.5,.8,1.][stage];wc=math.sqrt(5);omega=rat*wc;ph=omega*tt;c=C('09｜转盘：三档独立匀速对照','每档重新开始；不把加速转盘的切向摩擦混入原题');cx,cy=290,255;r=145;c.circle(cx,cy,r,GRAY,'#edf3ef');
 for phi in np.arange(0,2*math.pi,math.pi/6):c.line([(cx,cy),(cx+r*math.cos(phi+ph),cy+r*math.sin(phi+ph))],LIGHT,1)
 for rr,lab,col in [(r,'甲',B),(r/2,'乙',T)]:
  x=cx+rr*math.cos(ph);y=cy+rr*math.sin(ph);c.circle(x,y,8,col,col);c.text(x+11,y-22,lab,20,col,True);need=rat*rat*rr/r;c.arrow(x,y,-70*need*math.cos(ph),-70*need*math.sin(ph),col)
 c.text(560,135,'第'+str(stage+1)+'档：角速度 = '+ff(rat,1)+'倍临界值',20);c.text(560,190,'所需摩擦 / 最大静摩擦',19)
 for i,(lab,v,col) in enumerate([('甲',rat*rat,B),('乙',rat*rat/2,T)]):
  yy=250+i*70;c.text(555,yy-5,lab,21,col);c.rect(600,yy,220,18,'#e5ebe6',LIGHT);c.rect(600,yy,220*v,18,col,col);c.text(835,yy-5,ff(v,2),17,col)
 p='甲在边缘，乙在半径一半处；两者角速度相同' if stage<2 else '临界：甲恰好用尽最大静摩擦，乙仍未达到上限'
 c.footer(p,'箭头为所需静摩擦方向，始终指向圆心。','三档是独立的匀速情形；本段到临界结束，不外推未经计算的滑出轨迹。',tt,hold);return c,p

def scene10(t,hold=False):
 c=C('10｜平抛：速度方向与位移方向不同','水平初速1m/s，g=10m/s²，总时间0.2s');x=180+1400*t;y=120+7000*t*t;c.line([(100,400),(520,400)],GRAY,3);c.line([(180,120),(520,120)],LIGHT,1,True);c.line([(180+1400*z,120+7000*z*z) for z in np.linspace(0,.2,100)],GRAY,2,True);c.circle(x,y,9,B,B);c.line([(180,120),(x,y)],PURPLE,2,True);c.arrow(x,y,8,80*t,T)
 ox,oy=680,200;c.arrow(ox,oy,55,0,B);c.arrow(ox,oy,0,550*t,A);c.arrow(ox,oy,55,550*t,T);c.text(740,164,'水平速度1m/s',16,B);c.text(560,250,'竖直速度',17,A);c.text(755,290,'青色：合速度',17,T);c.text(600,350,'虚线：从抛出点到当前位置',17,PURPLE);c.text(600,385,'实箭头：该时刻的速度方向',17,T)
 p='速度角由速度分量决定；位移角由位移分量决定';c.footer(p,'x = '+ff(t,3)+'m　y = '+ff(5*t*t,3)+'m　vy = '+ff(10*t,2)+'m/s','在0.1s与0.2s暂停；右侧速度箭头采用同一标尺，轨迹纵横坐标按相同比例绘制。',t,hold);return c,p

def scene11(t,hold=False):
 z=M.power_u(t);c=C('11｜恒功率启动：车速增加得越来越慢','示例m=1000kg、P=20kW、阻力1000N；不是原题数值');end=M.power_u(M.PTEND)['s'];x=85+365*z['s']/end;c.line([(70,340),(550,340)],GRAY,3);c.car(x,325)
 X,Y=graph(c,620,350,280,170,M.PTEND,20,'时间 / s','速度 / (m/s)');c.line([(620,Y(20)),(910,Y(20))],GRAY,1,True);c.text(705,Y(20)-25,'最大速度参考线',14,GRAY)
 times=np.linspace(0,M.PTEND,90);c.line([(X(tt),Y(M.power_u(tt)['v'])) for tt in times],LIGHT,2);c.line([(X(0),Y(0)),(X(M.PTEND),Y(19))],A,2,True);c.line([(X(tt),Y(M.power_u(tt)['v'])) for tt in np.linspace(0,t,65)],B,3);c.circle(X(t),Y(z['v']),5,T,T)
 c.text(90,150,'初段：速度增加较快',22);c.text(90,196,'后段：速度增加较慢',22,T);c.text(90,245,'曲线下的面积 > 三角形面积',19,B)
 p='车速仍增加，加速度在减小；有限时段末速小于最大速度';c.footer(p,'车速 '+ff(z['v'])+'m/s　｜　实际路程 '+ff(z['s'],1)+'m','图线说明教材理想模型的趋势；真实零速起步受牵引力限制。本段不画有限时刻精确达到终速。',t,hold);return c,p

def scene12(t,hold=False):
 z=M.throw(t);c=C('12｜有阻力的上抛：上升、下降分开看','示例取初动能20J、m=1kg、阻力为0.3mg');scale=150;x=310;y=402-scale*z['y'];c.line([(200,402),(410,402)],GRAY,3);c.line([(310,125),(310,402)],LIGHT,1,True);c.circle(x,y,11,B,'#dceaf0');c.line([(240,402-scale*M.HUP),(380,402-scale*M.HUP)],GRAY,1,True);c.text(150,402-scale*M.HUP-28,'最高点',17,GRAY)
 apex=abs(t-M.TUP)<1e-8
 if apex:
  c.text(560,150,'最高点：瞬时速度为零',22,T);c.text(560,205,'上升结束，随后开始下降',20);c.text(560,255,'下一阶段的阻力将向上',19,T)
 else:
  c.text(560,120,'同一物体的受力示意',20);c.block(685,225,w=48,h=40);c.arrow(685,225,0,70,RED,'mg');drag=21 if t<M.TUP else -21;c.arrow(655,225,0,drag,T,'阻力');c.arrow(755,275,0,-10*z['v'],B,'v')
 for i,(lab,val,col) in enumerate([('动能',z['Ek'],B),('势能',z['Ep'],T)]):
  yy=345+i*35;c.text(540,yy-5,lab,17,col);c.rect(600,yy,240,12,'#e5ece8',LIGHT);c.rect(600,yy,240*val/20,12,col,col)
 p='最高点：速度瞬时为零，上升段结束' if apex else '上升：重力与阻力均向下' if t<M.TUP else '下降：阻力向上，重力仍向下'
 c.footer(p,'高度 '+ff(z['y'],3)+'m　｜　速率 '+ff(abs(z['v']),3)+'m/s　｜　'+('阶段分界' if apex else z['phase']),'阻力按题设恒定大小处理；最高点作为方向切换的分界，不套用无阻力的运动对称性。',t,hold);return c,p

def scene13(t,hold=False):
 z=M.belt(t);c=C('13｜传送带与弹簧：第一次向右运动的三个阶段','示例取a0=1m/s²、x0=1m、m=1kg；仅突出水平方向作用');x=145+140*z['x'];yb=292;left,right=100,790;cy=317;rr=25
 c.circle(left,cy,rr,GRAY,None,3);c.circle(right,cy,rr,GRAY,None,3);c.line([(left,cy-rr),(right,cy-rr)],GRAY,3);c.line([(left,cy+rr),(right,cy+rr)],GRAY,3)
 shift=(M.VB*140*t)%60
 for xx in np.arange(left-60,right,60):
  a=xx+shift;b=xx+60-shift
  if left<a<right:c.line([(a,cy-rr),(min(a+20,right),cy-rr)],B,4)
  if left<b<right:c.line([(b,cy+rr),(min(b+20,right),cy+rr)],B,3)
 for xc in [left,right]:c.line([(xc,cy),(xc+18*math.cos(M.VB*140*t/rr),cy+18*math.sin(M.VB*140*t/rr))],GRAY,2)
 c.rect(65,245,18,60,'#dfe5e3',GRAY);c.spring(83,270,x-20);c.block(x,270,w=40,h=44);c.arrow(x,270,35*z['f'],0,T,'摩擦');c.arrow(x,270,-35*z['spring'],0,A,'弹力');c.arrow(x,220,35*z['v'],0,B,'速度')
 for xx,lab in [(1,'x0'),(2,'2x0'),(2+math.sqrt(3),'最右端')]:
  q=145+140*xx;c.line([(q,355),(q,388)],LIGHT,1,True);c.text(q-15,390,lab,16,GRAY)
 phases={1:'阶段I：滑动追赶，物块越来越快',2:'阶段II：静摩擦平衡弹力，随带匀速',3:'阶段III：再次滑动，摩擦向右、加速度向左'};p=phases[z['phase']]
 if abs(t-M.BT3)<1e-7:p='到达最右端：速度瞬时为零，合力仍向左'
 c.footer(p,'x / x0 = '+ff(z['x'],3)+'　｜　v = '+ff(z['v'],3)+'m/s　｜　a = '+ff(z['a'],3)+'m/s²','按真实分段运动计时；到最右端结束本段。暂停不是永久静止，下一次循环明确重置。',t,hold);return c,p

def scene14a(t,hold=False):
 # t is a loading progress index; only the integer equilibrium samples are read as measurements.
 F=2*t;l=4+F;end=120+18*l;c=C('14A｜缓慢加载：总长度不是伸长量','加载进度示意；只在平衡状态读数，不据此研究振动')
 c.line([(210,115),(370,115)],GRAY,6);c.spring(300,0,300) if False else None
 pts=[]
 for i in range(97):
  yy=120+(end-120)*i/96;xx=300+(10*math.sin(i/96*12*math.pi) if i not in [0,96] else 0);pts.append((xx,yy))
 c.line(pts,GRAY,2);c.line([(300,end),(300,end+13)],GRAY,2)
 if F>.01:c.rect(275,end+13,50,28,'#e8dfcb',A);c.text(160,end+12,'F='+ff(F,1)+'N',17,A)
 c.line([(390,120),(390,322)],GRAY,2)
 for cm in range(0,12):c.line([(383,120+18*cm),(397,120+18*cm)],GRAY,1);c.text(405,112+18*cm,str(cm),13,GRAY)
 c.text(380,346,'长度 / cm',15,GRAY);c.line([(245,120+72),(360,120+72)],T,1,True);c.text(100,181,'原长4cm',18,T)
 X,Y=graph(c,585,350,285,205,12,7,'总长度l / cm','F / N');c.line([(X(4),Y(0)),(X(10),Y(6))],B,2)
 for force in [0,2,4,6]:
  if force<=F+1e-8:c.circle(X(4+force),Y(force),5,T,T)
 c.circle(X(l),Y(F),6,A,A);c.text(620,390,'横轴截距4cm；斜率100N/m',17,B)
 p=('平衡读数：' if abs(t-round(t))<1e-7 else '缓慢加载过渡，不作正式读数：')+'F='+ff(F,1)+'N，l='+ff(l,1)+'cm'
 c.footer(p,'总长度l = 原长4cm + 伸长量；本段仅示胡克定律的线性范围。','慢加载是操作示意，不把中间过渡帧当作严格静平衡测量；弯曲段与弹性范围见正文。',None,hold);return c,p

def scene14b(t,hold=False):
 stage=0 if t<4 else 1;tt=t if stage==0 else t-4;rl,rr=55,(30 if stage==0 else 55);cx1,cx2,cy=250,680,260;D=cx2-cx1;omega1=1.;omega2=rl/rr;ph1=omega1*tt;ph2=omega2*tt;c=C('14B｜皮带与塔轮：控制什么，改变什么','两个独立实验；换接皮带需停机，切换处重新计时')
 for xx,rad in [(cx1,rl),(cx2,rr)]:c.circle(xx,cy,rad,GRAY,'#e5ebe7');c.circle(xx,cy,85,LIGHT,None,1)
 nx=(rl-rr)/D;ny=math.sqrt(1-nx*nx)
 for sign in [-1,1]:
  p1=(cx1+rl*nx,cy+sign*rl*ny);p2=(cx2+rr*nx,cy+sign*rr*ny);c.line([p1,p2],GRAY,2)
  frac=(tt*.38)%1 if sign<0 else 1-(tt*.38)%1;c.circle(p1[0]+(p2[0]-p1[0])*frac,p1[1]+(p2[1]-p1[1])*frac,4,B,B)
 for xx,ph,mass,col,lab in [(cx1,ph1,4 if stage else 1,B,'甲'),(cx2,ph2,3 if stage else 1,T,'乙')]:
  bx=xx+85*math.cos(ph);by=cy+85*math.sin(ph);c.line([(xx,cy),(bx,by)],col,2);c.circle(bx,by,9,col,col);c.text(bx+10,by-25,lab,20,col,True);force=(mass/4 if stage else (1 if xx==cx1 else omega2**2));c.arrow(bx,by,-20*force*math.cos(ph),-20*force*math.sin(ph),col)
 if stage==0:
  c.text(105,125,'同质量、同轨道半径L',21);c.text(555,125,'右塔轮小，右侧角速度更大',21,T);p='研究角速度：皮带接不同半径塔轮；线速度相同，角速度不同';metrics='左角速度1倍　｜　右角速度'+ff(omega2,2)+'倍　｜　小球轨道半径相同'
 else:
  c.text(105,125,'改用相同半径塔轮，角速度相同',20);c.text(570,125,'甲乙质量比4:3',22,T);c.text(100,375,'相同标定：甲露4格，乙露3格',20);p='研究质量：保持轨道半径和角速度相同，只改变质量';metrics='甲质量 / 乙质量 = 4/3　｜　向心力之比 = 4:3'
 c.footer(p,metrics,'塔轮半径与小球的轨道半径是不同的量；此图简化外形，不补造装置内部结构。',tt,hold);return c,p

def scene15(t,hold=False):
 prep=t<0;z=M.gate(max(0,t));c=C('15｜剪约束绳：a上升，动滑轮与b下降','剪的是a下方固定绳，主连接绳保持完整；光电门局部慢放');sc=300;ya=365-sc*z['sA'];yb=220+sc*z['sB'];cx,cy,rr=330,120,30;c.line([(230,95),(460,95)],GRAY,5);c.circle(cx,cy,rr,GRAY,None,2);c.circle(390,yb,rr,GRAY,None,2)
 c.line([(300,ya-21),(300,120)],B,2);c.line([(cx+rr*math.cos(a),cy-rr*math.sin(a)) for a in np.linspace(math.pi,0,50)],B,2);c.line([(360,120),(360,yb)],B,2);c.line([(390+rr*math.cos(a),yb+rr*math.sin(a)) for a in np.linspace(math.pi,0,50)],B,2);c.line([(420,yb),(420,114)],B,2);c.rect(404,98,32,16,'#e1eae6',T);c.text(445,95,'传感器F',18,T)
 c.block(300,ya,w=54,h=42);c.text(292,ya-15,'a',23,B,True);c.line([(390,yb+30),(390,yb+42)],GRAY,2);c.block(390,yb+63,w=52,h=42,c=A,fill='#f0e5d4');c.text(383,yb+49,'b',23,A,True)
 if prep:c.line([(300,ya+21),(300,418)],A,2);c.text(175,390,'准备剪断此约束绳',16,A)
 else:c.line([(300,405),(300,418)],A,2);c.line([(290,396),(310,406)],RED,2);c.line([(290,406),(310,396)],RED,2)
 yg=365-sc*.5;c.rect(266,yg-10,19,20,'#e3eee9',T);c.rect(315,yg-10,19,20,'#e3eee9',T);c.line([(282,yg),(318,yg)],RED if z['blocked'] else '#bad1cb',2)
 c.line([(273,ya),(327,ya)],INK,3);
 if not prep:c.arrow(300,ya,0,-44,B,'F')
 c.text(80,145,'a上升s',22,B);c.text(80,190,'b下降s/2',22,A);c.text(80,235,'a只接一股绳',19)
 # Local magnification of a thin shutter; gate time is computed from the actual two edges.
 c.rect(590,145,300,235,'#f1f5ef',LIGHT);c.text(615,158,'光电门局部放大',20,T);gy=265;bar=gy-8000*(z['sA']-.5);c.line([(640,gy),(850,gy)],RED if z['blocked'] else T,3)
 if 205<bar<350:c.rect(715,bar-M.D_GATE*8000/2,60,M.D_GATE*8000,INK,INK)
 c.text(615,323,'挡光 '+ff(1000*z['elapsed'],3)+' ms',22,B)
 p='剪断前：系统静止，主绳完整；准备剪a下方固定绳' if prep else 'a正在上升；主绳两端与动滑轮满足绳长约束'
 if M.TIN<=t<=M.TOUT:p='遮光片经过光束：计时；此处专门慢放'
 elif t>M.TOUT:p='遮光片已离开光束：计时结束'
 c.footer(p,'a位移 '+ff(z['sA'],3)+'m　｜　b位移 '+ff(z['sB'],3)+'m　｜　挡光约2.400ms','演示取a加速度1m/s²；主图遮光片加粗便于看见，局部图放大。物理时钟在慢放时仍显示实际秒数。',None if prep else t,hold);return c,p

def scene16(t,hold=False):
 s=20*t-2.5*t*t;v=max(0,20-5*t);c=C('16｜从开始刹车到停止','相等时间的位置标记越来越密；不包含驾驶员反应阶段');c.line([(75,345),(600,345)],GRAY,3);c.car(90+10*s,330)
 for tt in [0,1,2,3,4]:
  xx=90+10*(20*tt-2.5*tt*tt);c.circle(xx,370,4,GRAY,GRAY);c.text(xx-8,385,str(tt)+'s',14,GRAY)
 X,Y=graph(c,665,350,220,170,4,20,'t / s','v / (m/s)');c.line([(X(0),Y(20)),(X(4),Y(0))],GRAY,2,True);c.line([(X(0),Y(20)),(X(t),Y(v))],B,3);c.circle(X(t),Y(v),5,T,T);c.text(100,145,'刹车加速度大小5m/s²',23);c.text(100,195,'速度越来越小，运动方向仍向前',20,T)
 p='仍在向前运动，但越来越慢' if t<4-1e-8 else '4s时停止：刹车距离40m；后续保持静止'
 c.footer(p,'v = '+ff(v,1)+'m/s　｜　从刹车起已走 '+ff(s,2)+'m','v—t图下方三角形面积等于40m；运动停止后不把原来的减速度延长成倒车。',t,hold);return c,p

def scene17(t,hold=False):
 z=M.track(t);c=C('17｜斜面、圆弧、水平面：逐段运动','按首问h=3.75m，以及整题求得的μ、m、R演示');sc=60;bx,by=630,415;R0=75;O=(bx,by-R0);A0=(bx-R0*math.sin(math.pi/3),by-R0/2);start=(435.1442841485013,152.5)
 # Derive the release point rather than use any illustrative independent geometry.
 release=(bx+sc*(-M.RARC*math.sin(math.pi/3)-M.ARC_LENGTH*.5),by-sc*(M.RARC/2+M.HARC))
 c.line([release,A0],A,4);angles=np.linspace(math.pi/3,0,80);c.line([(bx-R0*math.sin(ph),O[1]+R0*math.cos(ph)) for ph in angles],B,4);c.line([(bx,by),(880,by)],B,4);c.line([O,A0],GRAY,1,True);c.line([O,(bx,by)],GRAY,1,True);c.text(A0[0]-30,A0[1]-20,'A',21);c.text(bx+8,by-30,'B',21);c.text(bx+8,O[1]-12,'O',17,GRAY);c.text(550,315,'60°',17,GRAY)
 x=bx+sc*z['x'];y=by-sc*z['y'];angle=math.pi/3 if t<M.TA else (z['phi'] if z['phi'] is not None else 0);c.block(x,y-8,angle=angle,w=21,h=16)
 c.text(75,125,'粗糙斜面：有摩擦',21,A);c.text(75,170,'光滑圆弧：不损失机械能',19,B);c.text(75,215,'水平面：匀速前进',21,T)
 if t>=M.TB-1e-7:
  c.text(90,270,'B点受力回看',18);c.block(200,350,w=26,h=26);c.arrow(200,350,0,-80,B,'支持力20N');c.arrow(200,350,0,16,RED,'重力4N')
 p='到达B点：按圆弧侧计算向心合力' if abs(t-M.TB)<1e-8 else '当前路段：'+z['phase'];c.footer(p,'速率 '+ff(z['v'],3)+'m/s　｜　A比B高R/2　｜　B点需要向上的向心合力','物块尺寸仅用于辨识，轨道几何按60°与R=1.25m绘制；水平面按题设光滑处理。',t,hold);return c,p

def draw_collision_lane(c,z,y,x0=420,sc=140,width=24,wall=True):
 # The contact-edge coordinates preserve visible contact for widened schematic blocks.
 xa=x0+sc*z['xA'];xb=x0+sc*z['xB'];c.line([(x0-290,y+22),(x0+sc*2.75+width+15,y+22)],GRAY,2);c.rect(xa,y-width/2,width,width,'#dceaf0',B);c.rect(xb-width,y-width/2,width,width,'#eee0cd',A)
 if wall:
  xw=x0+sc*2.75+width;c.line([(xw,y-65),(xw,y+22)],GRAY,6)
 if abs(z['vA'])>.01:c.arrow(xa+width/2,y-25,10*z['vA'],0,B)
 if abs(z['vB'])>.01:c.arrow(xb-width/2,y+55,10*z['vB'],0,A)
 return xa,xb

def scene18a(t,hold=False):
 z=M.collision_at(M.COL,t);c=C('18A｜弹开后：撞墙、B先停、互撞、最终停止','第一、二问：初动能总和24J；弹开极短过程与尺寸忽略');xa,xb=draw_collision_lane(c,z,260);c.text(xa+4,215,'A',20,B,True);c.text(xb-23,275,'B',20,A,True)
 tw,tb,tc,tf=[e['t'] for e in M.COL['events']]
 if t<tw:p='刚弹开：A向右，B向左；弹簧已移走'
 elif t<tb:p='A已弹性撞墙，改向左运动；B仍在向左'
 elif t<tc:p='B已经停止；A继续向左追赶B'
 elif t<tf:p='两块已弹性互撞：A向右，B向左，逐渐停止'
 else:p='两块均已停止；最终间距1.25m'
 c.text(95,140,'蓝色A：1kg',21,B);c.text(95,180,'橙色B：3kg',21,A);c.text(680,140,'固定刚性墙',21);c.text(655,182,'初始墙距2.75m',18,GRAY)
 c.line([(130,385),(850,385)],LIGHT,2)
 for tt,label in [(tw,'撞墙'),(tb,'B停'),(tc,'互撞'),(tf,'终止')]:
  xx=130+720*tt/2.3;c.circle(xx,385,5,T if t>=tt else GRAY,T if t>=tt else BG);c.text(xx-17,398,label,14,GRAY)
 c.footer(p,'A位置 '+ff(z['xA'],3)+'m，速度 '+ff(z['vA'],3)+'m/s　｜　B位置 '+ff(z['xB'],3)+'m，速度 '+ff(z['vB'],3)+'m/s','图中色块加宽便于辨认，定量位移按忽略尺寸的题设计算；事件时刻使用碰撞后的速度。',t,hold);return c,p

def scene18b(t,hold=False):
 c=C('18B｜第三问：恰好不碰，临界质量2.10kg','本片初动能总和21J，与前一片24J分开；三组同一物理时钟')
 for i,model in enumerate(M.COL_COMPARE):
  y=165+i*100;z=M.collision_at(model,t);xa,xb=draw_collision_lane(c,z,y,x0=420,sc=110,width=20);mass=model['M'];c.text(50,y-20,'C='+ff(mass,2)+'kg',20,[B,T,RED][i],True)
  collided=any(e['kind']=='互撞' and e['t']<=t for e in model['events'])
  if t>=model['end']-1e-8:
   status='有余隙' if i==0 else '恰好接触停住' if i==1 else '已实际碰撞'
   c.text(745,y-20,status,18,[B,T,RED][i])
  elif collided:c.text(745,y-20,'互撞后运动',18,RED)
  else:c.text(745,y-20,'运动中',18,GRAY)
 p='同样的能量与摩擦，改变C质量，比较是否追上'
 c.footer(p,'蓝块均为A=1kg；橙块为替换后的C；墙距均为2.75m。','大于临界的第三组按真实弹性碰撞继续计算，未用假想的“负间距”代替实际运动。',t,hold);return c,p

# ---------- frame schedules, common palette and matching outputs ----------
def timeline(end,events=(),n=100,extra=None):
 vals=list(np.linspace(0,end,n+1))+list(events)
 if extra is not None:vals+=list(extra)
 vals=sorted(set(round(float(v),12) for v in vals if 0<=v<=end+1e-10));out=[]
 for v in vals:
  pause=8 if any(abs(v-e)<1e-9 for e in events) else 0
  if v==0:pause=max(pause,6)
  if abs(v-end)<1e-9:pause=max(pause,12)
  out.append((v,False));out += [(v,True)]*pause
 return out
CLIPS=[
 dict(id='q01',q=1,title='雨滴与线性阻力',fn=scene01,end=4.,events=[0.,4.],keys=[0.,1.,4.]),
 dict(id='q02',q=2,title='四种下落情境',fn=scene02,end=4.,events=[.98,1.98,2.98,4.],keys=[.65,1.65,2.65,3.98]),
 dict(id='q03',q=3,title='摆球与端点受力',fn=scene03,end=M.PEND_PERIOD,events=[0,M.PEND_PERIOD/4,M.PEND_PERIOD/2,M.PEND_PERIOD],keys=[0,M.PEND_PERIOD/4,M.PEND_PERIOD/2]),
 dict(id='q04',q=4,title='物块匀速上斜面',fn=scene04,end=4.,events=[0,4],keys=[0,2,4]),
 dict(id='q05',q=5,title='课本相对滑动',fn=scene05,end=1.5,events=[0,1.5],keys=[0,.75,1.5]),
 dict(id='q06',q=6,title='卫星圆轨道',fn=scene06,end=1.,events=[0,.25,.5,1],keys=[0,.25,.5]),
 dict(id='q07',q=7,title='定滑轮连接体',fn=scene07,end=.55,events=[0,.55],keys=[0,.35,.55]),
 dict(id='q08',q=8,title='踢球与动量变化',fn=scene08,end=2.5,events=[0,1.5,2.5],keys=[.75,1.5,2.5]),
 dict(id='q09',q=9,title='转盘静摩擦临界',fn=scene09,end=6.,events=[1.99,3.99,6.],keys=[1.2,3.2,5.2]),
 dict(id='q10',q=10,title='平抛与两个方向角',fn=scene10,end=.2,events=[0,.1,.2],keys=[0,.1,.2]),
 dict(id='q11',q=11,title='恒功率启动',fn=scene11,end=M.PTEND,events=[0,M.PTEND],keys=[0,M.PTEND*.3,M.PTEND]),
 dict(id='q12',q=12,title='有阻力的上抛',fn=scene12,end=M.THROW_END,events=[0,M.TUP,M.THROW_END],keys=[M.TUP*.5,M.TUP,M.THROW_END]),
 dict(id='q13',q=13,title='传送带与弹簧三阶段',fn=scene13,end=M.BT3,events=[0,M.BT1,M.BT2,M.BT3],keys=[M.BT1*.65,(M.BT1+M.BT2)/2,M.BT3]),
 dict(id='q14a',q=14,title='弹簧加载与图像',fn=scene14a,end=3.,events=[0,1,2,3],keys=[0,1,3]),
 dict(id='q14b',q=14,title='塔轮与控制变量',fn=scene14b,end=8.,events=[0,3.9,4,8],keys=[.8,3.6,7.5]),
 dict(id='q15',q=15,title='滑轮约束与光电门',fn=scene15,end=M.GATE_END,events=[0,M.TIN,M.TOUT,M.GATE_END],keys=[-1.,1.,M.GATE_END],n=75,extra=np.linspace(.995,1.005,35)),
 dict(id='q16',q=16,title='汽车匀减速刹车',fn=scene16,end=4.,events=[0,4],keys=[0,2,4]),
 dict(id='q17',q=17,title='斜面圆弧水平轨道',fn=scene17,end=M.ARC_END,events=[0,M.TA,M.TB,M.ARC_END],keys=[0,M.TA,M.TB]),
 dict(id='q18a',q=18,title='弹开与弹性碰撞全过程',fn=scene18a,end=M.COL['end'],events=[0]+[e['t'] for e in M.COL['events']],keys=[.5,1.,M.COL['events'][2]['t'],M.COL['end']]),
 dict(id='q18b',q=18,title='恰好不碰的临界对照',fn=scene18b,end=max(z['end'] for z in M.COL_COMPARE)+.05,events=[0,max(z['end'] for z in M.COL_COMPARE)+.05],keys=[0,.8,max(z['end'] for z in M.COL_COMPARE)+.05])]
def palette_image():
 colors=[]
 for h in [B,T,A,RED,INK,GRAY,LIGHT,PURPLE]:
  rgb=tuple(int(h[i:i+2],16) for i in [1,3,5])
  for a in np.linspace(0,1,26):colors.extend(tuple(round(255+(v-255)*a) for v in rgb))
 for k in np.linspace(0,255,48):colors.extend([int(k)]*3)
 p=Image.new('P',(1,1));p.putpalette(colors[:768]);return p
PAL=palette_image()
def key_stamp(cid,t):
 if t<0:return '准备阶段（未计时）  '
 if cid in ['q02','q06','q14a']:return ''
 if cid=='q09':t=t%2 if t<6 else 2.
 if cid=='q14b' and t>=4:t-=4
 return 't='+ff(t,3)+'s  '
def build_clip(spec):
 seq=timeline(spec['end'],spec['events'],spec.get('n',100),spec.get('extra'));
 if spec['id']=='q15':seq=[(-1.,True)]*9+seq
 frames=[];metadata=[]
 vp=R/'video'/f"{spec['id']}.mp4";gp=R/'gifs'/f"{spec['id']}.gif"
 cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(vp)]
 enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 for t,hold in seq:
  canvas,phase=spec['fn'](t,hold);im=canvas.image();enc.stdin.write(im.tobytes());frames.append(im.quantize(palette=PAL,dither=Image.Dither.NONE));metadata.append(dict(t=t,hold=hold,phase=phase))
 # Clear, explicit loop reset: never reverse a physical trajectory to restart.
 reset=C(spec['id'].upper()+'｜本段演示结束','下次循环重新从初始状态开始，不是物体实际倒放返回');reset.text(245,225,'重新开始演示',36,T,True);reset.footer('物理时钟将归零','','GIF循环仅为重复学习；关键帧中的暂停不代表物体处于平衡。',None,True);im=reset.image()
 for _ in range(6):enc.stdin.write(im.tobytes());frames.append(im.quantize(palette=PAL,dither=Image.Dither.NONE))
 enc.stdin.close();err=enc.stderr.read().decode();code=enc.wait();assert code==0,err
 frames[0].save(gp,save_all=True,append_images=frames[1:],duration=100,loop=0,optimize=True,disposal=1)
 # Poster and PDF contact strips come from exactly the same renderer and states.
 keyims=[]
 for idx,t in enumerate(spec['keys']):
  canvas,phase=spec['fn'](t,True);im=canvas.image();keyims.append((im,phase,t));
  if idx==len(spec['keys'])//2:im.save(R/'posters'/f"{spec['id']}.png")
 plates=[]
 for n in range(0,len(keyims),3):
  chunk=keyims[n:n+3];p=Image.new('RGB',(W,len(chunk)*405),'white');pd=ImageDraw.Draw(p)
  pf=ImageFont.truetype(FONT,20,index=2)
  for j,(im,phase,t) in enumerate(chunk):
   p.paste(im.crop((0,88,W,429)),(0,j*405));label=f'{n+j+1:02d}  '+key_stamp(spec['id'],t)+phase
   text='';yy=j*405+347
   for ch in label:
    if pf.getlength(text+ch)>900:pd.text((28,yy),text,font=pf,fill=INK);text=ch;yy+=25
    else:text+=ch
   pd.text((28,yy),text,font=pf,fill=INK)
  name=spec['id']+f'-keyframes-{n//3+1}.png';p.save(R/'plates'/name);plates.append(name)
 result=dict(id=spec['id'],question=spec['q'],title=spec['title'],gif=gp.name,video=vp.name,poster=spec['id']+'.png',plates=plates,physicalEnd=spec['end'],framesPlanned=len(seq)+6,playbackSeconds=(len(seq)+6)/FPS,keyTimes=[float(x) for x in spec['keys']],gifBytes=gp.stat().st_size,mp4Bytes=vp.stat().st_size)
 (R/'qa'/f"{spec['id']}-timeline.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
 print(spec['id'],len(seq)+6,'frames',gp.stat().st_size,'gif bytes',flush=True);return result
if __name__=='__main__':
 selected=sys.argv[1:];existing=[]
 if (R/'manifest.json').exists():existing=json.loads((R/'manifest.json').read_text())['clips']
 chosen=[s for s in CLIPS if not selected or s['id'] in selected];new=[build_clip(s) for s in chosen];mp={x['id']:x for x in existing};mp.update({x['id']:x for x in new});ordered=[mp[s['id']] for s in CLIPS if s['id'] in mp]
 (R/'manifest.json').write_text(json.dumps(dict(version='1.2',width=W,height=H,fps=FPS,clips=ordered),ensure_ascii=False,indent=2));print('done',len(ordered),'clips')
