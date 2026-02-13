import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

logger = logging.getLogger(__name__)

def get_driver(headless=True):
    """
    Attempts to create a Chrome driver. If it fails, attempts to create a Firefox driver.
    """
    options_chrome = webdriver.ChromeOptions()
    if headless:
        options_chrome.add_argument('--headless')

    # Enable performance logging to capture network traffic (for status codes)
    # Try both standard capability and experimental option
    prefs = {'performance': 'ALL'}
    options_chrome.set_capability('goog:loggingPrefs', prefs)
    
    # Sometimes this helps ensuring network logs are enabled
    options_chrome.add_experimental_option('perfLoggingPrefs', {'enableNetwork': True})

    try:
        logger.debug(f"Chrome Options Capabilities: {options_chrome.to_capabilities()}")
        logger.debug("Attempting to initialize Chrome driver...")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options_chrome)
        logger.debug("Chrome driver initialized successfully.")
        return driver
    except Exception as e:
        logger.warning(f"Failed to initialize Chrome driver: {e}")
        logger.debug("Attempting to initialize Firefox driver as fallback...")

    # Fallback to Firefox
    options_firefox = webdriver.FirefoxOptions()
    if headless:
        options_firefox.add_argument('--headless')

    try:
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options_firefox)
        logger.debug("Firefox driver initialized successfully.")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Firefox driver: {e}")
        raise RuntimeError("Could not initialize any browser driver (Chrome or Firefox).") from e
