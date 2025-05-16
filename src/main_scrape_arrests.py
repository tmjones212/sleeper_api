import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def get_nfl_arrests_table(url: str, output_csv: str = "nfl_arrests.csv"):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        # Wait for the table to be present in the DOM
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/div/div/div[3]/div[3]/div/div/div[1]/table"))
        )
        # Now get the table element
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframes")
        # If the table is in the first iframe:
        driver.switch_to.frame(iframes[0])
        table_element = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[3]/div[3]/div/div/div[1]/table")
        table_html = table_element.get_attribute('outerHTML')
        soup = BeautifulSoup(table_html, "lxml")

        # Extract headers
        headers = [th.get_text(strip=True) for th in soup.find_all("th")]

        # Extract rows
        rows = []
        for tr in soup.find_all("tr")[1:]:
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if cells:
                rows.append(cells)

        # Save to CSV
        df = pd.DataFrame(rows, columns=headers)
        df.to_csv(output_csv, index=False)
        print(f"Scraped {len(df)} rows. Data saved to {output_csv}")

    finally:
        driver.quit()

if __name__ == "__main__":
    get_nfl_arrests_table("https://databases.usatoday.com/nfl-arrests/")