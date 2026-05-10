from app.services.sponsorship_score import compute_sponsorship_score


def test_score_bounds() -> None:
    score = compute_sponsorship_score(
        total_filings=5000,
        recent_filings=1000,
        certification_rate=1.2,
        internship_ratio=0.8,
        consistency_ratio=0.9,
    )
    assert 0 <= score <= 100


def test_score_increases_with_recency() -> None:
    low = compute_sponsorship_score(
        total_filings=100,
        recent_filings=10,
        certification_rate=0.8,
        internship_ratio=0.2,
        consistency_ratio=0.6,
    )
    high = compute_sponsorship_score(
        total_filings=100,
        recent_filings=200,
        certification_rate=0.8,
        internship_ratio=0.2,
        consistency_ratio=0.6,
    )
    assert high > low
