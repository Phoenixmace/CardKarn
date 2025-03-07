from fileinput import lineno
from time import sleep
import keyboard
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
def click_button(buttons, name):
    time.sleep(0.7)
    for button in buttons:
        print(button.accessible_name)
        if button.accessible_name == name:
            button.click()
            return

# return [commander name, name list, bracket]
def get_moxfield_decklist(driver, link):
    driver.get(link)

    time.sleep(0.5)
    buttons = driver.find_elements(By.TAG_NAME, "button")
    click_button(buttons, 'Accept')
    time.sleep(0.25)
    buttons = driver.find_elements(By.TAG_NAME, "button")
    click_button(buttons, 'Accept All')

    # Locate the element with the id "commander-bracket-3"
    text = driver.page_source
    try:
        bracklist = int(text.split('commander-bracket-')[1][0])
    except:
        bracklist = 2


    more_button = driver.find_element(By.ID, "subheader-more")

    # Optionally, scroll into view before clicking (if necessary)
    driver.execute_script("arguments[0].scrollIntoView();", more_button)

    # Click the button
    more_button.click()


    # Find the "Export" button by its class and text and click it
    export_button = driver.find_element(By.XPATH, "//a[@class='dropdown-item cursor-pointer no-outline' and text()='Export']")
    export_button.click()

    links = driver.find_elements(By.CSS_SELECTOR, "a.text-body")
    name_list = []
    # Loop through each link and print its text (or any other attribute you want)
    for link in links:
        text = link.text
        if len(text) > 1 and '(' not in text:
            name_list.append(text)
    return  [name_list[0], name_list[1:], bracklist]

driver = webdriver.Chrome()


print(get_moxfield_decklist(driver, "https://moxfield.com/decks/sR1sq6cybkyvtk-92Wa-3Q"))
