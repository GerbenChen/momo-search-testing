import pytest
from utils.config_reader import load_config


@pytest.mark.api
@pytest.mark.smoke
def test_autocomplete_api_returns_suggestions_for_a_valid_keyword(api_context):

    config = load_config()
    keyword = config["default_search_keyword"]

    response = api_context.post(
        config["autocomplete_api_url"], data={"keyword": keyword}
    )

    assert response.status == 200, (
        f"Expected HTTP 200 from the autocomplete endpoint, got "
        f"{response.status}"
    )

    body = response.json()

    assert body["success"] is True, f"Expected success=true, got: {body!r}"
    assert body["resultCode"] == "200", (
        f"Expected resultCode '200', got {body['resultCode']!r}"
    )

    suggestions = body["resultList"]
    assert suggestions, (
        f"Expected at least one suggestion for '{keyword}', got an empty list"
    )

    for item in suggestions:
        assert item.get("text"), f"Suggestion missing 'text': {item!r}"
        assert item.get("action", {}).get("actionValue"), (
            f"Suggestion missing action.actionValue (the value the UI "
            f"searches for when clicked): {item!r}"
        )


    assert any(keyword in item["text"] for item in suggestions), (
        f"Expected at least one suggestion related to '{keyword}', got: "
        f"{[item['text'] for item in suggestions]}"
    )


@pytest.mark.api
def test_autocomplete_api_returns_empty_list_where_the_ui_shows_fallback_products(
    api_context,
):

    config = load_config()
    keyword = config["no_match_keyword"]
    response = api_context.post(
        config["autocomplete_api_url"], data={"keyword": keyword}
    )
    assert response.status == 200, (
        f"A no-match keyword should still be a successful request, got "
        f"HTTP {response.status}"
    )

    body = response.json()
    assert body["success"] is True, (
        f"A no-match keyword is not an error condition for this endpoint; "
        f"expected success=true, got: {body!r}"
    )

    assert body["resultList"] == [], (
        f"Expected no suggestions for a keyword crafted not to exist, got: "
        f"{body['resultList']!r}"
    )


@pytest.mark.api
def test_autocomplete_api_reports_invalid_input_in_the_body_not_the_status(
    api_context,
):

    config = load_config()
    response = api_context.post(
        config["autocomplete_api_url"], data={"keyword": ""}
    )

    assert response.status == 200, (
        f"This endpoint signals bad input in the body, not the HTTP "
        f"status -- expected 200, got {response.status}"
    )

    body = response.json()
    assert body["success"] is False, (
        f"Expected success=false for an empty keyword, got: {body!r}"
    )
    assert body["resultCode"] == "400", (
        f"Expected the in-body error code '400' for an empty keyword, got "
        f"{body['resultCode']!r}"
    )

