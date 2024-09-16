
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import sys
import time

def run():
    driver = create_driver()
    url = "http://br5f7-7uaaa-aaaaa-qaaca-cai.localhost:4943/#authorize"
    driver.get(url)
    
    # We are in the II login Page


    # Locate the button using XPath and its text content
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Home']"))
    )

    # Click the button
    button.click()
    
    print_elements(driver, file_path='elements.txt')
    with open('page01.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)    
    
    use_existing_button = driver.find_element(By.ID, "registerButton")
    use_existing_button.click()      
    
    # Wait until the button is clickable and then click it
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-action='construct-identity']"))
    )
    button.click()    
    

    # Wait until the input field is visible
    try:
        input_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'captchaInput'))
        )
        # Clear the field if necessary
        input_field.clear()
        # Enter 'a' into the input field
        input_field.send_keys('a')
    except TimeoutException:
        print("Input field not found or not visible on the page.")
    
    # time.sleep(10)
    
    try:
        # Wait until the button is clickable
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'confirmRegisterButton'))
        )
        # Click the button
        button.click()
    except TimeoutException:
        print("Button with id 'confirmRegisterButton' not found or not clickable.")    
        

    try:
        # Wait until the button is clickable
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'displayUserContinue'))
        )
        # # Click the button
        # button.click()
    except TimeoutException:
        print("Button with id 'displayUserContinue' not found or not clickable.")
            

    # time.sleep(10)

    with open('page02.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)    


def get_xpath(element: WebElement) -> str:
    tag = element.tag_name
    if tag == "html":
        return "/html"
    parent = element.find_element(By.XPATH, "..")
    siblings = parent.find_elements(By.XPATH, f"./{tag}")
    index = 1
    for i, sibling in enumerate(siblings):
        if sibling == element:
            index = i + 1
            break
    xpath = get_xpath(parent)
    return f"{xpath}/{tag}[{index}]"




def print_elements(driver, file_path=None):
    elements = driver.find_elements(By.XPATH, "//*")  # This will get all elements

    def print_element_details(element, output_file):
        try:
            # Get XPath for the element
            xpath = get_xpath(element)
            # Get element tag name, ID, class, and text content
            tag_name = element.tag_name
            element_id = element.get_attribute("id")
            element_class = element.get_attribute("class")
            element_text = element.text
            element_placeholder = element.get_attribute("placeholder")  # Get the placeholder attribute

            # Print the details
            print(f"Element XPath: {xpath}", file=output_file)
            print(f"Tag Name: {tag_name}", file=output_file)
            print(f"ID: {element_id}", file=output_file)
            print(f"Class: {element_class}", file=output_file)
            print(f"Text: {element_text}", file=output_file)
            print(f"Placeholder: {element_placeholder}", file=output_file)  # Print the placeholder
            print("-" * 50, file=output_file)
        except Exception as e:
            print(f"Error retrieving element details: {e}", file=output_file)

    output_file = sys.stdout  # Default to standard output
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as output_file:
            for element in elements:
                print_element_details(element, output_file)
    else:
        for element in elements:
            print_element_details(element, output_file)

    
def create_driver():
    options = Options()
    options.add_argument('--headless')  # Enable headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('window-size=1920x1080')  # Set window size (optional but recommended)
    driver = webdriver.Chrome(options=options)  # Pass options to the driver
    return driver

if __name__=="__main__":
  run()          