import os

from dotenv import load_dotenv

from course_extractor.app.scraper.scraper import scrap_data_and_download_pdfs
from course_extractor.app.storage.database import AtlasClient
from course_extractor.app.extractors.pdf_extractor import extract_text_from_pdf

# Defining global variables and constants ______________________________________________________________________________
load_dotenv()  # take environment variables from .env

# Download Path
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH")

# Mongodb SetUp
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")
mongodb_client = AtlasClient(MONGODB_URI, MONGODB_DB_NAME)

# Main _________________________________________________________________________________________________________________
# scrap_data_and_download_pdfs()

# Fetch all the documents data stored in the database
docs_data = mongodb_client.get_many(MONGODB_COLLECTION_NAME)

# Extract text from each pdf then insert it in the database

for doc in docs_data:
    file_path = os.path.join(DOWNLOAD_PATH, doc["file_path"])

    # Skip non-existing files
    if not os.path.exists(file_path):
        print(f"File with path ({file_path}) does not exist)")
        continue

    # Extract text from the PDF file
    text = extract_text_from_pdf(file_path)

    # Insert the extracted PDF file to the database
    mongodb_client.update_one(MONGODB_COLLECTION_NAME, doc["_id"], {"text": text})
