function p = pure_literature_reference_params()
%PURE_LITERATURE_REFERENCE_PARAMS Load locked parameters for the B1 benchmark.
%
%   P = PURE_LITERATURE_REFERENCE_PARAMS()
%
%   Reads the single source of truth
%     models/literature_reference/parameters.json
%   (Mavelli, Marangoni, Stano 2015, Tables 1-2, central/best-estimate
%   values, no sampling, no refitting) and flattens it into the parameter
%   struct P consumed by RHS_PURE_LITERATURE_REFERENCE.
%
%   P fields:
%     k_TX, k_TL, k_RS, k_EN, k_nt_deg, k_TL_deg          kinetic constants [1/s]
%     K_TX_DNA, K_TX_NTP, K_TL_nt, K_TL_AT, K_TL_NTP,
%     K_RS_A, K_RS_T, K_RS_NTP, K_EN_CP, K_EN_NXP         MM constants [uM]
%     TXcat, RScat, ENcat                                  fixed catalyst inputs [uM]
%     n_NTP, n_A, n_T                                      multiplicity factors
%     L                                                    protein length (GFP) [aa]
%     y0                                                   10x1 initial state [uM]
%     state_names, rate_names                              fixed ordering
%     state_order_json, rate_order_json                    ordering as in the JSON
%     derived                                              derived quantities (K_TL_RNA)
%     meta                                                 source/units/simulation info

thisdir = fileparts(mfilename('fullpath'));            % .../matlab/generated
root    = fileparts(fileparts(thisdir));               % project root
jsonfile = fullfile(root, 'models', 'literature_reference', 'parameters.json');
if ~exist(jsonfile, 'file')
    error('pure_ref:paramsNotFound', ...
        'parameters.json not found at %s', jsonfile);
end
S = jsondecode(fileread(jsonfile));

p = struct();

% --- kinetic constants and MM constants + fixed catalyst inputs (Table 2 / Table 1) ---
f = fieldnames(S.parameters);
for i = 1:numel(f)
    v = S.parameters.(f{i}).value;
    if isempty(v)
        error('pure_ref:nullParameter', ...
            'parameters.json: parameter "%s" has null value', f{i});
    end
    p.(f{i}) = v;
end

% --- multiplicity factors and protein length ---
p.n_NTP = S.multiplicity.n_NTP;
p.n_A   = S.multiplicity.n_A;
p.n_T   = S.multiplicity.n_T;
p.L     = S.protein.length_aa_L;

% --- initial conditions for the 10 dynamic states, in the locked order ---
state_order = {S.state_order{1:end}};                  % 10 dynamic states
p.state_names = state_order;
y0 = zeros(numel(state_order), 1);
for i = 1:numel(state_order)
    ic = S.initial_conditions.(state_order{i});
    if isempty(ic.value)
        error('pure_ref:nullInitial', ...
            'initial condition for "%s" is null (set per run); not valid for a dynamic state', ...
            state_order{i});
    end
    y0(i) = ic.value;
end
p.y0 = y0;
p.state_order_json = S.state_order;
p.rate_order_json  = S.rate_order;

p.rate_names = {'V_TX', 'V_nt_deg', 'V_RS', 'V_TL', 'V_TL_deg', 'V_EN'};

% --- derived quantities (QC only; K_TL_RNA is NOT used in the RHS) ---
p.derived = S.derived_quantities;

% --- provenance / units / simulation metadata ---
p.meta = struct();
p.meta.model_id  = S.model_id;
p.meta.doi       = S.source.doi;
p.meta.units     = S.units;
p.meta.simulation = S.simulation;
p.meta.json_file = jsonfile;
end
