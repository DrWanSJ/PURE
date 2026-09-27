%% Output initial value set to the model originally

initial_values = fMGG_synthesis();
species_names = fMGG_synthesis('states');
parameter_names = fMGG_synthesis('parameters');
parameter_values = fMGG_synthesis('parametervalues');

%% Read parameter values from csv

data_dir = './dat/';
parameter_file = 'fMGG_synthesis_parameters.csv';

parameter_data = importdata([data_dir parameter_file], ',', 1);
parameter_values = parameter_data.data;

%% Read initial values from from csv

data_dir = './dat/';
initial_values_file = 'fMGG_synthesis_initial_values.csv';

initial_values_data = importdata([data_dir initial_values_file], ',', 1);
initial_values = initial_values_data.data;

%% ODE setting

t=logspace(-4,3,200); %200 time points between 1e-5 and 1e3 sec
non_negative = 1:length(initial_values);
ode_opt = odeset('NonNegative', non_negative,'RelTol', 1e-3, 'AbsTol',1e-9);

%% simulation

model_h = @(t,x)fMGG_synthesis(t, x, parameter_values(:,1));
[t x] = ode15s(model_h, t,initial_values(:,1), ode_opt); 
%% Plot

figure();
loglog(t,x);
axis([10^(-4) 10^3 10^(-10) 10^5]); 