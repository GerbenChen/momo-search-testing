import pytest
from pages.search_page import SearchPage
from pages.search_result_page import SearchResultPage
from utils.config_reader import load_config


def _assert_relevant_results(page, result_page, keyword: str):
    """下方兩種送出方式共用的斷言邏輯。"""
    result_page.wait_for_results()

    assert result_page.product_count() > 0, (
        f"Expected at least one product for keyword '{keyword}'"
    )

    titles = result_page.product_titles(limit=20)
    assert titles, "Expected product titles to be present on the results page"

    matching = [title for title in titles if keyword in title]
    assert matching, (
        f"Expected at least one of the sampled titles to mention "
        f"'{keyword}', got: {titles}"
    )


@pytest.mark.smoke
def test_search_with_valid_keyword_returns_relevant_results(page):
    """正常路徑：輸入關鍵字、點擊搜尋按鈕、取得搜尋結果。"""
    config = load_config()
    keyword = config["default_search_keyword"]

    search_page = SearchPage(page)
    search_page.open(config["base_url"])
    search_page.search(keyword)

    result_page = SearchResultPage(page)
    _assert_relevant_results(page, result_page, keyword)


@pytest.mark.smoke
def test_search_using_enter_returns_relevant_results(page):

    config = load_config()
    keyword = config["default_search_keyword"]
    search_page = SearchPage(page)
    search_page.open(config["base_url"])
    search_page.search_via_enter(keyword)
    result_page = SearchResultPage(page)
    _assert_relevant_results(page, result_page, keyword)

