from selenium.webdriver.common.by import By

def scroller(driver):
    """
    Scroll down the web page.

    Parameters : 
    - driver: the Selenium web page driver.
    """
    
    main_scroll = driver.find_element(By.XPATH, '/html')
    driver.execute_script(
        "arguments[0].scrollTop = arguments[0].scrollHeight", main_scroll
    )