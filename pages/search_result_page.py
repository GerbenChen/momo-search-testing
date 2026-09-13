import re
from typing import Optional
from urllib.parse import urlparse, parse_qs
from pages.base_page import BasePage


class SearchResultPage(BasePage):

    PRODUCT_ITEM = "li.listAreaLi"
    PRODUCT_TITLE = "h3.prdName"
    NO_EXACT_MATCH_BANNER = "text=很抱歉，查無符合"
    PAGE_NUMBER_INDICATOR = ".page-number"
    FILTER_PANEL = ".attributesListArea"
    SEARCH_INPUT_ON_RESULTS = "#header-search-input"
    PAGINATION_LINK = ".pagination .pagination-link:visible"

    def wait_for_results(self, timeout: int = 15000):

        ready = self.page.locator(self.PRODUCT_ITEM).or_(
            self.page.locator(self.NO_EXACT_MATCH_BANNER)
        ).first
        ready.wait_for(state="visible", timeout=timeout)


    def product_count(self) -> int:

        return self.page.locator(self.PRODUCT_ITEM).count()

    def product_titles(self, limit: Optional[int] = None) -> list[str]:

        titles = self.page.locator(
            f"{self.PRODUCT_ITEM} {self.PRODUCT_TITLE}"
        ).all_inner_texts()
        return titles[:limit] if limit else titles


    def search_input_value(self) -> str:

        return self.page.locator(self.SEARCH_INPUT_ON_RESULTS).input_value()

    def has_filter_panel(self) -> bool:

        return self.page.locator(self.FILTER_PANEL).first.is_visible()


    def has_pagination_controls(self) -> bool:

        return self.page.locator(self.PAGINATION_LINK).count() > 0

    def is_fuzzy_fallback(self) -> bool:

        query = parse_qs(urlparse(self.page.url).query)
        is_fuzzy_param = query.get("_isFuzzy", ["0"])[0] == "1"
        has_banner = self.page.locator(self.NO_EXACT_MATCH_BANNER).count() > 0
        return is_fuzzy_param or has_banner

    def current_page_and_total(self) -> tuple[int, int]:

        text = self.page.locator(self.PAGE_NUMBER_INDICATOR).first.inner_text()
        match = re.search(r"(\d+)\D+(\d+)", text)
        assert match, f"Could not parse page indicator text: {text!r}"
        return int(match.group(1)), int(match.group(2))


    def current_page_from_url(self) -> int:

        query = parse_qs(urlparse(self.page.url).query)
        return int(query.get("curPage", ["1"])[0])


    def go_to_page(self, page_number: int):

        links = self.page.locator(self.PAGINATION_LINK)
        target = links.filter(has_text=re.compile(rf"^{page_number}$")).first
        target.scroll_into_view_if_needed()
        target.dispatch_event("click")
        self.page.wait_for_function(
            "expected => new URLSearchParams(location.search).get('curPage') === String(expected)",
            arg=page_number,
        )
