from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os

TIMEOUT_MULTIPLIER = 1

def create_driver():
    if 'ICPWILL_CHROME_HEADLESS_TESTING' in os.environ:
        options = Options()
        options.add_argument('--headless')  
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-gpu")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('window-size=1920x1080')
    else:
        options = Options()
        # options.add_argument('--headless')
        # options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options)

    print("Implicit Wait:", driver.timeouts.implicit_wait)
    print("Page Load Timeout:", driver.timeouts.page_load)
    print("Script Timeout:", driver.timeouts.script)
    
    driver.implicitly_wait(5)  # Wait for up to  seconds for elements to appear
    print("Implicit Wait:", driver.timeouts.implicit_wait)
    print("Page Load Timeout:", driver.timeouts.page_load)
    print("Script Timeout:", driver.timeouts.script)
    
    return driver


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


def save_page_source(driver, filename):
    print("All window handles:", driver.window_handles)
    print("Current windw handle: ", driver.current_window_handle)
    print(f'Saving page source to {filename}')
    # with open(filename, 'w', encoding='utf-8') as f:
    #     f.write(driver.page_source)


def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def click_element(driver, by_method, locator, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by_method, locator))
        )
        element.click()
        return element
    except TimeoutException:
        print(f"Element with locator '{locator}' not found or not clickable.")


def input_text(driver, by_method, locator, text, timeout=10):
    try:
        input_field = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by_method, locator))
        )
        input_field.clear()
        input_field.send_keys(text)
    except TimeoutException:
        print(f"Input field with locator '{locator}' not found or not visible.")


from screeninfo import get_monitors, ScreenInfoError
def get_all_monitors_resolution():
    try:
        monitors = get_monitors()
        for monitor in monitors:
            print(f"Monitor {monitor.name}: {monitor.width}x{monitor.height}")
    except ScreenInfoError:
        print("No monitors found or screen enumeration is not available.")
