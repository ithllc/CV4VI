# Next Steps

With the successful completion of the initial Proof of Concept, the following next steps can be considered to enhance and productionize the application:

### 1. Refinement and Robustness
*   **Advanced Location Matching:** Implement a more sophisticated location-to-camera matching algorithm. This could involve using a geocoding API to convert user queries to coordinates and finding the nearest camera from a pre-compiled list of camera locations.
*   **Selenium Hardening:** Continue to refine Selenium selectors and add more comprehensive error handling to make the web automation more resilient to changes in the NYCTMC website.
*   **Configuration Management:** Move hardcoded values (like XPaths or URLs) into a separate configuration file.

### 2. Model and Analysis Improvement
*   **VLM Evaluation:** Test with other Vision Language Models to compare performance, accuracy, and latency.
*   **Image Pre-processing:** Add steps to pre-process the captured image (e.g., enhance contrast, brightness) to improve the VLM's analysis, especially for nighttime or low-light conditions.
*   **Confidence Scoring:** Have the VLM provide a confidence score for its analysis. If the confidence is low, the system could state that it is unsure.

### 3. User Experience (UX) Enhancements
*   **Lower Latency:** Investigate methods to reduce the end-to-end latency. This could involve optimizing model loading, using a faster Selenium grid, or exploring ways to stream data between components more effectively.
*   **Interactive Map:** Add a map to the Streamlit UI showing the location of the selected camera.
*   **Accessibility Improvements:** Conduct formal accessibility testing to ensure the application is usable by a wider range of visually impaired users.

### 4. Deployment and Scalability
*   **Containerization:** Package the application in a Docker container for easier deployment.
*   **Cloud Deployment:** Deploy the application to a cloud service (e.g., Streamlit Cloud, AWS, GCP, Azure) for public access.
*   **Dedicated Infrastructure:** For a production system, move away from running Selenium locally on the same machine and use a dedicated, scalable Selenium Grid.
