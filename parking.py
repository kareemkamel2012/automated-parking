from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
import os
from dotenv import load_dotenv
import time

APP_URL = "https://mpls.flowbirdapp.com/#/Parking"
def pay_for_parking(spot_number, email, password, card_info):
    driver = webdriver.Chrome()
    try:
        driver.get(APP_URL)
        print("Opening app")

        # Wait for the page to load
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        print("Page loaded")

        # Find and fill Zone|Space Code
        zone_input = wait_and_find_element(driver, By.XPATH, '//*[@aria-label="Zone|Space Code"]', "zone number input")
        zone_input.send_keys(spot_number)

        # Click Start parking session button
        start_button = wait_and_find_element(driver, By.XPATH, '//button[contains(text(), "Start parking session")]', "start parking button")
        click_element(driver, start_button)

        # Find and fill Email
        email_input = wait_and_find_element(driver, By.XPATH, '//*[@aria-label="Email or phone number"]', "email input")
        
        # Try different methods to interact with the email input
        try:
            email_input.send_keys(email)
        except ElementNotInteractableException:
            print("Direct send_keys failed, trying alternative methods")
            try:
                driver.execute_script("arguments[0].value = arguments[1]", email_input, email)
                print("Filled email using JavaScript")
            except:
                ActionChains(driver).move_to_element(email_input).click().send_keys(email).perform()
                print("Filled email using Action Chains")

        # Find and fill Password
        password_input = wait_and_find_element(driver, By.XPATH, '//*[@aria-label="Password"]', "password input")
        try:
            password_input.send_keys(password)
        except ElementNotInteractableException:
            print("Direct send_keys failed, trying alternative methods")
            try:
                driver.execute_script("arguments[0].value = arguments[1]", password_input, password)
                print("Filled password using JavaScript")
            except:
                ActionChains(driver).move_to_element(password_input).click().send_keys(password).perform()
                print("Filled password using Action Chains")

        # Click Login button
        login_button = wait_and_find_element(driver, By.XPATH, '//button[contains(text(), "Log in")]', "login button")
        click_element(driver, login_button)

        # Wait for login to complete
        time.sleep(5)
        print("Login attempt completed")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        driver.save_screenshot("error_screenshot.png")
        print("Error screenshot saved as error_screenshot.png")
    finally:
        # Uncomment the next line to keep the browser open for inspection
        # input("Press Enter to close the browser...")
        driver.quit()

def wait_and_find_element(driver, by, value, element_name, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        print(f"Found {element_name}")
        return element
    except TimeoutException:
        print(f"Timeout: {element_name} not found")
        print("Current page title:", driver.title)
        print("Current URL:", driver.current_url)
        raise

def click_element(driver, element):
    try:
        element.click()
    except ElementNotInteractableException:
        print(f"Element not interactable, trying JavaScript click")
        driver.execute_script("arguments[0].click();", element)

load_dotenv()
pay_for_parking(os.getenv("SPOT_NUMBER"), os.getenv("EMAIL"), os.getenv("PASSWORD"), os.getenv("CARD_INFO"))