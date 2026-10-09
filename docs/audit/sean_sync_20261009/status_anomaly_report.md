# Status/index anomaly investigation

PR4: all 195 flagged files have equal HEAD, index, raw working-tree and cleaned working-tree blob hashes. Classification INDEX_METADATA_DIFFERENCE; no content edits.

Simulation: eight script raw blobs differ, but all eight cleaned blobs equal index and HEAD. The relevant attributes specify text/eol=crlf; normalized LF/CRLF comparisons establish FILTER_OR_EOL_DIFFERENCE. No scientific content edits. core.autocrlf=true and core.filemode=false. Entries have normal H flags, not assume-unchanged or skip-worktree. No staged differences, submodules, or LFS payloads. Original index-debug metadata and filter configurations are retained in the local audit archive; per-file hashes/attributes are in status_anomalies.csv.

Original indexes were never refreshed or rewritten. Reads used git --no-optional-locks. No commits were made to suppress these 203 historical status entries. Their continued presence does not imply unsynchronized research edits.
