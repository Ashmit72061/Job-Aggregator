#!/usr/bin/env python3
"""
Naukri.com Web Scraper using Selenium

This script uses Selenium WebDriver to scrape job listings from Naukri.com
with support for search filters like job title, location, and experience.
"""

import time
import random
import csv
import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager


class NaukriSeleniumScraper:
    def __init__(self, headless=True, disable_images=True):
        """
        Initialize the Naukri.com scraper with Selenium WebDriver
        
        Args:
            headless (bool): Whether to run Chrome in headless mode
            disable_images (bool): Whether to disable image loading to speed up scraping
        """
        # Set up Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # User agent to mimic a real browser
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        
        # Disable images to speed up the scraping
        if disable_images:
            chrome_prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", chrome_prefs)
        
        # Initialize the Chrome WebDriver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = "https://www.naukri.com"
    
    def close(self):
        """Close the WebDriver when done"""
        if self.driver:
            self.driver.quit()
    
    def navigate_to_search_page(self):
        """Navigate to Naukri's main search page"""
        self.driver.get(self.base_url)
        time.sleep(3)  # Allow page to load
        
        # Handle any popup that might appear
        try:
            popup_close = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "crossIcon"))
            )
            popup_close.click()
            time.sleep(1)
        except TimeoutException:
            pass  # No popup found, continue
    
    def search_jobs(self, keyword, location=None, experience=None):
        """
        Search for jobs with the given criteria
        
        Args:
            keyword (str): Job title or keywords
            location (str, optional): Job location
            experience (str, optional): Years of experience
        """
        self.navigate_to_search_page()
        
        try:
            # Find and fill the keyword search box
            search_box = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "suggestor-input"))
            )
            search_box.clear()
            search_box.send_keys(keyword)
            
            # Add location if provided
            if location:
                try:
                    location_box = self.driver.find_element(By.CSS_SELECTOR, '[placeholder="Enter location"]')
                    location_box.clear()
                    location_box.send_keys(location)
                except NoSuchElementException:
                    print("Location input field not found.")
            
            # Click the search button
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "qsbSubmit"))
            )
            search_button.click()
            
            # Wait for search results to load
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "list"))
            )
            
            # Apply experience filter if provided
            if experience:
                self.apply_experience_filter(experience)
            
            time.sleep(3)  # Allow filters to apply and results to update
        
        except Exception as e:
            print(f"Error during search: {e}")
    
    def apply_experience_filter(self, experience):
        """
        Apply experience filter on search results
        
        Args:
            experience (str): Experience range (e.g., "1", "2-5")
        """
        try:
            # Click to expand experience filter
            exp_filter = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Experience')]"))
            )
            exp_filter.click()
            time.sleep(1)
            
            # Find and click the appropriate experience checkbox
            if '-' in experience:
                # Range like "2-5"
                min_exp, max_exp = experience.split('-')
                exp_option = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//span[contains(text(), '{min_exp} - {max_exp} Yrs')]")
                    )
                )
            else:
                # Single value like "1"
                if experience == "0":
                    exp_option = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Fresher')]"))
                    )
                else:
                    exp_option = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{experience} Yrs')]"))
                    )
            
            exp_option.click()
            time.sleep(2)
            
        except TimeoutException:
            print(f"Could not find experience filter for '{experience}'")
            # Click outside to close the filter dropdown
            try:
                self.driver.find_element(By.TAG_NAME, "body").click()
            except:
                pass
    
    def extract_jobs_from_page(self):
        """
        Extract job details from the current search results page
        
        Returns:
            list: List of job dictionaries
        """
        jobs = []
        
        try:
            # Wait for job cards to be present
            job_cards = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "styles_job-listing-container__OCfZC"))
            )

            
            for card in job_cards:
                job = {}
                
                # Extract job title and URL
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, "a.title")
                    job['title'] = title_elem.text.strip()
                    job['url'] = title_elem.get_attribute("href")
                except NoSuchElementException:
                    continue  # Skip if title not found
                
                # Extract company name
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, "div.row2")
                    job['company'] = company_elem.find_element(By.CSS_SELECTOR, "a.comp-name").text.strip()
                except NoSuchElementException:
                    job['company'] = "Not specified"
                
                # Extract location
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, 'span.locWdth')
                    job['location'] = location_elem.text.strip()
                except NoSuchElementException:
                    job['location'] = "Not specified"
                
                # Extract experience requirement
                try:
                    exp_elem = card.find_element(By.CSS_SELECTOR, ".expwdth")
                    job['experience'] = exp_elem.text.strip()
                except NoSuchElementException:
                    job['experience'] = "Not specified"
                
                # Extract salary if available
                try:
                    salary_elem = card.find_element(By.CSS_SELECTOR, "sal-wrap span span")
                    job['salary'] = salary_elem.text.strip()
                except NoSuchElementException:
                    job['salary'] = "Not disclosed"
                
                # Extract job description
                try:
                    desc_elem = card.find_element(By.CLASS_NAME, "job-desc")
                    job['description'] = desc_elem.text.strip()
                except NoSuchElementException:
                    job['description'] = "No description provided"
                
                # Extract posting date
                try:
                    date_elem = card.find_element(By.XPATH, ".//span[contains(@class, 'jobDate')]")
                    job['posted_date'] = date_elem.text.strip().replace("Posted: ", "")
                except NoSuchElementException:
                    job['posted_date'] = "Not specified"
                
                # Extract skills
                try:
                    skills_elem = card.find_element(By.CLASS_NAME, "tags-gt")
                    skills = skills_elem.find_elements(By.CLASS_NAME, "ellipsis")
                    job['skills'] = ", ".join([skill.text.strip() for skill in skills])
                except NoSuchElementException:
                    job['skills'] = "Not specified"
                
                jobs.append(job)
            
            return jobs
        
        except TimeoutException:
            print("Timeout waiting for job cards to load.")
            return []
    
    def navigate_to_next_page(self):
        """
        Click on the next page button
        
        Returns:
            bool: True if successfully navigated to next page, False otherwise
        """
        try:
            next_button = self.driver.find_element(
                By.XPATH, "//a[contains(@class, 'fright') and contains(@class, 'pagination-active')]"
            )
            
            # Check if there is a next page
            if "disabled" in next_button.get_attribute("class"):
                return False
            
            # Scroll to the button to make it visible
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1)
            
            # Click the next page button
            next_button.click()
            
            # Wait for the new page to load
            self.wait.until(
                EC.staleness_of(next_button)
            )
            time.sleep(3)  # Additional wait for page to fully load
            
            return True
        
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Error navigating to next page: {e}")
            return False
    
    def get_job_details(self, job_url):
        """
        Visit individual job page and extract detailed information
        
        Args:
            job_url (str): URL of the job listing
            
        Returns:
            dict: Detailed job information
        """
        details = {}
        
        try:
            # Open the job page in a new window
            self.driver.execute_script(f"window.open('{job_url}', '_blank');")
            time.sleep(2)
            
            # Switch to the new window
            self.driver.switch_to.window(self.driver.window_handles[1])
            
            # Wait for the job page to load
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "jd-container"))
            )
            
            # Extract detailed job description
            try:
                jd_elem = self.driver.find_element(By.CLASS_NAME, "job-desc")
                details['full_description'] = jd_elem.text.strip()
            except NoSuchElementException:
                details['full_description'] = "Not provided"
            
            # Extract role details
            try:
                role_elem = self.driver.find_element(By.CLASS_NAME, "role-section")
                details['role'] = role_elem.text.strip()
            except NoSuchElementException:
                details['role'] = "Not specified"
            
            # Extract company details
            try:
                company_info = self.driver.find_element(By.CLASS_NAME, "about-company")
                details['company_details'] = company_info.text.strip()
            except NoSuchElementException:
                details['company_details'] = "Not provided"
            
            # Extract required skills
            try:
                skills_section = self.driver.find_element(By.CLASS_NAME, "key-skill")
                skills = skills_section.find_elements(By.CLASS_NAME, "chip")
                details['required_skills'] = ", ".join([skill.text.strip() for skill in skills])
            except NoSuchElementException:
                details['required_skills'] = "Not specified"
            
            # Close the job details window and switch back to results
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            return details
            
        except Exception as e:
            print(f"Error fetching job details: {e}")
            
            # Make sure to close the extra window and go back to results
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
                
            return {}
    
    def save_to_csv(self, jobs, filename=None):
        """
        Save job listings to a CSV file
        
        Args:
            jobs (list): List of job dictionaries
            filename (str, optional): Output filename
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"naukri_jobs_{timestamp}.csv"
        
        if not jobs:
            print("No jobs to save.")
            return
        
        # Extract all possible fields from jobs
        fieldnames = set()
        for job in jobs:
            for key in job.keys():
                fieldnames.add(key)
        
        fieldnames = sorted(list(fieldnames))
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(jobs)
            
            print(f"Successfully saved {len(jobs)} jobs to {filename}")
        
        except IOError as e:
            print(f"Error saving to CSV: {e}")
    
    def run_scraper(self, keyword, location=None, experience=None, pages=3, fetch_details=False):
        """
        Run the scraper for multiple pages and collect results
        
        Args:
            keyword (str): Job title or skills
            location (str, optional): City or location
            experience (str, optional): Experience in years
            pages (int, optional): Maximum number of pages to scrape
            fetch_details (bool, optional): Whether to fetch detailed job information
            
        Returns:
            list: Collected job listings
        """
        all_jobs = []
        
        try:
            # Perform the initial search
            self.search_jobs(keyword, location, experience)
            
            # Scrape pages
            page_count = 1
            
            while page_count <= pages:
                print(f"Scraping page {page_count}...")
                
                # Extract jobs from current page
                jobs = self.extract_jobs_from_page()
                print(f"Found {len(jobs)} jobs on page {page_count}")
                
                # Optionally fetch detailed information
                if fetch_details and jobs:
                    for i, job in enumerate(jobs):
                        if 'url' in job:
                            print(f"Fetching details for job {i+1}/{len(jobs)}...")
                            details = self.get_job_details(job['url'])
                            job.update(details)
                            
                            # Small delay between job detail requests
                            time.sleep(random.uniform(1.0, 2.0))
                
                all_jobs.extend(jobs)
                
                # Navigate to next page if available and not at page limit
                if page_count < pages:
                    has_next = self.navigate_to_next_page()
                    if not has_next:
                        print("No more pages available.")
                        break
                    time.sleep(random.uniform(2.0, 3.0))  # Delay between pages
                
                page_count += 1
            
            print(f"Total jobs collected: {len(all_jobs)}")
            return all_jobs
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return all_jobs
        
        finally:
            # Ensure we save whatever data we've collected even if there's an error
            if all_jobs:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.save_to_csv(all_jobs, f"naukri_jobs_{timestamp}.csv")


if __name__ == "__main__":
    # Example usage
    try:
        # Initialize the scraper
        scraper = NaukriSeleniumScraper(
            headless=True,       # Set to False to see the browser in action
            disable_images=True  # Disable images to speed up scraping
        )
        
        # Set your search parameters
        keyword = "Python Developer"
        location = "Bangalore"
        experience = "2"  # years
        
        # Run the scraper
        jobs = scraper.run_scraper(
            keyword=keyword,
            location=location, 
            experience=experience,
            pages=3,             # Number of pages to scrape
            fetch_details=False  # Set to True to fetch detailed job information
        )
        
        # Save results to CSV (this also happens automatically in the run_scraper method)
        if jobs:
            scraper.save_to_csv(jobs)
            
        print("Scraping completed!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Make sure to close the browser
        if 'scraper' in locals() and scraper:
            scraper.close()