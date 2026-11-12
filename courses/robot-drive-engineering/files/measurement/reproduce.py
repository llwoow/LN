"""Original LN calculation checks; synthetic inputs, no acquisition hardware."""
from pathlib import Path
import json,math

def calculate():
    ref,n,shunt,gain,offset=3.3,12,.005,20,1.65
    step=ref/2**n/(shunt*gain)
    # Half-LSB boundary at end of acquisition after a worst-case full-scale step.
    req,ch=10000,10e-12
    acquisition=(n+1)*math.log(2)*req*ch
    fs=20000; times=[k/fs for k in range(100)]
    alias=max(abs(math.cos(2*math.pi*19000*t)-math.cos(2*math.pi*1000*t)) for t in times)
    source,probe,cp=100000,1000000,15e-12
    parallel=source*probe/(source+probe)
    report={'evidence':'synthetic model calculations, not measured sensor accuracy',
      'current_step_A':step,'quantization_half_step_A':step/2,
      'current_output_V':[(i,offset+i*shunt*gain) for i in [-10,0,10]],
      'shunt_power_at_10A_W':10**2*shunt,
      'first_order_worst_case_bound_A':10*(.005+.002)+25e-6/shunt+.001/(shunt*gain)+step/2,
      'cm_input_error_V_80dB_12V':12/10**(80/20),
      'cm_current_error_A':12/10**4/shunt,
      'acquisition_half_LSB_s':acquisition,
      'alias_19k_1k_max_sample_difference':alias,
      'loaded_probe_dc_ratio':probe/(source+probe),
      'loaded_probe_pole_Hz':1/(2*math.pi*parallel*cp)}
    assert alias<1e-10
    assert math.isclose(step,.008056640625)
    assert math.isclose(acquisition,.9010913347279289e-6)
    return report
if __name__=='__main__':
    result=calculate()
    (Path(__file__).parent/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
