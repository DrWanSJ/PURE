function hex = pure_sha256_file(path)
%PURE_SHA256_FILE SHA-256 of a file, fixed algorithm (audit hardening).
%
%   HEX = PURE_SHA256_FILE(PATH)
%
%   Returns the SHA-256 digest of the file content as a lowercase hex
%   string (64 characters). Fixed algorithm: SHA-256, FIPS 180-4.
%   Primary implementation: MATLAB/.NET interop
%   (System.Security.Cryptography.SHA256Managed); fallback: the platform
%   CLI tools `sha256sum` / `certutil`. The fallback must agree with the
%   primary; see test_codegen_and_provenance.m for the known-vector test.

if ~exist(path, 'file')
    error('pure_ref:sha256:noFile', 'file not found: %s', path);
end
try
    sha = System.Security.Cryptography.SHA256Managed();
    cleanupObj = onCleanup(@() sha.Dispose());
    hashBytes = sha.ComputeHash(System.IO.File.ReadAllBytes(path));
    hex = lower(sprintf('%02x', double(hashBytes)));
    return;
catch
end
% fallback 1: sha256sum (Linux/macOS/Git Bash)
[st1, out1] = system(sprintf('sha256sum "%s"', path));
if st1 == 0
    hex = lower(strtrim(regexp(out1, '^[0-9a-fA-F]{64}', 'match', 'once')));
    if ischar(hex) && ~isempty(hex); return; end
end
% fallback 2: certutil (Windows)
[st2, out2] = system(sprintf('certutil -hashfile "%s" SHA256', path));
if st2 == 0
    tokens = regexp(out2, '[0-9a-fA-F]{64}', 'match');
    if ~isempty(tokens)
        hex = lower(tokens{1});
        return;
    end
end
error('pure_ref:sha256:failed', ...
    'SHA-256 computation failed for %s (no working provider)', path);
end
