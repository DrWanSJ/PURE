function p = enzyme_qssa_params(profile)
%ENZYME_QSSA_PARAMS Load a frozen synthetic QSSA test profile.
%
% valid   : small enzyme/substrate ratio.
% failure : large enzyme/substrate ratio; standard QSSA should fail.

if nargin < 1 || isempty(profile)
    profile = 'valid';
end
profile = validatestring(profile, {'valid','failure'});

thisdir = fileparts(mfilename('fullpath'));
root = fileparts(fileparts(fileparts(thisdir)));
jsonfile = fullfile(root, 'models', 'fixtures', 'enzyme_qssa', 'parameters.json');
raw = jsondecode(fileread(jsonfile));
r = raw.profiles.(profile);

p = struct();
p.fixture_id = raw.fixture_id;
p.evidence_type = raw.evidence_type;
p.profile = profile;
p.description = r.description;

p.k1 = r.k1;
p.k_minus1 = r.k_minus1;
p.k2 = r.k2;
p.e_T = r.e_T;

p.s0 = r.s0;
p.c0 = r.c0;
p.p0 = r.p0;
p.y0 = [p.s0;p.c0;p.p0];

% Tasklist Eq. (7.7).
p.K_M = (p.k_minus1+p.k2)/p.k1;

p.t_final = r.t_final;
p.output_dt = r.output_dt;
p.solver = raw.solver.name;
p.RelTol = raw.solver.RelTol;
p.AbsTol = raw.solver.AbsTol;
p.acceptance = raw.acceptance;
p.source_file = jsonfile;
end
