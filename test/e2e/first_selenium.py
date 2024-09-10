# vim test.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.remote.webelement import WebElement  # Import WebElement

from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By  # Ensure this import is present

import time

from selenium.webdriver.support.ui import WebDriverWait  # Import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  # Import expected conditions


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

# Open 3 isolated Chrome windows
drivers = [create_driver() for _ in range(3)]

url = "http://127.0.0.1:4943/?canisterId=be2us-64aaa-aaaaa-qaabq-cai"

a = 100

for driver in drivers:
    driver.get(url)
    driver.set_window_position(a,a)
    a += 300

# driver = drivers[0]

# elements = driver.find_elements(By.XPATH, "//*")  # This will get all elements



# for element in elements:
#     try:
#         xpath = get_xpath(element)
#         print(f"Element XPath: {xpath}")
#     except Exception as e:
#         print(f"Error retrieving XPath: {e}")




# Fill in the nickname in each browser instance
nicknames = ["A1", "B2", "C3"]

for i, driver in enumerate(drivers):
    # if i != 0:
    #     continue

    # nickname_input = driver.find_element(By.NAME, "Login")  # Change the selector if needed
    # nickname_input.send_keys(nicknames[i])
    login_button = driver.find_element(By.XPATH, "//button[text()='login']")
    login_button.click()
    time.sleep(5)


    original_tab = driver.current_window_handle
    # Get the window handles (list of tabs/windows)
    window_handles = driver.window_handles

    # Switch to the new tab (the last handle in the list)
    driver.switch_to.window(window_handles[-1])    



    use_existing_button = driver.find_element(By.ID, "loginButton")
    use_existing_button.click()            



    input_field = driver.find_element(By.XPATH, "//input[@placeholder='Internet Identity']")

    # Send the key '10000' to the input field
    identity_anchor=10000 + i
    input_field.send_keys(str(identity_anchor))
    time.sleep(5)

    continue_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-action='continue']"))
    )

    # Click the button
    continue_button.click()
    driver.switch_to.window(original_tab)

    time.sleep(5 )


        # print_elements(driver)
    nick_input_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='nick']"))
    )
    nick_input_field.send_keys(nicknames[i])

    register_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='register']"))
    )

    # Click the button
    register_button.click()


    time.sleep(10 )

    # Wait until the <p> element with "Balance" is present
    balance_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Balance:')]"))
    )

    # Extract the full text from the <p> element
    balance_text = balance_element.text


    # Extract the number from the text (e.g., "Balance: 136550" -> 136550)
    balance_number = balance_text.split(":")[1].strip()

    # Print the balance number
    print(f"Balance: {balance_number}")    


    time.sleep(5 )



time.sleep(30)

# # # Fill out additional fields in the first browser window
# # first_driver = drivers[0]
# # first_input = first_driver.find_element(By.NAME, "field1")  # Change as needed
# # first_input.send_keys("value for first field")
# # # Continue filling out more fields as required

# # # Wait for 10 seconds
# # time.sleep(10)

# # # Check the displayed value in all three windows
# # for i, driver in enumerate(drivers):
# #     displayed_value = driver.find_element(By.ID, "displayed_value")  # Adjust selector
# #     print(f"Displayed value in window {i + 1}: {displayed_value.text}")

# # # Close all drivers
# # for driver in drivers:
# #     driver.quit()