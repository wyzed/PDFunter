# PDFunter
PDFunter is a Python script designed to automate the process of finding and downloading PDF files from a specified website. It uses Selenium WebDriver to navigate the website and search for PDF files based on a user-defined query.

Automates the process of finding and downloading PDF files from a specified website. Technology: Uses Selenium for web scraping, PyPDF2 for PDF processing.

Key Components

Selenium WebDriver: Automates web browser interaction to search for and retrieve PDF links from a website.
PyPDF2: Processes PDF files for safety, removing potentially harmful elements.
Requests: Handles HTTP requests to download PDF files.
File Handling: Manages file names and directories, ensuring safe and organized storage of downloaded files.

Workflow Description

Initialization: Sets up browser options for Selenium and defines the main website URL and search parameters.
    File Sanitization and Safety Checks:
        Sanitizes file names to avoid filesystem issues.
        Checks for existing files to prevent re-downloading.
        Processes downloaded PDFs to remove potentially harmful elements.
    PDF Link Retrieval:
        Uses Selenium to interact with the website.
        Attempts to use a search box if available; otherwise, scans the page's source code for PDF links.
    PDF Downloading:
        Downloads new PDF files found in the search.
        Incorporates random wait times between requests to avoid overloading the server.
        Checks for embedded files in PDFs and skips downloading if found.
        Converts downloaded PDFs into a safer format by removing certain elements.
    Progress Tracking: Uses tqdm for visual progress tracking of the downloading process.
    Rate Limiting and Request Management:
        Implements rate limiting to control the number of requests sent to the server.
        Randomizes intervals between requests and the maximum number of requests before a longer wait.

Usage :
    Run the script and enter a search query when prompted.
    The script will automatically handle the searching, downloading, and processing of PDF files.

     $ python PDFunterv1.py

Safety and Efficiency Features :
    Rate Limiting: Prevents server overload and potential IP blocking.
    File Safety Checks: Ensures that only new and safe PDFs are downloaded and stored.
    User Feedback: Provides real-time updates on the script's progress and actions.

![image](https://github.com/wyzed/PDFunter/assets/1706569/0e4d43c7-e9b7-4fd4-aecf-9dd071194e41)



    
