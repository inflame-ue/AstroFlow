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