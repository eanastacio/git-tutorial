from __future__ import annotations


def compute_sponsorship_score(
    total_filings: int,
    recent_filings: int,
    certification_rate: float,
    internship_ratio: float,
    consistency_ratio: float,
) -> float:
    """
    Weighted score from 0-100 estimating sponsorship friendliness.
    """
    filing_signal = min(total_filings / 1000, 1.0) * 30
    recency_signal = min(recent_filings / 250, 1.0) * 25
    certification_signal = max(min(certification_rate, 1.0), 0) * 20
    internship_signal = max(min(internship_ratio, 1.0), 0) * 10
    consistency_signal = max(min(consistency_ratio, 1.0), 0) * 15
    return round(filing_signal + recency_signal + certification_signal + internship_signal + consistency_signal, 2)
