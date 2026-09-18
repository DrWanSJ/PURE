function hex = pure_sha256_string(str)
%PURE_SHA256_STRING SHA-256 of a UTF-8 encoded string (fixed algorithm).
%
%   HEX = PURE_SHA256_STRING(STR)
%
%   Hash of the UTF-8 byte encoding of STR; lowercase hex output.
%   Used for canonical input descriptors (e.g. the JSON serialization of a
%   run's inputs). Implementation mirrors pure_sha256_file (.NET primary).

try
    sha = System.Security.Cryptography.SHA256Managed();
    cleanupObj = onCleanup(@() sha.Dispose());
    utf8 = System.Text.Encoding.UTF8.GetBytes(char(str));
    hashBytes = sha.ComputeHash(utf8);
    hex = lower(sprintf('%02x', double(hashBytes)));
    return;
catch
end
% fallback: write bytes to a temp file and hash it
tmp = [tempname(), '.utf8.txt'];
fid = fopen(tmp, 'w', 'n', 'UTF-8');
if fid == -1
    error('pure_ref:sha256:failed', 'cannot create temp file for hashing');
end
cleanupFile = onCleanup(@() delete(tmp));
fwrite(fid, unicode2native(char(str), 'UTF-8'), 'uint8');
fclose(fid);
hex = pure_sha256_file(tmp);
end
