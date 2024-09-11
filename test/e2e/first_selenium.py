from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from colorama import Fore, Style


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
    initial_balances = t.readBalances()

    
    t.setupAndRunInheritance()

    time.sleep(10)
    t.refreshAll()
    
    t.registerUser()

    
    final_balances = t.readBalances()
    
    firstBeneficiaryExpectedBalance = inheritance[1] + initial_balances[1]
    
        
    def inheritance_report(expected1, got1, expected2, got2, approval_fee, transaction_fee_per_beneficiary, total_transaction_fees, inheritance_paid, total_expenses ):
        report = f"""
    Inheritance Report:

    1st Beneficiary:
    - Expected Inheritance: {expected1}
    - Actual Inheritance: {got1}

    2nd Beneficiary:
    - Expected Inheritance: {expected2}
    - Actual Inheritance: {got2}

    Testator's Expenses:
    - Approval Fee: {approval_fee}
    - Transaction Fee per Beneficiary: {transaction_fee_per_beneficiary} (Total: {total_transaction_fees})
    - Inheritance Paid: {inheritance_paid}
    - Total Expenses: {total_expenses}
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
    assert(final_balances[0] + testatorExpenses , final_balances[0])
    
    assert(firstBeneficiaryExpectedBalance == final_balances[1])
    
    assert(secondBeneficiaryExpectedBalance == final_balances[2])
    
    
    

    print(Fore.GREEN + 'Test passed' + Style.RESET_ALL)    
    
    #time.sleep(600)



class Test:
    def __init__(self, drivers):
        self.drivers = drivers
        self.testator = self.drivers[0]

    def refreshAll(self):
        for i, driver in enumerate(self.drivers):
            driver.refresh()
            
        
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
    def logoutAll(self):
        for i, driver in enumerate(self.drivers):
            logout_button = driver.find_element(By.XPATH, "//button[contains(text(), 'logout')]")
            logout_button.click()
        
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
        print('Entering readBalances')
        time.sleep(10)
        balances = []
        for i, driver in enumerate(self.drivers):

            # Wait until the <p> element with "Balance" is present
            balance_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Balance:')]"))
            )

            balance_text = balance_element.text
            balance_number = balance_text.split(":")[1].strip()
            print(f"Balance: {balance_number}")
            balances.append(int(balance_number))
        return balances


    def setupAndRunInheritance(self):
        print('Entering setupAndRunInheritance')
        # Wait for the combobox button to be clickable and click it to open the dropdown
        combobox_button = WebDriverWait(self.testator, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@role='combobox']"))
        )
        combobox_button.click()

        # Wait for the B2 option to appear in the dropdown and click it
        b2_option = WebDriverWait(self.testator, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='B2']"))
        )
        b2_option.click()

        add_beneficiary_button = WebDriverWait(self.testator, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Add beneficiary']"))
        )
        
        add_beneficiary_button.click()            
        
        # Wait for the ICP input field to be present
        icp_input_field = WebDriverWait(self.testator, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='ICP value']"))
        )

        icp_input_field.send_keys(str(inheritance[1]))
        
        ### Select C3
        
        combobox_button = WebDriverWait(self.testator, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@role='combobox']"))
        )
        combobox_button.click()

        # Wait for the B2 option to appear in the dropdown and click it
        c3_option = WebDriverWait(self.testator, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='C3']"))
        )
        c3_option.click()

        add_beneficiary_button = WebDriverWait(self.testator, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Add beneficiary']"))
        )
        
        add_beneficiary_button.click()            


#################

        row_with_input = WebDriverWait(self.testator, 10).until(
            EC.presence_of_element_located((By.XPATH, "//tr[contains(@class, 'bg-gray-50') and .//input[@value='C3']]"))
        )
        
        icp_input_field = row_with_input.find_element(By.XPATH, ".//input[@placeholder='ICP value']")
        
        
        


        icp_input_field.send_keys(str(inheritance[2]))
        
        
        
#################


        seconds_input_field = WebDriverWait(self.testator, 10).until(
                    EC.presence_of_element_located((By.ID, "seconds"))
                )
        seconds_input_field.send_keys("4")
        
        save_activate_button = WebDriverWait(self.testator, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Save and Activate']"))
        )
        save_activate_button.click()        
        

        
        
        
        



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
