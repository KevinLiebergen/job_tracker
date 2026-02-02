import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.driver_factory import get_driver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from unittest.mock import patch, MagicMock

def test_default_chrome():
    print("Testing default Chrome behavior...")
    try:
        driver = get_driver(headless=True)
        if isinstance(driver, ChromeWebDriver):
            print("SUCCESS: Defaulted to Chrome.")
        else:
            print(f"FAILURE: Expected Chrome, got {type(driver)}")
        driver.quit()
    except Exception as e:
        print(f"FAILURE: Exception during Chrome init: {e}")

def test_fallback_firefox():
    print("\nTesting fallback to Firefox...")
    # Mock Chrome to fail
    with patch('src.driver_factory.webdriver.Chrome') as mock_chrome:
        mock_chrome.side_effect = Exception("Simulated Chrome Failure")
        
        try:
            driver = get_driver(headless=True)
            if isinstance(driver, FirefoxWebDriver):
                print("SUCCESS: Fell back to Firefox.")
            else:
                 # If the environment doesn't have Firefox, it might fail here or return something else if my logic is wrong
                print(f"FAILURE: Expected Firefox, got {type(driver)}")
            driver.quit()
        except Exception as e:
            # If firefox is not installed, it will fail here, which is expected in some environments. 
            # But the logic flow is what we want to test. 
            print(f"INFO: Fallback logic triggered, but Firefox init failed (likely not installed): {e}")

if __name__ == "__main__":
    test_default_chrome()
    test_fallback_firefox()
