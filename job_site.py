import pandas as pd
import numpy as np
import time
from datetime import datetime
from urllib import request
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By


class _BaseSite:
    """
    A base class for job site scraping.

    This class provides common functionalities needed for scraping job listings from various job sites.
    It includes methods for fetching job description pages, and loading geographical data which can be
    used for filtering or categorization of job listings.

    Attributes:
        name (str): The name of the job site.
        url (str): The base URL of the job site.

    Methods:
        __init__(self, name, url): Constructor to initialize the job site with a name and URL.
        _get_job_desc_page_source(self, job_info_dict): Fetches and parses the job description page
            given a dictionary containing the job description URL ('desc' key). Returns a BeautifulSoup
            object of the page source, or None if an error occurs.
        _foreign_countries(self): Loads and returns a list of foreign country names from a CSV file.
        _non_us_cities(self): Loads and returns a list of non-US city names from a CSV file.
        _us_cities(self): Loads and returns a list of US city names from a CSV file.
        _us_states_full(self): Loads and returns a list of full US state names from a CSV file.
        _us_states_abbreviated(self): Loads and returns a list of abbreviated US state names from a CSV file.
    """

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def _get_job_desc_page_source(self, job_info_dict):
        try:
            job_page = request.urlopen(job_info_dict['desc'])
            return BeautifulSoup(job_page, features="lxml")
        except:
            return None

    def _foreign_countries(self):
        return pd.read_csv(
            'files/helpers/foreign_countries.csv')['name'].values.flatten()

    def _non_us_cities(self):
        return pd.read_csv(
            'files/helpers/non_us_cities.csv')['name'].values.flatten()

    def _us_cities(self):
        return pd.read_csv(
            'files/helpers/us_cities.csv')['name'].values.flatten()

    def _us_states_full(self):
        return pd.read_csv(
            'files/helpers/us_states_full.csv')['name'].values.flatten()

    def _us_states_abbreviated(self):
        return pd.read_csv('files/helpers/us_states_abbreviated.csv'
                           )['name'].values.flatten()


