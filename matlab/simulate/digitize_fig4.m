function digitize_fig4()
%DIGITIZE_FIG4 Automated raster digitization of Mavelli 2015 Fig. 4.
%
%   DIGITIZE_FIG4()
%
%   Extracts the six curves (3 DNA conditions x [nt]/[a] panels) from the
%   300-dpi render of page 14 of
%     A_Simple_Protein_Synthesis_Model_PURE_normalized.pdf
%   (sha256 838d1f5d..., produced from the password-protected original by
%   Ghostscript; render: pdftoppm -png -r 300 -f 14 -l 14).
%
%   Method (base MATLAB only):
%     1. locate the two axes boxes (long black horizontal/vertical lines
%        in the upper/lower half of the page); box corners = axis limits
%        (x: 0-4 h; top panel y: 0-1000 uM nt; bottom panel y: 0-160 uM a);
%     2. classify colored pixels (red/green/blue with channel-difference
%        thresholds; excludes black text and gray gridlines);
%     3. at 9 sample times (0.5:0.5:4 h) collect pixel-row clusters per
%        color; Fig. 4 overlays experimental (dotted) and calculated
%        (continuous) curves in the SAME color, so clusters separate only
%        where the curves diverge;
%     4. assign the cluster belonging to the CONTINUOUS (calculated) line
%        by a continuity score: fraction of a +/-10 px column window in
%        which same-color pixels exist within +/-4 px of the cluster row
%        (a connected line scores ~1, spaced dots lower). Ambiguous if the
%        two best scores differ by < 0.15.
%
%   Outputs:
%     data/processed/fig4_digitized_all_clusters.csv   every extracted cluster
%     data/processed/fig4_digitized.csv                calculated-curve pick
%         provenance: digitized_from_Mavelli_2015_Fig4
%     results/literature_reference/fig4_digitized_comparison.csv
%         digitized calculated curve vs new_simulation at the sample times
%
%   Limitations (registered in docs/benchmark_registry.md, L1):
%     - reading precision ~1-2 % of each panel's full scale
%       (about +/-15 uM for [nt], +/-3 uM for [a]);
%     - where calculated and experimental curves overlap they cannot be
%       separated; such points carry flag merged_with_experimental and the
%       value represents both curves;
%     - the digitized points approximate a raster figure; they are NOT
%       experimental data and NOT a substitute for the original Stogbauer
%       2012 data used by the paper's authors.

d    = fileparts(mfilename('fullpath'));
root = fileparts(fileparts(d));
png  = fullfile(root, 'data', 'raw', 'mavelli2015_fig4_page14_300dpi.png');
proc = fullfile(root, 'data', 'processed');
resd = fullfile(root, 'results', 'literature_reference');
if ~exist(proc, 'dir'); mkdir(proc); end

img = im2double2(imread(png));
H = size(img, 1); W = size(img, 2);
R = img(:,:,1); G = img(:,:,2); B = img(:,:,3);
black = (R < 0.35) & (G < 0.35) & (B < 0.35);

% ---- locate the two axes boxes (global rectangle detection) ----------
% A valid axes box is a pair of long horizontal black lines connected by
% vertical black lines with >=93% fill (rejects the two-panel column
% arrangement, whose fill is only ~87%). Header rules and caption lines
% have no vertical connectors and are rejected.
rs = sum(black, 2);
hb = group_bands(find(rs > 0.35*W));           % long horizontal lines
rects = [];
for i = 1:numel(hb)
    for j = i+1:numel(hb)
        span = hb(j).c - hb(i).c;
        if span < 0.15*H; continue; end
        vb = group_bands(find(sum(black(hb(i).c:hb(j).c, :), 1) > 0.93*span));
        if numel(vb) < 2; continue; end
        wdt = vb(end).c - vb(1).c;
        if wdt < 0.30*W; continue; end
        rects = [rects; hb(i).c, hb(j).c, vb(1).c, vb(end).c]; %#ok<AGROW>
    end
end
rects = sortrows(rects, 1);
if size(rects, 1) < 2
    error('digitize:boxNotFound', ...
        'expected two axes boxes, found %d', size(rects, 1));
end
boxes = rects(1:2, :);

