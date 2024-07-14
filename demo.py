import json
import pandas as pd
from Bot import Bot
from job_site import Lever
from search_engine import DuckDuckGo
from Browser import Browser

# necessary objects
web_driver = Browser()
job_board = Lever()
search_engine = DuckDuckGo(web_driver)
bot = Bot(search_engine, job_board)

################################################################################
########################### Scrape Jobs ########################################
################################################################################
bot.get_jobs('Remote Data Scientist', pages=1)

# this will create a main.csv file in files/output with scraped info
# Note: if you no new data is being scraped, its because of files/output/scraped_urls.txt
# which holds all previously scraped urls so we do not scrape them again.
# simply remove everything in this file to scrape all urls again
bot.save_job_info()
web_driver.quit()

################################################################################
########################### Apply to Jobs #######################################
################################################################################

with open('files/user_info.json') as f:
    user_data = json.load(f)

scraped_jobs = pd.read_csv('files/output/main.csv')
not_applied_to_yet = scraped_jobs.query(f'applied == {False}')

for iUrl in not_applied_to_yet['apply'].unique():
    bot.apply_to_job(user_info=user_data, url=iUrl)
    bot.record_job_as_applied_to(iUrl, scraped_jobs)

scraped_jobs.to_csv('files/output/main.csv', index=False)

web_driver.quit()
