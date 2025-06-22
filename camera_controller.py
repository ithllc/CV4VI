import tempfile
import shutil
import time
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_camera_feed_screenshot(location_query: str) -> str | None:
    """
    Navigates to the NYCTMC website, finds a camera by location query,
    and captures a screenshot of its expanded feed.

    Args:
        location_query: The location to search for (e.g., "1 Ave @ 110 St").

    Returns:
        The path to the screenshot file, or None if an error occurred.
    """
    driver = None
    user_data_dir = None
    screenshot_path = "live_feed.png"
    try:
        logging.info(f"Starting camera feed capture for query: {location_query}")
        user_data_dir = tempfile.mkdtemp()
        options = Options()
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--headless")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        url = "https://webcams.nyctmc.org/cameras-list"
        logging.info(f"Navigating to {url}")
        driver.get(url)

        wait = WebDriverWait(driver, 30)

        logging.info("Locating search box.")
        # Use a more robust selector for the search box
        search_box_xpath = "//*[@id='mat-input-0']"
        search_box = wait.until(
            EC.presence_of_element_located((By.XPATH, search_box_xpath))
        )
        search_box.clear()
        search_box.send_keys(location_query)
        logging.info(f"Entered search query: {location_query}")

        logging.info("Clicking search button.")
        # Use a more robust selector for the search button
        search_button_xpath = "/html/body/app-root/body/div/div[2]/app-cameras-list/div/div[1]/app-search/form/button[1]"
        search_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, search_button_xpath))
        )
        search_button.click()

        time.sleep(2)  # Allow time for the list to filter

        logging.info(f"Locating camera checkbox for: {location_query}")
        # Split the query to search for both streets for a more flexible match
        parts = location_query.split(' @ ')
        street1 = parts[0]
        street2 = parts[1] if len(parts) > 1 else ''
        
        if street2:
            camera_xpath = f"//td[contains(normalize-space(), '{street1}') and contains(normalize-space(), '{street2}')]/ancestor::tr//mat-checkbox"
        else:
            camera_xpath = f"//td[contains(normalize-space(), '{street1}')]/ancestor::tr//mat-checkbox"

        camera_checkbox = wait.until(
            EC.element_to_be_clickable((By.XPATH, camera_xpath))
        )
        camera_checkbox.click()
        logging.info("Clicked camera checkbox.")

        logging.info("Clicking 'View Selected' button.")
        view_button_xpath = "//button[contains(., 'View Selected')]"
        view_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, view_button_xpath))
        )
        driver.execute_script("arguments[0].click();", view_button)

        logging.info("Waiting for camera feed pop-up.")
        popup_xpath = "//app-dialog-camera-preview"
        popup = wait.until(
            EC.presence_of_element_located((By.XPATH, popup_xpath))
        )

        logging.info("Clicking expand button.")
        expand_button_xpath = "//button[@mattooltip='Toggle full screen']"
        expand_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, expand_button_xpath))
        )
        expand_button.click()

        time.sleep(2)  # Wait for expanded view to load

        logging.info("Locating feed image element.")
        feed_element_xpath = '//*[@id="mat-dialog-1"]/app-dialog-camera-preview/div/div[2]/app-camera-view/div/div/img[2]'
        feed_element = wait.until(
            EC.presence_of_element_located((By.XPATH, feed_element_xpath))
        )
        logging.info("Taking screenshot.")
        feed_element.screenshot(screenshot_path)
        logging.info(f"Screenshot saved to {screenshot_path}")
        
        return screenshot_path

    except TimeoutException as e:
        logging.error(f"A timeout occurred: {e}")
        return None
    except NoSuchElementException as e:
        logging.error(f"An element was not found: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None
    finally:
        if driver:
            driver.quit()
            logging.info("WebDriver closed.")
        if user_data_dir and os.path.exists(user_data_dir):
            shutil.rmtree(user_data_dir)
            logging.info(f"Cleaned up temporary directory: {user_data_dir}")