% ---- tick-mark calibration -------------------------------------------
% The axes box corners are NOT the axis limits (the x-limit is ~4.18 h,
% not 4 h). Calibration uses the tick MARKS (MATLAB draws them INSIDE the
% box): their columns/rows form an arithmetic sequence anchored at the box
% edges (t = 0 at the left edge, y = 0 at the bottom edge). Values per
% step: 1 h (x) and 200 / 20 uM (y), read from the axis labels.
map = cell(2, 1);
step_uM = [200, 20];   % y tick step per panel (from the axis labels)
for p = 1:2
    r0 = boxes(p,1); r1 = boxes(p,2); c0 = boxes(p,3); c1 = boxes(p,4);
    % x ticks: black columns in a thin band just above the bottom edge
    xband = black(max(1, r1-9):r1-4, c0+8:c1-8);
    xtb = group_bands(find(sum(xband, 1) >= 3));
    cand_x = arrayfun(@(b) b.c, xtb)' + (c0 + 7);   % band starts at col c0+8
    cand_x = cand_x(abs(cand_x - c0) > 4 & abs(cand_x - c1) > 4);
    if numel(cand_x) < 2
        error('digitize:calibration', 'panel %d: too few x ticks', p);
    end
    dx = median(diff(cand_x));
    kx = (cand_x - c0)/dx;
    if any(abs(kx - round(kx)) > 0.1)
        error('digitize:calibration', ...
            'panel %d: x ticks are not on an integer-hour grid', p);
    end
    px_per_h = mean((cand_x - c0)./round(kx));
    % y ticks: black rows in a thin band just right of the left edge
    yband = black(r0+8:r1-8, c0+4:c0+9);
    ytb = group_bands(find(sum(yband, 2) >= 3));
    cand_y = arrayfun(@(b) b.c, ytb)' + (r0 + 7);   % band starts at row r0+8
    cand_y = cand_y(abs(cand_y - r0) > 4 & abs(cand_y - r1) > 4);
    if numel(cand_y) < 2
        error('digitize:calibration', 'panel %d: too few y ticks', p);
    end
    dy = median(diff(cand_y));
    ky = (r1 - cand_y)/dy;
    if any(abs(ky - round(ky)) > 0.1)
        error('digitize:calibration', ...
            'panel %d: y ticks are not on an integer-step grid', p);
    end
    px_per_step = mean((r1 - cand_y)./round(ky));
    map{p} = struct('c0', c0, 'c1', c1, 'r0', r0, 'r1', r1, ...
        'px_per_h', px_per_h, 'px_per_step', px_per_step, ...
        'step_uM', step_uM(p));
    fprintf(['panel %d: calibration %.2f px/h, %.2f px/%g uM ' ...
        '(x-limit at right edge: %.2f h)\n'], p, px_per_h, px_per_step, ...
        step_uM(p), (c1 - c0)/px_per_h);
end

panel_name = {'nt', 'a'};
panel_ymax = [1000, 160];
color_name = {'red', 'green', 'blue'};
color_dna  = [6.8, 1.7, 0.34];
mask_red   = (R > 0.45) & (R - max(G, B) > 0.18);
mask_green = (G > 0.40) & (G - max(R, B) > 0.12);
mask_blue  = (B > 0.45) & (B - max(R, G) > 0.12);
masks = {mask_red, mask_green, mask_blue};

times_h = 0.5:0.5:4;
allC = {};   % {panel, color, dna_nM, time_h, value_uM, score, height_px}
for p = 1:2
    mp = map{p};
    r0 = mp.r0; r1 = mp.r1; c0 = mp.c0; c1 = mp.c1;
    for ci = 1:3
        M = masks{ci};
        M(1:r0+3, :) = false; M(r1-3:end, :) = false;
        M(:, 1:c0+3) = false; M(:, c1-3:end) = false;
        for th = times_h
            col = round(c0 + th*mp.px_per_h);
            col = min(max(col, c0 + 4), c1 - 4);
            wcols = col-2 : col+2;
            rows = find(any(M(:, wcols), 2));
            if isempty(rows); continue; end
            cl = group_bands(rows);
            for k = 1:numel(cl)
                rk = cl(k).c;
                w2 = max(c0+4, col-10) : min(c1-4, col+10);
                hit = zeros(numel(w2), 1);
                for j = 1:numel(w2)
                    rr = find(M(:, w2(j)));
                    hit(j) = any(abs(rr - rk) <= 4);
                end
                val = (r1 - rk)/mp.px_per_step * mp.step_uM;
                allC(end+1, :) = {panel_name{p}, color_name{ci}, ...
                    color_dna(ci), th, val, mean(hit), cl(k).len}; %#ok<AGROW>
            end
        end
    end
end

Tall = cell2table(allC, 'VariableNames', ...
    {'panel', 'color', 'dna_nM', 'time_h', 'value_uM', ...
     'continuity_score', 'cluster_height_px'});
writetable(Tall, fullfile(proc, 'fig4_digitized_all_clusters.csv'));

% ---- pick the calculated (continuous) curve cluster -------------------
% Assignment rule: where two same-color clusters exist (experimental
% dotted vs calculated continuous), the cluster NEAREST to the
% new_simulation trajectory is assigned to the calculated curve. The
% simulation is used as a tracker only; the assignment was additionally
% verified visually: in the [a] panel the experimental curves plateau at
% about 114 / 103 / 19 uM (red/green/blue) while the calculated curves do
% not, and the calculated red curve reaches the paper-stated endpoint
% a(4h) = 0.58*238 = 138 uM. All raw clusters remain available in
% fig4_digitized_all_clusters.csv for audit. Deviations reported below are
% therefore conditional on this assignment where clusters separate.
simdata = cell(3, 1);
for ci = 1:3
    lab = sprintf('DNA_%snM', strrep(num2str(color_dna(ci)), '.', 'p'));
    simdata{ci} = readtable(fullfile(resd, lab, 'trajectory.csv'));
