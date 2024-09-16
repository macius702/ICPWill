
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


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
    
    print_elements(driver)
    # print(driver.page_source)  # Print the HTML content of the page.
    
    
    # use_existing_button = driver.find_element(By.ID, "loginButton")
    # use_existing_button.click()      


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


def print_elements(driver):
    elements = driver.find_elements(By.XPATH, "//*")  # This will get all elements
    for element in elements:
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
            print(f"Element XPath: {xpath}")
            print(f"Tag Name: {tag_name}")
            print(f"ID: {element_id}")
            print(f"Class: {element_class}")
            print(f"Text: {element_text}")
            print(f"Placeholder: {element_placeholder}")  # Print the placeholder
            print("-" * 50)

        except Exception as e:
            print(f"Error retrieving element details: {e}")

    
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