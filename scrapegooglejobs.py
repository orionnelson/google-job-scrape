import csv
import os
import pyperclip
import pandas as pd
from time import sleep
from selenium import webdriver  # automate web browser interaction from Python
from selenium.webdriver.common.keys import Keys  # refer to keyboard key presses i.e. Keys.RETURN = 'Enter' on keyboard
from selenium.webdriver.common.by import By  # refer to elements by their tag name

class JobListing:
    def __init__(self, *args, **kwargs):
        if len(args) == 2 and isinstance(args[0], list):
            self.title = args[0][0]
            self.company = args[0][1]
            self.location = args[0][2]
            self.via = args[0][3]
            self.age = args[0][4]
            self.time = args[0][5]
            self.link = args[1]
        else:
            self.title = kwargs.get('title', '')
            self.company = kwargs.get('company', '')
            self.location = kwargs.get('location', '')
            self.via = kwargs.get('via', '')
            self.age = kwargs.get('age', '')
            self.time = kwargs.get('time', '')
            self.link = kwargs.get('link', '')

    def __str__(self):
        return f"""Title: {self.title}\nCompany: {self.company}\nLocation: {self.location}\nVia: {self.via}\nAge: {self.age}\nTime: {self.time}\nLink: {self.link}"""
    
    def to_dict(self):
        return {
            'Job Title': self.title,
            'Company': self.company,
            'Location': self.location,
            'Via': self.via,
            'Age': self.age,
            'Time': self.time,
            'Link': self.link
        }



class GoogleJobsScraper:
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_experimental_option("detach",True)
    driver = webdriver.Chrome(options=options)

    def __init__(self, jobtitle):
        self.current_driver = GoogleJobsScraper.driver
        self.jobtitle = jobtitle
        self.results = {}

    def fetch_jobs(self):
        all_jobs = set()
        self.current_driver.get(f"""https://www.google.com/search?q={self.jobtitle}&ibp=htl;jobs#htivrt=jobs&fpstate=tldetail&htichips=date_posted:3days&htischips=date_posted;3days""")
        sleep(2)  # Wait for the page to load

        ul_element = self.current_driver.find_element(By.TAG_NAME, 'ul')
        #scroll downward on the ul until the li elements do not change
        
        ## Get the scrollable element
        scrollable_element = self.current_driver.find_element(By.XPATH, "//*[contains(@aria-label,'Jobs list')]/..")

        # Get the ul element that is a child of the scrollable element
        ul_element = scrollable_element.find_element(By.TAG_NAME, 'ul')

        # Keep track of the current and previous number of li elements
        previous_li_count = 0 
        current_li_count = len(ul_element.find_elements(By.TAG_NAME, 'li'))
        x = 1
        while x > 0:
            ul_element = self.current_driver.find_element(By.TAG_NAME, 'ul')
            li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
            x -= 1
       
            for li in li_elements:
                li.click()  # Click on each li element
                link = self.fetch_link()
                sleep(2)  # Wait for the page to load
                
                job_elements = self.current_driver.find_elements(By.CLASS_NAME, 'gws-plugins-horizon-jobs__tl-lif')
                # Keep Track Of a Bunch Of Job Listings But Require Matching
                # Array Of Arrays We need To find The array that Matches the following text 
                current_title = self.current_driver.find_elements(By.XPATH, "//*[contains(@id,'tl_ditc')]//h2")
                title_text = ""
                for item in current_title:
                    if item.text:
                        title_text = item.text
                for job in job_elements:
                    job_info = job.text.split('\n')  # Assuming a set order and split by new line character
                    # Job info may Contain an Erronious One Character Entry So We Should Remove this one Character Entry From The List
                    #Filter Job Info List to Remove Items With length less than 1 
                    job_info = list(filter(lambda x: len(x) > 1, job_info))

                    if title_text in job_info:
                        try:
                            #print("ADDED JOB")
                            j_listing = JobListing(job_info, link)
                        except IndexError:
                            #print(f"""Error: {job_info}""")
                            j_listing = f"Error: {job_info} {link}"
                        all_jobs.add(j_listing)
            self.current_driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_element)
            sleep(1)  # Wait for new li elements to load
        #print(link)
        return all_jobs



                
                # self.results.append(job_info)

    def fetch_link(self):
        svg_path = self.current_driver.find_element(By.XPATH, "//*[contains(@id,'tl_ditc')]//*[contains(@d,'M18 16.08c-.76 0-1.44.3-1.96.77')]")#"//svg/path[@d='M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z']")
        svg_parent = svg_path.find_element(By.XPATH, '..')
        svg_parent.click()
        sleep(1)  # Wait for the page to react

        # Click on input with aria-label "Share link"


        input_element = self.current_driver.find_element(By.XPATH, "//*[contains(@id,'lb')]//*[contains(@d,'M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41')]/../../..//*[contains(@type,'url')]")
        #input_element.screenshot("test.png")
        input_element.click()
    
     
        #input_element_parent.screenshot("test.png")
        #input_element_parent.click()
        sleep(1)  # Wait for the page to react
        self.current_driver.find_element(By.XPATH, "//*[contains(@id,'lb')]//*[contains(@d,'M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41')]").click()
        sleep(5)
       #print(pyperclip.paste())
        #click exit button
        return pyperclip.paste()
    
    def output_to_csv(self, jobtitle,jobs):
        #Make results folder if it does not exist
        results_folder = os.path.join(os.path.dirname(__file__),'results')
        if not os.path.exists(results_folder):
            os.mkdir('results')
        new_filename = os.path.join(results_folder,f"{'_'.join(jobtitle.split())}.csv")
        with open(new_filename, 'w', newline='', encoding='utf-8', errors='ignore') as csvfile:
            fieldnames = ['Job Title', 'Company', 'Location', 'Via', 'Age', 'Time', 'Link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # assuming fetch_jobs() has been called and self.results is a list of JobListing objects
            for job_listing in jobs:
                try:
                    writer.writerow(job_listing.to_dict())
                except:
                    pass
        #Clean Up With Pandas After
        job_listings_file = pd.read_csv(new_filename)
        job_listings_file_removed_duplicates = job_listings_file.drop_duplicates(subset=["Job Title", "Company", "Location"], keep="first")
        job_listings_file_removed_duplicates.to_csv(new_filename, index=False) 

    def close_browser(self):
        self.current_driver.quit()



if __name__ == '__main__':
    while True:
        jobtitle = input('Enter job title: ')
        if jobtitle == "text":
            with open("Positions.txt", "r", encoding='utf-8',errors='ignore') as f:
                for listing in f.readlines():
                    scraper = GoogleJobsScraper(listing)
                    jobs = scraper.fetch_jobs()
                    scraper.output_to_csv(listing,jobs)
        else:
            scraper = GoogleJobsScraper(jobtitle)
            jobs = scraper.fetch_jobs()
            scraper.output_to_csv(jobtitle,jobs)
        #scraper.close_browser()