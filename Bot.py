class Bot:
    """
    A class representing a job search bot.

    This class encapsulates the functionality of a job search bot, allowing for searching, scraping,
    and applying to job listings found on specified job sites. It leverages a search engine and a job site
    object to perform these tasks, ensuring modularity and flexibility in the job search process.

    Attributes:
        search_engine (SearchEngine): The search engine used for job searches. This object is expected
                                      to have a method for searching jobs that returns a list of job links.
        job_site (JobSite): The job site to search for jobs. This object is responsible for the specifics
                            of scraping job listings, cleaning the scraped data, and saving job information.
                            It should provide methods for these tasks.

    Methods:
        __init__(self, search_engine, job_site): Initializes a new instance of the Bot class. It sets up
                                                 the search engine and job site to be used for job searches
                                                 and loads previously scraped links to avoid duplication.
        get_jobs(self, job_title, pages=5): Public method to initiate the job search process based on the
                                            given job title and number of pages to search through. It delegates
                                            the task to a private method.
        _get_job_links(self, job_title, pages=5): Private method that performs the actual search for job links
                                                  using the search engine, filters out previously scraped links,
                                                  and cleans the new links using the job site object.
        save_job_info(self): Saves information from the scraped jobs to a .csv file. This method relies on the
                             job site object's ability to process and save job information.
        apply_to_job(self, user_info, url): Applies to a job using the provided user information and job URL.
        record_job_as_applied_to(self, url, scraped_jobs): Update the applied column of given URL in the scraped jobs table.

    """

    def __init__(self, search_engine, job_site):
        # Initialize the bot with a search engine and a job site, and load previously scraped links
        # to avoid re-scraping the same job listings.
        self.search_engine = search_engine
        self.job_site = job_site
        with open('files/output/scraped_urls.txt') as file:
            self._previously_scraped_links = [line.rstrip() for line in file]

    def get_jobs(self, job_title, pages=5):
        # simply calls the private method to get job links for the specified job title and number of pages.
        self._get_job_links(job_title=job_title, pages=pages)

    def _get_job_links(self, job_title, pages=5):
        # Private method that uses the search engine to find job links, filters out previously
        # scraped links, and then cleans the new links using the job site object.
        scraped_links = self.search_engine.search_jobs(job_title,
                                                       self.job_site.url,
                                                       pages)
        new_links = [
            iLink for iLink in scraped_links
            if iLink not in self._previously_scraped_links
        ]
        self.jobs = self.job_site.clean_scraped_links(new_links)

    def save_job_info(self):
        # Saves the job information of the scraped and cleaned job links. This method delegates
        # the task of saving job information to the job site object.
        self.job_site.save_job_info(self.jobs)

    def apply_to_job(self, user_info, url):
        # Applies to a job using provided user information and job URL. This method delegates the
        # application process to the job site object.
        self.job_site.apply_to_job(self.search_engine.browser, user_info, url)

    def record_job_as_applied_to(self, url, scraped_jobs):
        # Update the applied column of the given URL in the scraped jobs table to indicate that the job
        # has been applied to.
        scraped_jobs.loc[scraped_jobs['apply'] == url, 'applied'] = True
