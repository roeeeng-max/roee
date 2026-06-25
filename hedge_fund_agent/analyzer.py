from dataclasses import dataclass
from typing import Optional


@dataclass
class PositionChange:
    issuer:        str
    cusip:         str
    change_type:   str           # "new" | "closed" | "increased" | "decreased"
    current_value: int           # thousands USD
    prev_value:    Optional[int]
    change_pct:    Optional[float]
    current_shares: int
    prev_shares:   Optional[int]


def analyze_changes(
    current: list[dict],
    previous: list[dict],
    min_value_k: int,
    min_change_pct: float,
) -> list[PositionChange]:
    """
    Compare two lists of holdings dicts (keys: cusip, issuer, value, shares).
    Returns significant changes filtered by min_value_k and min_change_pct.
    """
    curr_map = {h["cusip"]: h for h in current  if h["value"] >= min_value_k}
    prev_map = {h["cusip"]: h for h in previous}

    changes: list[PositionChange] = []

    for cusip, curr in curr_map.items():
        if cusip not in prev_map:
            changes.append(
                PositionChange(
                    issuer=curr["issuer"],
                    cusip=cusip,
                    change_type="new",
                    current_value=curr["value"],
                    prev_value=None,
                    change_pct=None,
                    current_shares=curr["shares"],
                    prev_shares=None,
                )
            )
        else:
            prev = prev_map[cusip]
            if prev["value"] > 0:
                pct = (curr["value"] - prev["value"]) / prev["value"] * 100
                if abs(pct) >= min_change_pct:
                    changes.append(
                        PositionChange(
                            issuer=curr["issuer"],
                            cusip=cusip,
                            change_type="increased" if pct > 0 else "decreased",
                            current_value=curr["value"],
                            prev_value=prev["value"],
                            change_pct=pct,
                            current_shares=curr["shares"],
                            prev_shares=prev["shares"],
                        )
                    )

    for cusip, prev in prev_map.items():
        if cusip not in curr_map and prev["value"] >= min_value_k:
            changes.append(
                PositionChange(
                    issuer=prev["issuer"],
                    cusip=cusip,
                    change_type="closed",
                    current_value=0,
                    prev_value=prev["value"],
                    change_pct=-100.0,
                    current_shares=0,
                    prev_shares=prev["shares"],
                )
            )

    return changes
