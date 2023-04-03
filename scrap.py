import seleniumwire.undetected_chromedriver as uc
from python_anticaptcha import AnticaptchaClient, ImageToTextTask
from selenium.webdriver.common.by import By
from seleniumwire.utils import decode
import time
import json
from datetime import datetime

# Add your anti-captcha API key
api_key = '7cd2d1fa0817c3d8af67f8b3c0da517e'

def get_captcha_solution(image_path):
    client = AnticaptchaClient(api_key)
    task = ImageToTextTask(image_path)
    job = client.createTask(task)
    job.join()
    return job.get_captcha_text()

# Add a function to handle CAPTCHAs
def handle_captcha(driver):
    # Locate the CAPTCHA image and get its src attribute
    captcha_img = driver.find_element(By.CSS_SELECTOR, '.block')
    captcha_img_src = captcha_img.get_attribute('src')

    # Download the CAPTCHA image and save it locally
    with open('captcha.png', 'wb') as file:
        file.write(driver.get_screenshot_as_png())

    # Solve the CAPTCHA using the anti-captcha service
    captcha_solution = get_captcha_solution('captcha.png')

    # Locate the CAPTCHA input field and submit the solution
    captcha_input = driver.find_element(By.CSS_SELECTOR, '.captcha-input-selector')
    captcha_input.send_keys(captcha_solution)

    # Click the submit button to verify the CAPTCHA solution
    submit_button = driver.find_element(By.CSS_SELECTOR, '.submit-button-selector')
    submit_button.click()

chrome_options = uc.ChromeOptions()

options = {
    'disable_encoding': True,
    'ignore_http_methods': ['OPTIONS', 'GET'] ,
    'request_storage_base_dir': 'selenium_storage'
}

# Set the URL you want to scrape from
url = "https://www.seloger.com/list.htm?projects=2%2C5&types=2%2C1&natures=1%2C2%2C4&places=%5B%7B%22divisions%22%3A%5B2238%5D%7D%5D&price=10000%2F10000000&mandatorycommodities=0&enterprise=0&qsVersion=1.0&LISTING-LISTpg=6"

# Create the driver with browser-specific options and/or selenium-wire options
driver = uc.Chrome(
    executable_path='/home/arthur/webdriver/chromedriver',
    options=chrome_options,
    seleniumwire_options=options
)

# Open the URL
driver.get(url)

# if 'captcha' in driver.page_source.lower():
#     handle_captcha(driver)

time.sleep(20)

i=0
while i < 7000:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(10)
    next = driver.find_element(By.PARTIAL_LINK_TEXT , "Suivant")
    next.click()
    
    # Add a wait to ensure the page has loaded before scraping
    time.sleep(20)
    
    try: 
        driver.wait_for_request('/search-bff/api/externaldata', timeout=30)
        for req in driver.requests:
            if req.method == 'POST' and 'externaldata' in req.path and req.response != None and req.response.body != None:
                    body = req.response.body
                    try:
                        body = decode(body, req.response.headers.get('Content-Encoding', 'identity'))
                        # Load the JSON data from the request body
                        json_data = json.loads(body)

                        # Write the JSON data to a file
                        now = datetime.now()
                        output_name = f'data/scrapping_seloger_page_{now}.json'
                        with open(output_name, 'w') as file:
                            json.dump(json_data, file, indent=4)

                        print("JSON data decoded from the request")
                    except json.JSONDecodeError:
                        print("Failed to decode JSON data from the request")
    except:
        print("No request with data")
    finally:
        time.sleep(10)    
    
    time.sleep(10)
    i=i+1