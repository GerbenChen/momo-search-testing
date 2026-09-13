from __future__ import annotations
import json
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage


class SearchPage(BasePage):

    SEARCH_INPUT = "[data-testid='header-search-input']"
    SEARCH_BUTTON = "[data-testid='header-search-button']"
    SUGGESTION_BUTTONS = "div.mu-z-dropdown button"
    AUTOCOMPLETE_ENDPOINT = "autocompleteKeywordV3"

    def open(self, url: str):

        self.page.goto(url, wait_until="domcontentloaded")
        self.page.locator(self.SEARCH_INPUT).wait_for(state="visible")

    def get_search_placeholder(self) -> str:

        locator = self.page.locator(self.SEARCH_INPUT)
        locator.page.wait_for_function(
            """(sel) => {
                const el = document.querySelector(sel);
                return !!(el && el.getAttribute('placeholder'));
            }""",
            arg=self.SEARCH_INPUT,
        )
        return locator.get_attribute("placeholder")


    def type_keyword(self, keyword: str):

        search_input = self.page.locator(self.SEARCH_INPUT)
        search_input.click()
        search_input.fill("")
        search_input.press_sequentially(keyword, delay=50)

    def search(self, keyword: str):

        self.type_keyword(keyword)
        self.page.locator(self.SEARCH_BUTTON).click()
        self.page.wait_for_load_state("domcontentloaded")

    def search_via_enter(self, keyword: str):

        self.type_keyword(keyword)
        self.page.keyboard.press("Enter")
        self.page.wait_for_load_state("domcontentloaded")

    def submit_empty_search(self):

        self.get_search_placeholder()
        search_input = self.page.locator(self.SEARCH_INPUT)
        search_input.click()
        search_input.fill("")
        self.page.locator(self.SEARCH_BUTTON).click()
        self.page.wait_for_load_state("domcontentloaded")

    def type_keyword_and_wait_for_suggestions(self, keyword: str):
        
        seen_request_keywords: list[str | None] = []
        def record_autocomplete_request(request):
            if self.AUTOCOMPLETE_ENDPOINT in request.url:
                try:
                    body = json.loads(request.post_data or "{}")

                except ValueError:
                    seen_request_keywords.append("<unparseable request body>")

                else:
                    seen_request_keywords.append(body.get("keyword"))


        def is_response_for_this_keyword(response) -> bool:

            if self.AUTOCOMPLETE_ENDPOINT not in response.url:
                return False
            try:
                body = json.loads(response.request.post_data or "{}")
            except ValueError:
                return False
            return body.get("keyword") == keyword
            
        self.page.on("request", record_autocomplete_request)

        try:
            with self.page.expect_response(is_response_for_this_keyword):
                self.type_keyword(keyword)
        except PlaywrightTimeoutError as exc:
            raise AssertionError(
                f"momo's autocomplete request for {keyword!r} never completed "
                f"within the timeout.\n"
                f"  Autocomplete requests observed while typing: "
                f"{seen_request_keywords or 'NONE'}\n"
                f"  Text actually in the search box: "
                f"{self.page.locator(self.SEARCH_INPUT).input_value()!r}\n"
                f"If NO requests were observed, the keystrokes reached the "
                f"input but the site never issued its suggestion lookup at "
                f"all -- run diagnose_autocomplete.py to see which browser "
                f"configurations this feature does activate under."
            ) from exc
        finally:
            self.page.remove_listener("request", record_autocomplete_request)

    def get_autocomplete_suggestions(self) -> list[str]:
        suggestions = self.page.locator(self.SUGGESTION_BUTTONS)
        suggestions.first.wait_for(state="visible")
        return suggestions.all_inner_texts()

    def click_first_suggestion(self):
        suggestions = self.page.locator(self.SUGGESTION_BUTTONS)
        suggestions.first.wait_for(state="visible")
        suggestions.first.click()
        self.page.wait_for_load_state("domcontentloaded")
