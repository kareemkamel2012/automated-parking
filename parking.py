from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os
from dotenv import load_dotenv
from fake_useragent import UserAgent
import time
from cardinfo import CardInfo
from datetime import datetime
import math

APP_URL = "https://mpls.flowbirdapp.com/#/Parking"

def pay_for_parking(spot_number: str, duration: int, email: str, password: str, card_info: CardInfo):
    
    """
    Create a red circle at the given coordinates on the page for 1 second.

    This can be used to show where a click is happening for debugging purposes.

    Args:
        x (int): The x coordinate of the click.
        y (int): The y coordinate of the click.
    """
    def show_click(x, y):
        script = f"""
        var marker = document.createElement('div');
        marker.style.position = 'absolute';
        marker.style.width = '20px';
        marker.style.height = '20px';
        marker.style.backgroundColor = 'red';
        marker.style.borderRadius = '50%';
        marker.style.left = '{x - 10}px';  // Center the circle at the click position
        marker.style.top = '{y - 10}px';
        marker.style.zIndex = '9999';
        document.body.appendChild(marker);
        """
        driver.execute_script(script)


    driver = webdriver.Chrome()
    ua = UserAgent()
    userAgent = ua.random
    options = webdriver.ChromeOptions()
    options.add_argument("window-size=1920,1080")
    options.add_argument(f'user-agent={userAgent}')

    try:
        driver.get(APP_URL)
        print("Opening app")

        # Wait for the page to load
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        print("Page loaded")

        # Find and click Guest button
        guest_button = wait_and_find_element(driver, By.XPATH, '//span[contains(text(), "Guest")]', "guest button")
        click_element(driver, guest_button)

        # Find and click Log in button
        login_button = wait_and_find_element(driver, By.XPATH, '//button[contains(text(), "Log in")]', "login button")
        click_element(driver, login_button)

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

        # Remove last character from email_input, then add it back
        email_input.send_keys(Keys.BACKSPACE)
        email_input.send_keys(email[-1])

        # Remove last character from password_input, then add it back
        password_input.send_keys(Keys.BACKSPACE)
        password_input.send_keys(password[-1])

        # Log In
        password_input.send_keys(Keys.RETURN)

        # Wait for login to complete
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span.user-title'))
        )
        print("Login successful")

        # Wait for login screen to disappear
        WebDriverWait(driver, 20).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.login-container'))
        )
        print("Login screen disappeared")

        # Ensure page is fully loaded
        time.sleep(5)

        # Find and click user title
        user_title = wait_and_find_element(driver, By.CSS_SELECTOR, 'span.user-title', "user title")
        click_element(driver, user_title)

        # Find and click Parking button
        parking_button = wait_and_find_element(driver, By.XPATH, '//a//span[contains(text(), "Parking")]', "parking button")
        click_element(driver, parking_button)

        # Find and fill Zone|Space Code
        zone_input = wait_and_find_element(driver, By.XPATH, '//*[@aria-label="Zone|Space Code"]', "zone number input")
        zone_input.send_keys(spot_number)

        # Click Start parking session button
        start_button = wait_and_find_element(driver, By.XPATH, '//button[contains(text(), "Start parking session")]', "start parking button")
        click_element(driver, start_button)

        # Click End Time link
        end_time_link = wait_and_find_element(driver, By.CSS_SELECTOR, 'div.w-output.simulate-input.w-empty.ng-star-inserted', "End time link")
        click_element(driver, end_time_link)

        # Wait for wheel to appear
        time.sleep(5)

        # Find canvas element and click on it
        canvas = wait_and_find_element(driver, By.CSS_SELECTOR, 'canvas', "canvas")
        canvas_location = canvas.location
        canvas_size = canvas.size

        # Move mouse to center of canvas
        x = canvas_location['x'] + canvas_size['width'] / 2
        y = canvas_location['y'] + canvas_size['height'] / 2
        # divide duration in hours by the max duration, 8, then multiply by 360 to get the angle
        angle = duration * 45
        # approximate radius of wheel
        unit = canvas_size['width'] * 0.3
        y -= math.cos(math.radians(angle)) * unit
        x += math.sin(math.radians(angle)) * unit

        ActionChains(driver).move_by_offset(x, y).click().perform()

        # Find and click Confirm button
        confirm_button = wait_and_find_element(driver, By.XPATH, '//button[contains(text(), "CONFIRM")]', "confirm button")
        click_element(driver, confirm_button)

        # Find and click Proceed to payment button
        proceed_button = wait_and_find_element(driver, By.XPATH, '//button//span[contains(text(), "Proceed to payment")]', "proceed to payment button")
        click_element(driver, proceed_button)

        # Find and click Purchase button
        purchase_button = wait_and_find_element(driver, By.XPATH, '//button//span[contains(text(), "Purchase")]', "purchase button")
        click_element(driver, purchase_button)

        # Switch to other tab
        time.sleep(5)
        handles = driver.window_handles
        driver.switch_to.window(handles[1])

        # Find and click radio element with label matching card_info['type']
        card_type_label = wait_and_find_element(driver, By.XPATH, f'//label[contains(text(), "{card_info.type}")]', "card type label")
        card_type_input = card_type_label.find_element(By.XPATH, '../input')
        click_element(driver, card_type_input)

        # Find and fill card number
        card_number_input = wait_and_find_element(driver, By.XPATH, '//input[@name="card_number"]', "card number input")
        card_number_input.send_keys(card_info.number)

        # Find and fill card expiry month
        card_expiry_month_input = wait_and_find_element(driver, By.XPATH, '//select[@name="card_expiry_month"]', "card expiry month input")
        card_expiry_month_input.send_keys(card_info.exp_month)

        # Find and fill card expiry year
        card_expiry_year_input = wait_and_find_element(driver, By.XPATH, '//select[@name="card_expiry_year"]', "card expiry year input")
        card_expiry_year_input.send_keys(card_info.exp_year)

        # Find and fill card cvn
        card_cvn_input = wait_and_find_element(driver, By.XPATH, '//input[@name="card_cvn"]', "card cvn input")
        card_cvn_input.send_keys(card_info.cvn)

        # Submit payment
        card_cvn_input.send_keys(Keys.RETURN)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        driver.save_screenshot("error_screenshot.png")
        print("Error screenshot saved as error_screenshot.png")
    finally:
        # Uncomment the next line to keep the browser open for inspection
        # input("Press Enter to close the browser...")
        driver.quit()

