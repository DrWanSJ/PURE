function out = simulate_pure_rs_explicit(DNA_uM, varargin)
%SIMULATE_PURE_RS_EXPLICIT Eleven physical states plus two accounting sinks.
out = simulate_pure_rs_model('explicit', DNA_uM, varargin{:});
end
