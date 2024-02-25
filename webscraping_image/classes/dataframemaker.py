import pandas as pd
from datetime import datetime

class DataFrameMaker:
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
        
    def job_append(self, lower_job_name, job_name, company, city, link):
        """
        If the job to search is in the job title, then the data is 
        added to the dictionary.

        Parameters:
        - lower_job_name (str): Lower job title.
        - job_name (str): Job title.
        - company (str): Company name.
        - city (str): City name.
        - link (str): Link to the job offer.
        """
        
        if self.job_search in lower_job_name:
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