import time
import os
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Function to get a unique filename if a file already exists
def get_unique_filename(file_path):
    base, ext = os.path.splitext(file_path)
    counter = 1
    new_file_path = file_path

    while os.path.exists(new_file_path):
        new_file_path = f"{base}_{counter}{ext}"
        counter += 1

    return new_file_path

# Get course name and number of pages to scrape
course_name = input("Enter the course name (e.g., 'cours de java'): ").strip()
pages_to_scrape = int(input("Enter the number of pages to scrape (e.g., 5): ").strip())

# Set download path
download_path = os.path.join(os.getcwd(), "downloads", course_name.replace(" ", "_"))
os.makedirs(download_path, exist_ok=True)

# Scribd search URL
base_url = f"https://fr.scribd.com/search?query={course_name.replace(' ', '+')}&ct_lang=1&filters={{%22language%22:[%225%22],%22filetype%22:[%22pdf%22],%22num_pages%22:%224-100%22}}&page="

# Selenium WebDriver setup
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Extract document details
documents = []
for page in range(1, pages_to_scrape + 1):
    driver.get(base_url + str(page))
    time.sleep(3)  # Allow page to load

    for article in driver.find_elements(By.XPATH, "//article[contains(@class, 'ListItem-module_wrapper__p5Vay')]"):
        try:
            link_element = article.find_element(By.XPATH, ".//a[contains(@href, '/document/')]")
            url = link_element.get_attribute("href")
            title = link_element.text.strip()

            # Extract views, pages, and upload date
            views = article.find_element(By.XPATH, ".//p[contains(text(), 'vues')]").text if article.find_elements(By.XPATH, ".//p[contains(text(), 'vues')]") else "N/A"
            pages = article.find_element(By.XPATH, ".//p[contains(text(), 'pages')]").text if article.find_elements(By.XPATH, ".//p[contains(text(), 'pages')]") else "N/A"
            upload_date = article.find_element(By.XPATH, ".//div[contains(@class, 'Document-module_authorDateCategories__8dnW3')]").text.split("le")[-1].strip() if "le" in article.text else "N/A"

            if url and title:
                documents.append((title, url, views, pages, upload_date))
        except Exception as e:
            print(f"⚠️ Skipped an item due to an error: {e}")

# Remove duplicates
documents = list(set(documents))

# Save data to CSV
csv_filename = f"{course_name.replace(' ', '_')}_links.csv"
df = pd.DataFrame(documents, columns=["Title", "Link", "Views", "Pages", "Upload Date"])

# Ensure pandas optimizes downcasting as needed
pd.set_option('future.no_silent_downcasting', True)

# Fix 'Views' and 'Pages' columns
df["Views"] = df["Views"].str.replace(" vues", "").str.replace(",", "").astype(str).str.extract(r"(\d+)").fillna(0).astype(int).infer_objects()
df["Pages"] = df["Pages"].str.replace(" pages", "").str.extract(r"(\d+)").fillna(0).astype(int).infer_objects()

# Sort by views and pages (descending)
df_sorted = df.sort_values(by=["Views", "Pages"], ascending=False)

# Select top 50
df_top_50 = df_sorted.head(50)

# Save the top 50 to CSV
df_top_50.to_csv(csv_filename, index=False, encoding="utf-8")
print(f"✅ Extracted {len(documents)} documents, sorted by views and pages, and saved top 50 to {csv_filename}.")

# Close browser after scraping
driver.quit()

# Ensure CSV exists before reading
if not os.path.exists(csv_filename):
    print(f"❌ Error: The file '{csv_filename}' does not exist. Check if scraping was successful.")
    exit()

try:
    df = pd.read_csv(csv_filename)

    # Ensure "Link" column exists
    if "Link" not in df.columns:
        print("❌ Error: 'Link' column not found in CSV file. Check your data extraction process.")
        exit()

    # Extract valid links
    links = df["Link"].dropna().tolist()
    if not links:
        print("❌ Error: No valid links found in the CSV file. Exiting...")
        exit()

    print(f"✅ Found {len(links)} links to process.")

except Exception as e:
    print(f"❌ Error reading {csv_filename}: {e}")
    exit()

# Reinitialize WebDriver for downloading PDFs
driver = webdriver.Chrome(service=service, options=chrome_options)

# Process and download PDFs
for index, link in enumerate(links, start=1):
    try:
        print(f"\nProcessing {index}/{len(links)}: {link}")
        start_time = time.time()

        file_name = link.split("/")[-1]
        file_name = re.sub(r'[^a-zA-Z0-9]', '_', file_name).upper()
        pdf_filename = f"{file_name}.pdf"
        pdf_path = os.path.join(download_path, pdf_filename)

        driver.get("https://www.slidesdownloader.com/scribd")

        print("Waiting for input field...")
        input_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "link"))
        )
        input_field.clear()
        input_field.send_keys(link)
        print("Link entered successfully.")

        print("Waiting for download button...")
        download_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download')]"))
        )
        download_button.click()
        print("Download button clicked. Waiting for file...")

        print("Waiting for processing to complete...")
        WebDriverWait(driver, 300).until_not(
            EC.presence_of_element_located((By.CLASS_NAME, "spinner"))
        )
        print("Processing complete. Checking for file...")

        timeout = 300
        while not any(fname.endswith('.pdf') for fname in os.listdir(download_path)):
            if time.time() - start_time > timeout:
                print("Download timeout! Moving to next link.")
                break
            time.sleep(5)

        for fname in os.listdir(download_path):
            if fname.endswith(".pdf"):
                old_path = os.path.join(download_path, fname)
                unique_pdf_path = get_unique_filename(pdf_path)
                os.rename(old_path, unique_pdf_path)
                print(f"✅ File saved as: {unique_pdf_path}")
                break

        elapsed_time = time.time() - start_time
        print(f"✅ Download completed for: {link} (Time: {elapsed_time:.2f} seconds)")

    except Exception as e:
        print(f"❌ Error processing {link}: {e}")

driver.quit()
print("\n✅ All downloads processed successfully.")

