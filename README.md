# AstroFlow 🚀

Welcome to AstroFlow! This application lets you design and visualize complex space missions involving multiple orbits, satellites, and a servicing tanker. Configure your mission parameters and watch the simulation unfold!

## What Can You Do with AstroFlow?

*   **Design Your Mission:** Easily set up your space environment using a simple web form. Define:
    *   Launch locations on Earth.
    *   Multiple orbital paths around Earth (by radius).
    *   Satellites positioned in specific orbits.
*   **Visualize the Journey:** Watch an animated simulation showing the main tanker spacecraft's journey:
    *   Launching from Earth.
    *   Performing orbital transfers (Hohmann transfers) to reach different altitudes.
    *   Deploying smaller shuttle craft in each target orbit.
    *   Returning through the orbits, recovering the shuttles.
    *   Performing a final reentry and landing.
*   **Track Key Events:** Follow the major steps of the mission as they happen through status updates during the simulation.
*   **Review Configuration:** Easily see the parameters you submitted for the simulation run.

## How It Works

1.  **Configure:** You start by filling out the 'AstroFlow Configuration' form, adding details about your desired launchpads, orbits, and satellites.
2.  **Submit:** Click "Generate Configuration". Your setup is sent to the server.
3.  **Simulate:** The server uses your configuration to run a detailed physics-based simulation of the entire mission sequence in the background.
4.  **Visualize:** You're automatically taken to the simulation page where you can (usually) see an animation of the tanker's path and key mission events unfold based on the complex calculations performed.

## Getting Started (Running Locally)

Want to try AstroFlow on your own computer?

1.  **Download:** Get the project files (e.g., using `git clone` or downloading a zip).
2.  **Setup Environment:** It's best to use a Python virtual environment.
3.  **Install Requirements:** Install the necessary Python packages (usually listed in a `requirements.txt` file) using pip:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Environment Key:** Create a `.env` file in the main project folder and add a line like `SECRET_KEY='your_very_secret_random_string_here'` (replace with your own secret string). This is needed for the web application to remember your configuration between steps.
5.  **Run:** Start the application from your terminal:
    ```bash
    python main.py
    ```
6.  **Access:** Open your web browser to `http://127.0.0.1:5000/`.

## Using the Application

1.  Navigate to the main page (`http://127.0.0.1:5000/`).
2.  Use the '+' buttons to add launchpads, orbits, and satellites. Fill in the required details (angles, radii).
3.  Assign satellites to the orbits you've created.
4.  Click "Generate Configuration".
5.  You will be redirected to the simulation page. Observe the status messages and the visualization (if implemented visually). You can toggle the visibility of your submitted configuration data on this page.

## Technology

AstroFlow is built using:

*   **Python:** For the core simulation logic and web server.
*   **Flask:** A Python web framework to handle web requests and pages.
*   **HTML/CSS/JavaScript:** For the user interface (form, simulation display).
*   **PixiJS:** A JavaScript library used for rendering graphics (like the starry background).
*   **NumPy:** A Python library used for numerical calculations.
*   **Matplotlib:** (Used internally by the algorithm for plotting, not directly by the web interface).

## License

This project is licensed under the MIT License. See the LICENSE file for details.