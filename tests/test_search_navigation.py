import pytest
from pages.search_page import SearchPage
from pages.search_result_page import SearchResultPage
from utils.config_reader import load_config



@pytest.mark.headed
def test_autocomplete_suggestions_appear_and_navigate_correctly(page):

    config = load_config()
    keyword = config["default_search_keyword"]
    search_page = SearchPage(page)
    search_page.open(config["base_url"])
    search_page.type_keyword_and_wait_for_suggestions(keyword)

    suggestions = search_page.get_autocomplete_suggestions()
    assert suggestions, "Expected at least one autocomplete suggestion"
    assert any(keyword in suggestion for suggestion in suggestions), (
        f"Expected at least one suggestion to relate to '{keyword}', "
        f"got: {suggestions}"
    )

    chosen = suggestions[0]
    search_page.click_first_suggestion()
    result_page = SearchResultPage(page)
    result_page.wait_for_results()
    assert result_page.product_count() > 0
    assert page.title().startswith(chosen), (
        f"Expected the result page title to start with the chosen "
        f"suggestion '{chosen}', got title: {page.title()!r}"
    )


@pytest.mark.smoke
def test_pagination_navigates_to_next_page(page):

    config = load_config()
    keyword = config["default_search_keyword"]
    search_page = SearchPage(page)
    search_page.open(config["base_url"])
    search_page.search(keyword)

    result_page = SearchResultPage(page)
    result_page.wait_for_results()
    start_page, total_pages = result_page.current_page_and_total()
    assert start_page == 1
    assert total_pages > 1, (
        "Test keyword should have more than one page of results for "
        "this test to be meaningful"
    )

    result_page.go_to_page(2)
    assert result_page.current_page_from_url() == 2
    current_page, _ = result_page.current_page_and_total()
    assert current_page == 2

