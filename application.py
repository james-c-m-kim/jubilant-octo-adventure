import sys
import time
import getpass

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

class ScraperApplication:
    driver = None
    people_search = "https://www.linkedin.com/search/results/people/?network=[\"F\"]&origin=FACETED_SEARCH"
    total_pages = 0
    connections = []

    def __init__(self, driver_path):
        self.driver = webdriver.Chrome(executable_path=driver_path)
    
    def perform_login(self):
        driver = self.driver

        driver.minimize_window()

        user_email = input("Type your Linkedin email here: ")
        user_password = getpass.getpass("Type your Linkedin password in the hidden field...")

        driver.get("https://linkedin.com")
        driver.maximize_window()

        email_input = driver.find_element_by_xpath("//input[contains(@name, 'session_key')]")
        password_input = driver.find_element_by_xpath("//input[contains(@name, 'session_password')]")
        submit_btn = driver.find_element_by_xpath("//button[contains(@class, 'sign-in-form__submit-button')]")

        email_input.send_keys(user_email)
        password_input.send_keys(user_password)
        submit_btn.click()
    
    def get_page(self, number):
        driver = self.driver

        driver.get(self.people_search + "&page=" + str(number))
        driver.find_element_by_tag_name("body").send_keys(Keys.END)

    def list_results_in_page(self):
        driver = self.driver

        return driver.find_elements_by_xpath("//span//span//a")

    def extract(self):
        driver = self.driver

        for current_page_idx in range(1, self.total_pages):
            self.get_page(current_page_idx)
            
            results = self.list_results_in_page()
            info = {}
    
            for result in results:
                result_url = result.get_attribute("href") + "/detail/contact-info/"

                driver.execute_script("window.open('', '_BLANC')")
                driver.switch_to.window(driver.window_handles[1])

                driver.get(result_url)

                try:
                    info["email"] = driver.find_element_by_xpath("//a[contains(@href, 'mailto')]").text
                    info["occupation"] = driver.find_element_by_xpath("//h2[contains(@class, 'mt1 t-18 t-black t-normal break-words')]").text
                    info["company name"] = driver.find_element_by_xpath("//span[contains(@class, 'text-align-left ml2 t-14 t-black t-bold full-width lt-line-clamp lt-line-clamp--multi-line ember-view')]").text
                    info["phone number"] = driver.find_element_by_xpath("//li[contains(@class, 'pv-contact-info__ci-container t-14')]/span[contains(@class, 't-14 t-black t-normal')]").text
                except:
                    pass
                
                self.connections.append(info)

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            sheet = pd.DataFrame(self.connections)
            sheet.to_csv('connections.csv')

    def begin(self):
        driver = self.driver

        self.get_page(1)

        # Determines how many pages it will need to scan
        try:
            pagination_list = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class, 'artdeco-pagination')]"))
            )

            last_page_btn_span = pagination_list.find_elements_by_xpath("//li[contains(@class, 'artdeco-pagination__indicator artdeco-pagination__indicator--number ember-view')]//span")[-1]
            last_page_value = int(last_page_btn_span.text)

            self.total_pages = last_page_value

            print("Found {0} pages.".format(last_page_value))

            self.extract()
        finally:
            self.save_all_and_quit()

    def save_all_and_quit(self):
        self.driver.quit()

    def run(self):
        self.perform_login()
        self.begin()
        self.extract()

if __name__ == "__main__":
    app = ScraperApplication(sys.argv[1])
    app.run()
