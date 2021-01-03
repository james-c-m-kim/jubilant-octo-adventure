import sys
import time
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd


class ScraperApplication:
    driver = None
    login_url = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
    people_search = "https://www.linkedin.com/search/results/people/?network=[\"F\"]&origin=FACETED_SEARCH"
    connections_url = 'https://www.linkedin.com/mynetwork/invite-connect/connections/'
    total_pages = 0
    connections = []

    def __init__(self, driver_path):
        self.driver = webdriver.Chrome(executable_path=driver_path)
    
    def perform_login(self):
        driver = self.driver
        # user_email = input("Type your Linkedin email here: ")
        # user_password = getpass.getpass("Type your Linkedin password in the hidden field...")

        user_email = 'marian.goldberg@gmail.com'
        user_password = 'Gav1n*Br1'

        driver.get(self.login_url)

        email_input = driver.find_element_by_id('username')
        email_input.send_keys(user_email)

        password_input = driver.find_element_by_id('password')
        password_input.send_keys(user_password)

        password_input.submit()

    def get_page(self, number):
        driver = self.driver

        driver.get(self.people_search + "&page=" + str(number))
        driver.find_element_by_tag_name("body").send_keys(Keys.END)

    def list_results_in_page(self):
        driver = self.driver

        return driver.find_elements_by_xpath("//span//span//a")

    def extract(self, df: pd.DataFrame):
        driver = self.driver

        for index, r in df.iterrows():
            if r.isnull(r['profileUrl']):
                continue

            profile_url = r['profileUrl']
            driver.execute_script("window.open('', '_BLANC')")
            driver.switch_to.window(driver.window_handles[1])

            driver.get(profile_url)

            try:
                df.at[index, "email"] = driver.find_element_by_xpath("//a[contains(@href, 'mailto')]").text
                df.at[index, "occupation"] = driver.find_element_by_xpath(
                    "//h2[contains(@class, 'mt1 t-18 t-black t-normal break-words')]").text
                df.at[index, "company name"] = driver.find_element_by_xpath(
                    "//span[contains(@class, 'text-align-left ml2 t-14 t-black t-bold full-width lt-line-clamp lt-line-clamp--multi-line ember-view')]").text
                df.at[index, "phone number"] = driver.find_element_by_xpath(
                    "//li[contains(@class, 'pv-contact-info__ci-container t-14')]/span[contains(@class, 't-14 t-black t-normal')]").text
            except:
                pass


    def page_down(self):
        body = self.driver.find_element_by_tag_name('body')
        body.send_keys(Keys.PAGE_DOWN)

    def page_up(self):
        body = self.driver.find_element_by_tag_name('body')
        body.send_keys(Keys.PAGE_UP)

    def fetch_list(self):
        items = self.driver.find_elements_by_xpath('/html/body/div[7]/div[3]/div/div/div/div/div/div/div/div/section/ul/li')
        contact_list = [self.scrape_email(i) for i in items]
        return contact_list

    def scrape_email(self, item):
        anchor = item.find_element_by_class_name('mn-connection-card__picture')
        href = anchor.get_attribute('href')
        contact = item.find_element_by_class_name('mn-connection-card__details')\
            .find_element_by_tag_name('a')\
            .find_element_by_class_name('mn-connection-card__name')

        contact_name = contact.text
        return {'name': contact_name, 'href': href}

    def scroll_to_bottom(self, web_driver):
        tolerance = 0
        while True:
            # Get old scroll position
            old_position = web_driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))
            # Sleep and Scroll
            time.sleep(1)
            web_driver.execute_script((
                "var scrollingElement = (document.scrollingElement ||"
                " document.body);scrollingElement.scrollTop ="
                " scrollingElement.scrollHeight;"))
            # Get new position
            new_position = web_driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))

            if new_position == old_position:
                self.page_up()
                time.sleep(1)
                tolerance += 1

            if tolerance > 15:
                break

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

        self.driver.get(self.connections_url)
        time.sleep(2)
        body = self.driver.find_element_by_tag_name('body')
        body.click()
        self.scroll_to_bottom(self.driver)

        file_path = "C:\\dev\\scratches\\"
        file_name = "2020-12-31-results-1.csv"

        df = pd.read_csv(os.path.join(file_name, file_name))
        df.drop(columns=['First Name', 'Last Name', 'Email Address', 'timestamp'])
        df['email'] = None
        df['occupation'] = None
        df['company name'] = None
        df['phone number'] = None

        # self.begin()
        self.extract(df)
        df.to_csv(os.path.join(file_path, f'(MATCHED) {file_name}'))
        print('done.')


if __name__ == "__main__":
    app = ScraperApplication(sys.argv[1])
    app.run()
