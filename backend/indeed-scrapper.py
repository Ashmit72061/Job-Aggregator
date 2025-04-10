import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

def scrape_indeed_with_selenium(job_title, location, num_pages=2):
    # Initialize the browser
    driver = uc.Chrome()
    jobs_list = []
    
    try:
        # Navigate to Indeed
        driver.get("https://www.indeed.com")
        time.sleep(5)  # Wait for page to load
        
        # Find and fill the search fields
        what_field = driver.find_element(By.ID, "text-input-what")
        where_field = driver.find_element(By.ID, "text-input-where")
        
        what_field.clear()
        where_field.clear()
        
        what_field.send_keys(job_title)
        where_field.send_keys(location)
        where_field.send_keys(Keys.RETURN)
        
        # Wait for results page
        time.sleep(5)
        
        for page in range(num_pages):
            # Extract job listings
            job_cards = driver.find_elements(By.CSS_SELECTOR, ".job_seen_beacon")
            
            for card in job_cards:
                try:
                    title = card.find_element(By.CSS_SELECTOR, "h2.jobTitle span").text
                    company = card.find_element(By.CSS_SELECTOR, '[data-testid="company-name"]').text
                    location = card.find_element(By.CSS_SELECTOR, '[data-testid="text-location"]').text
                    
                    jobs_list.append({
                        "title": title,
                        "company": company,
                        "location": location
                    })
                except Exception as e:
                    print(f"Error extracting job data: {e}")
            
            # Check if there's a next page button and click it
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, '[data-testid="pagination-page-next"]')
                next_button.click()
                time.sleep(5)  # Wait for next page to load
            except:
                print("No more pages available")
                break
    
    finally:
        driver.quit()
    
    return pd.DataFrame(jobs_list)

# Usage
df = scrape_indeed_with_selenium("Machine Learning", "New Delhi", num_pages=2)
df.to_csv("indeed_jobs.csv", index=False)