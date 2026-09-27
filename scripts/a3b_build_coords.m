function C = a3b_build_coords(species, artifact_dir)
%A3B_BUILD_COORDS  Load the frozen A3b coordinate artifacts and bind them to
%the author state ordering.
%
%C fields:
%   .names        241x1 author species names (reference ordering)
%   .idx          map container species -> 1..241
%   .keepIdx      nIdent x1 integrated identity-row species indices (A0..)
%   .keepPos      nIdent x1 their positions inside y (== 1..nIdent)
%   .elimIdx      21x1 eliminated complex indices (Q0..Q20 order)
%   .elimNames    21x1 eliminated names
%   .ledger(k)    struct for the total-coordinate rows (A<nIdent>..):
%       .name       ledger name
%       .replaces   replaced free-carrier species name
%       .replIdx    its species index (1..241)
%       .pos        its y position (nIdent+k)
%       .members    member species indices (1..241), carrier INCLUDED
%       .weights    member weights (carrier weight included)
%       .wself      the carrier's own weight
%       .dotS       struct: .rid (cell), .ridx (reaction indices), .vals
%                   the exact w^T S row (nonzero entries only)
%   .nLedger      8
%   .Ny           nIdent + nLedger (candidate-dependent; 220 for A3b-21)
%
% The artifacts are the frozen outputs of
% scripts/analyze_pnas2017_aa_a3bc_coordinates.py (coordinate_matrix_A.csv,
% ledger_dot_S.json); this loader only BINDS them to the author ordering and
% never re-derives the reduction.

if nargin < 2
    artifact_dir = fullfile(fileparts(mfilename('fullpath')), '..', ...
        'docs', 'audit', 'pnas2017_aminoacylation_A3b');
end

% --- parse coordinate_matrix_A.csv (manual parse: the writer emits plain
% LF rows, no quoted fields; the first three columns are row_id/kind/label)
raw = fileread(fullfile(artifact_dir, 'coordinate_matrix_A.csv'));
lines = strsplit(strtrim(raw), newline, 'CollapseDelimiters', false);
hdr = strsplit(lines{1}, ',');
assert(strcmp(hdr{1}, 'row_id') && strcmp(hdr{2}, 'kind') && strcmp(hdr{3}, 'label'), ...
    'unexpected coordinate_matrix_A.csv header');
sp_names = hdr(4:end);
assert(numel(sp_names) == 241, 'coordinate matrix must have 241 species columns');
% bind to the AUTHOR ordering (species arg): the artifact columns are the
% same author ordering by construction, but assert rather than assume
assert(isequal(sp_names(:), species(:)), ...
    'coordinate artifact species ordering differs from the author ordering');

idx = containers.Map(sp_names, 1:241);
keepIdx = [];  elimIdx = [];
led = struct('name', {}, 'replaces', {}, 'replIdx', {}, 'pos', {}, ...
    'members', {}, 'weights', {}, 'wself', {}, 'row', {});
nLed = 0;
nIdent = -1;   % resolved against the fast-selector count below
for i = 2:numel(lines)
    f = strsplit(lines{i}, ',');
    rid = f{1}; kind = f{2}; label = f{3};
    vals = str2double(f(4:end));
    switch kind
        case 'identity'
            assert(strcmp(rid, sprintf('A%d', numel(keepIdx))), 'row order break');
            assert(sum(vals ~= 0) == 1 && any(vals == 1), 'identity row malformed');
            keepIdx(end+1, 1) = find(vals == 1, 1); %#ok<AGROW>
        case 'ledger_total'
            nLed = nLed + 1;
            mem = find(vals ~= 0);
            led(nLed).name = label;
            led(nLed).row = vals;
            led(nLed).members = mem(:);
            led(nLed).weights = reshape(vals(mem), [], 1);   % column: member-aligned
            led(nLed).pos = -1;   % bound after the identity count is known
            % the replaced carrier is named in the reconstruction JSON; resolved below
            led(nLed).replaces = '';
        otherwise
            error('unknown coordinate row kind %s', kind);
    end
end
nIdent = numel(keepIdx);
for k = 1:nLed
    led(k).pos = nIdent + k;
end

% fast selectors
raw = fileread(fullfile(artifact_dir, 'fast_selector_Q.csv'));
lines = strsplit(strtrim(raw), newline, 'CollapseDelimiters', false);
hdr = strsplit(lines{1}, ',');
assert(strcmp(hdr{1}, 'row_id') && strcmp(hdr{2}, 'species'), 'unexpected Q header');
for k = 2:numel(lines)
    f = strsplit(lines{k}, ',');
    vals = str2double(f(3:end));
    assert(sum(vals == 1) == 1, 'Q row must be a unit selector');
    elimIdx(end+1, 1) = find(vals == 1, 1); %#ok<AGROW>
end
assert(numel(elimIdx) >= 1, 'no fast selectors in the artifact');

% reconstruction.json binds each ledger row to its replaced free carrier
rj = jsondecode(fileread(fullfile(artifact_dir, 'reconstruction.json')));
repl_of = containers.Map();
carriers = rj.carriers;
fnames = fieldnames(carriers);
for k = 1:numel(fnames)
    repl_of(carriers.(fnames{k}).total_row) = fnames{k};
end
for k = 1:nLed
    assert(isKey(repl_of, led(k).name), 'ledger %s unbound in reconstruction.json', led(k).name);
    led(k).replaces = repl_of(led(k).name);
    led(k).replIdx = idx(led(k).replaces);
    led(k).pos = nIdent + k;   % re-bind (reconstruction.json may arrive later)
    % the carrier must be a member with its own weight > 0
    j = find(led(k).members == led(k).replIdx, 1);
    assert(~isempty(j) && led(k).weights(j) > 0, ...
        'carrier %s absent from its own ledger %s', led(k).replaces, led(k).name);
    led(k).wself = led(k).weights(j);
end

% ledger_dot_S.json: exact w^T S rows (nonzero per-reaction balances)
dS = jsondecode(fileread(fullfile(artifact_dir, 'ledger_dot_S.json')));
fn = fieldnames(dS);
assert(numel(fn) == nLed, 'ledger_dot_S.json must carry all %d rows', nLed);
for k = 1:nLed
    assert(isfield(dS, led(k).name), 'ledger_dot_S.json missing %s', led(k).name);
    rj2 = dS.(led(k).name);
    rf = fieldnames(rj2);
    ridx = zeros(numel(rf), 1); vals = zeros(numel(rf), 1);
    for m = 1:numel(rf)
        ridx(m) = str2double(rf{m}(3:end));
        vals(m) = rj2.(rf{m});
    end
    [ridx, order] = sort(ridx);
    vals = vals(order);
    led(k).dotS.ridx = ridx;
    led(k).dotS.vals = vals;
    led(k).dotS.rid = rf(order);
end

C = struct();
C.names = species(:);
C.idx = idx;
C.keepIdx = keepIdx;
C.keepPos = (1:numel(keepIdx))';
C.elimIdx = elimIdx;
C.elimNames = species(elimIdx);
C.ledger = led;
C.nLedger = nLed;
C.Ny = numel(keepIdx) + nLed;
end
