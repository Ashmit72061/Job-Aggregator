#!/usr/bin/env python3

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
        
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        
        if disable_images:
            chrome_prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", chrome_prefs)
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = "https://www.naukri.com"
    
    def close(self):
        if self.driver:
            self.driver.quit()
    
    def navigate_to_search_page(self):
        self.driver.get(self.base_url)
        time.sleep(3) 
        
        try:
            popup_close = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "crossIcon"))
            )
            popup_close.click()
            time.sleep(1)
        except TimeoutException:
            pass 
    
    def search_jobs(self, keyword, location=None, experience=None):
        self.navigate_to_search_page()
        
        try:
            search_box = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "suggestor-input"))
            )
            search_box.clear()
            search_box.send_keys(keyword)
            
            if location:
                try:
                    location_box = self.driver.find_element(By.CSS_SELECTOR, '[placeholder="Enter location"]')
                    location_box.clear()
                    location_box.send_keys(location)
                except NoSuchElementException:
                    print("Location input field not found.")
            
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "qsbSubmit"))
            )
            search_button.click()
            
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "list"))
            )
            
            if experience:
                self.apply_experience_filter(experience)
            
            time.sleep(3) 
        
        except Exception as e:
            print(f"Error during search: {e}")
    
    def apply_experience_filter(self, experience):
        try:
            exp_filter = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Experience')]"))
            )
            exp_filter.click()
            time.sleep(1)
            
            if '-' in experience:
                min_exp, max_exp = experience.split('-')
                exp_option = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//span[contains(text(), '{min_exp} - {max_exp} Yrs')]")
                    )
                )
            else:
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
            try:
                self.driver.find_element(By.TAG_NAME, "body").click()
            except:
                pass
    
    def extract_jobs_from_page(self):
        jobs = []
        
        try:
            job_cards = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "styles_job-listing-container__OCfZC"))
            )

            
            for card in job_cards:
                job = {}
                
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, "a.title")
                    job['title'] = title_elem.text.strip()
                    job['url'] = title_elem.get_attribute("href")
                except NoSuchElementException:
                    continue 
                
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, "div.row2")
                    job['company'] = company_elem.find_element(By.CSS_SELECTOR, "a.comp-name").text.strip()
                except NoSuchElementException:
                    job['company'] = "Not specified"
                
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, 'span.locWdth')
                    job['location'] = location_elem.text.strip()
                except NoSuchElementException:
                    job['location'] = "Not specified"
                
                try:
                    exp_elem = card.find_element(By.CSS_SELECTOR, ".expwdth")
                    job['experience'] = exp_elem.text.strip()
                except NoSuchElementException:
                    job['experience'] = "Not specified"
                
                try:
                    salary_elem = card.find_element(By.CSS_SELECTOR, "sal-wrap span span")
                    job['salary'] = salary_elem.text.strip()
                except NoSuchElementException:
                    job['salary'] = "Not disclosed"
                
                try:
                    desc_elem = card.find_element(By.CLASS_NAME, "job-desc")
                    job['description'] = desc_elem.text.strip()
                except NoSuchElementException:
                    job['description'] = "No description provided"
                
                try:
                    date_elem = card.find_element(By.XPATH, ".//span[contains(@class, 'jobDate')]")
                    job['posted_date'] = date_elem.text.strip().replace("Posted: ", "")
                except NoSuchElementException:
                    job['posted_date'] = "Not specified"
                
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
        try:
            next_button = self.driver.find_element(
                By.XPATH, "//a[contains(@class, 'fright') and contains(@class, 'pagination-active')]"
            )
            
            if "disabled" in next_button.get_attribute("class"):
                return False
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1)
            
            next_button.click()
            
            self.wait.until(
                EC.staleness_of(next_button)
            )
            time.sleep(3) 
            
            return True
        
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Error navigating to next page: {e}")
            return False
    
    def get_job_details(self, job_url):
        details = {}
        
        try:
            self.driver.execute_script(f"window.open('{job_url}', '_blank');")
            time.sleep(2)
            
            self.driver.switch_to.window(self.driver.window_handles[1])
            
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "jd-container"))
            )
            
            try:
                jd_elem = self.driver.find_element(By.CLASS_NAME, "job-desc")
                details['full_description'] = jd_elem.text.strip()
            except NoSuchElementException:
                details['full_description'] = "Not provided"
            
            try:
                role_elem = self.driver.find_element(By.CLASS_NAME, "role-section")
                details['role'] = role_elem.text.strip()
            except NoSuchElementException:
                details['role'] = "Not specified"
            
            try:
                company_info = self.driver.find_element(By.CLASS_NAME, "about-company")
                details['company_details'] = company_info.text.strip()
            except NoSuchElementException:
                details['company_details'] = "Not provided"
            
            try:
                skills_section = self.driver.find_element(By.CLASS_NAME, "key-skill")
                skills = skills_section.find_elements(By.CLASS_NAME, "chip")
                details['required_skills'] = ", ".join([skill.text.strip() for skill in skills])
            except NoSuchElementException:
                details['required_skills'] = "Not specified"
            
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            return details
            
        except Exception as e:
            print(f"Error fetching job details: {e}")
            
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
                
            return {}
    

    def run_scraper(self, keyword, location=None, experience=None, pages=3, fetch_details=False):
        all_jobs = []
        
        try:
            self.search_jobs(keyword, location, experience)
            
            page_count = 1
            
            while page_count <= pages:
                print(f"Scraping page {page_count}...")
                
                jobs = self.extract_jobs_from_page()
                print(f"Found {len(jobs)} jobs on page {page_count}")
                print(jobs)
                
                if fetch_details and jobs:
                    for i, job in enumerate(jobs):
                        if 'url' in job:
                            print(f"Fetching details for job {i+1}/{len(jobs)}...")
                            details = self.get_job_details(job['url'])
                            job.update(details)
                            
                            time.sleep(random.uniform(1.0, 2.0))
                
                all_jobs.extend(jobs)
                
                if page_count < pages:
                    has_next = self.navigate_to_next_page()
                    if not has_next:
                        print("No more pages available.")
                        break
                    time.sleep(random.uniform(2.0, 3.0)) 
                
                page_count += 1
            
            print(f"Total jobs collected: {len(all_jobs)}")
            return all_jobs
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return all_jobs
        
        finally:
            pass


if __name__ == "__main__":
    try:
        scraper = NaukriSeleniumScraper(
            headless=True, 
            disable_images=True 
        )
        
        keyword = "Python Developer"
        location = "Bangalore"
        experience = "2" 
        
        jobs = scraper.run_scraper(
            keyword=keyword,
            location=location, 
            experience=experience,
            pages=3, 
            fetch_details=False 
        )
        
        # if jobs:
        #     scraper.save_to_csv(jobs)
            
        print("Scraping completed!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        if 'scraper' in locals() and scraper:
            scraper.close()