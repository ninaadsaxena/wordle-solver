import time
from playwright.sync_api import sync_playwright

STATE_MAP = {
    "correct": "G",
    "present": "Y",
    "absent": "B",
}

class WordleBot:
    def __init__(self, headless=False):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.page = self.browser.new_page()

    def start_game(self):
        self.page.goto("https://www.nytimes.com/games/wordle/index.html")
        time.sleep(2)

        # Dismiss GDPR / cookie consent banners
        for text in ["Accept all", "Reject all", "Accept", "Reject", "Continue"]:
            try:
                btn = self.page.locator(f'#fides-banner button:has-text("{text}")').first
                if btn.count() > 0:
                    btn.click(timeout=1000)
                    time.sleep(1)
                    break
            except Exception:
                pass

        # Click the Play button on welcome overlay
        try:
            self.page.get_by_test_id("Play").click(timeout=2000)
        except Exception:
            pass

        time.sleep(1)

        # Close the "How to Play" tutorial dialog
        for close_selector in [
            'button[aria-label="Close"]',
            '[data-testid="icon-close"]',
            "button:has-text('Continue')",
        ]:
            try:
                self.page.locator(close_selector).first.click(timeout=1000)
                time.sleep(0.5)
            except Exception:
                pass

        time.sleep(1)

    def type_guess(self, word):
        for char in word:
            self.page.keyboard.press(char.upper())
            time.sleep(0.05)
        self.page.keyboard.press("Enter")
        # Wait for tile animation to finish
        time.sleep(2.5)

    def clear_row(self, word_length=5):
        """Backspace out an invalid/rejected guess."""
        for _ in range(word_length):
            self.page.keyboard.press("Backspace")
            time.sleep(0.05)

    def is_rejected(self, turn_index):
        """Check if NYT rejected the guess (tiles remain tbd/empty instead of flipping)."""
        row = self.page.locator('div[class*="Row-module_row__"]').nth(turn_index)
        tiles = row.locator('[data-testid="tile"]')
        if tiles.count() != 5:
            return True
        states = [tiles.nth(i).get_attribute("data-state") for i in range(5)]
        return not any(s in STATE_MAP for s in states)

    def read_feedback(self, turn_index):
        """Read tile states for a row and return GYB pattern string."""
        row = self.page.locator('div[class*="Row-module_row__"]').nth(turn_index)
        tiles = row.locator('[data-testid="tile"]')
        if tiles.count() != 5:
            return None

        feedback_str = ""
        for i in range(5):
            state = tiles.nth(i).get_attribute("data-state")
            feedback_str += STATE_MAP.get(state, "B")

        return feedback_str

    def close(self):
        try:
            self.browser.close()
        except Exception:
            pass
        try:
            self.playwright.stop()
        except Exception:
            pass
