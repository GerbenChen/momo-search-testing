from urllib.parse import quote
import pytest
from pages.search_page import SearchPage
from pages.search_result_page import SearchResultPage
from utils.config_reader import load_config


def test_empty_search_falls_back_to_placeholder_keyword(page):

    config = load_config()
    search_page = SearchPage(page)
    search_page.open(config["base_url"])
    placeholder = search_page.get_search_placeholder()
    assert placeholder, "Expected the search box to expose placeholder text"
    search_page.submit_empty_search()

    result_page = SearchResultPage(page)
    result_page.wait_for_results()
    assert page.title().startswith(placeholder), (
        f"Expected an empty search to fall back to the placeholder "
        f"'{placeholder}', got title: {page.title()!r}"
    )
    assert result_page.product_count() > 0


def test_direct_search_url_without_keyword_shows_not_found_page(page):

    config = load_config()
    page.goto(config["search_base_url"])
    assert "err404" in page.url.lower() or "404" in page.url.lower(), (
        f"Expected navigating to a keyword-less search URL to redirect "
        f"to momo's not-found page, got: {page.url}"
    )


def test_no_exact_match_falls_back_to_fuzzy_recommendations(page):

    config = load_config()
    keyword = config["no_match_keyword"]
    search_page = SearchPage(page)
    search_page.open(config["base_url"])
    search_page.search(keyword)

    result_page = SearchResultPage(page)
    result_page.wait_for_results()
    assert result_page.is_fuzzy_fallback(), (
        "Expected a nonsense keyword to trigger momo's fuzzy-search fallback"
    )

    assert result_page.product_count() > 0, (
        "Expected the fuzzy fallback to still show recommended products, "
        "not an empty page"
    )


def test_script_tag_search_is_rejected_not_reflected(page):

    config = load_config()
    payload = config["xss_payload"]
    search_url = config["search_base_url"] + quote(payload, safe="")
    response = page.goto(search_url)

    if response is not None and response.status == 200:
        assert payload not in page.content(), (
            "Search payload was reflected unescaped into the page "
            "(possible XSS)"
        )
    else:
        status = response.status if response else None
        assert status is not None and 400 <= status < 500, (
            f"Expected the script-tag search to be rejected with a 4xx "
            f"status, got {status}"
        )



@pytest.mark.parametrize(
    "config_key",
    ["keyword_with_whitespace", "keyword_with_special_characters"],
    ids=["leading-trailing-whitespace", "embedded-punctuation"],
)
def test_search_with_spaces_and_special_characters_still_returns_results(
    page, config_key
):

    config = load_config()
    keyword = config[config_key]
    search_page = SearchPage(page)
    search_page.open(config["base_url"])
    search_page.search(keyword)
    result_page = SearchResultPage(page)
    result_page.wait_for_results()

    assert not result_page.is_fuzzy_fallback(), (
        f"Expected {keyword!r} to still return real matches, not trigger "
        f"the fuzzy-search fallback"
    )
    assert result_page.product_count() > 0, (
        f"Expected at least one product for keyword {keyword!r}"
    )

