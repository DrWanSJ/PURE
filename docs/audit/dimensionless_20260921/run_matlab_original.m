% Execute the unmodified audit-entry version in scratch (it writes a file).
root = fileparts(fileparts(fileparts(fileparts(mfilename('fullpath')))));
target = fullfile(root, 'results', 'runs', 'dimensionless_audit_20260921', ...
    'original', 'derive_dimensionless.m');
fprintf('MATLAB: %s\n', version);
fprintf('Symbolic toolbox available: %d\n', license('test', 'Symbolic_Toolbox'));
disp(checkcode(target, '-id'));
run(target);
