"""Frozen registered-pool evidence, without inventing token memberships.

All scalar statistics use the primary author samples. Supplemental t=0 is
retained in the long table and initial total only. Raw negatives are retained;
one negative member invalidates every ratio for that pool at that sample.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def _stats(values: np.ndarray, reason: str) -> tuple:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if not len(values):
        return reason, reason, reason
    return float(np.min(values)), float(np.median(values)), float(np.max(values))


def compute_pools(root, pre, species, S, k, x, classes, times):
    """Return serializable pool tables, state fields and linking maps.

    ``valid`` means the registered coefficient-one sum has an exact zero
    derivative in every author-enabled reaction. ``quantified`` additionally
    requires a unique approved Class-I free counterpart or the explicit
    preregistered ribosome counterpart. Neither status approves a reduction.
    """
    root = Path(root)
    species = list(species)
    S, k, x, times = map(np.asarray, (S, k, x, times))
    if len(set(species)) != len(species):
        raise ValueError("Repeated source species")
    if S.shape != (len(species), len(k)) or x.shape != (len(times), len(species)):
        raise ValueError("Pool matrix shape mismatch")
    if not all(np.all(np.isfinite(a)) for a in (S, k, x, times)):
        raise ValueError("Pool inputs must be finite raw values")
    if not np.array_equal(S, S.astype(np.int64)):
        raise ValueError("Pool exact certificate requires literal integer stoichiometry")
    if set(classes) != set(species):
        raise ValueError("Pool classes must cover exactly the source species")
    primary = times > 0
    if int(primary.sum()) != pre["sampling"]["primary_points"]:
        raise ValueError("Pool summaries require exactly the registered primary samples")
    if np.count_nonzero(times == 0) != 1 or times[0] != 0:
        raise ValueError("Pool inputs require separate exact-author t=0")
    registered = pre["registered_pools"]
    source = json.loads((root / registered["source"]).read_text(encoding="utf-8-sig"))
    members = registered["membership"]
    if members != source["pools"]:
        raise ValueError("Registered pool lists differ from source lists")
    index = {sid: j for j, sid in enumerate(species)}
    enabled = k != 0
    integer_S = S.astype(np.int64)
    floor = float(pre["numeric"]["concentration_denominator_floor"])
    explicit = registered["explicit_free_counterparts"]
    pool_rows, member_rows, sample_rows = [], [], []
    valid, quantified, by_id = {}, {}, {}
    state_pool_ids = {sid: [] for sid in species}
    member_by_key = {}

    for pool_id, pool_members in members.items():
        if not pool_members or len(set(pool_members)) != len(pool_members):
            raise ValueError(f"Empty or repeated registered members: {pool_id}")
        if not set(pool_members) <= set(index):
            raise ValueError(f"Unknown registered species: {pool_id}")
        indices = [index[sid] for sid in pool_members]
        residual = np.sum(integer_S[indices], axis=0, dtype=np.int64)
        reference_conserved = bool(np.all(residual[enabled] == 0))
        unconditional_conserved = bool(np.all(residual == 0))
        valid[pool_id] = reference_conserved
        free_candidates = [sid for sid in pool_members if classes[sid] == "I"]
        if pool_id in explicit:
            free_sid = explicit[pool_id]
            coarse_id = {"RS30S": "coarse:R30_free", "RS50S": "coarse:R50_free"}.get(free_sid)
            if free_sid not in pool_members or members.get(coarse_id) != [free_sid]:
                raise ValueError(f"Unsupported explicit ribosome counterpart: {pool_id}")
            free_basis = "PREREGISTERED_EXPLICIT_RIBOSOME_SINGLETON"
        elif len(free_candidates) == 1:
            free_sid = free_candidates[0]
            free_basis = "UNIQUE_HUMAN_APPROVED_CLASS_I_MEMBER"
        else:
            free_sid = None
            free_basis = "N/A_FREE_COUNTERPART_UNRESOLVED"
        quantified[pool_id] = bool(reference_conserved and free_sid is not None)
        total = np.sum(x[:, indices], axis=1)
        negative = np.any(x[:, indices] < 0, axis=1)
        zero_total = total <= floor
        ratio_mask = reference_conserved & ~negative & ~zero_total
        free_mask = ratio_mask & (free_sid is not None)
        ratio_reason = np.full(len(times), "INFORMATIVE", dtype=object)
        ratio_reason[zero_total] = "N/A_ZERO_POOL_TOTAL"
        ratio_reason[negative] = "N/A_NEGATIVE_POOL_MEMBER"
        if not reference_conserved:
            ratio_reason[:] = "N/A_POOL_NOT_REFERENCE_CONSERVED"
        free_reason = ratio_reason.copy()
        if reference_conserved and free_sid is None:
            free_reason[:] = "N/A_FREE_COUNTERPART_UNRESOLVED"
        ratio = np.full(len(times), np.nan)
        if free_sid is not None:
            ratio[free_mask] = x[free_mask, index[free_sid]] / total[free_mask]
        bound = 1 - ratio
        primary_reasons = sorted(set(str(v) for v in free_reason[primary] if v != "INFORMATIVE"))
        unavailable = primary_reasons[0] if len(primary_reasons) == 1 else "N/A_NO_INFORMATIVE_POOL_SAMPLES"
        ratio_min, ratio_median, ratio_max = _stats(ratio[primary], unavailable)
        bound_max = _stats(bound[primary], unavailable)[2]
        total_min, total_median, total_max = _stats(total[primary], "N/A_NO_PRIMARY_SAMPLES")
        status = "COMPUTED_REFERENCE_CONDITION_ONLY" if np.any(free_mask & primary) else unavailable
        limitations = ["AUTHOR_REFERENCE_CONDITION_ONLY", "COEFFICIENT_ONE_REGISTERED_MEMBERS_ONLY", "NO_KINETIC_REDUCTION_APPROVED", "BOUND_SUBSTRATE_TOKEN_MEMBERSHIP_UNRESOLVED"]
        if not unconditional_conserved and reference_conserved:
            limitations.append("CONSERVATION_REQUIRES_AUTHOR_DISABLED_DIRECTIONS")
        if pool_id.endswith("_family_total"):
            limitations.append("NONFREE_FRACTION_INCLUDES_REGISTERED_DEGRADED_SINK")
        if not reference_conserved:
            limitations.append("REGISTERED_CANDIDATE_SUM_NOT_REFERENCE_CONSERVED")
        if np.any(negative[primary]):
            limitations.append("RAW_NEGATIVE_MEMBER_SAMPLES_EXCLUDED_WITHOUT_CLIPPING")
        row = {
            "pool_id": pool_id,
            "member_species_ids": ";".join(pool_members),
            "member_count": len(pool_members),
            "member_coefficients": "1",
            "membership_source": registered["source"],
            "membership_status": "REGISTERED_REFERENCE_CONSERVED" if reference_conserved else "REGISTERED_NOT_REFERENCE_CONSERVED",
            "reference_conserved": reference_conserved,
            "unconditional_conserved": unconditional_conserved,
            "reference_stoichiometric_residual_max_abs": int(np.max(np.abs(residual[enabled]))) if np.any(enabled) else 0,
            "unconditional_stoichiometric_residual_max_abs": int(np.max(np.abs(residual))),
            "free_species_id": free_sid or "N/A_FREE_COUNTERPART_UNRESOLVED",
            "free_counterpart_basis": free_basis,
            "total_initial": float(total[0]),
            "total_min": total_min,
            "total_median": total_median,
            "total_max": total_max,
            "free_total_ratio_min": ratio_min,
            "free_total_ratio_median": ratio_median,
            "free_total_ratio_max": ratio_max,
            "max_bound_fraction": bound_max,
            "primary_sample_count": int(primary.sum()),
            "informative_fraction": float(np.mean(free_mask[primary])),
            "occupancy_informative_fraction": float(np.mean(ratio_mask[primary])),
            "negative_member_sample_count": int(np.sum(negative[primary])),
            "zero_denominator_sample_count": int(np.sum(zero_total[primary])),
            "sequestration_metric_status": status,
            "unavailable_reasons": ";".join(primary_reasons) or "NONE",
            "evidence_limitations": ";".join(limitations),
        }
        pool_rows.append(row)
        by_id[pool_id] = row
        for n, time in enumerate(times):
            sample_rows.append({
                "time": float(time), "pool_id": pool_id,
                "sample_kind": "PRIMARY_AUTHOR_GRID" if primary[n] else "SUPPLEMENTAL_NUMERICAL_DIAGNOSTIC",
                "total_concentration": float(total[n]),
                "free_species_id": free_sid or "N/A_FREE_COUNTERPART_UNRESOLVED",
                "free_concentration": float(x[n, index[free_sid]]) if free_sid is not None else "N/A_FREE_COUNTERPART_UNRESOLVED",
                "free_fraction": float(ratio[n]) if free_mask[n] else str(free_reason[n]),
                "bound_fraction": float(bound[n]) if free_mask[n] else str(free_reason[n]),
                "negative_member": bool(negative[n]),
                "informative": bool(free_mask[n]), "reason": str(free_reason[n]),
                "occupancy_informative": bool(ratio_mask[n]), "occupancy_reason": str(ratio_reason[n]),
            })
        for sid in pool_members:
            state_pool_ids[sid].append(pool_id)
            occupancy = np.full(len(times), np.nan)
            occupancy[ratio_mask] = x[ratio_mask, index[sid]] / total[ratio_mask]
            occupancy_reasons = sorted(set(str(v) for v in ratio_reason[primary] if v != "INFORMATIVE"))
            occupancy_na = occupancy_reasons[0] if len(occupancy_reasons) == 1 else "N/A_NO_INFORMATIVE_POOL_SAMPLES"
            occ_min, occ_med, occ_max = _stats(occupancy[primary], occupancy_na)
            member_row = {
                "state_pool_metric_id": f"{sid}::{pool_id}", "species_id": sid, "pool_id": pool_id,
                "member_coefficient": 1,
                "free_species_id": row["free_species_id"],
                "is_free_counterpart": sid == free_sid,
                "occupancy_min": occ_min, "occupancy_median": occ_med, "occupancy_max": occ_max,
                "free_total_ratio_min": ratio_min, "free_total_ratio_median": ratio_median,
                "free_total_ratio_max": ratio_max, "max_bound_fraction": bound_max,
                "occupancy_informative_fraction": float(np.mean(ratio_mask[primary])),
                "free_fraction_informative_fraction": float(np.mean(free_mask[primary])),
                "occupancy_metric_status": "COMPUTED_REFERENCE_CONDITION_ONLY" if np.any(ratio_mask & primary) else occupancy_na,
                "sequestration_metric_status": status,
                "evidence_limitations": row["evidence_limitations"],
            }
            member_rows.append(member_row)
            member_by_key[sid, pool_id] = member_row

    state_fields = {}
    for sid in species:
        pools = state_pool_ids[sid]
        active = [p for p in pools if not p.startswith("coarse:") and p.endswith("_active_pool") and quantified[p]]
        reason = "N/A_MULTIPLE_POOLS" if len(active) > 1 else "N/A_POOL_MEMBERSHIP_UNRESOLVED"
        state_row = {
            "known_pool_ids": ";".join(pools) or "N/A_POOL_MEMBERSHIP_UNRESOLVED",
            "pool_membership_status": "REGISTERED_REFERENCE_CONSERVED" if any(valid[p] for p in pools) else "UNRESOLVED",
            "free_species_for_pool": reason,
            "free_total_ratio_min": reason, "free_total_ratio_median": reason, "free_total_ratio_max": reason,
            "max_bound_fraction": reason, "sequestration_metric_status": reason,
            "scalar_pool_id": reason,
            "occupancy_min": reason, "occupancy_median": reason, "occupancy_max": reason,
            "state_pool_metric_ids": ";".join(f"{sid}::{p}" for p in pools) or "N/A_POOL_MEMBERSHIP_UNRESOLVED",
        }
        if len(active) == 1:
            p = active[0]
            pr, sr = by_id[p], member_by_key[sid, p]
            state_row.update({
                "scalar_pool_id": p, "free_species_for_pool": pr["free_species_id"],
                **{key: pr[key] for key in ("free_total_ratio_min", "free_total_ratio_median", "free_total_ratio_max", "max_bound_fraction", "sequestration_metric_status")},
                **{key: sr[key] for key in ("occupancy_min", "occupancy_median", "occupancy_max")},
            })
        state_fields[sid] = state_row
    return {
        "pool_evidence": pool_rows, "state_pool_metrics": member_rows,
        "pool_timeseries": sample_rows, "state_fields": state_fields,
        "members": members, "valid": valid, "quantified": quantified,
        "state_pool_ids": state_pool_ids, "pool_by_id": by_id,
    }
