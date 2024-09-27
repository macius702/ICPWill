import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By

# using Selenium Manager before running this script:
# ./venv/lib/python3.10/site-packages/selenium/webdriver/common/linux/selenium-manager --driver=chromedriver

import time
from colorama import Fore, Style
import os

from utils import click_element, wait_for_element, create_driver, get_all_monitors_resolution, TIMEOUT_MULTIPLIER

mode_is_local = True

@pytest.fixture(scope="function")
def setup_drivers():
    # Open 3 isolated Chrome windows
    drivers = [create_driver() for _ in range(3)]
    if mode_is_local:
        url = "http://127.0.0.1:4943/?canisterId=be2us-64aaa-aaaaa-qaabq-cai"
    else:
        url = "https://d627x-vyaaa-aaaan-qmvva-cai.icp0.io/"

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

    print(Style.RESET_ALL)    
    yield drivers
    for driver in drivers:
        driver.quit()

@pytest.fixture
def test_instance(setup_drivers):

    nicknames = ["A1", "B2", "C3"]
    inheritance = [ 0, 13000, 14000]

    return Mytest(setup_drivers, nicknames, inheritance)

def inheritance_report(expected1, got1, expected2, got2, approval_fee, transaction_fee_per_beneficiary, total_transaction_fees, inheritance_paid, total_expenses):
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

def run_inheritance_test(t, cancel=False, seconds=4):
    if mode_is_local:
        t.login_all()
    else:
        # Manual login
        input("Press Enter to continue...")

    initial_balances = t.read_balances()

    t.setup_and_run_inheritance(seconds)

    time.sleep(10 * TIMEOUT_MULTIPLIER)
    t.refresh_all()

    if cancel:
        t.cancel_transfer()
        time.sleep(10 * TIMEOUT_MULTIPLIER)
        t.refresh_all()

    final_balances = t.read_balances()

    fee = 10_000
    if cancel:
        testatorExpenses = fee
        firstBeneficiaryExpectedBalance = initial_balances[1]
        secondBeneficiaryExpectedBalance = initial_balances[2]
    else:
        testatorExpenses = fee + fee * 2 + t.inheritance[1] + t.inheritance[2]
        firstBeneficiaryExpectedBalance = t.inheritance[1] + initial_balances[1]
        secondBeneficiaryExpectedBalance = t.inheritance[2] + initial_balances[2]

    print(
        inheritance_report(
            t.inheritance[1],
            final_balances[1] - initial_balances[1],
            t.inheritance[2],
            final_balances[2] - initial_balances[2],
            fee,
            fee,
            fee * 2,
            t.inheritance[1] + t.inheritance[2],
            testatorExpenses,
        )
    )

    # Setup RED color in case of asserts
    print(Fore.RED)

    try:
        assert initial_balances[0] - testatorExpenses == final_balances[0]
        assert firstBeneficiaryExpectedBalance == final_balances[1]
        assert secondBeneficiaryExpectedBalance == final_balances[2]
        print(Fore.GREEN + "Test passed" + Style.RESET_ALL)
    finally:
        # Test cleanup
        print(Style.RESET_ALL)
        t.clear_beneficiaries()

def test_send(test_instance):
    t = test_instance
    run_inheritance_test(t, cancel=False, seconds=4)

def test_cancel_send(test_instance):
    t = test_instance
    run_inheritance_test(t, cancel=True, seconds=30)




class Mytest:
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
            login_button = click_element(driver, By.XPATH, "//button[text()='login']")
            time.sleep(1 * TIMEOUT_MULTIPLIER)
            
            original_tab = driver.current_window_handle
            self.switch_to_last_tab(driver)
            
            # We are in the II login Page
            use_existing_button = click_element(driver, By.ID, "loginButton")
                        
            input_field = click_element(driver, By.XPATH, "//input[@placeholder='Internet Identity']")
            identity_anchor = 10000 + i
            input_field.send_keys(str(identity_anchor))

            click_element(driver, By.XPATH, "//button[@data-action='continue']")

            self.switch_back_to_original_tab(driver, original_tab)

    def logout_all(self):
        for driver in self.drivers:
            logout_button = click_element(driver, By.XPATH, "//button[contains(text(), 'logout')]")

    def register_user(self):
        for i, driver in enumerate(self.drivers):
            nick_input_field = wait_for_element(driver, By.XPATH, "//input[@placeholder='nick']")
            nick_input_field.send_keys(nicknames[i])
            click_element(driver, By.XPATH, "//button[text()='register']")

    def read_balances(self):
        print('Entering readBalances')
        balances = []
        for driver in self.drivers:
            balance_element = wait_for_element(driver, By.XPATH, "//p[contains(text(), 'Balance:')]")
            balance_text = balance_element.text.split(":")[1].strip()
            print(f"Balance: {balance_text}")
            balances.append(int(balance_text))
        return balances

    def clear_beneficiaries(self):
        click_element(self.testator, By.XPATH, "//button[text()='Clear']")

    def cancel_transfer(self):
        click_element(self.testator, By.XPATH, "//button[text()='Cancel']")

    def setup_and_run_inheritance(self, seconds = 4):
        print('Entering setupAndRunInheritance')
        self.select_combobox_option('B2')
        self.add_beneficiary_and_enter_icp('B2', self.inheritance[1])

        self.select_combobox_option('C3')
        self.add_beneficiary_and_enter_icp('C3', self.inheritance[2])

        self.enter_seconds_and_activate(str(seconds))

    def select_combobox_option(self, option_text):
        click_element(self.testator, By.XPATH, "//button[@role='combobox']")

        click_element(self.testator, By.XPATH, f"//span[text()='{option_text}']")

    def add_beneficiary_and_enter_icp(self, nick, icp_value):
        click_element(self.testator, By.XPATH, "//button[text()='Add beneficiary']")
        row_with_input = wait_for_element(
            self.testator, By.XPATH, f"//tr[.//input[@value='{nick}']]"
        )
        icp_input_field = row_with_input.find_element(By.XPATH, ".//input[@placeholder='ICP value']")
        icp_input_field.send_keys(str(icp_value))

    def enter_seconds_and_activate(self, seconds):
        seconds_input_field = wait_for_element(self.testator, By.ID, "seconds")
        seconds_input_field.send_keys(seconds)

        click_element(self.testator, By.XPATH, "//button[text()='Save and Activate']")

get_all_monitors_resolution()


if __name__ == "__main__":
    run()
