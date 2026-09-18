function reproduce_b1(varargin)
%REPRODUCE_B1 Entry point: reproduce the B1 Fig. 4 benchmark.
%
%   REPRODUCE_B1()
%   REPRODUCE_B1('RunId', RUN_ID)
%
%   Thin wrapper around run_fig4_benchmark (kept in matlab/src/simulate for
%   continuity of the function name). Outputs are written to
%   results/runs/<run_id>/ and are NOT committed (see results/runs/README.md);
%   compare them against the frozen baseline results/baselines/b1_mavelli2015/.

d = fileparts(mfilename('fullpath'));   % .../scripts
root = fileparts(d);
addpath(fullfile(root, 'matlab', 'src', 'simulate'));
run_fig4_benchmark(varargin{:});
end
