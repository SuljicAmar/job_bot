from selenium.webdriver.common.by import By


class DuckDuckGo:
    """
    A class to interact with the DuckDuckGo search engine for job searching.

    This class uses a web browser controlled by Selenium to navigate DuckDuckGo,
    submit search queries, and scrape job posting links from the search results.

    Attributes:
        browser: A WebDriver instance for browser automation.
        name (str): A name identifier for the search engine, set to 'DuckDuckGo'.
        url (str): The URL of the DuckDuckGo search engine homepage.

    Methods:
        __init__(self, browser): Initializes the DuckDuckGo instance with a browser.
        search_jobs(self, job_title, job_site, pages): Searches for jobs on DuckDuckGo
            by submitting a query for a specific job title on a specific job site across
            a specified number of pages.
        _scrape_job_postings(self, page_source, html_tag='a'): Private method to scrape
            job posting links from the page source. By default, it looks for 'a' tags.
    """

    def __init__(self, browser):
        # Initialize the DuckDuckGo object with a Selenium WebDriver instance.
        self.browser = browser
        self.name = 'DuckDuckGo'
        self.url = 'https://duckduckgo.com/'

    def search_jobs(self, job_title, job_site, pages):
        # Navigate to DuckDuckGo and submit a search query for job postings.
        self.browser.navigate(self.url)
        self.browser.submit_input(By.ID, 'searchbox_input',
                                  f'{job_title} site:{job_site}')
        self.browser.wait_for_element_to_load(By.ID, 'more-results')

        # If more than one page of results is requested, attempt to load additional pages.
        if pages > 1:
            for iPage in range(pages):
                self.browser.scroll_to_bottom_of_page()
                if self.browser.wait_and_click_button(By.ID,
                                                      'more-results') is False:
                    break  # Stop if the more results button is not found or not clickable.
            self.browser.wait_for_element_to_load(By.ID, 'more-results')

        # Scrape and return unique job posting links from the search results.
        return self._scrape_job_postings(self.browser.parse_page_source())

    def _scrape_job_postings(self, page_source, html_tag='a'):
        # Scrape job posting links from the page source using BeautifulSoup.
        all_links = page_source.find_all(html_tag)
        uniq_links = set([i.get('href') for i in all_links])
        return uniq_links