def wait_and_find_element(driver, by, value, element_name, timeout=30):
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

def wait_for_clickable_element(driver, by, value, element_name, timeout=30):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        print(f"Found clickable {element_name}")
        return element
    except TimeoutException:
        print(f"Timeout: {element_name} not clickable")
        print("Current page title:", driver.title)
        print("Current URL:", driver.current_url)
        raise

def click_element(driver, element):
    try:
        element.click()
    except ElementNotInteractableException:
        print(f"Element not interactable, trying JavaScript click")
        driver.execute_script("arguments[0].click();", element)

def calculate_duration(start_time, end_time):
    fmt = "%I:%M %p"
    start_time_obj = datetime.strptime(start_time, fmt)
    end_time_obj = datetime.strptime(end_time, fmt)

    duration_delta = end_time_obj - start_time_obj
    return duration_delta.total_seconds() / 3600

if __name__ == "__main__":
    load_dotenv(override=True)
    duration = calculate_duration(os.getenv("START_TIME"), os.getenv("END_TIME"))
    card_info = CardInfo(os.getenv("CARD_TYPE"), os.getenv("CARD_NUMBER"), os.getenv("CARD_EXPIRATION_MONTH"), os.getenv("CARD_EXPIRATION_YEAR"), os.getenv("CARD_CVN"))
    pay_for_parking(os.getenv("SPOT_NUMBER"), duration, os.getenv("EMAIL"), os.getenv("PASSWORD"), card_info)

