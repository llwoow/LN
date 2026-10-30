"""Original paper-model checks; no real motor or material measurement claimed."""
import json
from pathlib import Path
import numpy as np
import control as ct
import magpylib as magpy
from scipy.integrate import trapezoid
# DC armature current i and speed w, voltage v and resisting torque TL.
R,L,k,J,b=1.0,0.02,0.5,0.02,0.01
A=np.array([[-R/L,-k/L],[k/J,-b/J]])
B=np.array([[1/L,0],[0,-1/J]])
system=ct.ss(A,B,np.eye(2),np.zeros((2,2)))
t=np.linspace(0,4,40001);u=np.vstack([np.full(t.size,24.0),np.full(t.size,2.0)])
y=ct.forced_response(system,t,u).outputs
i,w=y
xss=-np.linalg.solve(A,B@u[:,0])
energy_input=trapezoid(24*i,t)
energy_loss=trapezoid(R*i*i+b*w*w+2*w,t)
stored=(L*i[-1]**2+J*w[-1]**2)/2
# Magnetic loop: compare Biot-Savart on-axis closed form with library.
I,r=2.,0.03
loop=magpy.current.Circle(current=I,diameter=2*r)
z=np.array([0.,0.01,0.03,0.1]);points=np.column_stack([0*z,0*z,z])
Bnum=loop.getB(points)
Bexact=4*np.pi*1e-7*I*r*r/(2*(r*r+z*z)**1.5)
# Current reversal and double-current linearity are model-based checks.
loop.current=-I;Brev=loop.getB(points)
loop.current=2*I;Bdouble=loop.getB(points)
results={
 'control_version':ct.__version__,'magpylib_version':magpy.__version__,
 'dc_model':{'assumed_parameters':{'R_ohm':R,'L_H':L,'k_SI':k,'J_kg_m2':J,'b_Nm_s_per_rad':b,'V_V':24,'load_torque_Nm':2},'state_order':['armature_current_A','angular_velocity_rad_s'],'final_state':y[:,-1].tolist(),'analytic_steady_state':xss.tolist(),'max_steady_error':float(np.max(np.abs(y[:,-1]-xss))),'input_energy_J':float(energy_input),'loss_plus_load_J':float(energy_loss),'stored_energy_J':float(stored),'energy_balance_residual_J':float(energy_input-energy_loss-stored)},
 'field_model':{'circle_current_A':I,'radius_m':r,'axis_z_m':z.tolist(),'computed_Bz_T':Bnum[:,2].tolist(),'closed_form_Bz_T':Bexact.tolist(),'max_abs_error_T':float(np.max(np.abs(Bnum[:,2]-Bexact))),'current_reversal_max_error_T':float(np.max(np.abs(Brev+Bnum))),'double_current_max_error_T':float(np.max(np.abs(Bdouble-2*Bnum)))},
 'limits':['Both datasets are generated from declared mathematical models, not measured hardware.','The linear motor omits saturation, brush switching, current limit and heating.','The current loop is a prescribed free-space source; no nonlinear iron response was solved.','No FEMM, OpenModelica or SysId executable was run.']}
assert results['dc_model']['max_steady_error']<1e-7
assert abs(results['dc_model']['energy_balance_residual_J'])<1e-3
assert results['field_model']['max_abs_error_T']<1e-12
Path(__file__).with_name('engineering-check-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
