import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

def scrape_monster_jobs(job_title, location, num_pages=2):
    driver = uc.Chrome()
    jobs_list = []

    try:
        base_url = "https://www.monster.com/jobs/search/"
        query = f"?q={job_title.replace(' ', '-')}&where={location.replace(' ', '-')}"
        full_url = base_url + query

        driver.get(full_url)
        time.sleep(5)

        for page in range(num_pages):
            print(f"📄 Scanning Page {page + 1}: {driver.current_url}")

            job_cards = driver.find_elements(By.CSS_SELECTOR, "div.card-content")

            print(f"🔍 Found {len(job_cards)} job cards.")

            for card in job_cards:
                try:
                    title = card.find_element(By.CSS_SELECTOR, "h2.title > a").text.strip()
                    url = card.find_element(By.CSS_SELECTOR, "h2.title > a").get_attribute("href")
                    company = card.find_element(By.CSS_SELECTOR, "div.company > span.name").text.strip()
                    location = card.find_element(By.CSS_SELECTOR, "div.location > span.name").text.strip()

                    jobs_list.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "url": url
                    })
                except Exception as e:
                    print(f"❌ Error extracting job: {e}")

            # Try to go to the next page
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "a.btn-next")
                if "disabled" in next_button.get_attribute("class"):
                    print("⛔ Next button disabled.")
                    break
                next_button.click()
                time.sleep(4)
            except Exception as e:
                print("🚫 No more pages or next button not found.")
                break

    finally:
        driver.quit()

    return pd.DataFrame(jobs_list)
    
    # Usage
df = scrape_monster_jobs("Machine Learning", "New Delhi", num_pages=2)
df.to_csv("monster_jobs.csv", index=False)
    
    
