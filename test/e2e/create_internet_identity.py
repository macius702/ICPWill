#  ./build.sh 
#  python3 test/e2e/create_internet_identity.py 


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # Make sure this line is included
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import sys
import time

def create_with_feed():
    driver = create_driver()
    url = "http://127.0.0.1:4943/?canisterId=be2us-64aaa-aaaaa-qaabq-cai"
    driver.get(url)

    save_page_source(driver, 'page03.html')
    
    click_element(driver, By.XPATH, "//button[text()='login']")
    
    time.sleep(10)
    time.sleep(1)
    
    original_tab = driver.current_window_handle
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(5)

    save_page_source(driver, 'page035.html')
    
    register_button = driver.find_element(By.ID, "registerButton")
    register_button.click()    
    time.sleep(5)
    save_page_source(driver, 'page04c.html')
    
    create_passkey_button = driver.find_element(By.CSS_SELECTOR, "button[data-action='construct-identity']")
    create_passkey_button.click()

    time.sleep(5)
    save_page_source(driver, 'page05c.html')
    
    
    captcha_input = driver.find_element(By.ID, "captchaInput")
    captcha_input.click()  # Click to ensure focus, although autofocus is set
    captcha_input.send_keys('a' + Keys.ENTER)  # Type 'a'a', followed by pressing the Enter key
    time.sleep(5)
    save_page_source(driver, 'page06c.html')
    
    # # Locate the button by its ID and click it
    # next_button = driver.find_element(By.ID, "confirmRegisterButton")
    # next_button.click()


    # time.sleep(5)
    # save_page_source(driver, 'page07c.html')
    
    
    continue_button = driver.find_element(By.ID, "displayUserContinue")
    continue_button.click()


    driver.switch_to.window(original_tab)

    
    time.sleep(15)
    save_page_source(driver, 'page07d.html')

    input_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder='nick']")
    input_field.click()

    # Optional: To type something in the input field
    input_field.send_keys("ExampleNickname")

    time.sleep(5)
    save_page_source(driver, 'page08d.html')
    
    
    register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'register')]")
    register_button.click()    
    time.sleep(5)
    save_page_source(driver, 'page09d.html')
    
    
    principal_paragraph = driver.find_element(By.XPATH, "//p[contains(text(), 'Principal:')]")
    principal_text = principal_paragraph.text
    principal_value = principal_text.split(': ')[1]  
    time.sleep(5)
    save_page_source(driver, 'page10d.html')

    print("Principal Value:", principal_value)    
        
    
    


def feed_with_money():
    driver = create_driver()
    url = "http://127.0.0.1:4943/?canisterId=be2us-64aaa-aaaaa-qaabq-cai"
    driver.get(url)

    save_page_source(driver, 'page03.html')
    
    click_element(driver, By.XPATH, "//button[text()='login']")
    
    time.sleep(10)
    time.sleep(1)
    
    original_tab = driver.current_window_handle
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(5)

    save_page_source(driver, 'page035.html')


    use_existing_button = driver.find_element(By.ID, "loginButton")
    use_existing_button.click()      
    time.sleep(5)
                
    
    
    save_page_source(driver, 'page04.html')
    
    
    add_new_device_button = driver.find_element(By.ID, "addNewDeviceButton")
    add_new_device_button.click()    


    time.sleep(5)
    save_page_source(driver, 'page04b.html')
    
    
    input_element = driver.find_element(By.CSS_SELECTOR, "input.c-input--vip")
    print('input_element: ', input_element)
    print("Tag Name:", input_element.tag_name)
    print("Text:", input_element.text)
    print("Class:", input_element.get_attribute('class'))
    print("ID:", input_element.get_attribute('id'))
    print("Placeholder:", input_element.get_attribute('placeholder'))

    # Click on the input element
    input_element.click()  # This will focus the input and simulate a click
    time.sleep(5)
    save_page_source(driver, 'page05b.html')

    # Optionally, send keys if you need to simulate typing
    input_element.send_keys("10000" + Keys.RETURN)  # Example to type '12345' and press Enter
    time.sleep(5)
    save_page_source(driver, 'page06b.html')
    
    
    trust_device_button = driver.find_element(By.ID, "trustDeviceConfirm")
    trust_device_button.click()    
    time.sleep(10)
    save_page_source(driver, 'page07b.html')
    

    driver.switch_to.window(original_tab)
    
    time.sleep(5)
    save_page_source(driver, 'page08b.html')

    
    # input_field = driver.find_element(By.XPATH, "//input[@placeholder='Internet Identity']")
    # print('input_field: ', input_field)
    # identity_anchor = 10000
    # identity_anchor = str(identity_anchor)
    # input_field.send_keys(identity_anchor)
    
    # time.sleep(5)
    
    # save_page_source(driver, 'page05.html')
    

    # continue_button = WebDriverWait(driver, 10).until(
    #     EC.element_to_be_clickable((By.XPATH, "//button[@data-action='continue']"))
    # )
    # continue_button.click()
    
    # driver.switch_to.window(original_tab)
    
    # time.sleep(5)
    # save_page_source(driver, 'page06.html')
    
    
    
    

def run():
    driver = create_driver()
    url = "http://br5f7-7uaaa-aaaaa-qaaca-cai.localhost:4943/#authorize"
    driver.get(url)

    try:
        # Click the "Home" button
        click_element(driver, By.XPATH, "//button[normalize-space()='Home']")

        # Save elements and page source
        print_elements(driver, file_path='elements.txt')
        save_page_source(driver, 'page01.html')

        # Click the "Register" button
        click_element(driver, By.ID, "registerButton")

        # Click the "Construct Identity" button
        click_element(driver, By.CSS_SELECTOR, "button[data-action='construct-identity']")

        # Input 'a' into the captcha input field
        input_text(driver, By.ID, 'captchaInput', 'a')

        # Click the "Confirm Register" button
        click_element(driver, By.ID, 'confirmRegisterButton')

        # Click the "Display User Continue" button
        click_element(driver, By.ID, 'displayUserContinue')

        # Save page source
        save_page_source(driver, 'page02.html')

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()


def click_element(driver, by_method, locator, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by_method, locator))
        )
        element.click()
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


def save_page_source(driver, filename):
    print("All window handles:", driver.window_handles)
    print("Current windw handle: ", driver.current_window_handle)
    print(f'Saving page source to {filename}')
    with open(filename, 'w', encoding='utf-8') as f:
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
    create_with_feed()
#   run()
#   feed_with_money()