class Lever(_BaseSite):
    """
    A specialized scraper for the Lever job site.

    Inherits from _BaseSite to use its common scraping functionalities and implements site-specific
    methods for processing, validating, and saving job listings from Lever.

    Methods:
        __init__(self): Initializes the scraper with Lever's name and URL.
        clean_scraped_links(self, links): Cleans and processes a list of scraped job links.
        _process_links(self, links): Processes each link to ensure it is a valid job link and
            formats it for further processing.
        _validate_link(self, link): Checks if a given link is a valid job link for Lever.
        _write_links_to_history(self, links): Writes the processed job links to a history file.
        _parse_location_info(self, page_source): Parses the location information from a job's page source.
        _check_if_exists_in_array(self, value_to_check, array): Checks if a given value exists in an array.
        _validate_location_in_usa(self, locations, us_states_full, us_states_abbreviated,
                                  us_cities, non_us_cities, foreign_countries): Validates if the job location
                                  is in the USA based on various location arrays.
        save_job_info(self, jobs): Saves the information of jobs that are located in the USA.
        apply_to_job(self, browser, user_info, url): Automates the job application process on Lever.
    """

    def __init__(self):
        super().__init__(name='lever', url='lever.co')

    def clean_scraped_links(self, links):
        clean_links = self._process_links(links)
        self._write_links_to_history(clean_links)
        return clean_links

    def _process_links(self, links):
        jobs = []
        for iLink in links:
            record = {'desc': None, 'apply': None}
            if self._validate_link(iLink) is True:
                if iLink.split('/')[-1].lower() != 'apply':
                    record['desc'] = iLink
                    if iLink[-1] != '/':
                        iLink += '/'
                    iLink += 'apply'
                    record['apply'] = iLink
                else:
                    record['apply'] = iLink
                    record['desc'] = iLink.replace('apply', '')
                jobs.append(record)
        return jobs

    def _validate_link(self, link):
        if link:
            if len(link) > len(self.url):
                if self.url in link[:len(self.url)]:
                    if '/?q=' not in link:
                        if len(
                                link.replace('https://jobs.lever.co/',
                                             '').split('/')) > 1:
                            return True
        return False

    def _write_links_to_history(self, links):
        with open('files/output/scraped_urls.txt', 'a') as file:
            for iLink in links:
                file.write(iLink['apply'])
                file.write('\n')
                file.write(iLink['desc'])
                file.write('\n')

    def _parse_location_info(self, page_source):
        try:
            return [
                i.lower() for i in set(
                    page_source.find('div', class_='location').text.replace(
                        ',', '').split(' ')) if i != ''
            ]
        except Exception as e:
            return None

    def _check_if_exists_in_array(self, value_to_check, array):
        return bool(np.where(array == value_to_check)[0].size)

    def _validate_location_in_usa(self, locations, us_states_full,
                                  us_states_abbreviated, us_cities,
                                  non_us_cities, foreign_countries):
        for iLocation in locations:
            if len(iLocation) == 2:
                if self._check_if_exists_in_array(
                        iLocation, us_states_abbreviated) == True:
                    return True

            if self._check_if_exists_in_array(iLocation,
                                              foreign_countries) == True:
                return False

            if self._check_if_exists_in_array(iLocation,
                                              us_states_full) == True:
                return True

            if self._check_if_exists_in_array(iLocation, us_cities) == True:
                return True

            if self._check_if_exists_in_array(iLocation,
                                              non_us_cities) == True:
                return False

        return None

    def save_job_info(self, jobs):
        job_info = []
        foreign_countries = self._foreign_countries()
        non_us_cities = self._non_us_cities()
        us_cities = self._us_cities()
        us_states_full = self._us_states_full()
        us_states_abbreviated = self._us_states_abbreviated()
        for iJob in jobs:
            job_page_source = self._get_job_desc_page_source(iJob)
            if job_page_source is not None:
                job_location = self._parse_location_info(job_page_source)
                if job_location is not None:
                    is_usa = self._validate_location_in_usa(
                        job_location, us_states_full, us_states_abbreviated,
                        us_cities, non_us_cities, foreign_countries)

                    if is_usa is True:
                        job_data = _LeverJob(job_page_source, iJob['desc'],
                                             iJob['apply'])
                        job_info.append(job_data.export_posting_info())

        if len(job_info) > 1:
            job_info = pd.DataFrame.from_records(job_info)
            save_path = 'files/output/main.csv'
            try:
                job_info.to_csv(save_path,
                                index=False,
                                mode='x',
                                header=True,
                                lineterminator='\n')
            except:
                job_info.to_csv(save_path,
                                index=False,
                                mode='a',
                                header=False,
                                lineterminator='\n')

    def apply_to_job(self, browser, user_info, url):
        apply_to_lever = _LeverApply(browser, user_info)
        apply_to_lever._apply_to_job(url)


