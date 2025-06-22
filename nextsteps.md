## Next Steps

**Phase 2: Web Automation & Camera Image Capture**

1.  **Restructure Project:**
    *   Create a new `AICHackathon/app` directory for the main application files.
    *   Move `testing/test_integration.py` to `app/main.py`.
    *   Move `testing/test_moondream_helper.py` to `app/moondream_helper.py`.
    *   Move `testing/individual_component_tests/test_selenium_flow.py` to `app/camera_handler.py`.
    *   Update all imports to reflect the new structure.

2.  **Enhance Selenium Workflow (`camera_handler.py`):**
    *   Modify the `get_camera_screenshot` function to accept a natural language `location_query` (e.g., "1st Avenue and 110th Street") instead of a hardcoded camera name.
    *   Implement logic to iterate through the camera list on the NYCTMC website and find the camera that best matches the user's query. This will likely involve text parsing and string similarity matching.
    *   Refactor the function to return the path to the captured screenshot or `None` if a camera cannot be found.

3.  **Implement Robust Error Handling:**
    *   Wrap the Selenium interactions in `try...except` blocks to gracefully handle `TimeoutException` and `NoSuchElementException`.
    *   Provide clear logging and user-facing error messages when the camera feed cannot be accessed or a match for the location is not found.

4.  **Update Main Application (`main.py`):**
    *   Integrate the enhanced `get_camera_screenshot` function.
    *   Update the Streamlit UI to take a natural language location query from the user (either via text input or voice transcription).
    *   Handle the case where `get_camera_screenshot` returns `None` by displaying an appropriate error message to the user.
