function out = simulate_pure_rs_qssa(DNA_uM, varargin)
%SIMULATE_PURE_RS_QSSA Ten slow states plus two accounting sinks.
out = simulate_pure_rs_model('qssa', DNA_uM, varargin{:});
end
