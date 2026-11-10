from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as pa
from matplotlib.font_manager import FontProperties
import numpy as np
R=Path(__file__).resolve().parent.parent/'figures';R.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'Noto Sans CJK JP','font.size':10,'axes.unicode_minus':False,'svg.fonttype':'path','mathtext.fontset':'stix','axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#9aabb4','axes.labelcolor':'#334955','text.color':'#203540','xtick.color':'#566b76','ytick.color':'#566b76','figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white'})
B='#205b82';T='#107b79';A='#c1832f';RED='#b04b42';G='#91a0a8'
def save(name,fig):
 fig.savefig(R/(name+'.pdf'),bbox_inches='tight');fig.savefig(R/(name+'.svg'),bbox_inches='tight');fig.savefig(R/(name+'.png'),dpi=160,bbox_inches='tight');plt.close(fig)
def arr(ax,xy,d,label='',color=B,offset=(.03,.03),ls='-'):
 ax.annotate('',xy=(xy[0]+d[0],xy[1]+d[1]),xytext=xy,arrowprops=dict(arrowstyle='-|>',lw=2,color=color,linestyle=ls,mutation_scale=13));ax.text(xy[0]+d[0]+offset[0],xy[1]+d[1]+offset[1],label,color=color)
def clean(ax,xlim,ylim):ax.set_aspect('equal');ax.set_xlim(*xlim);ax.set_ylim(*ylim);ax.axis('off')
# 3
fig,axs=plt.subplots(1,2,figsize=(8,3.1));u=np.array([.5,np.sqrt(3)/2]);p=np.array([-.8,-.7]);g=np.array([0.,-1.]);f1=-np.sqrt(3)/2*u;f2=g-f1
for ax in axs:
 clean(ax,(-1.5,.9),(-1.9,.6));ax.plot([p[0],p[0]+u[0]],[p[1],p[1]+u[1]],color=G,lw=1);ax.scatter(*p,color='#203540',zorder=5,s=30)
