import os
import time
from playwright.sync_api import sync_playwright

STATE_MAP = {
    "correct": "G",
    "present": "Y",
    "absent": "B",
}

class WordleBot:
    def __init__(self, headless=False, reattempt=False, user_data_dir="./user_data"):
        self.playwright = sync_playwright().start()
        self.persistent = not reattempt  # Persistent profile by default; incognito if reattempt=True
        
        if self.persistent:
            abs_dir = os.path.abspath(user_data_dir)
            print(f"Using persistent Chrome profile at: {abs_dir}")
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=abs_dir,
                channel="chrome",
                headless=headless,
            )
            self.browser = None
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        else:
            print("Launching fresh incognito browser (reattempt mode)...")
            self.browser = self.playwright.chromium.launch(headless=headless)
            self.context = None
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

        # Click "Continue" on Welcome Back overlay if present
        for cont_selector in [
            'button:has-text("Continue")',
            'button[class*="momentButton"]',
        ]:
            try:
                btn = self.page.locator(cont_selector).first
                if btn.count() > 0 and btn.is_visible():
                    btn.click(timeout=1000)
                    time.sleep(1)
            except Exception:
                pass

        # Close the "How to Play" tutorial dialog
        for close_selector in [
            'button[aria-label="Close"]',
            '[data-testid="icon-close"]',
        ]:
            try:
                btn = self.page.locator(close_selector).first
                if btn.count() > 0 and btn.is_visible():
                    btn.click(timeout=1000)
                    time.sleep(0.5)
            except Exception:
                pass

        time.sleep(1)

    def get_existing_history(self):
        """Scrape the board for any already-submitted guesses and feedback."""
        history = []
        try:
            rows = self.page.locator('div[class*="Row-module_row__"]')
            count = rows.count()
            for i in range(count):
                row = rows.nth(i)
                tiles = row.locator('[data-testid="tile"]')
                if tiles.count() != 5:
                    break

                letters = ""
                pattern = ""
                is_submitted_row = True

                for t in range(5):
                    tile = tiles.nth(t)
                    char = tile.inner_text().strip().upper()
                    state = tile.get_attribute("data-state")

                    if not char or state not in STATE_MAP:
                        is_submitted_row = False
                        break

                    letters += char
                    pattern += STATE_MAP[state]

                if is_submitted_row and len(letters) == 5:
                    history.append((letters, pattern))
                else:
                    break
        except Exception:
            pass
        return history

    def is_already_completed(self):
        """Check if today's game has already been fully completed (won or lost)."""
        try:
            # Check if Statistics dialog is visible
            stats = self.page.locator('h2:has-text("STATISTICS")')
            if stats.count() > 0 and stats.is_visible():
                return True

            history = self.get_existing_history()
            if len(history) >= 6:
                return True
            for _, pattern in history:
                if pattern == "GGGGG":
                    return True
        except Exception:
            pass
        return False

    def is_already_played(self):
        """Deprecated alias for is_already_completed."""
        return self.is_already_completed()

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
            if self.context:
                self.context.close()
            elif self.browser:
                self.browser.close()
        except Exception:
            pass
        try:
            self.playwright.stop()
        except Exception:
            pass