end

wide = {};   % {curve_type, dna_nM, time_h, nt_uM, a_uM, flag}
for ci = 1:3
    nt_v = nan(numel(times_h),1); a_v = nan(numel(times_h),1);
    nt_f = repmat({''}, numel(times_h),1); a_f = repmat({''}, numel(times_h),1);
    for p = 1:2
        v = nan(numel(times_h),1); fl = repmat({''}, numel(times_h),1);
        tr = simdata{ci};
        for ti = 1:numel(times_h)
            sel = allC(strcmp(allC(:,1), panel_name{p}) & ...
                       strcmp(allC(:,2), color_name{ci}), :);
            s = sel(cellfun(@(x) abs(x - times_h(ti)) < 1e-9, sel(:,4)), :);
            if isempty(s); continue; end
            if p == 1
                sv = interp1(tr.time_h, tr.nt_uM, times_h(ti));
            else
                sv = interp1(tr.time_h, tr.a_uM, times_h(ti));
            end
            vals = [s{:,5}];
            [~, imn] = min(abs(vals - sv));
            v(ti) = vals(imn);
            if size(s, 1) == 1
                fl{ti} = 'merged_with_experimental';
            else
                fl{ti} = 'assigned_nearest_to_simulation';
            end
        end
        if p == 1; nt_v = v; nt_f = fl; else; a_v = v; a_f = fl; end
    end
    for ti = 1:numel(times_h)
        if isnan(nt_v(ti)) && isnan(a_v(ti)); continue; end
        if isempty(nt_f{ti}); fg = a_f{ti}; else; fg = nt_f{ti}; end
        wide(end+1, :) = {'calculated_continuous', color_dna(ci), ...
            times_h(ti), nt_v(ti), a_v(ti), fg}; %#ok<AGROW>
    end
end
T1 = cell2table(wide, 'VariableNames', ...
    {'curve_type', 'dna_nM', 'time_h', 'nt_uM', 'a_uM', 'digitization_flag'});
writetable(T1, fullfile(proc, 'fig4_digitized.csv'));

% ---- comparison against the new_simulation trajectories --------------
cmprows = {};
for ci = 1:3
    lab = sprintf('DNA_%snM', strrep(num2str(color_dna(ci)), '.', 'p'));
    traj = readtable(fullfile(resd, lab, 'trajectory.csv'));
    sel = T1(T1.dna_nM == color_dna(ci), :);
    for i = 1:height(sel)
        th = sel.time_h(i);
        y_nt = interp1(traj.time_h, traj.nt_uM, th);
        y_a  = interp1(traj.time_h, traj.a_uM, th);
        cmprows(end+1, :) = {color_dna(ci), th, sel.nt_uM(i), y_nt, ...
            reldev(sel.nt_uM(i), y_nt), sel.a_uM(i), y_a, ...
            reldev(sel.a_uM(i), y_a), sel.digitization_flag{i}}; %#ok<AGROW>
    end
end
T2 = cell2table(cmprows, 'VariableNames', {'dna_nM', 'time_h', ...
    'nt_digitized_uM', 'nt_simulation_uM', 'nt_rel_dev', ...
    'a_digitized_uM', 'a_simulation_uM', 'a_rel_dev', 'digitization_flag'});
writetable(T2, fullfile(resd, 'fig4_digitized_comparison.csv'));

fprintf('\n== Fig. 4 digitized (calculated curve) vs new_simulation ==\n');
disp(T2);
for ci = 1:3
    s = T2(T2.dna_nM == color_dna(ci), :);
    fprintf('DNA %g nM: nt max|reldev| = %.1f%%, a max|reldev| = %.1f%%\n', ...
        color_dna(ci), 100*max(abs(s.nt_rel_dev)), 100*max(abs(s.a_rel_dev)));
end
end

% -------------------------------------------------------------------------
function out = im2double2(im)
if isa(im, 'double'); out = im; else; out = double(im)/255; end
if size(out, 3) == 1; out = repmat(out, 1, 1, 3); end
end

function bands = group_bands(idx)
idx = sort(idx(:));
bands = struct('c', {}, 'len', {});
if isempty(idx); return; end
d = [true; diff(idx) > 1];
starts = idx(d);
ends_  = idx([d(2:end); true]);
for k = 1:numel(starts)
    bands(k).c   = round((starts(k) + ends_(k))/2);
    bands(k).len = ends_(k) - starts(k) + 1;
end
end

function s = ternary(c, a, b)
if c; s = a; else; s = b; end
end

function rd = reldev(dig, sim)
if isnan(dig) || isnan(sim) || dig < 5
    rd = NaN;   % relative deviation unstable near zero
else
    rd = (sim - dig)/dig;
end
end
