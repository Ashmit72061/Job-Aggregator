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

        for _ in range(num_pages):
            print("📄 Scanning page:", driver.current_url)

            job_cards = driver.find_elements(By.CSS_SELECTOR, "section.card-content")

            for card in job_cards:
                try:
                    title = card.find_element(By.CSS_SELECTOR, "h2.title").text.strip()
                    company = card.find_element(By.CSS_SELECTOR, "div.company span.name").text.strip()
                    loc = card.find_element(By.CSS_SELECTOR, "div.location span.name").text.strip()
                    link = card.find_element(By.CSS_SELECTOR, "h2.title a").get_attribute("href")

                    jobs_list.append({
                        "title": title,
                        "company": company,
                        "location": loc,
                        "url": link
                    })
                except Exception as e:
                    print(f"❌ Error extracting job: {e}")

            # Move to next page if exists
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "a.btn-next")
                next_button.click()
                time.sleep(4)
            except:
                print("🚫 No more pages.")
                break

    finally:
        driver.quit()

    return pd.DataFrame(jobs_list)

# Example usage
df = scrape_monster_jobs("Machine Learning Engineer", "New Delhi", num_pages=3)
df.to_csv("monster_jobs.csv", index=False)
print("✅ Job data saved to monster_jobs.csv")
