"""Recompute explicitly hypothetical transformer examples; no hardware data."""
import cmath
import json
import math
from pathlib import Path

def compute():
    R=.2;X=math.sqrt(.21);I=10;E=100
    A=I*(R*.8+X*.6);B=I*(X*.8-R*.6)
    Z1=Z2=.2+.4j;E1=100;E2=101;load=20
    i1=(Z2*load+E1-E2)/(Z1+Z2);i2=load-i1
    output=E1-Z1*i1
    node=100/(1+.01+1/9);out_i=node/9;in_i=out_i+node/100
    t_loss=out_i**2*(8+1)+in_i**2+node**2/100
    omega=2*math.pi*50;ratio=10;tau=ratio/omega;angle=math.atan(ratio);peak=math.sqrt(2)*2000
    def current(t):return peak*(math.sin(omega*t-angle)+math.sin(angle)*math.exp(-t/tau))
    def derivative(t):return peak*(omega*math.cos(omega*t-angle)-math.sin(angle)/tau*math.exp(-t/tau))
    lo=.008;hi=.011
    for _ in range(70):
        mid=(lo+hi)/2
        if derivative(mid)>0:lo=mid
        else:hi=mid
    when=(lo+hi)/2
    three_node=100/(1+1/9+1/20);three_i2=three_node/9;three_i3=three_node/20;three_i1=three_i2+three_i3
    return {
        'scope':'hypothetical model checks, not measurements or hardware validation',
        'T_resistive':{'E_V':node,'I2_A':out_i,'I1_A':in_i,'U2_V':8*out_i,'power_residual_W':100*in_i-t_loss},
        'test_parameters':{'Rc_LV_ohm':1000,'Xm_LV_ohm':100/math.sqrt(.2**2-.1**2),'Zk_HV_ohm':50,'Rk_HV_ohm':20,'Xk_HV_ohm':math.sqrt(50**2-20**2)},
        'regulation':{'A_V':A,'B_V':B,'approx_U2_V':E-A,'series_U2_V':math.sqrt(E**2-B**2)-A,'leading_approx_percent':I*(R*.8-X*.6)},
        'efficiency':{'rated':800/(800+10+20),'beta_best':math.sqrt(10/20)},
        'parallel':{'I1_re_im_A':[i1.real,i1.imag],'I2_re_im_A':[i2.real,i2.imag],'I1_abs_A':abs(i1),'I2_abs_A':abs(i2),'kcl_abs_A':abs(i1+i2-load),'bus_match_V':abs(output-(E2-Z2*i2))},
        'neutral':{'equal_R_load_V':math.sqrt(3)*230/2,'larger_R_load_V':.9*math.sqrt(3)*230},
        'three_winding':{'pair_x_pu':[.10,.04,.02],'star_x_pu':[.06,.04,-.02],'restricted_matrix':[[.04,-.02],[-.02,.02]],'determinant':.04*.02-.02**2,'example_quadratic':.06+.04*.25-.02*.25},
        'three_winding_loaded':{'E_V':three_node,'I2_A':three_i2,'I3_A':three_i3,'U2_V':8*three_i2,'U3_V':18*three_i3,'power_residual_W':100*three_i1-(three_i1**2+9*three_i2**2+20*three_i3**2)},
        'autotransformer':{'original_I_H_A':1000/220,'original_I_L_A':1000/22,'add_S_VA':242*1000/22,'subtract_S_VA':198*1000/22,'add_common_A':50-1000/22,'subtract_common_A':9000/220-1000/22},
        'transients':{'inrush_flux_half_cycle_Wb':.003+2*.01,'short_tau_s':tau,'first_peak_s':when,'first_peak_A':current(when),'half_cycle_A':current(.01),'initial_A':current(0)},
        'burden':{'CT_VA':25*.18,'CT_longer_VA':25*.30,'VT_I_A':5/100,'VT_ohm':100**2/5}}

if __name__=='__main__':
    results=compute();Path(__file__).with_name('results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print(json.dumps(results,ensure_ascii=False))
