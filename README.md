Title: Scraping Employee Data from API

As a developer,
I want to scrape employee data from the provided API endpoint (https://api.slingacademy.com/v1/sample-data/files/employees.json),
so that I can ingest the data into our data warehouse for further analysis.

Acceptance Criteria:
Data Retrieval:

The scraper must make a successful HTTP request to the provided URL: https://api.slingacademy.com/v1/sample-data/files/employees.json.
The request must return a valid JSON response with employee data.
Data Structure Validation:

The scraper must parse the JSON data into the appropriate fields, including (but not limited to):
Employee ID
First Name
Last Name
Email
Job Title
Phone Number
Hire Date

Each field should be properly extracted and mapped to the respective schema for ingestion.
Error Handling:

If the API returns a non-200 status code, the scraper should log the error with the appropriate error message.
The scraper should handle any timeout errors or failed connections gracefully and retry the request a limited number of times before logging a failure.

COMMANDS TO RUN CODE
streamlit run scraper.py -- --ui
py -m pytest test_scraper.py -v     
python scraper.py                                                          
