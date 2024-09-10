from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


def run():
    # Open 3 isolated Chrome windows
    drivers = [create_driver() for _ in range(3)]


    url = "http://127.0.0.1:4943/?canisterId=be2us-64aaa-aaaaa-qaabq-cai"

    screen_width = 1920
    screen_height = 1200

    # Calculate window width (each window takes 1/3 of the screen width)
    window_width = screen_width // 3
    window_height = screen_height  # Use full screen height for each window

    x_position = 0
    y_position = 0

    for driver in drivers:
        driver.get(url)
        # Set window size and position
        driver.set_window_position(x_position, y_position)
        driver.set_window_size(window_width, window_height)
        # Move the x position for the next window
        x_position += window_width

    t = Test(drivers)
    t.loginAll()
    t.registerUser()
    t.readBalances()


nicknames = ["A1", "B2", "C3"]

class Test:
    def __init__(self, drivers):
        self.drivers = drivers

    def loginAll(self):
        for i, driver in enumerate(self.drivers):
            login_button = driver.find_element(By.XPATH, "//button[text()='login']")
            login_button.click()
            time.sleep(1)

            original_tab = driver.current_window_handle
            window_handles = driver.window_handles
            # Switch to the new tab (the last handle in the list)
            driver.switch_to.window(window_handles[-1])    

            # We are in the II login Page
            use_existing_button = driver.find_element(By.ID, "loginButton")
            use_existing_button.click()            

            input_field = driver.find_element(By.XPATH, "//input[@placeholder='Internet Identity']")

            identity_anchor=10000 + i
            input_field.send_keys(str(identity_anchor))
            

            continue_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-action='continue']"))
            )
            continue_button.click()

            # Switch to the home page
            driver.switch_to.window(original_tab)
            # We are back in the original page, let the II tab do it's job
            

        #####################################################
    def registerUser(self):
        for i, driver in enumerate(self.drivers):
            nick_input_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='nick']"))
            )
            nick_input_field.send_keys(nicknames[i])
            register_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='register']"))
            )
            register_button.click()
    
    def readBalances(self):
        # We must  wait for Balance to appear
        time.sleep(10)
        for i, driver in enumerate(self.drivers):

            # Wait until the <p> element with "Balance" is present
            balance_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Balance:')]"))
            )

            balance_text = balance_element.text
            balance_number = balance_text.split(":")[1].strip()
            print(f"Balance: {balance_number}")    

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
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

from screeninfo import get_monitors
def get_all_monitors_resolution():
    monitors = get_monitors()
    for monitor in monitors:
        print(f"Monitor: {monitor.name}, Width: {monitor.width}, Height: {monitor.height}, x: {monitor.x}, y: {monitor.y}")

get_all_monitors_resolution()


if __name__ == "__main__":
    run()
