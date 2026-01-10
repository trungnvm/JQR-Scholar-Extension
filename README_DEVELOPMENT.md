# Development Environment Setup

This document provides instructions for setting up the development environment for the Scholar Extension Trung project.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Setup Instructions

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <repository-url>
    cd scholar_extention_trung
    ```

2.  **Create a virtual environment**:
    It is recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment**:
    -   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    -   On Windows:
        ```bash
        venv\Scripts\activate
        ```

4.  **Install dependencies**:
    Install the required Python packages using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

## Project Structure

- `requirements.txt`: List of Python dependencies.
- `.gitignore`: Files and directories to be ignored by Git.
- `README_DEVELOPMENT.md`: This setup guide.

## Development Workflow

- Always ensure your virtual environment is activated before running the project or installing new packages.
- If you add new dependencies, remember to update the `requirements.txt` file:
    ```bash
    pip freeze > requirements.txt
    ```
