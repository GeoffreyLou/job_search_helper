from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import pandas as pd
import boto3
import time
import os

# All jobs to scrap
jobs_list = ['data analyst', 'data engineer', 'analytics engineer']


class JobsFinder:
    """
    Class to scrap data from job offers and create a DataFrame.

    Attributes:
    - date (str): The date of the scrap.
    - Week (int): The ISO week number of the scrap.
    - job_search (str): The name of the job to search.
    - jobs_dict (dict): An empty dictionary to store scraped data.
    """

    def __init__(self, job_search):
        """
        Initiate a new instance of JobsFinder.

        Parameters:
        - job_search (str): The name of the job to search.
        """
        date = datetime.now()
        self.date_formatted = date.strftime("%Y-%m-%d")
        self.week = date.isocalendar()[1]
        self.job_search = job_search
        self.jobs_dict = {
            'Date': [],
            'Week': [],
            'Job search': [],
            'Job name': [],
            'Company': [],
            'City': [],
            'Link': []
        }
        
    def job_append(self, html_element, job_name, company, city, link):
        
        """
        If the job to search is in the job title, then the data is 
        added to the dictionary.

        Parameters:
        - html_element (str): HTML element of job title.
        - job_name (str): Job title.
        - company (str): Company name.
        - city (str): City name.
        - link (str): Link to the job offer.
        """
        
        if self.job_search in html_element:
            self.jobs_dict['Date'].append(self.date_formatted)
            self.jobs_dict['Week'].append(self.week)
            self.jobs_dict['Job search'].append(self.job_search)
            self.jobs_dict['Job name'].append(job_name)
            self.jobs_dict['Company'].append(company)
            self.jobs_dict['City'].append(city)   
            self.jobs_dict['Link'].append(link)                
        
    def make_dataframe(self):
        
        """
        Create and return a DataFrame with all the data for the job to search.

        Returns:
        - pd.DataFrame: The DataFrame with all the data.
        """
        
        df_name = f'{self.job_search}_df'
        df = pd.DataFrame(self.jobs_dict)
        setattr(self, df_name, df)
        return df
    
    
def aws_bucket_upload(filename, 
                      bucket_name,
                      s3_file,
                      aws_access_key_id, 
                      aws_secret_access_key, 
                      region):
    
    """
    Load Pandas DataFrame to a AWS S3 Bucket.

    Parameters : 
    - dataframe: Pandas DataFrame to upload.
    - bucket_name: Name of the AWS S3 Bucket.
    - s3_file: Name of the file after upload on S3 Bucket.
    - aws_access_key_id: AWS access key.
    - aws_secret_access_key: AWS secret access key.
    - region: The region where the S3 bucket is.
    """
    
    try: 
        
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region
            )
        
        s3.upload_file(
            filename,
            bucket_name,
            s3_file
            )
        
    except Exception as e:
        print(e)
        

# Selenium options
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors') # Avoid certificate errors
options.add_argument('--incognito') # Incognito mode for better results
options.add_argument('--headless') # The page will not show, better for Docker & virtual machines
options.add_argument('--disable-gpu') 
options.add_argument('--lang=fr-FR')
options.add_argument('--disable-features=MediaSessionService')
options.add_argument('--disable-features=VizDisplayCompositor')

# Empty list to store DataFrames
dataframes_list = []

for job_search in jobs_list:
    
    # Class instance
    scrap_data = JobsFinder(job_search)

    # Url to scrap
    url = f"https://www.linkedin.com/jobs/search/?currentJobId=3743863619&f_TPR=\
        r86400&geoId=104246759&keywords={job_search.replace(' ', '%20')}&location\
        =%C3%8Ele-de-France%2C%20France&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true"

    # Selenium open browser and get the url
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # You need to scroll to see all available jobs.
    # Scroll down three times, it's enough to display all jobs
    for i in range(3):
        try:
            main_scroll = driver.find_element(By.XPATH, '/html')
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", main_scroll)
            time.sleep(3)
        except:
            time.sleep(5)
            try:
                main_scroll = driver.find_element(By.XPATH, '/html')
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", main_scroll)
                time.sleep(3)
            except:
                pass

    # The web page is ready for Beautifulsoup
    webpage = driver.page_source
    soup = BeautifulSoup(webpage, "html.parser")

    # Each job is a list item
    for i in soup.find('ul', {'class': 'jobs-search__results-list'}).find_all('li'):
        html_element = i.find('h3', {'class': 'base-search-card__title'}).text.lower().strip()
        job_name = i.find('h3').text.strip()
        
        # Sometimes the company is empty
        try: 
            company = i.select_one('.base-search-card__info h4.base-search-card__subtitle a.hidden-nested-link').text.strip()
        except:
            company = 'Not found'
            
        city = i.find('span', {'class': 'job-search-card__location'}).text.strip()
        link = i.find('a', href=True)['href']
        
        # Adding scraped data to the instance        
        scrap_data.job_append(
            html_element,
            job_name,
            company,
            city,
            link)
        
    # Making the Dataframe
    df = scrap_data.make_dataframe()
    dataframes_list.append(df)
    
    driver.quit()
    

final_df = pd.concat(dataframes_list)

current_date_time = datetime.now()
formatted_date_time = current_date_time.strftime("%Y-%m-%d-%H-%M")
file_name = f'jobs_scrap_{formatted_date_time}.csv'

final_df.to_csv(file_name, index=False, encoding='utf-8')

bucket_name = os.environ['BUCKET_NAME']
s3_file = os.environ['FOLDER'] + file_name
aws_access_key_id = os.environ['KEY_ID']
aws_secret_access_key = os.environ['SECRET_KEY']
region = os.environ['REGION']

aws_bucket_upload(
    file_name, 
    bucket_name,
    s3_file,
    aws_access_key_id, 
    aws_secret_access_key, 
    region)

os.remove(file_name)
