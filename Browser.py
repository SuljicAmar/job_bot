import undetected_chromedriver as uc
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup


class Browser:
    """
    A wrapper class for Selenium WebDriver to simplify interactions with web pages.

    This class provides simplified methods for common web automation tasks such as
    navigating to a URL, clicking buttons, selecting from dropdowns, and parsing
    the page source with BeautifulSoup.

    Attributes:
        _browser: A Selenium WebDriver instance for browser automation.

    Methods:
        __init__: Initializes the Browser with an undetected ChromeDriver instance.
        set_value_of_select_element: Selects an option in a dropdown by its value.
        navigate: Navigates the browser to a specified URL.
        wait_and_click_button: Waits for a button to be clickable and then clicks it.
        get_single_element: Returns a single web element found by a specific selector.
        get_array_of_elements: Returns a list of web elements found by a specific selector.
        click_button: Clicks a button found by a specific selector.
        execute: Executes a JavaScript script in the context of the current page.
        scroll_to_bottom_of_page: Scrolls the browser window to the bottom of the page.
        wait_for_element_to_load: Waits for an element to be present on the page.
        parse_page_source: Parses the current page source with BeautifulSoup.
        clear_input_element: Clears the text of an input field.
        _write_to_input_element: Writes text to an input field (private method).
        write_input: Writes text to an input field.
        submit_input: Writes text to an input field and submits the form.
        upload_file: Uploads a file to an input field of type 'file'.
        quit: Closes the browser and quits the WebDriver session.
    """

    def __init__(self):
        # Initialize the Browser object with an undetected ChromeDriver instance.
        self._browser = uc.Chrome(use_subprocess=False)

    def set_value_of_select_element(self, find_element_by, selector_value,
                                    input_value):
        # Selects an option in a dropdown by its value.
        Select(self._browser.find_element(
            find_element_by, selector_value)).select_by_value(input_value)

    def navigate(self, url):
        # Navigates the browser to a specified URL.
        self._browser.get(url)

    def wait_and_click_button(self, find_element_by, selector_value):
        # Waits for a button to be clickable and then clicks it.
        button = WebDriverWait(driver=self._browser,
                               timeout=10,
                               poll_frequency=1).until(
                                   EC.element_to_be_clickable(
                                       (find_element_by, selector_value)))
        if button:
            button.click()
            return True
        return False

    def get_single_element(self, find_element_by, selector_value):
        # Returns a single web element found by a specific selector.
        return self._browser.find_element(find_element_by, selector_value)

    def get_array_of_elements(self, find_element_by, selector_value):
        # Returns a list of web elements found by a specific selector.
        return self._browser.find_elements(find_element_by, selector_value)

    def click_button(self, find_element_by, selector_value):
        # Clicks a button found by a specific selector.
        self._browser.find_element(find_element_by, selector_value).click()

    def execute(self, script, args=None):
        # Executes a JavaScript script in the context of the current page.
        if args is None:
            self._browser.execute_script(script)
        else:
            self._browser.execute_script(script, args)

    def scroll_to_bottom_of_page(self):
        # Scrolls the browser window to the bottom of the page.
        self.execute('window.scrollTo(0, document.body.scrollHeight);')

    def wait_for_element_to_load(self, find_element_by, selector_value):
        # Waits for an element to be present on the page.
        WebDriverWait(self._browser, 10).until(
            EC.presence_of_element_located((find_element_by, selector_value)))

    def parse_page_source(self, features='lxml'):
        # Parses the current page source with BeautifulSoup.
        return BeautifulSoup(self._browser.page_source, features=features)

    def clear_input_element(self, find_input_field_by, input_field_name):
        # Clears the text of an input field.
        self._browser.find_element(find_input_field_by,
                                   input_field_name).clear()

    def _write_to_input_element(self, find_input_field_by, input_field_name,
                                input_value):
        # Writes text to an input field (private method).
        search_field = self._browser.find_element(find_input_field_by,
                                                  input_field_name)
        search_field.clear()
        time.sleep(1)
        search_field.send_keys(input_value)
        return search_field

    def write_input(self, find_input_field_by, input_field_name, input_value):
        # Writes text to an input field.
        self._write_to_input_element(find_input_field_by, input_field_name,
                                     input_value)

    def submit_input(self, find_input_field_by, input_field_name, input_value):
        # Writes text to an input field and submits the form.
        search_field = self._write_to_input_element(find_input_field_by,
                                                    input_field_name,
                                                    input_value)
        search_field.submit()

    def upload_file(self, find_input_field_by, input_field_name, file_path):
        # Uploads a file to an input field of type 'file'.
        self._browser.find_element(find_input_field_by,
                                   input_field_name).send_keys(file_path)

    def quit(self):
        # Closes the browser and quits the WebDriver session.
        self._browser.quit()
