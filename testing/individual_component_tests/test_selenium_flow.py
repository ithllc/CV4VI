import tempfile
import shutil
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

def get_camera_screenshot(camera_name: str, screenshot_path: str):
    """Capture a screenshot of a specific camera from the NYCTMC website."""
    driver = None
    user_data_dir = None
    try:
        user_data_dir = tempfile.mkdtemp()
        print(f"Created temporary user data directory: {user_data_dir}")
        options = Options()
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--headless")  # Run in headless mode
        print("Initializing WebDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        url = "https://webcams.nyctmc.org/cameras-list"
        print(f"Navigating to {url}")
        driver.get(url)

        wait = WebDriverWait(driver, 30)

        # Wait for the search box to be present and enter search text
        search_box_xpath = "//*[@id='mat-input-0']"
        print(f"Waiting for search box with XPath: {search_box_xpath}")
        search_box = wait.until(
            EC.presence_of_element_located((By.XPATH, search_box_xpath))
        )
        search_box.send_keys(camera_name)
        print(f"Entered search text: {camera_name}")

        # Click the search button
        search_button_xpath = "/html/body/app-root/body/div/div[2]/app-cameras-list/div/div[1]/app-search/form/button[1]"
        print(f"Waiting for search button with XPath: {search_button_xpath}")
        search_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, search_button_xpath))
        )
        search_button.click()
        print("Clicked search button.")

        # Wait for the camera list to update
        time.sleep(2) # Give it a moment to filter

        # Select a camera using a more robust XPath
        camera_xpath = f"//td[normalize-space()='{camera_name}']/ancestor::tr//mat-checkbox"
        print(f"Waiting for camera checkbox with XPath: {camera_xpath}")
        camera_checkbox = wait.until(
            EC.element_to_be_clickable((By.XPATH, camera_xpath))
        )
        camera_checkbox.click()
        print(f"Selected camera: {camera_name}")

        # Click the "View Selected" button
        view_button_xpath = "//button[contains(., 'View Selected')]"
        print(f"Waiting for 'View Selected' button with XPath: {view_button_xpath}")
        view_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, view_button_xpath))
        )
        driver.execute_script("arguments[0].click();", view_button)
        print("Clicked 'View Selected' button.")

        # Wait for the camera feed pop-up
        popup_xpath = "//app-dialog-camera-preview"
        print(f"Waiting for popup with XPath: {popup_xpath}")
        popup = wait.until(
            EC.presence_of_element_located((By.XPATH, popup_xpath))
        )
        print("Camera feed pop-up appeared.")

        # Click the expand button
        expand_button_xpath = "//button[@mattooltip='Toggle full screen']"
        print(f"Waiting for expand button with XPath: {expand_button_xpath}")
        expand_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, expand_button_xpath))
        )
        expand_button.click()
        print("Clicked expand button.")

        # Wait for the expanded view to be stable
        time.sleep(2) 
        print("Waited for expanded view.")

        # Take a screenshot of the camera feed
        screenshot = driver.get_screenshot_as_png()
        with open(screenshot_path, "wb") as f:
            f.write(screenshot)
        print(f"Screenshot saved to {screenshot_path}")

        # Close the pop-up
        close_button_xpath = "//button[@mattooltip='Close dialog']"
        print(f"Waiting for close button with XPath: {close_button_xpath}")
        close_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, close_button_xpath))
        )
        close_button.click()
        print("Closed the pop-up.")

        print("Screenshot capture completed successfully!")
        return screenshot_path

    except TimeoutException as e:
        print(f"A timeout occurred: {e}")
        if driver:
            print(driver.page_source)
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        if driver:
            driver.quit()
            print("WebDriver closed.")
        if user_data_dir:
            try:
                shutil.rmtree(user_data_dir)
                print(f"Removed temporary user data directory: {user_data_dir}")
            except Exception as e:
                print(f"Error removing user data directory: {e}")

if __name__ == "__main__":
    get_camera_screenshot("1 Ave @ 110 St", "camera_feed.png")
