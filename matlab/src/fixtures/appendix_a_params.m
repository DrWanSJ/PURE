function p = appendix_a_params(profile)
%APPENDIX_A_PARAMS Load one synthetic Appendix-A parameter profile.
%
% baseline  : generic fixed-point/Jacobian tests.
% low_load  : tests the assumptions behind Eq. (A.13).
% saturated : tests the assumptions behind Eq. (A.14).
%
% All quantities are dimensionless and must stay outside PURE parameters.

if nargin < 1 || isempty(profile)
    profile = 'baseline';
end
profile = validatestring(profile,{'baseline','low_load','saturated'});

thisdir = fileparts(mfilename('fullpath'));
root = fileparts(fileparts(fileparts(thisdir)));
jsonfile = fullfile(root,'models','fixtures','appendix_a','parameters.json');
raw = jsondecode(fileread(jsonfile));
r = raw.profiles.(profile);

p = struct();
p.fixture_id = raw.fixture_id;
p.evidence_type = raw.evidence_type;
p.parameter_origin = raw.parameter_origin;
p.profile = profile;
p.description = r.description;

p.alpha = r.alpha;
p.rho = r.rho;
p.eta = r.eta;
p.delta = r.delta;
p.K_e = r.K_e;
p.u0 = r.u0;
p.e0 = r.e0;
p.y0 = [p.u0;p.e0];

p.tau_final = r.tau_final;
p.output_dt = r.output_dt;
p.RelTol = raw.solver.RelTol;
p.AbsTol = raw.solver.AbsTol;
p.solver = raw.solver.name;
p.acceptance = raw.acceptance;
p.source_file = jsonfile;
end
