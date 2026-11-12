#!/usr/bin/env python3
"""Original LN teaching-model calculations. No board is connected or tested.

Run: python power_checks.py --output power-results.json
A forced-synchronous ideal buck is integrated by RK4; transistor/driver losses
are separate first-order estimates, not a validated device electrothermal model.
"""
import argparse,csv,json,math
from pathlib import Path

def rk4(x,dt,u,vin,L,C,R):
 def f(z):return ((u*vin-z[1])/L,(z[0]-z[1]/R)/C)
 k1=f(x);k2=f([x[j]+dt*k1[j]/2 for j in range(2)]);k3=f([x[j]+dt*k2[j]/2 for j in range(2)]);k4=f([x[j]+dt*k3[j] for j in range(2)])
 return tuple(x[j]+dt*(k1[j]+2*k2[j]+2*k3[j]+k4[j])/6 for j in range(2))

def calculate():
 vin,vo,fs,L,C,R,D=24.,12.,1e5,100e-6,100e-6,6.,.5
 ripple=(vin-vo)*D/(fs*L)
 # 200 switching periods after settling; fixed duty, no closed-loop controller.
 steps=100;dt=1/fs/steps;x=(0.,0.);samples=[]
 for n in range(200000):
  phase=n%steps;u=1. if phase<50 else 0.
  x=rk4(x,dt,u,vin,L,C,R)
  if n>=199900:samples.append(x)
 numerical={'i_average_A':sum(z[0] for z in samples)/len(samples),'v_average_V':sum(z[1] for z in samples)/len(samples),'i_pp_A':max(z[0] for z in samples)-min(z[0] for z in samples),'v_pp_V':max(z[1] for z in samples)-min(z[1] for z in samples),'dt_s':dt,'cycles':2000}
 assert abs(numerical['v_average_V']-vo)<.01
 assert abs(numerical['i_pp_A']-ripple)<.005
 assert abs(numerical['v_pp_V']-ripple/(8*fs*C))<.0005
 qg,qgd,vgs,fs_gate=20e-9,8e-9,10.,2e4
 charge=qg+.2e-3*40e-6+1e-9
 t1=math.sqrt(3)*10/24*50e-6*math.sin(math.pi/6);t2=t1;t0=50e-6-t1-t2
 da=(t1+t2+t0/2)/50e-6;db=(t2+t0/2)/50e-6;dc=(t0/2)/50e-6
 neutral=24*(da+db+dc)/3
 phasev=[24*d-neutral for d in [da,db,dc]]
 alpha=(2*phasev[0]-phasev[1]-phasev[2])/3;beta=(phasev[1]-phasev[2])/math.sqrt(3)
 assert abs(alpha-10*math.cos(math.pi/6))<1e-10 and abs(beta-5)<1e-10
 return {'conditions':'All input values are teaching assumptions; no hardware measurements.',
 'gate':{'average_gate_current_A':qg*fs_gate,'miller_current_A':qgd/40e-9,'gate_supply_power_W':qg*vgs*fs_gate,'bootstrap_charge_C':charge,'bootstrap_Cmin_F':charge/.25,'bootstrap_drop_at_220nF_V':charge/220e-9,'conduction_at_on_5A_D_half_R10mohm_W':5**2*.010*.5,'switching_overlap_24V_5A_100ns_20kHz_W':.5*24*5*100e-9*2e4},
 'buck':{'D':D,'i_pp_A':ripple,'i_peak_A':vo/R+ripple/2,'i_min_A':vo/R-ripple/2,'capacitor_pp_V':ripple/(8*fs*C),'ESR_pp_V':.020*ripple,'component_ripple_sum_bound_V':ripple/(8*fs*C)+.020*ripple,'i_rms2_A2':(vo/R)**2+ripple**2/12,'inductor_copper_W':.1*((vo/R)**2+ripple**2/12),'lightload_boundary_A_for_nonnegative_current':ripple/2,'f0_Hz':1/(2*math.pi*math.sqrt(L*C)),'numerical':numerical},
 'inverter':{'pole_100_V':[24,0,0],'phase_100_V':[16,-8,-8],'Vref_V':10,'theta_deg':30,'T1_s':t1,'T2_s':t2,'T0_s':t0,'duties':[da,db,dc],'phase_average_V':phasev,'alpha_V':alpha,'beta_V':beta,'linear_circle_limit_V':24/math.sqrt(3),'deadtime_pole_error_magnitude_V':24*.5e-6/50e-6,'opposite_current_line_error_magnitude_V':2*24*.5e-6/50e-6},
 'limits':['Ideal forced-synchronous buck allows negative current during startup; it is not a diode-emulation DCM solver.','Output ripple excludes ESR in the numerical model; ESR contribution is reported separately.','Loss terms omit reverse recovery, output capacitance, magnetic core, temperature dependence and PCB parasitics.','Sampling, controller stability, device limits and real hardware are not validated by these calculations.']}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args();d=calculate();s=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
 if args.output:args.output.write_text(s)
 print(s)
if __name__=='__main__':main()
