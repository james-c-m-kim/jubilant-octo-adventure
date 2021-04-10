import sys
import time
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

RESULT_PATH = 'C:\\Users\\kimjc\\Google Drive (kimjc@code4lifesoftware.com)\\marian (1)\\chopped'
RESULT_FILES = [
    '2020-12-31-results-1.csv',
    '2020-12-31-results-2.csv',
    '2020-12-31-results-3b.csv',
    '2020-12-31-results-4.csv',
    '2020-12-31-results-5.csv'
]


class ScraperApplication:
    driver = None
    logout_url = 'https://www.linkedin.com//m/logout'
    login_url = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
    people_search = "https://www.linkedin.com/search/results/people/?network=[\"F\"]&origin=FACETED_SEARCH"
    connections_url = 'https://www.linkedin.com/mynetwork/invite-connect/connections/'
    total_pages = 0
    connections = []

    def __init__(self, driver_path):
        self.driver_path = driver_path

    def perform_login(self):
        driver = webdriver.Chrome(executable_path=self.driver_path)
        driver.implicitly_wait(5)
        driver.get(self.logout_url)
        time.sleep(2)
        driver.get(self.login_url)
        # user_email = input("Type your Linkedin email here: ")
        # user_password = getpass.getpass("Type your Linkedin password in the hidden field...")

        user_email = 'marian.goldberg@gmail.com'
        user_password = 'Br1@Gav1n@MG'

        driver.get(self.login_url)

        email_input = driver.find_element_by_id('username')
        email_input.send_keys(user_email)

        password_input = driver.find_element_by_id('password')
        password_input.send_keys(user_password)

        password_input.submit()

        return driver

    # def get_page(self, number):
    #     driver = self.driver
    #
    #     driver.get(self.people_search + "&page=" + str(number))
    #     driver.find_element_by_tag_name("body").send_keys(Keys.END)
    #
    # def list_results_in_page(self):
    #     driver = self.driver
    #
    #     return driver.find_elements_by_xpath("//span//span//a")

    def extract(self, df: pd.DataFrame, driver: webdriver):
        # df2 = pd.DataFrame(columns=['first', 'last', 'profile', 'email', 'occupation', 'company', 'phone'])
        result = []
        total_rows = len(df)
        control_count = 0

        try:
            for index, r in df.iterrows():
                if (control_count % 100 == 0) and (control_count > 0):
                    driver = self.perform_login()
                    control_count = 0

                control_count += 1
                found_email = None
                found_job = None
                found_company = None
                found_phone = None
                found_location = None

                if pd.isnull(r['profileUrl']):
                    continue

                first_name =  r['firstName']
                last_name =  r['lastName']
                profile_url = r['profileUrl']

                # driver.execute_script("window.open('', '_BLANK')")
                # driver.switch_to.window(driver.window_handles[1])
                driver.get(profile_url + '/detail/contact-info')
                not_found = driver.current_url == 'https://www.linkedin.com/in/unavailable/'

                # noinspection PyBroadException
                try:
                    email = driver.find_element_by_xpath("//a[contains(@href, 'mailto')]")
                    if email is not None:
                        found_email = email.text
                except:
                    found_email = None

                try:
                    occupation = driver.find_element_by_xpath(
                        "//h2[contains(@class, 'mt1 t-18 t-black t-normal break-words')]")
                    if occupation is not None:
                        found_job = occupation.text
                except:
                    found_job = None

                try:
                    company_name = driver.find_element_by_xpath(
                        "//span[contains(@class, 'text-align-left ml2 t-14 t-black t-bold full-width lt-line-clamp lt-line-clamp--multi-line ember-view')]")
                    if company_name is not None:
                        found_company = company_name.text
                except:
                    found_company = None

                try:
                    phone_number = driver.find_element_by_xpath(
                        "//li[contains(@class, 'pv-contact-info__ci-container t-14')]/span[contains(@class, 't-14 t-black t-normal')]")
                    if phone_number is not None:
                        found_phone = phone_number.text
                except:
                    found_phone = None

                try:
                    e1 = driver.find_elements_by_class_name("ph5")
                    e2 = e1[0].find_elements_by_class_name("pv-top-card--list-bullet")
                    e3 = e2[0].find_element_by_class_name("t-16")
                    found_location = e3.text
                except:
                    found_location = None

                if (found_phone is None) and (found_company is None) \
                    and (found_email is None) and (found_job is None) \
                    and (found_location is None):
                    if not not_found:
                        breakpoint()
                        driver = self.perform_login()

                result.append({
                    'first': first_name,
                    'last': last_name,
                    'profile': profile_url,
                    'location': found_location,
                    'email': found_email,
                    'company': found_company,
                    'occupation': found_job,
                    'phone': found_phone,
                })

                found_not_found = 'NOT FOUND' if not_found else 'Found'
                if not_found:
                    print(f'NOT FOUND: {first_name} {last_name} - {profile_url}')
                else:
                    print(f'Found and added: {first_name} {last_name} {found_email} / {found_location} ({index}/{total_rows})')
                # time.sleep(10)
        finally:
            return pd.DataFrame(result)

    # def page_down(self):
    #     body = self.driver.find_element_by_tag_name('body')
    #     body.send_keys(Keys.PAGE_DOWN)
    #
    # def page_up(self):
    #     body = self.driver.find_element_by_tag_name('body')
    #     body.send_keys(Keys.PAGE_UP)
    #
    # def fetch_list(self):
    #     items = self.driver.find_elements_by_xpath('/html/body/div[7]/div[3]/div/div/div/div/div/div/div/div/section/ul/li')
    #     contact_list = [self.scrape_email(i) for i in items]
    #     return contact_list
    #
    # def scrape_email(self, item):
    #     anchor = item.find_element_by_class_name('mn-connection-card__picture')
    #     href = anchor.get_attribute('href')
    #     contact = item.find_element_by_class_name('mn-connection-card__details')\
    #         .find_element_by_tag_name('a')\
    #         .find_element_by_class_name('mn-connection-card__name')
    #
    #     contact_name = contact.text
    #     return {'name': contact_name, 'href': href}
    #
    # def scroll_to_bottom(self, web_driver):
    #     tolerance = 0
    #     while True:
    #         # Get old scroll position
    #         old_position = web_driver.execute_script(
    #             ("return (window.pageYOffset !== undefined) ?"
    #              " window.pageYOffset : (document.documentElement ||"
    #              " document.body.parentNode || document.body);"))
    #         # Sleep and Scroll
    #         time.sleep(1)
    #         web_driver.execute_script((
    #             "var scrollingElement = (document.scrollingElement ||"
    #             " document.body);scrollingElement.scrollTop ="
    #             " scrollingElement.scrollHeight;"))
    #         # Get new position
    #         new_position = web_driver.execute_script(
    #             ("return (window.pageYOffset !== undefined) ?"
    #              " window.pageYOffset : (document.documentElement ||"
    #              " document.body.parentNode || document.body);"))
    #
    #         if new_position == old_position:
    #             self.page_up()
    #             time.sleep(1)
    #             tolerance += 1
    #
    #         if tolerance > 15:
    #             break

    # def begin(self):
    #
    #     driver = self.driver
    #
    #     self.get_page(1)
    #
    #     # Determines how many pages it will need to scan
    #     try:
    #         pagination_list = WebDriverWait(driver, 10).until(
    #             EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class, 'artdeco-pagination')]"))
    #         )
    #
    #         last_page_btn_span = pagination_list.find_elements_by_xpath(
    #             "//li[contains(@class, 'artdeco-pagination__indicator artdeco-pagination__indicator--number ember-view')]//span")[
    #             -1]
    #         last_page_value = int(last_page_btn_span.text)
    #
    #         self.total_pages = last_page_value
    #
    #         print("Found {0} pages.".format(last_page_value))
    #
    #         self.extract()
    #     finally:
    #         self.save_all_and_quit()

    # def save_all_and_quit(self):
    #     self.driver.quit()

    def run(self):
        # self.driver.get(self.connections_url)
        # time.sleep(2)
        # body = self.driver.find_element_by_tag_name('body')
        # body.click()
        # self.scroll_to_bottom(self.driver)
        #
        # file_path = "C:\\dev\\scratches\\"
        # file_name = "2020-12-31-results-1.csv"

        for rf in RESULT_FILES:
            driver = self.perform_login()

            df = pd.read_csv(os.path.join(RESULT_PATH, rf))
            df2 = self.extract(df, driver)

            df2.to_csv(os.path.join(RESULT_PATH, f'(MATCHED) {rf}'))

        print('done.')


if __name__ == "__main__":
    app = ScraperApplication(sys.argv[1])
    app.run()
