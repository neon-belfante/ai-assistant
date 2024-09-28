from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options as ChromeOptions
import json
import base64
from io import BytesIO
import time
import os


def download_pdf_from_url(url: str, relative_download_dir: str, pdf_name: str):
    download_dir = os.path.abspath(relative_download_dir)
    
    firefox_options=Options()
    firefox_options.add_argument("--headless")
    firefox_options.set_preference("accessibility.blockautorefresh", True)
    firefox_options.set_preference("network.prefetch-next", False)  
    firefox_options.set_preference("network.http.speculative-parallel-limit", 0)
    firefox_options.set_preference("dom.disable_beforeunload", True)
    firefox_options.set_preference("dom.allow_scripts_to_close_windows", False) 

    firefox_profile = {
        "browser.download.folderList": 2,
        "browser.download.dir": download_dir,
        "browser.helperApps.neverAsk.saveToDisk": "application/pdf",
        "pdfjs.disabled": True,
    }

    for key, value in firefox_profile.items():
        firefox_options.set_preference(key, value)

    driver = webdriver.Firefox(options=firefox_options)

    try:
        driver.set_page_load_timeout(10)
        try:
            driver.set_page_load_timeout(10)
            driver.get(url)
            time.sleep(10)
            download_complete = False
            while not download_complete:
                files_in_directory = os.listdir(download_dir)
                if any(file.endswith(".part") for file in files_in_directory):
                    time.sleep(1)
                else:
                    download_complete=True
        except:
            pass
        list_of_files = os.listdir(download_dir)
        latest_file = max([os.path.join(download_dir, f) for f in list_of_files], key=os.path.getctime)
        new_file_name = os.path.join(download_dir, pdf_name)
        os.rename(latest_file, new_file_name)
    finally:
        driver.quit()


# def download_pdf_from_url_with_playwright(url: str, relative_download_dir: str, pdf_name: str):
#     import asyncio
#     from playwright.async_api import async_playwright
#     download_dir = os.path.abspath(relative_download_dir)
#     new_file_name = os.path.join(download_dir, pdf_name)

#     async def url_to_pdf(url, output_path):
#         async with async_playwright() as p:
#             browser = await p.chromium.launch()
#             page = await browser.new_page()
#             await page.goto(url)
#             await page.pdf(path=output_path)
#             await browser.close()

#     asyncio.run(url_to_pdf(url, new_file_name))

def print_webpage_as_pdf(url: str, relative_download_dir: str, pdf_name: str):
    download_dir = os.path.abspath(relative_download_dir)
    new_file_name = os.path.join(download_dir, pdf_name)
    webdriver_options = ChromeOptions()
    # webdriver_options.add_argument("--headless")
    # webdriver_options.add_argument("--disable-gpu")
    webdriver_options.add_argument("--window-size=20,10")
    driver = webdriver.Chrome(options=webdriver_options)
    driver.get(url)
    time.sleep(3)
    print_options = {
        'landscape' : False,
        'displayHeaderFooter': False,
        'printBackground' : True,
        'preferCSSPageSize' : True,
        'paperWidth':6.97,
        'paperHeight':16.5
    }
    resource = f"/session/{driver.session_id}/chromium/send_command_and_get_result"
    url = driver.command_executor._url + resource
    cmd = "Page.printToPDF"
    body = json.dumps({'cmd':cmd, 'params': print_options})
    response = driver.command_executor._request('POST', url, body)
    result = response.get('value')
    raw_file = base64.b64decode(result['data'])
    file = BytesIO()
    file.write(raw_file)
    with open(new_file_name, "wb") as outfile:
        outfile.write(file.getbuffer())
    driver.close()