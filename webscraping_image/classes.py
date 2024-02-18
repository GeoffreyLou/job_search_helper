from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

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
  

class JobScraper:
    """
    Class to scrap informations from jobs such as name, city, company, etc.
    
    Parameters:
    - job : The html element with all the job informations.
    """
    
    def __init__(self, job):
        """
        Initiate a new instance of JobScraper.

        Parameters:
        - job (str): The complete html element with the job informations.
        """
        self.job = job
        
    def get_html_element(self):
        """
        Get the secific html element with the required informations.

        Returns:
        - element: The html element.
        """
                
        element = self.job.find(
            'h3', 
            {'class': 'base-search-card__title'})\
            .text.lower().strip()
            
        return element
    
    def get_job_name(self):
        """
        Get the secific job name with the required informations.

        Returns:
        - job: The job name.
        """
                
        job = self.job.find('h3').text.strip()
        
        return job
    
    def get_company_name(self):
        """
        Get the secific company name with the required informations.

        Returns:
        - company: The company name.
        """

        # Sometimes the company is empty
        try:
            company = self.job.select_one(
                '.base-search-card__info h4.base-search-card__subtitle a.hidden-nested-link')\
                .text.strip()
        except:
            company = 'Not found'
            
        return company
    
    def get_city(self):
        """
        Get the secific city name with the required informations.

        Returns:
        - city: The city name.
        """
        
        city = self.job.select_one('.base-search-card__info span.job-search-card__location')\
            .text.strip()
            
        return city
    
    def get_link(self):
        """
        Get the link to access the job html web page.

        Returns:
        - link: The complete link for that job.
        """
        
        link = self.job.find('a', href=True)['href']
        
        return link