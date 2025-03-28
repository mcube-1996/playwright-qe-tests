import logging
from playwright.sync_api import sync_playwright
import random

#adding comment
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SauceDemoTest:
    def __init__(self):
        self.login_url = "https://www.saucedemo.com/v1/"
        self.username = "standard_user"
        self.password = "secret_sauce"

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
    
    def login(self):
        self.page.goto(self.login_url)
        self.page.fill("#user-name", self.username)
        self.page.fill("#password", self.password)
        self.page.click("#login-button")
        if self.page.url == "https://www.saucedemo.com/v1/inventory.html":
            logging.info("Login successful")
        else:
            logging.info("Login failed")

    def add_products_to_cart(self):
        products = self.page.query_selector_all(".inventory_item button")
        if len(products) < 2:
            logging.info("Not enough products found!")
            return
        
        # Randomly select 2 unique products
        selected_products = random.sample(products, 2)

        for product in selected_products:
            product.click()

        cart_count = self.page.inner_text(".shopping_cart_badge")
        if int(cart_count) == 2:
            logging.info("Cart updated correctly with 2 random items")
        else:
            logging.info("Cart count mismatch!")

    def checkout_process(self):
        self.page.click(".shopping_cart_link")
        self.page.click("a.btn_action.checkout_button")
        self.page.fill("#first-name", "Milton")
        self.page.fill("#last-name", "M")
        self.page.fill("#postal-code", "12345")
        self.page.click("input.btn_primary.cart_button")
        total_price = self.page.inner_text(".summary_total_label")
        if "Total" in total_price:
            logging.info(f"Checkout price validated: {total_price}")
        self.page.click("//a[contains(text(), 'FINISH')]")
        success_message = self.page.inner_text(".complete-header")
        if "THANK YOU FOR YOUR ORDER" in success_message:
            logging.info("Checkout completed successfully")
        else:
            logging.info("Checkout failed!")

    def run_tests(self):
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                logging.info(f"=== Running Web UI Tests (Attempt {attempt}/{max_attempts}) ===")
                self.login()
                self.add_products_to_cart()
                self.checkout_process()
                logging.info("All tests passed successfully!")
                break  # Exit loop on success
            except Exception as e:
                logging.error(f"Test attempt {attempt} failed: {e}")
                if attempt == max_attempts:
                    logging.error("Max attempts reached. Tests failed.")
        self.browser.close()
        self.playwright.stop()

if __name__ == "__main__":
    test = SauceDemoTest()
    test.run_tests()
