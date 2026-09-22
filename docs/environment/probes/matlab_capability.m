function matlab_capability()
% Inventory product versions and test explicitly named license features.
fprintf('MATLAB_RUNTIME=%s\nRELEASE=%s\nARCH=%s\n', version, version('-release'), computer);
v = ver;
for i = 1:numel(v)
    fprintf('PRODUCT | %s | %s | %s\n', v(i).Name, v(i).Version, v(i).Release);
end
features = {'MATLAB', 'Symbolic_Toolbox', 'Optimization_Toolbox', 'SimBiology'};
functions = {'ode15s', 'syms', 'lsqnonlin', 'sbiomodel'};
for i = 1:numel(features)
    fprintf('LICENSE_TEST | %s | %d\n', features{i}, license('test', features{i}));
    fprintf('FUNCTION | %s | %s\n', functions{i}, which(functions{i}));
end
end