class _LeverJob:
    """
    Represents a job posting scraped from the Lever job site.

    This class encapsulates the details of a job posting, including company name, job title, team,
    working hours, work-from-home availability, salary range, job description, qualifications, and
    links to the job posting and application page. It provides methods to parse these details from
    the job page source.

    Attributes:
        job_page_source (BeautifulSoup): The BeautifulSoup object containing the HTML of the job page.
        location (str): The location of the job.
        company (str): The name of the company posting the job.
        title (str): The title of the job.
        team (str): The team or department the job belongs to.
        hours (str): The working hours for the job.
        wfh (str): Work-from-home availability.
        min_salary (float): The minimum salary offered for the job.
        max_salary (float): The maximum salary offered for the job.
        desc (str): The job description.
        qual (str): The qualifications required for the job.
        posting (str): The URL of the job description page.
        apply (str): The URL of the job application page.
        scraped (str): The date when the job was scraped.

    Methods:
        __init__(self, job_page_source, description_link=None, apply_link=None): Initializes a new instance of the class.
        _parse_using_title_tag(self): Parses the company name and job title from the page title tag.
        _parse_location(self): Parses the job location.
        _parse_team(self): Parses the team or department.
        _parse_hours(self): Parses the working hours.
        _parse_wfh(self): Parses the work-from-home availability.
        _parse_desc_and_qual(self): Parses the job description and qualifications.
        _clean_desc_and_qual(self, desc_or_qual): Cleans and formats the job description and qualifications.
        _clean_money_string(self, money_string): Cleans and formats the salary string.
        _parse_salary(self): Parses the salary range.
        export_posting_info(self): Calls parsing methods and returns a dictionary of the job details.
        _record_of_details(self): Returns a dictionary of the job details.
    """

    def __init__(self,
                 job_page_source,
                 description_link=None,
                 apply_link=None):
        self.job_page_source = job_page_source
        self.location = None
        self.company = None
        self.title = None
        self.team = None
        self.hours = None
        self.wfh = None
        self.min_salary = None
        self.max_salary = None
        self.desc = None
        self.qual = None
        self.posting = description_link
        self.apply = apply_link
        self.scraped = datetime.today().strftime('%m/%d/%Y')

    def _parse_using_title_tag(self):
        header_text = self.job_page_source.find('title')
        if header_text:
            try:
                self.company = header_text.text.split('-')[0].strip()
            except:
                self.company = None
            try:
                self.title = header_text.text.split('-')[-1].strip()
            except:
                self.title = None
            if 'remote' in header_text.text.lower():
                self.location = 'Remote'

    def _parse_location(self):
        try:
            if self.location is None:
                self.location = self.job_page_source.find(
                    'div', class_='location').text.rstrip('/')
        except:
            self.location = None

    def _parse_team(self):
        try:
            self.team = self.job_page_source.find(
                'div', class_='department').text.rstrip('/')
        except:
            self.team = None

    def _parse_hours(self):
        try:
            self.hours = self.job_page_source.find(
                'div', class_='commitment').text.rstrip('/')
        except:
            self.hours = None

    def _parse_wfh(self):
        try:
            self.wfh = self.job_page_source.find(
                'div', class_='workplaceTypes').text.rstrip('/')
        except:
            self.wfh = None

    def _parse_desc_and_qual(self):
        try:
            posting_info = self.job_page_source.find_all(
                'div', class_='section page-centered')
        except:
            self.desc = None
            self.qual = None
        try:
            self.desc = self._clean_desc_and_qual(
                posting_info[1].find_all('li'))
        except:
            self.desc = None
        try:
            self.qual = self._clean_desc_and_qual(
                posting_info[2].find_all('li'))
        except:
            self.qual = None

    def _clean_desc_and_qual(self, desc_or_qual):
        raw_string = [
            j.replace('\\xa0', ' ').replace('[', '').replace(']', '')
            for j in [i.text for i in desc_or_qual] if len(j) > 3
        ]
        clean_string = ''
        for iString in raw_string:
            clean_string += iString.replace('"', '') + ' '
        return clean_string

    def _clean_money_string(self, money_string):
        return [
            float(
                i.replace(',', '').replace('$',
                                           '').replace('.',
                                                       '').replace('-', ''))
            for i in money_string.text.split(' ') if '$' in i
        ]

    def _parse_salary(self):
        try:
            salary = []
            potential_salary = self.job_page_source.find(
                'div', {
                    'class': 'section page-centered',
                    'data-qa': 'salary-range'
                })
            if potential_salary:
                salary = self._clean_money_string(potential_salary)
            else:
                closing_paragraph = self.job_page_source.find(
                    'div', {
                        'class': 'section page-centered',
                        'data-qa': 'closing-description'
                    })
                if closing_paragraph:
                    salary = self._clean_money_string(closing_paragraph)
            if len(salary) > 1:
                salary.sort(reverse=True)

                self.max_salary = salary[0]
                self.min_salary = salary[1]
        except:
            self.max_salary = None
            self.min_salary = None

    def export_posting_info(self):
        self._parse_using_title_tag()
        self._parse_location()
        self._parse_team()
        self._parse_hours()
        self._parse_wfh()
        self._parse_desc_and_qual()
        self._parse_salary()
        return self._record_of_details()

    def _record_of_details(self):
        return {
            'company': self.company,
            'title': self.title,
            'team': self.team,
            'location': self.location,
            'hours': self.hours,
            'wfh': self.wfh,
            'min_salary': self.min_salary,
            'max_salary': self.max_salary,
            'desc': self.desc,
            'qual': self.qual,
            'posting': self.posting,
            'apply': self.apply,
            'scraped': self.scraped,
            'applied': False
        }


