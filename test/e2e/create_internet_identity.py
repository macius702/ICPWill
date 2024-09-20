#  ./build.sh 
#  python3 test/e2e/create_internet_identity.py 



from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys





import time
import subprocess

from utils import create_driver, TIMEOUT_MULTIPLIER
from utils import save_page_source, click_element




def create__internet_identity(with_icp_feed = False):
    driver = create_driver()
    url = "http://127.0.0.1:4943/?canisterId=be2us-64aaa-aaaaa-qaabq-cai"
    driver.get(url)

    click_element(driver, By.XPATH, "//button[text()='login']")
    
    time.sleep(1 * TIMEOUT_MULTIPLIER)
    
    original_tab = driver.current_window_handle
    driver.switch_to.window(driver.window_handles[-1])

    register_button = click_element(driver, By.ID, "registerButton")
    
    create_passkey_button = click_element(driver, By.CSS_SELECTOR, "button[data-action='construct-identity']")

    time.sleep(5 * TIMEOUT_MULTIPLIER)


    captcha_input = click_element(driver, By.ID, "captchaInput")
    captcha_input.send_keys('a' + Keys.ENTER)


    continue_button = click_element(driver, By.ID, "displayUserContinue")

    if with_icp_feed:
        driver.switch_to.window(original_tab)

        input_field = click_element(driver, By.CSS_SELECTOR, "input[placeholder='nick']")
        input_field.send_keys("ExampleNickname")

        register_button = click_element(driver, By.XPATH, "//button[contains(text(), 'register')]")
        
        
        principal_paragraph = click_element(driver, By.XPATH, "//p[contains(text(), 'Principal:')]")
        principal_text = principal_paragraph.text
        principal_value = principal_text.split(': ')[1]  

        print("Principal Value:", principal_value)    
    
        subprocess.call(["./feed_local.sh", principal_value])
    
    print('DONE.')
        



if __name__=="__main__":
    create__internet_identity(with_icp_feed = True)
    create__internet_identity()
    create__internet_identity()
