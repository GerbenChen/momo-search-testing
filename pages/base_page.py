class BasePage:


    def __init__(self, page):
        self.page = page

    def click(self, locator: str): 
        self.page.locator(locator).click()  

    def fill(self, locator: str, text: str): 
        self.page.locator(locator).fill(text) 

    def wait(self, milliseconds: int):
        self.page.wait_for_timeout(milliseconds)

    def screenshot(self, path: str):
        self.page.screenshot(path=path, full_page=True) 

    def get_text(self, locator: str) -> str:
        return self.page.locator(locator).inner_text()

    def is_visible(self, locator: str) -> bool:
        try:
            return self.page.locator(locator).first.is_visible() 
        except Exception:
            return False