arr(axs[0],p,np.sqrt(3)/2*u,'T',B);arr(axs[0],p,g,'mg',RED);axs[0].set_title('真实受力：两个力',loc='left',fontsize=11)
arr(axs[1],p,np.sqrt(3)/2*u,'T',B);arr(axs[1],p,f1,r'$G_1$',A,ls='--');arr(axs[1],p,f2,r'$G_2$',T,ls='--');axs[1].plot([p[0]+f1[0],p[0]+g[0]],[p[1]+f1[1],p[1]+g[1]],ls=':',color=G);axs[1].text(-1.35,.35,r'$\vec G=\vec G_1+\vec G_2$',fontsize=12);axs[1].set_title('计算替换：重力用分力表示',loc='left',fontsize=11);fig.tight_layout();save('q03',fig)
#4
fig,axs=plt.subplots(1,2,figsize=(8,2.8));ax=axs[0];clean(ax,(-.3,4.5),(-.3,2.7));ax.plot([0,3.464,3.464,0],[0,2,0,0],color=G);p=(1.7,.98);ax.add_patch(pa.Rectangle((1.4,.8),.5,.3,angle=30,facecolor='#d9e7ef',edgecolor=B));arr(ax,p,(.85,.49),'F',B);arr(ax,p,(-.57,-.33),'f',A,(-.16,-.04));arr(ax,p,(0,-.85),'mg',RED);arr(ax,p,(-.35,.606),'N',T,(-.2,.06));ax.text(3.6,1,'h=2m');ax.text(.5,-.22,'s=4m');ax.set_title('受力与斜面几何',loc='left',fontsize=11)
axs[1].barh(['重力','摩擦力','外力','合力'],[-20,-20,40,0],color=[RED,A,B,T]);axs[1].axvline(0,color=G,lw=.8);axs[1].set_xlabel('功 / J');axs[1].set_xlim(-30,49);axs[1].invert_yaxis();axs[1].set_title('有符号的功：40−20−20=0',loc='left',fontsize=11);fig.tight_layout();save('q04',fig)
#5
fig,axs=plt.subplots(1,2,figsize=(8,3.2))
for ax in axs:clean(ax,(-1.45,1.55),(-1.45,1.45));ax.add_patch(pa.Rectangle((-.23,-.16),.46,.32,facecolor='#e9eff3',edgecolor=G))
arr(axs[0],(0,0),(0,-1),'mg',RED);arr(axs[0],(0,0),(0,1),'N',B);arr(axs[0],(0,0),(1,0),'F',B);arr(axs[0],(0,0),(-.85,0),'f',A,(-.18,.07));axs[0].set_title('甲：4个力；未给出匀速条件',loc='left',fontsize=11)
arr(axs[1],(0,0),(0,1.1),'N(桌)',B);arr(axs[1],(-.12,0),(0,-.8),'m乙g',RED,(-.4,-.1));arr(axs[1],(.17,0),(0,-1.1),'N(甲)',A);arr(axs[1],(0,0),(.9,0),'f(甲)',A);arr(axs[1],(0,0),(-.9,0),'f(桌)',T,(-.3,.06));axs[1].set_title('乙：5个力；上下摩擦类型不同',loc='left',fontsize=11);fig.tight_layout();save('q05',fig)
#6
fig,ax=plt.subplots(figsize=(6.5,3));clean(ax,(-2.7,3.8),(-1.6,1.6));ax.add_patch(pa.Circle((0,0),1,facecolor='#e0edf0',edgecolor=T));ax.add_patch(pa.Circle((0,0),1.5,fill=False,ls='--',edgecolor=B));ax.scatter([0,1.5],[0,0],color=B);arr(ax,(0,0),(.71,.71),'R',T);ax.annotate('',xy=(1.5,-.5),xytext=(0,-.5),arrowprops=dict(arrowstyle='<->',color=B));ax.text(.5,-.75,'r=R+h');ax.annotate('',xy=(1.5,.25),xytext=(1,.25),arrowprops=dict(arrowstyle='<->',color=A));ax.text(1.07,.48,'h');ax.text(1.85,.6,r'$r=R(1+1/n)$',fontsize=15);ax.text(1.85,-.05,r'$GM/r^2=4\pi^2r/T^2$',fontsize=14);ax.text(1.85,-.7,'引力中的距离取地心到卫星');save('q06',fig)
#7
fig,ax=plt.subplots(figsize=(7,2.8));clean(ax,(-.5,5),(-2,1));ax.plot([-.3,2.55],[0,0],color=G);ax.add_patch(pa.Rectangle((.6,.02),.6,.45,facecolor='#e9eff3',edgecolor=B));ax.add_patch(pa.Circle((2.8,.03),.22,fill=False,edgecolor=G));ax.plot([1.2,2.8],[.25,.25],color=B);ang=np.linspace(np.pi/2,0,40);ax.plot(2.8+.22*np.cos(ang),.03+.22*np.sin(ang),color=B);ax.plot([3.02,3.02],[.03,-.7],color=B);ax.add_patch(pa.Rectangle((2.75,-1.2),.55,.5,facecolor='#e9eff3',edgecolor=A));arr(ax,(1,.3),(.9,0),'T',B);arr(ax,(3,-.9),(0,-.75),r'$3mg/2$',RED);arr(ax,(3,-.9),(0,.30),'T',B);ax.text(.55,.7,'甲：m');ax.text(3.45,-1.1,r'乙：$3m/2$');save('q07',fig)
#8
fig,axs=plt.subplots(1,2,figsize=(8,3));ax=axs[0];clean(ax,(-1.1,1.5),(-1.1,1.5));arr(ax,(-.8,0),(.8,0),r'$\vec v_i$',B,(-.05,.12));arr(ax,(0,0),(0,1),r'$\vec v_f$',T);ax.scatter([0],[0],color=G);ax.text(-.15,-.25,'a');ax.text(-.7,-.6,'踢前后速率相同，方向改变');ax.set_title('把速度方向画成箭头',loc='left',fontsize=11)
ax=axs[1];clean(ax,(-.4,1.7),(-.4,1.7));arr(ax,(0,0),(1,0),r'$\vec p_i$',B);arr(ax,(0,0),(0,1),r'$\vec p_f$',T);arr(ax,(1,0),(-1,1),r'$\Delta\vec p$',A,(.12,.05));ax.text(.1,-.35,r'$J=\sqrt{2}mv,\quad W=0$',fontsize=14);ax.set_title('从初动量箭头尖指向末动量箭头尖',loc='left',fontsize=11);fig.tight_layout();save('q08',fig)
#9
fig,ax=plt.subplots(figsize=(7,3));w=np.linspace(0,1.2,100);ax.plot(w,w*w,label='甲：r=R',color=B,lw=2);ax.plot(w,.5*w*w,label='乙：r=R/2',color=T,lw=2);ax.axhline(.5,color=A,ls='--',label='最大静摩擦 / mg = 0.5');ax.axvline(np.sqrt(.5),color=G,ls=':');ax.scatter([np.sqrt(.5)],[.5],color=RED);ax.set(xlabel=r'角速度 $\omega/\sqrt{g/R}$',ylabel=r'随盘不滑所需摩擦 $f_s/(mg)$',ylim=(0,1.05));ax.legend(frameon=False,fontsize=9,loc='upper left');ax.text(.76,.58,'甲的临界');ax.text(.85,.95,'越过上限：不滑模型失效',color=RED,fontsize=9);fig.tight_layout();save('q09',fig)
#10
fig,axs=plt.subplots(1,2,figsize=(8,3));ts=np.linspace(0,.2,100);axs[0].plot(ts,5*ts**2,color=B);axs[0].invert_yaxis();axs[0].set(xlabel='水平位移 / m',ylabel='向下位移 / m');axs[0].scatter([.1,.2],[.05,.2],color=[T,A]);axs[0].text(.105,.045,'t=0.1s');axs[0].text(.09,.185,'t=0.2s');axs[0].set_title('轨迹：位移角不等于速度角',loc='left',fontsize=11)
ax=axs[1];clean(ax,(-.4,2.1),(-2.6,.8));arr(ax,(0,0),(1,0),r'$v_x=1$',B);arr(ax,(0,0),(0,-2),r'$v_y=2$',A);arr(ax,(0,0),(1,-2),r'$v_f=\sqrt{5}$',T);ax.text(.4,-.6,r'$\theta$');ax.set_title('落地速度分解 / (m/s)',loc='left',fontsize=11);fig.tight_layout();save('q10',fig)
#11 high-school axes, no dimensionless variables on the student figure
fig,ax=plt.subplots(figsize=(7,3));u=np.linspace(0,.995,500);times=20*(-u-np.log1p(-u));velocities=20*u;uend=.95;te=20*(-uend-np.log1p(-uend));mask=times<=te;ax.plot(times,velocities,color=B,lw=2,label='速度增加越来越慢');ax.plot([0,te],[0,20*uend],ls='--',color=A,label='起终点连线');ax.fill_between(times[mask],velocities[mask],20*uend*times[mask]/te,color='#dfebf1');ax.axhline(20,ls=':',color=G);ax.text(48,20.4,'最大速度参考线',fontsize=9);ax.scatter([te],[20*uend],color=T);ax.set(xlabel='时间 / s',ylabel='速度 / (m/s)',ylim=(0,22.8),xlim=(0,88));ax.legend(frameon=False,fontsize=9,loc='lower right');fig.tight_layout();save('q11',fig)
#12
fig,ax=plt.subplots(figsize=(7,2.7));ks=np.linspace(0,.95,100);ax.plot(ks,1/(1+ks),color=B,label=r'$H/H_0=1/(1+k)$');ax.plot(ks,(1-ks)/(1+ks),color=T,label=r'$E_{k,f}/E_{k0}=(1-k)/(1+k)$');ax.set(xlabel='阻力与重力之比 k',ylabel='相对值',ylim=(0,1.08));ax.legend(frameon=False,fontsize=10);fig.tight_layout();save('q12',fig)
#13
fig,axs=plt.subplots(1,2,figsize=(9,3.1));xm=2+np.sqrt(3);x1=np.linspace(0,1,100);x2=np.linspace(1,2,100);x3=np.linspace(2,xm,150);ax=axs[0];ax.plot(x1,1-x1/2,color=B,lw=2);ax.plot([1,2],[0,0],color=T,lw=4);ax.plot(x3,1-x3/2,color=A,lw=2);ax.plot(x2,1-x2/2,color=G,ls='--');ax.plot([1,1],[.5,0],color=G,ls=':');ax.axhline(0,color=G,lw=.7);ax.set(xlabel=r'$x/x_0$',ylabel=r'$a/a_0$',xticks=[0,1,2,xm],xticklabels=['0','1','2',r'$2+\sqrt{3}$']);ax.set_title('实际a—x：中间段是零，不是虚线',loc='left',fontsize=11)
ax=axs[1];ax.plot(x1,2*x1-.5*x1*x1,color=B,lw=2,label='I 追赶');ax.plot([1,2],[1.5,1.5],color=T,lw=2,label='II 随带匀速');ax.plot(x3,1.5-.5*(x3-2)**2,color=A,lw=2,label='III 再次滑动');ax.set(xlabel=r'$x/x_0$',ylabel=r'$v^2/(a_0x_0)$',xticks=[0,1,2,xm],xticklabels=['0','1','2',r'$2+\sqrt{3}$']);ax.legend(frameon=False,fontsize=9);fig.tight_layout();save('q13',fig)
#14
fig,axs=plt.subplots(1,2,figsize=(8,3));ax=axs[0];ax.plot([4,6,8,10],[0,2,4,6],'o-',color=B);xx=np.linspace(10,14,50);ax.plot(xx,6+.9*(xx-10)-.1*(xx-10)**2,color=A);ax.scatter([4],[0],color=T);ax.text(4.3,.35,r'$l_0=4\,cm$');ax.text(6,5,r'$K=100\,N/m$');ax.set(xlabel='总长度 l / cm',ylabel='拉力 F / N',xlim=(0,15),ylim=(0,9));ax.set_title('截距与斜率分别有物理意义',loc='left',fontsize=11)
ax=axs[1];ax.axis('off');rows=[['研究m','同r','同ω','改m'],['研究r','同m','同ω','改r'],['研究ω','同m','同r','改ω']];tab=ax.table(cellText=rows,colLabels=['目标','控制量1','控制量2','改变的量'],cellLoc='center',loc='center');tab.auto_set_font_size(False);tab.set_fontsize(10);tab.scale(1,1.8)
for (r,c),cell in tab.get_celld().items():cell.set_edgecolor('#d8e1e6');cell.set_facecolor('#e8f0f4' if r==0 else 'white')
ax.set_title('控制变量：每次只改变一个量',loc='left',fontsize=11);fig.tight_layout();save('q14',fig)
#15
fig,axs=plt.subplots(1,2,figsize=(8,3));ax=axs[0];clean(ax,(-1.5,1.8),(-1.4,1.7));ax.add_patch(pa.Rectangle((-.3,-.3),.6,.6,facecolor='#e8f0f4',edgecolor=B));arr(ax,(0,0),(0,1.2),'F',B);arr(ax,(0,0),(0,-1),'mg',RED);ax.text(.65,.35,'a端只有一股绳');ax.text(.65,-.15,'传感器读单股张力');ax.text(-1.2,-1.35,r'$Fh-mgh=\frac{1}{2}mv^2$',fontsize=14);ax.set_title('隔离a，避免误写2F',loc='left',fontsize=11)
ax=axs[1];f=np.linspace(1,5,100);ax.plot(f,2*(f-1),color=B);ax.plot([0,1],[-2,0],color=G,ls='--');ax.axhline(0,color=G,lw=.7);ax.axvline(0,color=G,lw=.7);ax.scatter([1],[0],color=T);ax.text(1.12,-.7,r'$F_0=mg$');ax.text(2.1,2,r'$k=2h/m$',rotation=35);ax.text(.1,-2.25,r'$-2gh$');ax.set(xlabel='拉力 F',ylabel=r'$v^2$',ylim=(-2.7,8.7));ax.set_title('横截距与纵截距不要混淆',loc='left',fontsize=11);fig.tight_layout();save('q15',fig)
#16
fig,ax=plt.subplots(figsize=(7,2.7));ax.plot([0,4],[20,0],color=B,lw=2);ax.fill_between([0,4],[20,0],color='#deebf2');ax.text(1,5,'面积 = 40m');ax.set(xlabel='刹车时间 / s',ylabel='速度 / (m/s)',xlim=(0,4.5),ylim=(0,23),xticks=[0,1,2,3,4]);ax.text(2,16,r'$a_x=-5\,m/s^2$');fig.tight_layout();save('q16',fig)
#17
fig,axs=plt.subplots(1,2,figsize=(8,3.2));ax=axs[0];R0=1.4;phi=np.linspace(-150,-90,100)*np.pi/180;cx=0;cy=R0;xx=R0*np.cos(phi);yy=cy+R0*np.sin(phi);AA=np.array([xx[0],yy[0]]);BB=np.array([0,0]);top=AA+np.array([-.7,1.212]);ax.plot([top[0],AA[0]],[top[1],AA[1]],color=A,lw=2);ax.plot(xx,yy,color=B,lw=2);ax.plot([0,1.3],[0,0],color=B,lw=2);ax.plot([0,AA[0]],[cy,AA[1]],ls=':',color=G);ax.plot([0,0],[cy,0],ls=':',color=G);ax.scatter([AA[0],0,0],[AA[1],0,cy],color=B);ax.text(AA[0]-.2,AA[1]-.15,'A');ax.text(.1,-.15,'B');ax.text(.1,cy,'O');ax.annotate('',xy=(.6,AA[1]),xytext=(.6,0),arrowprops=dict(arrowstyle='<->',color=T));ax.text(.72,.3,'R/2');ax.text(-.42,1.03,'60°');clean(ax,(-2.2,1.5),(-.4,2.5));ax.set_title('切线几何：斜面60°，A高于B为R/2',loc='left',fontsize=11)
ax=axs[1];h=np.linspace(0,4,80);ax.plot(h,8+3.2*h,color=B,lw=2);ax.scatter([0,2.5],[8,16],color=T);ax.plot([2.5,2.5,0],[0,16,16],ls=':',color=G);ax.text(.2,8.5,'截距 2mg=8N');ax.text(.7,18,'斜率 mg/R=3.2N/m');ax.set(xlabel='释放高度 h / m',ylabel='对轨道压力 F / N',ylim=(0,23));fig.tight_layout();save('q17',fig)
#18 exact piecewise paths
sq=np.sqrt(10);tc=3-sq/2;tf=tc+sq/4
def pos(t):
 if t<=.5:Apos=6*t-t*t
 elif t<=tc:Apos=2.75-5*(t-.5)+(t-.5)**2
 elif t<=tf:Apos=-1+sq/2*(t-tc)-(t-tc)**2
 else:Apos=-3/8
 if t<=1:Bpos=-2*t+t*t
 elif t<=tc:Bpos=-1
 elif t<=tf:Bpos=-1-sq/2*(t-tc)+(t-tc)**2
 else:Bpos=-13/8
 return Apos,Bpos
