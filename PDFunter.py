import os, re, sys, time, random, requests, urllib.parse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from colorama import Fore, Style
import PyPDF2

options = Options() 
options.add_argument("-headless") 

custom_prompt = f"{Fore.LIGHTGREEN_EX}PDFunter@local:{Style.RESET_ALL}{Fore.BLUE}~{Style.RESET_ALL}$ "
script_description = """
PDFunter is a Python script designed to automate the process of finding and downloading PDF files from a specified website. 
It uses Selenium WebDriver to navigate the website and search for PDF files based on a user-defined query.

How it works:
1. The user provides a search query (e.g., '*.pdf') to specify the type of PDF files to look for.
2. PDFunter first attempts to use a search box on the website (if available) to find PDF links.
3. If a search box is not available, or no results are found, PDFunter then searches the website's source code directly for PDF links.
4. Each found PDF file is downloaded to a local 'downloads' directory.
5. The script implements rate limiting to avoid overwhelming the server, with random intervals between downloads.
6. If a PDF file already exists in the 'downloads' directory, it will not be downloaded again.

To use PDFunter, simply run the script and enter your search query when prompted.
"""
print(custom_prompt + script_description)

def is_valid_url(url):
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_website_url():
    while True:
        url = input(custom_prompt + f"Enter the website URL: ").strip()
        if is_valid_url(url):
            return url
        else:
            print(custom_prompt + "Invalid URL. Please enter a valid URL.")

main_website_url = get_website_url()
search_box_id = 'search_text'
search_query = input(custom_prompt + "Enter your search query (e.g., '*.pdf'): ").strip()
if not search_query:
    search_query = "*.pdf"

REQUEST_INTERVAL = random.randint(1, 3)
MAX_REQUESTS = random.randint(5, 10)
LONG_WAIT = random.randint(5, 10)

def sanitize_filename(file_name):
    sanitized_name = re.sub(r"[^\w.]", "_", file_name)
    sanitized_name = re.sub(r"_+", "_", sanitized_name)
    sanitized_name = sanitized_name.strip("_")
    return sanitized_name

def safe_file_exists(file_name, download_dir):
    decoded_file_name = urllib.parse.unquote(file_name)
    truncated_name = truncate_filename(decoded_file_name)
    sanitized_file_name = sanitize_filename(truncated_name)
    safe_file_name = 'safe_' + sanitized_file_name
    safe_file_path = os.path.join(download_dir, safe_file_name)
    return os.path.exists(safe_file_path)


def safer_pdf(input_path, output_path):
    try:
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()

            for page in reader.pages:
                writer.add_page(page)
                if '/AA' in page:
                    del page['/AA']
                if '/OpenAction' in page:
                    del page['/OpenAction']

            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

        return True
    except Exception as e:
        print(custom_prompt + f"Error processing PDF: {e}")
        return False

def contains_embedded_files(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            if '/EmbeddedFiles' in page['/Resources']:
                return True
        if '/Names' in reader.trailer['/Root']:
            names = reader.trailer['/Root']['/Names']
            if '/EmbeddedFiles' in names:
                return True
        return False
    
def check_all_files_safer(download_dir):
    all_files = os.listdir(download_dir)

    for file in all_files:
        if file.startswith('safe_'):
            continue

        file_path = os.path.join(download_dir, file)
        if file.endswith('.temp'):
            os.remove(file_path)
            print(custom_prompt + f"Removed temporary file: {file}")
            continue

        sanitized_file_name = sanitize_filename(file)
        sanitized_file_path = os.path.join(download_dir, sanitized_file_name)

        if sanitized_file_name != file:
            os.rename(file_path, sanitized_file_path)
            file_path = sanitized_file_path

        if not file.startswith('safe_'):
            safe_file_path = os.path.join(download_dir, 'safe_' + sanitized_file_name)

            if 'safe_' + sanitized_file_name not in all_files:
                if safer_pdf(file_path, safe_file_path):
                    os.remove(file_path)
                else:
                    print(custom_prompt + f"Failed to process file: {sanitized_file_name}")

download_dir = os.path.join(os.getcwd(), 'downloads')
check_all_files_safer(download_dir)


def get_pdf_links_with_selenium(url, search_box_id, search_query):
    driver = webdriver.Firefox(options=options)
    driver.get(url)

    pdf_links = []
    search_box_found = False

    try:
        try:
            # Attempt to find and use the search box
            search_box_xpath = f"//input[contains(@id, '{search_box_id}') or contains(@class, '{search_box_id}')]"
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, search_box_xpath)))
            search_box = driver.find_element(By.XPATH, search_box_xpath)
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            search_box_found = True
        except TimeoutException:
            print("Search box not found or timeout occurred. Scanning page for links.")

        # Finding and processing PDF links
        for link in driver.find_elements(By.TAG_NAME, 'a'):
            href = link.get_attribute('href')
            if href:
                # Check for direct PDF links or arXiv pattern
                if href.lower().endswith('.pdf') or ('arxiv.org/pdf/' in href and 'arxiv.org' in url):
                    if 'arxiv.org/pdf/' in href and not href.lower().endswith('.pdf'):
                        href += '.pdf'  # Append '.pdf' for arXiv links
                    pdf_links.append(href)

    except TimeoutException:
        print("Timeout occurred - either the page did not load properly.")

    finally:
        driver.quit()

    return pdf_links




