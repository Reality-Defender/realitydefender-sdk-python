from realitydefender.detection.results import format_result


def test_format_result_includes_heatmaps_for_artificial_image_models() -> None:
    response = {
        "requestId": "req-1",
        "mediaType": "IMAGE",
        "resultsSummary": {"status": "FAKE", "metadata": {"finalScore": 95}},
        "models": [
            {"name": "rd-cedar-img", "status": "FAKE"},
            {"name": "rd-elm-img", "status": "AUTHENTIC"},
            {"name": "rd-img-ensemble", "status": "FAKE"},
        ],
        "heatmaps": {
            "rd-cedar-img": "https://example.com/heatmap.png",
            "rd-elm-img": "https://example.com/authentic.png",
            "rd-img-ensemble": "https://example.com/ensemble.png",
            "rd-missing-img": "https://example.com/missing.png",
        },
    }

    result = format_result(response)

    assert result["heatmaps"] == {"rd-cedar-img": "https://example.com/heatmap.png"}


def test_format_result_nulls_empty_heatmaps() -> None:
    response = {
        "requestId": "req-1",
        "mediaType": "IMAGE",
        "resultsSummary": {"status": "FAKE", "metadata": {"finalScore": 95}},
        "models": [{"name": "rd-cedar-img", "status": "FAKE"}],
        "heatmaps": {"rd-cedar-img": ""},
    }

    result = format_result(response)

    assert result["heatmaps"] is None


def test_format_result_ignores_heatmaps_for_non_image() -> None:
    response = {
        "requestId": "req-1",
        "mediaType": "VIDEO",
        "resultsSummary": {"status": "FAKE", "metadata": {"finalScore": 95}},
        "models": [{"name": "rd-vid-ensemble", "status": "FAKE"}],
        "heatmaps": {"rd-vid-ensemble": "https://example.com/heatmap.png"},
    }

    result = format_result(response)

    assert result["heatmaps"] is None
