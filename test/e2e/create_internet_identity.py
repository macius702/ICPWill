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

    save_page_source(driver, 'page03.html')
    
    click_element(driver, By.XPATH, "//button[text()='login']")
    
    time.sleep(1 * TIMEOUT_MULTIPLIER)
    
    original_tab = driver.current_window_handle
    driver.switch_to.window(driver.window_handles[-1])


    save_page_source(driver, 'page035.html')
    
    register_button = driver.find_element(By.ID, "registerButton")
    register_button.click()    
    save_page_source(driver, 'page04c.html')
    
    create_passkey_button = driver.find_element(By.CSS_SELECTOR, "button[data-action='construct-identity']")
    create_passkey_button.click()

    time.sleep(5 * TIMEOUT_MULTIPLIER)
    save_page_source(driver, 'page05c.html')
    
    
    captcha_input = driver.find_element(By.ID, "captchaInput")
    captcha_input.click()
    captcha_input.send_keys('a' + Keys.ENTER)
    save_page_source(driver, 'page06c.html')
    

    continue_button = driver.find_element(By.ID, "displayUserContinue")
    continue_button.click()


    driver.switch_to.window(original_tab)

    
    save_page_source(driver, 'page07d.html')

    input_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder='nick']")
    input_field.click()


    input_field.send_keys("ExampleNickname")

    save_page_source(driver, 'page08d.html')
    
    
    register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'register')]")
    register_button.click()    
    save_page_source(driver, 'page09d.html')
    
    
    principal_paragraph = driver.find_element(By.XPATH, "//p[contains(text(), 'Principal:')]")
    principal_text = principal_paragraph.text
    principal_value = principal_text.split(': ')[1]  
    save_page_source(driver, 'page10d.html')

    print("Principal Value:", principal_value)    
    
    if with_icp_feed:
        subprocess.call(["./feed_local.sh", principal_value])
    
    print('DONE.')
        



if __name__=="__main__":
    create__internet_identity(with_icp_feed = True)
    create__internet_identity()
    create__internet_identity()