def truncate_filename(filename, max_length=250):
    """ Truncate the filename to a specified maximum length """
    if len(filename) > max_length:
        extension = filename.split('.')[-1]
        truncated = filename[:max_length - len(extension) - 1]
        return truncated + '.' + extension
    return filename


def download_pdf(url, file_name):
    download_dir = os.path.join(os.getcwd(), 'downloads')
    os.makedirs(download_dir, exist_ok=True)
    decoded_file_name = urllib.parse.unquote(file_name)
    truncated_name = truncate_filename(decoded_file_name)
    name, ext = os.path.splitext(truncated_name)
    sanitized_name = sanitize_filename(name)
    sanitized_file_name = sanitized_name + ext
    file_path = os.path.join(download_dir, sanitized_file_name)

    if safe_file_exists(sanitized_file_name, download_dir):
        return False

    try:
        response = requests.get(url)
        if response.status_code == 200:
            temp_file_path = file_path + ".temp"
            with open(temp_file_path, 'wb') as file:
                file.write(response.content)

            try:
                if contains_embedded_files(temp_file_path):
                    print(custom_prompt + f"Warning: PDF contains embedded files, skipping download: {sanitized_file_name}")
                    os.remove(temp_file_path)
                    return False

                safe_file_path = os.path.join(download_dir, 'safe_' + sanitized_file_name)
                if not safer_pdf(temp_file_path, safe_file_path):
                    os.remove(temp_file_path)
                    return False

                os.remove(temp_file_path)
                return True
            except PyPDF2.errors.PdfReadError as e:
                print(custom_prompt + f"PDF processing error: {e}. Skipping file: {decoded_file_name}")
                os.remove(temp_file_path)
                return False
        else:
            print(custom_prompt + f"Failed to download: {decoded_file_name} (HTTP status: {response.status_code})")
            return False
    except requests.RequestException as e:
        print(custom_prompt + f"Error during download: {e}")
        return False



def main():
    print(custom_prompt + "Performing Selenium-based search for PDFs...")
    MAX_REQUESTS = random.randint(5, 10)
    LONG_WAIT = random.randint(4, 8)
    pdf_links = get_pdf_links_with_selenium(main_website_url, search_box_id, search_query)
    download_dir = os.path.join(os.getcwd(), 'downloads')
    os.makedirs(download_dir, exist_ok=True)
    already_downloaded_count = sum(safe_file_exists(link.split('/')[-1], download_dir) for link in pdf_links)
    new_pdf_links = [link for link in pdf_links if not safe_file_exists(link.split('/')[-1], download_dir)]
    total_files = len(pdf_links)
    new_files_count = len(new_pdf_links)

    print(custom_prompt + f"Total PDF files found: {total_files}")
    print(custom_prompt + f"New PDF files to download: {new_files_count}")
    print(custom_prompt + f"Already downloaded 'safe' files: {already_downloaded_count}")

    request_count = 0
    with tqdm(total=total_files, desc=custom_prompt + "Overall Progress", unit="files", colour='#37B6BD') as overall_pbar:
        overall_pbar.update(already_downloaded_count)

        for link in new_pdf_links:
            REQUEST_INTERVAL = random.randint(1, 3)
            file_name = link.split('/')[-1]

            download_attempted = download_pdf(link, file_name)
            if download_attempted:
                overall_pbar.update(1)
                request_count += 1
                if request_count >= MAX_REQUESTS:
                    update_message(f"Reached {MAX_REQUESTS} requests, waiting for {LONG_WAIT} seconds...")
                    time.sleep(LONG_WAIT)
                    request_count = 0
                    MAX_REQUESTS = random.randint(5, 10)
                    LONG_WAIT = random.randint(5, 10)
                else:
                    update_message(f"Waiting for {REQUEST_INTERVAL} seconds before the next download...")
                    time.sleep(REQUEST_INTERVAL)

    print(custom_prompt + "Operation completed.")


def update_message(message):
    sys.stdout.write('\r' + custom_prompt + message)
    sys.stdout.flush()

main()
