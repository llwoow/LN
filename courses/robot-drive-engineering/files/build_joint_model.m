% LN original continuous average model. MATLAB/Simulink has NOT been run here.
% Requires a local licensed MATLAB + Simulink. This builds an OPEN LOOP model,
% not a DSP/FOC controller, code-generation configuration or hardware model.
R=2; L=.004; Kt=.05; Ke=.05; J=2e-4; b=1e-4;
A=[-R/L,-Ke/L,0;Kt/J,-b/J,0;0,1,0];
B=[1/L,0;0,-1/J;0,0]; C=eye(3); D=zeros(3,2);
name='ln_joint_average';
if bdIsLoaded(name), error('Close the existing model before building.'); end
if exist([name '.slx'],'file'), error('Model file already exists; choose a clean folder.'); end
new_system(name);
set_param(name,'SolverType','Fixed-step','Solver','ode4','FixedStep','2e-5','StopTime','1');
add_block('simulink/Sources/Step',[name '/Voltage'],'Time','0','Before','0','After','12','Position',[30 40 70 70]);
add_block('simulink/Sources/Constant',[name '/LoadTorque'],'Value','0','Position',[30 110 70 140]);
add_block('simulink/Signal Routing/Mux',[name '/Inputs'],'Inputs','2','Position',[130 45 135 135]);
add_block('simulink/Continuous/State-Space',[name '/Plant'],'A',mat2str(A,17),'B',mat2str(B,17),'C',mat2str(C),'D',mat2str(D),'X0','[0;0;0]','Position',[220 60 350 120]);
add_block('simulink/Sinks/To Workspace',[name '/States'],'VariableName','ln_states','SaveFormat','Timeseries','Position',[430 70 530 110]);
add_line(name,'Voltage/1','Inputs/1'); add_line(name,'LoadTorque/1','Inputs/2');
add_line(name,'Inputs/1','Plant/1'); add_line(name,'Plant/1','States/1');
save_system(name); open_system(name);
% Run manually: result=sim(name); states=result.get('ln_states');
% Output columns: current A, motor speed rad/s, motor angle rad.
% Initial states: zero. Inputs: voltage V, opposing load torque N*m.
% Compare the final speed at 1s with Python's approx. 221.98 rad/s.
% Halve FixedStep while retaining the same inputs and compare the trajectory.