fig,axs=plt.subplots(1,2,figsize=(9,3.5));tt=np.linspace(0,tf+.3,600);p=np.array([pos(t) for t in tt]);ax=axs[0];ax.plot(tt,p[:,0],color=B,label='A');ax.plot(tt,p[:,1],color=A,label='B');ax.axhline(2.75,color=G,ls='--',label='台阶墙');
for t,txt in [(.5,'撞墙'),(1,'B停'),(tc,'互撞'),(tf,'终止')]:ax.axvline(t,color=G,ls=':',lw=.7);ax.text(t,3.05,txt,fontsize=8,rotation=45)
ax.set(xlabel='时间 / s',ylabel='位置 x / m',ylim=(-2,3.8));ax.legend(frameon=False,fontsize=9,loc='lower left');ax.set_title('按事件连接轨迹，碰撞时位置连续',loc='left',fontsize=11)
ax=axs[1];rat=np.linspace(1.05,3,150);gap=5.5-10.5*(1-1/rat);ax.plot(rat,gap,color=T);ax.axhline(0,color=G,lw=.8);ax.scatter([2.1],[0],color=RED);ax.text(2.15,.4,'M=2.1kg');ax.fill_between(rat,0,gap,where=gap<0,color='#f1dedb');ax.text(2.3,-1.7,'负间距表示假想轨迹穿越\n实际必已互撞',fontsize=9,color=RED);ax.set(xlabel='第三问C质量 / kg',ylabel='假设不互撞时的最终间距 / m');ax.set_title('临界：最小间距恰为0',loc='left',fontsize=11);fig.tight_layout();save('q18',fig)
print('figures',len(list(R.glob('*.pdf'))))
