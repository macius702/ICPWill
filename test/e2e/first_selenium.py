

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# using Selenium Manager before running this script:
# ./venv/lib/python3.10/site-packages/selenium/webdriver/common/linux/selenium-manager --driver=chromedriver

import time
from colorama import Fore, Style
import os

from utils import click_element

mode_is_local = True
nicknames = ["A1", "B2", "C3"]
inheritance = [ 0, 13000, 14000]

def run():
    # Open 3 isolated Chrome windows
    drivers = [create_driver() for _ in range(3)]

    url = "http://127.0.0.1:4943/?canisterId=be2us-64aaa-aaaaa-qaabq-cai"

    screen_width = 1920
    screen_height = 1200

    # Calculate window width (each window takes 1/3 of the screen width)
    window_width = screen_width // 3
    window_height = screen_height - 200  # Use full screen height for each window

    x_position = 0
    y_position = 0

    for driver in drivers:
        driver.get(url)
        # Set window size and position
        driver.set_window_position(x_position, y_position)
        driver.set_window_size(window_width, window_height)
        # Move the x position for the next window
        x_position += window_width

    # Pass nicknames and inheritance to the Test class instance
    t = Test(drivers, nicknames, inheritance)

    if mode_is_local:
        t.login_all()
    else:
        # manual login
        input("Press Enter to continue...")

    t.register_user()
    initial_balances = t.read_balances()

    t.setup_and_run_inheritance()

    time.sleep(10)
    t.refresh_all()

    t.register_user()

    final_balances = t.read_balances()
    
    firstBeneficiaryExpectedBalance = inheritance[1] + initial_balances[1]
    
        
    def inheritance_report(expected1, got1, expected2, got2, approval_fee, transaction_fee_per_beneficiary, total_transaction_fees, inheritance_paid, total_expenses ):
        report = f"""
        Inheritance Report:

        1st Beneficiary:
        - Expected Inheritance:   {expected1:>10,}
        - Actual Inheritance:     {got1:>10,}

        2nd Beneficiary:
        - Expected Inheritance:   {expected2:>10,}
        - Actual Inheritance:     {got2:>10,}

        Testator's Expenses:
        - Approval Fee:           {approval_fee:>10,}
        - Total Transaction Fees: {total_transaction_fees:>10,} (Fee per Beneficiary: {transaction_fee_per_beneficiary:>10,})
        - Inheritance Paid:       {inheritance_paid:>10,}
        - Total Expenses:         {total_expenses:>10,}
        """
        return report
    
    fee = 10_000
    testatorExpenses = fee + fee *2 + inheritance[1] + inheritance[2]
    firstBeneficiaryExpectedBalance = inheritance[1] + initial_balances[1]
    secondBeneficiaryExpectedBalance = inheritance[2] + initial_balances[2]

    print(inheritance_report(
        inheritance[1],
        final_balances[1]-initial_balances[1],
        inheritance[2],
        final_balances[2]-initial_balances[2],
        fee,
        fee,
        fee * 2,
        inheritance[1] + inheritance[2],
        testatorExpenses))
    
    # setup RED color in case of asserts
    print(Fore.RED)
    
    assert(initial_balances[0] - testatorExpenses == final_balances[0])
    
    assert(firstBeneficiaryExpectedBalance == final_balances[1])
    
    assert(secondBeneficiaryExpectedBalance == final_balances[2])

    print(Style.RESET_ALL)    

    print(Fore.GREEN + 'Test passed' + Style.RESET_ALL)    
    
    #time.sleep(600)



class Test:
    def __init__(self, drivers, nicknames, inheritance):
        self.drivers = drivers
        self.testator = self.drivers[0]
        self.nicknames = nicknames
        self.inheritance = inheritance

    def refresh_all(self):
        for driver in self.drivers:
            driver.refresh()
    
    def switch_to_last_tab(self, driver):
        driver.switch_to.window(driver.window_handles[-1])
    
    def switch_back_to_original_tab(self, driver, original_tab):
        driver.switch_to.window(original_tab)
    
    def login_all(self):
        for i, driver in enumerate(self.drivers):
            login_button = driver.find_element(By.XPATH, "//button[text()='login']")
            login_button.click()
            time.sleep(1)
            
            original_tab = driver.current_window_handle
            self.switch_to_last_tab(driver)
            
            # We are in the II login Page
            use_existing_button = driver.find_element(By.ID, "loginButton")
            use_existing_button.click()      
                        
            input_field = driver.find_element(By.XPATH, "//input[@placeholder='Internet Identity']")
            identity_anchor = 10000 + i
            input_field.send_keys(str(identity_anchor))

            continue_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-action='continue']"))
            )
            continue_button.click()

            self.switch_back_to_original_tab(driver, original_tab)

    def logout_all(self):
        for driver in self.drivers:
            logout_button = driver.find_element(By.XPATH, "//button[contains(text(), 'logout')]")
            logout_button.click()

    def register_user(self):
        for i, driver in enumerate(self.drivers):
            nick_input_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='nick']"))
            )
            nick_input_field.send_keys(nicknames[i])
            click_element(driver, By.XPATH, "//button[text()='register']")

    def read_balances(self):
        print('Entering readBalances')
        if mode_is_local:
            time.sleep(10)
        else:
            time.sleep(30)
        balances = []
        for driver in self.drivers:
            balance_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Balance:')]"))
            )
            balance_text = balance_element.text.split(":")[1].strip()
            print(f"Balance: {balance_text}")
            balances.append(int(balance_text))
        return balances

    def setup_and_run_inheritance(self):
        print('Entering setupAndRunInheritance')
        self.select_combobox_option('B2')
        self.add_beneficiary_and_enter_icp('B2', inheritance[1])

        self.select_combobox_option('C3')
        self.add_beneficiary_and_enter_icp('C3', inheritance[2])

        self.enter_seconds_and_activate("4")

    def select_combobox_option(self, option_text):
        combobox_button = WebDriverWait(self.testator, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@role='combobox']"))
        )
        combobox_button.click()

        option = WebDriverWait(self.testator, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[text()='{option_text}']"))
        )
        option.click()

    def add_beneficiary_and_enter_icp(self, nick, icp_value):
        click_element(self.testator, By.XPATH, "//button[text()='Add beneficiary']")

        row_with_input = WebDriverWait(self.testator, 10).until(EC.presence_of_element_located((By.XPATH, f"//tr[.//input[@value='{nick}']]")))
        icp_input_field = row_with_input.find_element(By.XPATH, ".//input[@placeholder='ICP value']")
        icp_input_field.send_keys(str(icp_value))

    def enter_seconds_and_activate(self, seconds):
        seconds_input_field = WebDriverWait(self.testator, 10).until(
            EC.presence_of_element_located((By.ID, "seconds"))
        )
        seconds_input_field.send_keys(seconds)

        click_element(self.testator, By.XPATH, "//button[text()='Save and Activate']")



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
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options)    
    return driver

from screeninfo import get_monitors, ScreenInfoError
def get_all_monitors_resolution():
    try:
        monitors = get_monitors()
        for monitor in monitors:
            print(f"Monitor {monitor.name}: {monitor.width}x{monitor.height}")
    except ScreenInfoError:
        print("No monitors found or screen enumeration is not available.")


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

from screeninfo import get_monitors, ScreenInfoError
def get_all_monitors_resolution():
    try:
        monitors = get_monitors()
        for monitor in monitors:
            print(f"Monitor {monitor.name}: {monitor.width}x{monitor.height}")
    except ScreenInfoError:
        print("No monitors found or screen enumeration is not available.")

get_all_monitors_resolution()


if __name__ == "__main__":
    run()
