class JobScraper:
    """
    Class to scrap informations from jobs such as name, city, company, etc.
    
    Parameters:
    - job : The html element with all the job informations.
    """
    
    def __init__(self, job_html_element):
        """
        Initiate a new instance of JobScraper.

        Parameters:
        - job (str): The complete html element with the job informations.
        """
        self.job_html_element = job_html_element
        
    def get_lower_job_name(self):
        """
        Get the secific html element with the required informations.

        Returns:
        - element: The html element.
        """
                
        element = self.job_html_element.find(
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
                
        job = self.job_html_element.find('h3').text.strip()
        
        return job
    
    def get_company_name(self):
        """
        Get the secific company name with the required informations.

        Returns:
        - company: The company name.
        """

        # Sometimes the company is empty
        try:
            company = self.job_html_element.select_one(
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
        
        city = self.job_html_element.select_one('.base-search-card__info span.job-search-card__location')\
            .text.strip()
            
        return city
    
    def get_link(self):
        """
        Get the link to access the job html web page.

        Returns:
        - link: The complete link for that job.
        """
        
        link = self.job_html_element.find('a', href=True)['href']
        
        return link