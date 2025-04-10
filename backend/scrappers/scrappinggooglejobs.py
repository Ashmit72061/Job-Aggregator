import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

def scrape_google_jobs(job_title, location, num_pages=1):
    driver = uc.Chrome()
    jobs_list = []

    try:
        # Step 1: Search on Google
        query = f"{job_title} jobs in {location}"
        driver.get("https://www.google.com/")
        time.sleep(2)

        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        # Step 2: Click on the Google Jobs "View all" link
        try:
            jobs_button = driver.find_element(By.XPATH, "//span[text()='More jobs'] | //div[@class='BjJfJf PUpOsf']")
            jobs_button.click()
            time.sleep(5)
        except:
            print("⚠️ Google Jobs panel not found. Aborting.")
            return pd.DataFrame()

        # Step 3: Extract job cards
        for _ in range(num_pages):
            job_cards = driver.find_elements(By.CLASS_NAME, "PwjeAc")
            print(f"🔍 Found {len(job_cards)} job cards.")

            for card in job_cards:
                try:
                    title = card.find_element(By.CLASS_NAME, "BjJfJf").text
                    company = card.find_element(By.CLASS_NAME, "vNEEBe").text
                    loc = card.find_element(By.CLASS_NAME, "Qk80Jf").text

                    jobs_list.append({
                        "title": title,
                        "company": company,
                        "location": loc
                    })
                except Exception as e:
                    print(f"❌ Error parsing card: {e}")

            # Try to scroll to load more jobs
            job_container = driver.find_element(By.CLASS_NAME, "gws-plugins-horizon-jobs__tl-lvc")
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", job_container)
            time.sleep(3)

    finally:
        driver.quit()

    return pd.DataFrame(jobs_list)

# Usage
df = scrape_google_jobs("Machine Learning", "New Delhi", num_pages=2)
df.to_csv("google_jobs.csv", index=False)
print("✅ Job data saved to google_jobs.csv")
