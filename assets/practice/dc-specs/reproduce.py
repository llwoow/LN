"""Original LN model check using published motor specifications, not a hardware test.
Run beside specification.json: python reproduce.py
Dependencies: numpy, scipy, control==0.10.2, matplotlib.
Outputs separate catalogue facts, calibrated assumptions, simulations and residuals.
"""
from pathlib import Path
import csv
import json
import math
import numpy as np
import control as ct
from scipy.integrate import trapezoid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
s = json.loads((ROOT/'specification.json').read_text())
k = s['torque_constant_Nm_per_A']  # impose Ke=Kt in coherent SI units
w0 = s['no_load_rpm'] * 2 * math.pi / 60
tau0 = k * s['no_load_current_A']

def steady(load, alpha=1., resistance_factor=1., calibrate_offset=False):
    """Positive-speed branch only. alpha splits one observed loss budget."""
    resistance = s['terminal_resistance_ohm'] * resistance_factor
    constant_loss = alpha * tau0
    viscous_loss = (1-alpha) * tau0 / w0
    offset = (s['voltage_V'] - resistance*s['no_load_current_A'] - k*w0) if calibrate_offset else 0.
    speed = (s['voltage_V'] - offset - resistance*(load+constant_loss)/k) / (k+resistance*viscous_loss/k)
    current = (load+constant_loss+viscous_loss*speed)/k
    return {'rpm': speed*60/(2*math.pi), 'current_A': current, 'effective_offset_V': offset,
            'b_Nm_s_per_rad':viscous_loss, 'constant_loss_Nm':constant_loss}

baseline = steady(s['nominal_torque_Nm'])
calibrated = steady(s['nominal_torque_Nm'], calibrate_offset=True)
comparison = {
    'fact_type':s['sourceType'], 'control_version':ct.__version__,
    'nominal_catalogue':{'rpm':s['nominal_rpm'], 'current_A':s['nominal_current_A']},
    'constant_friction_baseline_prediction':baseline,
    'baseline_speed_error_percent':100*(baseline['rpm']/s['nominal_rpm']-1),
    'offset_calibrated_at_no_load_prediction':calibrated,
    'calibrated_speed_error_percent':100*(calibrated['rpm']/s['nominal_rpm']-1),
    'interpretation':'Offset is fitted to no-load data, not independently validated or identified as physical brush drop. Different loss partitions can fit one no-load point.',
    'assumptions':['constant SI Ke=Kt','positive rotation','fixed resistance and excitation','no PWM, commutation, thermal state or current limit']
}

# Separate dynamic candidate: all no-load loss assigned to viscous damping.
# This is a different assumption from the steady default and is labelled explicitly.
R,L,J = s['terminal_resistance_ohm'],s['terminal_inductance_H'],s['rotor_inertia_kg_m2']
b=tau0/w0
A=np.array([[-R/L,-k/L],[k/J,-b/J]])
B=np.array([[1/L,0],[0,-1/J]])
system=ct.ss(A,B,np.eye(2),np.zeros((2,2)))
t=np.linspace(0,.15,30001)
load=np.where(t>=.05,s['nominal_torque_Nm'],0.)
inputs=np.vstack([np.full(t.size,s['voltage_V']),load])
i,w=ct.forced_response(system,t,inputs).outputs
input_energy=trapezoid(s['voltage_V']*i,t)
loss_and_load=trapezoid(R*i*i+b*w*w+load*w,t)
stored=.5*L*i[-1]**2+.5*J*w[-1]**2
residual=input_energy-loss_and_load-stored
comparison['dynamic_viscous_candidate']={
    'description':'Simulation only, not measured. 15 V step; load becomes 0.0205 Nm at 0.05 s; no hardware current limit.',
    'last_rpm':float(w[-1]*60/(2*math.pi)), 'last_current_A':float(i[-1]),
    'peak_current_A':float(max(i)), 'input_energy_J':float(input_energy),
    'loss_and_load_energy_J':float(loss_and_load), 'stored_energy_J':float(stored),
    'energy_residual_J':float(residual)
}
assert abs(residual)<1e-4
assert abs(baseline['rpm']-s['nominal_rpm'])>1  # preserve mismatch; do not pretend a perfect fit
assert abs(steady(0,calibrate_offset=True)['rpm']-s['no_load_rpm'])<1e-8
(ROOT/'results.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n')
with (ROOT/'simulation.csv').open('w',newline='') as f:
    writer=csv.writer(f);writer.writerow(['time_s','voltage_V','load_Nm','sim_current_A','sim_rpm'])
    writer.writerows(zip(t[::30],inputs[0,::30],load[::30],i[::30],w[::30]*60/(2*math.pi)))
torques=np.linspace(0,.03,61)
fig,ax=plt.subplots(figsize=(7,4.2))
ax.plot(torques*1000,[steady(x)['rpm'] for x in torques],label='Model: constant loss, no offset')
ax.plot(torques*1000,[steady(x,calibrate_offset=True)['rpm'] for x in torques],label='Offset fitted at no-load only')
ax.scatter([0,s['nominal_torque_Nm']*1000],[s['no_load_rpm'],s['nominal_rpm']],color='black',marker='x',s=60,label='Published catalogue points')
ax.set(xlabel='Load torque (mNm)',ylabel='Speed (rpm)',title='Catalogue facts vs declared candidate models')
ax.legend(fontsize=8);ax.grid(alpha=.25);fig.tight_layout();fig.savefig(ROOT/'comparison.svg');plt.close(fig)
print(json.dumps(comparison,ensure_ascii=False,indent=2))