class _LeverApply:
    """
    Automates the job application process on the Lever platform.

    This class encapsulates the automation of various steps involved in applying for a job through
    the Lever job application portal. It uses a browser automation tool to interact with the web
    interface, filling out forms and submitting the application on behalf of the user.

    Attributes:
        browser (BrowserAutomationTool): An instance of a browser automation tool.
        user_info (dict): A dictionary containing user information such as name, email, resume path, etc.

    Methods:
        __init__(self, browser, user_info): Initializes the _LeverApply instance with a browser tool and user information.
        _apply_to_job(self, url): Navigates to the job application URL and performs the application process.
        _fill_out_basic_info(self): Fills out basic information fields in the application form.
        _fill_out_location_info(self, location): Fills out the location information in the application form.
        _fill_out_custom_questions(self): Fills out custom question fields in the application form.
        _fill_out_sponsorship(self, custom_question): Fills out sponsorship-related questions in the application form.
        _upload_resume(self): Uploads the user's resume to the application form.
        _submit_application(self): Submits the completed job application form.
        _wrap_try_catch(self, func, **kwargs): Wraps function calls in a try-catch block to handle exceptions gracefully.
    """

    def __init__(self, browser, user_info):
        self.browser = browser
        self.user_info = user_info

    def _apply_to_job(self, url):
        self.browser.navigate(url)
        self._upload_resume()
        self._fill_out_basic_info()
        self._wrap_try_catch(self._fill_out_custom_questions)
        self._submit_application()

    def _fill_out_basic_info(self):
        self._wrap_try_catch(self.browser.write_input,
                             find_input_field_by=By.NAME,
                             input_field_name='name',
                             input_value=self.user_info['name'])
        self._wrap_try_catch(self.browser.write_input,
                             find_input_field_by=By.NAME,
                             input_field_name='email',
                             input_value=self.user_info['email'])
        self._wrap_try_catch(self.browser.write_input,
                             find_input_field_by=By.NAME,
                             input_field_name='phone',
                             input_value=self.user_info['phone'])
        self._wrap_try_catch(self._fill_out_location_info,
                             location=self.user_info['location'])
        self._wrap_try_catch(self.browser.write_input,
                             find_input_field_by=By.NAME,
                             input_field_name='org',
                             input_value=self.user_info['current_company'])
        self._wrap_try_catch(self.browser.write_input,
                             find_input_field_by=By.NAME,
                             input_field_name='urls[LinkedIn]',
                             input_value=self.user_info['linkedin'])
        self._wrap_try_catch(self.browser.set_value_of_select_element,
                             find_element_by=By.NAME,
                             selector_value='eeo[gender]',
                             input_value=self.user_info['gender'])
        self._wrap_try_catch(self.browser.set_value_of_select_element,
                             find_element_by=By.NAME,
                             selector_value='eeo[race]',
                             input_value=self.user_info['race'])
        self._wrap_try_catch(self.browser.set_value_of_select_element,
                             find_element_by=By.NAME,
                             selector_value='eeo[veteran]',
                             input_value=self.user_info['veteran_status'])

    def _fill_out_location_info(self, location):
        self.browser.write_input(By.ID, 'location-input', location)
        time.sleep(3)
        self.browser.get_single_element(By.CLASS_NAME,
                                        'dropdown-results').find_element(
                                            By.TAG_NAME, 'div').click()

    def _fill_out_custom_questions(self):
        questions = self.browser.get_array_of_elements(By.CLASS_NAME,
                                                       'custom-question')
        for iQuestion in questions:
            self._fill_out_sponsorship(iQuestion)

    def _fill_out_sponsorship(self, custom_question):
        if 'eligible' in custom_question.text.lower(
        ) or 'author' in custom_question.text.lower():
            current_element_inputs = custom_question.find_elements(
                By.TAG_NAME, 'input')
            if current_element_inputs is not None:
                for iElement in current_element_inputs:
                    if iElement.get_attribute('value').lower(
                    ) == self.user_info['authorized'].lower():
                        try:
                            iElement.click()
                        except:
                            self.browser.execute("arguments[0].click();",
                                                 iElement)

        elif 'sponsor' in custom_question.text.lower():
            current_element_inputs = custom_question.find_elements(
                By.TAG_NAME, 'input')
            if current_element_inputs is not None:
                for iElement in current_element_inputs:
                    if iElement.get_attribute('value').lower(
                    ) == self.user_info['sponsor'].lower():
                        try:
                            iElement.click()
                        except:
                            self.browser.execute("arguments[0].click();",
                                                 iElement)

    def _upload_resume(self):
        self._wrap_try_catch(self.browser.upload_file,
                             find_input_field_by=By.ID,
                             input_field_name='resume-upload-input',
                             file_path=self.user_info['resume_path'])
        time.sleep(5)

    def _submit_application(self):
        self._wrap_try_catch(self.browser.click_button,
                             find_element_by=By.ID,
                             selector_value='btn-submit')

    def _wrap_try_catch(self, func, **kwargs):
        try:
            func(**kwargs)
            time.sleep(np.random.uniform(0.05, 1))
        except Exception as e:
            print(e)
