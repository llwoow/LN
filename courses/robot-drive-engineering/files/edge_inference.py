"""LN synthetic RL regression -> ONNX -> actual CPU inference; no device control.

Run in an environment with the supplied requirements-edge.txt.
Training data are generated from a declared fixed-rotor RL equation, not measured.
The exported regression is a deployment exercise, not a foundation robot policy.
"""
import json,math,platform,time
from pathlib import Path
import numpy as np
import onnx
from onnx import helper,TensorProto,numpy_helper
import onnxruntime as ort

def main():
    out=Path(__file__).parent
    rng=np.random.default_rng(2401)
    R,L,Ts=2.0,.004,.0005
    a=math.exp(-R*Ts/L);b=(1-a)/R
    x=np.column_stack([rng.uniform(-1,1,500),rng.uniform(-3,3,500)])
    y=a*x[:,0]+b*x[:,1]+rng.normal(0,.002,500)
    design=np.column_stack([x[:350],np.ones(350)])
    coef=np.linalg.lstsq(design,y[:350],rcond=None)[0]
    w=coef[:2].astype(np.float32).reshape(2,1);bias=coef[2:].astype(np.float32)
    graph=helper.make_graph([helper.make_node('MatMul',['x','W'],['linear']),helper.make_node('Add',['linear','B'],['next_current'])],
        'LN_RL_regression',[helper.make_tensor_value_info('x',TensorProto.FLOAT,['batch',2])],
        [helper.make_tensor_value_info('next_current',TensorProto.FLOAT,['batch',1])],
        [numpy_helper.from_array(w,'W'),numpy_helper.from_array(bias,'B')])
    model=helper.make_model(graph,opset_imports=[helper.make_opsetid('',17)],producer_name='LN synthetic lesson')
    model.ir_version=10;onnx.checker.check_model(model);onnx.save(model,out/'rl_predictor.onnx')
    options=ort.SessionOptions();options.intra_op_num_threads=1;options.inter_op_num_threads=1
    session=ort.InferenceSession(str(out/'rl_predictor.onnx'),sess_options=options,providers=['CPUExecutionProvider'])
    data=x[350:].astype(np.float32)
    actual=session.run(None,{'x':data})[0].ravel();expected=(data@w+bias).ravel()
    maxdiff=float(np.max(np.abs(actual-expected)));assert maxdiff<1e-6
    validation=float(np.sqrt(np.mean((actual-y[350:])**2)))
    changed_R=2.4;new_a=math.exp(-changed_R*Ts/L);new_b=(1-new_a)/changed_R
    changed_truth=new_a*data[:,0]+new_b*data[:,1]
    changed_error=float(np.sqrt(np.mean((actual-changed_truth)**2)))
    one=data[:1]
    for _ in range(100):session.run(None,{'x':one})
    samples=[]
    for _ in range(500):
        t0=time.perf_counter_ns();session.run(None,{'x':one});samples.append(time.perf_counter_ns()-t0)
    report={'kind':'synthetic regression and observed host CPU inference, not a robot or edge-board trial',
        'plant':{'R_ohm':R,'L_H':L,'Ts_s':Ts,'exact_a':a,'exact_b_A_per_V':b},
        'fit':{'train_samples':350,'heldout_samples':150,'a':float(w[0,0]),'b_A_per_V':float(w[1,0]),'bias_A':float(bias[0]),
               'heldout_same_distribution_RMSE_A':validation,'changed_R_ohm':changed_R,'changed_R_RMSE_A':changed_error},
        'onnx_vs_same_coefficients_max_abs_error_A':maxdiff,
        'inference_timing':{'boundary':'session.run on one prepared float32 row; excludes data loading, preprocessing, model loading, network and motor control',
            'warmup':100,'samples':500,'median_us':float(np.median(samples)/1000),'p99_us_linear':float(np.quantile(samples,.99,method='linear')/1000),'max_us':max(samples)/1000},
        'versions':{'python':platform.python_version(),'numpy':np.__version__,'onnx':onnx.__version__,'onnxruntime':ort.__version__,'machine':platform.machine()},
        'limits':['No foundation model or real robot policy was run.','Host timing does not guarantee worst-case latency on any target board.','Synthetic held-out data are not independent physical measurements.']}
    (out/'edge-results.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'inference-timings-ns.json').write_text(json.dumps(samples)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
