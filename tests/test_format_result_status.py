from realitydefender.detection.results import IN_PROGRESS_STATUSES, format_result


def test_format_result_null_summary_uses_overall_status_downloading() -> None:
    result = format_result(
        {
            "requestId": "req-social",
            "overallStatus": "DOWNLOADING",
            "resultsSummary": None,
            "models": [],
        }
    )
    assert result["status"] == "DOWNLOADING"


def test_format_result_null_summary_uses_overall_status_analyzing() -> None:
    result = format_result(
        {
            "requestId": "req-social",
            "overallStatus": "ANALYZING",
            "resultsSummary": None,
            "models": [],
        }
    )
    assert result["status"] == "ANALYZING"


def test_format_result_explicit_downloading_in_summary() -> None:
    result = format_result(
        {
            "requestId": "req-social",
            "overallStatus": "DOWNLOADING",
            "resultsSummary": {
                "status": "DOWNLOADING",
                "metadata": {"finalScore": None},
            },
            "models": [],
        }
    )
    assert result["status"] == "DOWNLOADING"


def test_in_progress_statuses_match_api_in_progress_values() -> None:
    assert IN_PROGRESS_STATUSES == frozenset({"ANALYZING", "DOWNLOADING"})
