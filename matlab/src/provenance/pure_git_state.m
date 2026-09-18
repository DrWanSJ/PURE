function st = pure_git_state(root)
%PURE_GIT_STATE Live git facts for run provenance (audit hardening).
%
%   ST = PURE_GIT_STATE(ROOT)
%
%   ST.in_repo  logical  - true if ROOT is inside a git work tree
%   ST.commit   char     - `git rev-parse HEAD` output (40 hex), or
%                          'no_commit_yet' / 'unavailable_git_not_found'
%   ST.dirty    logical|char - true/false from `git status --porcelain`
%                          (includes untracked files); 'unknown' if it
%                          cannot be determined
%
%   Both values are read LIVE from the repository at call time; nothing is
%   cached or inferred. This is the only sanctioned source for the
%   git_commit / git_dirty fields of a run manifest.

st = struct('in_repo', false, 'commit', 'unavailable_git_not_found', ...
    'dirty', 'unknown');

[stIn, outIn] = system(sprintf('git -C "%s" rev-parse --is-inside-work-tree', root));
if stIn ~= 0 || ~strcmp(strtrim(outIn), 'true')
    return;
end
st.in_repo = true;

[stHead, outHead] = system(sprintf('git -C "%s" rev-parse HEAD', root));
if stHead == 0
    head = strtrim(outHead);
    if ~isempty(regexp(head, '^[0-9a-f]{40}$', 'once'))
        st.commit = head;
    else
        st.commit = 'no_commit_yet';
    end
end

[stSt, outSt] = system(sprintf('git -C "%s" status --porcelain', root));
if stSt == 0
    st.dirty = ~isempty(strtrim(outSt));
end
end
