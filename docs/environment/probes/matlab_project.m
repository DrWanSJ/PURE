function matlab_project(kind)
% Execute unchanged project source in a verified scratch snapshot.
root = getenv('PURE_AUDIT_SCRATCH');
assert(~isempty(root), 'PURE_AUDIT_SCRATCH must name the isolated snapshot.');
switch kind
    case 'literature'
        result = runtests(fullfile(root, 'matlab', 'tests', 'test_pure_literature_reference.m'));
        disp(table(result));
        fprintf('LITERATURE_TESTS total=%d passed=%d failed=%d incomplete=%d\n', ...
            numel(result), sum([result.Passed]), sum([result.Failed]), sum([result.Incomplete]));
        assert(~isempty(result) && all([result.Passed]) && ~any([result.Incomplete]));
    case 'dimensionless'
        run(fullfile(root, 'models', 'literature_reference', 'dimensionless', 'derive_dimensionless.m'));
    otherwise
        error('CZEnvironment:UnknownProjectProbe', 'Unknown project check.');
end
fprintf('PROJECT_PASS=%s\n', kind);
end
