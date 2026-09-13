from urllib.parse import unquote
import pytest
from pages.search_page import SearchPage
from pages.search_result_page import SearchResultPage
from utils.config_reader import load_config


@pytest.mark.smoke
def test_search_keyword_persists_in_search_box(page):

    config = load_config()
    keyword = config["default_search_keyword"]
    search_page = SearchPage(page)
    search_page.open(config["base_url"])
    search_page.search(keyword)
    result_page = SearchResultPage(page)
    result_page.wait_for_results()

    assert result_page.search_input_value() == keyword, (
        f"Expected the search box to still show '{keyword}' after "
        f"landing on the results page, got: "
        f"{result_page.search_input_value()!r}"
    )

@pytest.mark.smoke
def test_search_result_page_is_well_formed(page):

    config = load_config()
    keyword = config["default_search_keyword"]
    search_page = SearchPage(page)
    search_page.open(config["base_url"])
    search_page.search(keyword)
    result_page = SearchResultPage(page)
    result_page.wait_for_results()

    decoded_url = unquote(page.url)
    assert keyword in decoded_url, (
        f"Expected the search results URL to contain the keyword, "
        f"got: {decoded_url}"
    )

    assert page.title().startswith(keyword), (
        f"Expected the page title to start with the search keyword, "
        f"got: {page.title()!r}"
    )

    assert result_page.has_filter_panel(), (
        "Expected the category/brand filter sidebar to be present"
    )

    assert result_page.has_pagination_controls(), (
        "Expected pagination controls to be present for a keyword with "
        "this many results"
    )

