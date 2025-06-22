from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_nyctmc_website():
    """
    Tests the interaction with the NYCTMC website using Selenium.
    """
    # Initialize the Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        # Navigate to the NYCTMC website
        driver.get("https://webcams.nyctmc.org/cameras-list")

        # Wait for the camera list to load
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, "camera-list")))
        print("Camera list loaded successfully.")

        # Locate and click the checkbox for a specific camera
        camera_name = "1 Ave @ 110 St"
        camera_xpath = f"//div[contains(text(), '{camera_name}')]"
        camera_element = wait.until(EC.presence_of_element_located((By.XPATH, camera_xpath)))
        
        # Find the parent row and then the checkbox
        camera_row = camera_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'camera-item')]")
        checkbox = camera_row.find_element(By.XPATH, ".//input[@type='checkbox']")
        checkbox.click()
        print(f"Checkbox for '{camera_name}' clicked.")

        # Locate and click the "View Selected" button
        view_selected_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'View Selected')]")))
        view_selected_button.click()
        print("'View Selected' button clicked.")

        # Wait for the camera feed pop-up window to appear
        popup_xpath = "//div[contains(@class, 'camera-popup')]"
        wait.until(EC.presence_of_element_located((By.XPATH, popup_xpath)))
        print("Camera feed pop-up appeared.")

        # Within this pop-up, locate and click the "expand" button
        expand_button_xpath = "//button[contains(@title, 'Expand')]"
        expand_button = wait.until(EC.element_to_be_clickable((By.XPATH, expand_button_xpath)))
        expand_button.click()
        print("Expand button clicked.")

        # Wait for the expanded camera view to load
        time.sleep(5) # Allow time for the view to expand
        print("Expanded camera view loaded.")

        # Locate and click the "X" (close) button
        close_button_xpath = "//button[contains(@title, 'Close')]"
        close_button = wait.until(EC.element_to_be_clickable((By.XPATH, close_button_xpath)))
        close_button.click()
        print("Close button clicked.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser instance
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    test_nyctmc_website()
