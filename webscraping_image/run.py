from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from fake_useragent import UserAgent
from functions import aws_bucket_upload, scroller
from dataframemaker import DataFrameMaker
from jobscraper import JobScraper
import pandas as pd
import time
import os

if __name__ == '__main__':

    # All jobs to scrap
    jobs_to_find = [
        'data analyst', 
        'data engineer', 
        'analytics engineer'
        ]

    # Generate a random user agent
    user_agent = UserAgent().random

    # Selenium options
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')  # Set the user agent
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--ignore-certificate-errors') # Avoid certificate errors
    options.add_argument('--ignore-ssl-errors') # Avoid SSL errors
    options.add_argument('--incognito') # Incognito mode for better results
    options.add_argument('--headless') # The page will not show, better for Docker
    options.add_argument('--disable-gpu') 
    options.add_argument('--lang=fr-FR')
    options.add_argument('--no-sandbox') # Important for Docker usage
    options.add_argument('--disable-dev-shm-usage') # Important for Docker usage
    options.add_argument('--disable-features=MediaSessionService')
    options.add_argument('--disable-features=VizDisplayCompositor')
    driver = webdriver.Chrome(options=options)

    # Empty list to store DataFrames
    dataframes_list = []

    for job_search in jobs_to_find:
        
        # Class instance creation
        scrap_data = DataFrameMaker(job_search)

        # Url to scrap
        # Region = Île-de-France
        # Last 24 hours only          
        url =  f"https://www.linkedin.com/jobs/search/?keywords=\
            {job_search.replace(' ', '%20')}&location=%C3%8Ele-de-France%2C%20\
            France&locationId=&geoId=104246759&f_TPR=r86400&position=1&pageNum=0"

        # Selenium open browser and get the url
        driver.get(url)
        webpage = driver.page_source
        soup = BeautifulSoup(webpage, "html.parser")
        
        # If we have a jobs result list, we can scrap
        jobs_count = False

        try:
            
            # Trying to get a job result count
            soup.find('h1', {'class':'results-context-header__context'}).\
                find('span', {'class': 'results-context-header__job-count'}).text

            jobs_count = True
        
        # If none, maybe Linkedin asked to login
        except Exception as e:
            print("Failed to have jobs results on first try :", e)
            
            # Then waiting and trying again three times
            try:
                
                for i in range(3):
                    time.sleep(15)
                    driver.get(url)
                    webpage = driver.page_source
                    soup = BeautifulSoup(webpage, "html.parser")
                    
                    # Trying again to get a job result count                
                    if soup.find('h1', {'class':'results-context-header__context'})\
                        .find('span', {'class': 'results-context-header__job-count'}).text:
                            
                        # If yes, the loop end
                        jobs_count = True
                        break
                    
                    else:
                        # Else, we try again
                        continue
                    
            except Exception as e:
                print("Failed to get jobs results on second try :", e)
                jobs_count = False
                
        # Jobs count is not None, scrap can start
        if jobs_count:
                    
            # You need to scroll down three times, it's enough to display all jobs
            for i in range(3):
                
                try:
                    scroller(driver)
                    time.sleep(5)
                    
                except Exception as e:
                    print("Unable to scroll on page on first try :", e)
                    time.sleep(5)
                    
                    try:
                        scroller(driver)
                        time.sleep(5)
                        
                    except Exception as e:
                        print("Unable to scroll on page on second try :", e)
                        pass

            jobs_list = soup.find(
                'ul', 
                {'class': 'jobs-search__results-list'}).find_all('li')

            # Each job is a list item
            try:
                
                for job in jobs_list:
                    
                    #  JobScraper class instance creation
                    job_element = JobScraper(job)
                    
                    # Get elements from instance
                    html_element = job_element.get_html_element()
                    job_name = job_element.get_job_name()
                    company = job_element.get_company_name()
                    city = job_element.get_city()
                    link = job_element.get_link()
                    
                    # Adding scraped data to the JobsFinder instance
                    scrap_data.job_append(
                        html_element,
                        job_name,
                        company,
                        city,
                        link)
                    
            except Exception as e:
                # The scrap failed for this job
                print(f'Scrap failed for {job_search} :', e)
                pass
                
            # Making the Dataframe
            df = scrap_data.make_dataframe()
            dataframes_list.append(df)
        
        else:
            # No jobs results, going on next job search
            time.sleep(15)
            continue
        
    # Closing the driver
    driver.quit()

    # Creating dataframe to upload on S3
    final_df = pd.concat(dataframes_list)

    # Creating the dataframe filename
    current_date_time = datetime.now()
    formatted_date_time = current_date_time.strftime("%Y-%m-%d-%H-%M")
    file_name = f'jobs_scrap_{formatted_date_time}.csv'

    # Créating the final DataFrame
    final_df.to_csv(file_name, index=False, encoding='utf-8')

    # AWS connection informations
    bucket_name = os.environ['BUCKET_NAME']
    s3_file = os.environ['FOLDER'] + file_name
    aws_access_key_id = os.environ['KEY_ID']
    aws_secret_access_key = os.environ['SECRET_KEY']
    region = os.environ['REGION']

    # Upload to S3 Bucket
    aws_bucket_upload(
        file_name, 
        bucket_name,
        s3_file,
        aws_access_key_id, 
        aws_secret_access_key, 
        region)

    # Removing the file
    os.remove(file_name)