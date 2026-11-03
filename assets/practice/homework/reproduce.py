"""Recompute the stated textbook exercise models. Python standard library only.
No hardware data are measured. The original PDF's conflicting book answers stay separate.
"""
import cmath
import json
import math
from pathlib import Path

def phasor(z):return {'real':z.real,'imag':z.imag,'magnitude':abs(z),'angle_deg':math.degrees(cmath.phase(z))}
def compute():
    k=876/260;z1=complex(2.19,15.4);z2=complex(.15,.964);zm=complex(1250,12600)
    u2=complex(6000,0);i2=complex(144,-108)
    # Solve on the high side, independently of the low-side sequence in the page.
    u2h=k*u2;i2h=i2/k;z2h=k*k*z2;e1=u2h+z2h*i2h;im=e1/zm;i1=i2h+im;u1=e1+z1*i1
    input_power=(u1*i1.conjugate()).real;output_power=(u2*i2.conjugate()).real
    copper1=abs(i1)**2*z1.real;copper2=abs(i2)**2*z2.real;core=abs(im)**2*zm.real
    us=e1+z1*i2h
    r_m=4900/25;x_m=math.sqrt((10000/5)**2-r_m**2)
    z_k=520/100;r_k=14000/100**2;x_k=math.sqrt(z_k*z_k-r_k*r_k)
    beta=math.sqrt(4900/14000);pmax=beta*1e6*.8
    zc1=.05*3050**2/(5600000/3);zc2=.055*3000**2/(3200000/3);ic=50/(zc1+zc2)
    weights=[180/.07,320/.065];shares=[400*w/sum(weights) for w in weights];ratios=[shares[0]/180,shares[1]/320]
    max_s1=320*weights[0]/weights[1];line1=5e6/(math.sqrt(3)*1e4);line2=5e6/(math.sqrt(3)*6300)
    return {
      'scope':'Arithmetic and consistency checks for the declared idealized exercise models, not real equipment validation.',
      'q2_2':{'flux_ratio':60/50,'leakage_reactance_ratio':50/60,'empirical_iron_loss_ratio':(50/60)**(-.7)},
      'q2_17':{'primary_line_A':line1,'secondary_line_A':line2,'primary_phase_V':1e4/math.sqrt(3),'secondary_phase_A':line2/math.sqrt(3),'primary_three_phase_VA':3*(1e4/math.sqrt(3))*line1,'secondary_three_phase_VA':3*6300*(line2/math.sqrt(3))},
      'q2_19':{'ratio':k,'ratio_squared':k*k,'secondary_impedance_on_HV_ohm':phasor(z2h),'E2_V':phasor(e1/k),'magnetizing_current_on_LV_A':phasor(im*k),'I1_A':phasor(i1),'U1_V':phasor(u1),'I1_series_only_A':phasor(i2h),'U1_series_only_V':phasor(us),'input_W':input_power,'output_W':output_power,'primary_copper_W':copper1,'secondary_copper_W':copper2,'core_W':core,'power_balance_residual_W':input_power-output_power-copper1-copper2-core,'magnetizing_node_residual_A':abs(i1-i2h-im)},
      'q2_20':{'HV_line_angle_deg':30,'LV_line_angle_a_deg':180,'LV_line_angle_b_deg':180,'LV_lag_mod360_deg':(30-180)%360,'clock_group':((30-180)%360)/30},
      'q2_22':{'series_Rm_ohm':r_m,'series_Xm_ohm':x_m,'parallel_Rfe_ohm':10000**2/4900,'Rk_ohm':r_k,'Xk_ohm':x_k,'each_referred_R_ohm':r_k/2,'each_referred_X_ohm':x_k/2,'base_ohm':100,'regulation_percent':100*(r_k/100*.8+x_k/100*.6),'rated_efficiency_percent':100*800000/(800000+4900+14000),'beta_max':beta,'load_at_max_efficiency_VA':beta*1e6,'secondary_current_at_max_efficiency_A':beta*1e6/6300,'max_output_W':pmax,'max_efficiency_percent':100*pmax/(pmax+9800),'loss_equality_residual_W':beta*beta*14000-4900},
      'q2_25':{'secondary_phase_Z1_ohm':zc1,'secondary_phase_Z2_ohm':zc2,'secondary_phase_current_A':ic,'machine1_primary_phase_A':ic*3050/(6000/math.sqrt(3)),'machine2_primary_phase_A':ic*3000/(6000/math.sqrt(3)),'loop_voltage_residual_V':ic*(zc1+zc2)-50,'book_secondary_phase_current_A':68.79,'loop_impedance_required_by_book_ohm':50/68.79},
      'q2_26':{'machine1_kVA':shares[0],'machine2_kVA':shares[1],'machine1_load_ratio':ratios[0],'machine2_load_ratio':ratios[1],'machine1_at_limit_kVA':max_s1,'maximum_total_kVA':max_s1+320,'primary_of_distribution_sum_residual_kVA':sum(shares)-400,'machine1_secondary_rated_line_A':180/(math.sqrt(3)*.4)}}

if __name__=='__main__':
    data=compute();path=Path(__file__).with_name('results.json');path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(json.dumps(data,ensure_ascii=False,indent=2))
