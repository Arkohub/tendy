from bs4 import BeautifulSoup
import requests
import csv

# Base URL for pagination
base_url = "https://www.tenders.gov.au/atm"

# Enhanced headers for the request
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/",
    "DNT": "1",  # Do Not Track request
    "Upgrade-Insecure-Requests": "1",
}

# List to store all tenders
tenders = []

# Start with the first page
page = 1

while True:
    # Construct the URL for the current page
    url = f"{base_url}?page={page}"
    print(f"Fetching page {page}...")

    response = requests.get(url, headers=headers)

    # Check for forbidden or other errors
    if response.status_code == 403:
        print("Access forbidden: The server is blocking your request.")
        break
    response.raise_for_status()

    # Parse the webpage content
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract tenders with category, title, and description
    rows = soup.find_all("div", class_="row")
    if not rows:
        # Stop if no more rows are found (end of results)
        print("No more results found. Exiting.")
        break

    for row in rows:
        # Extract title
        title_tag = row.find("p", class_="lead")
        title = title_tag.get_text(strip=True) if title_tag else "No title"

        # Extract category
        category = "No category"
        for desc in row.find_all("div", class_="list-desc"):
            span = desc.find("span")
            if span and span.get_text(strip=True) == "Category:":
                category_inner = desc.find("div", class_="list-desc-inner")
                if category_inner:
                    category = category_inner.get_text(strip=True)
                    break

        # Extract description
        description = "No description"
        for desc in row.find_all("div", class_="list-desc"):
            span = desc.find("span")
            if span and span.get_text(strip=True) == "Description:":
                desc_inner = desc.find("div", class_="list-desc-inner")
                if desc_inner:
                    description = desc_inner.get_text(strip=True)
                    break
        
        # Extract ATM ID
        atmid = "no ID"
        for desc in row.find_all("div", class_="list-desc"):
            span = desc.find("span")
            if span and span.get_text(strip=True) == "ATM ID:":
                                      desc_inner = desc.find("div", class_="list-desc-inner")
                                      if desc_inner:
                                        atmid = desc_inner.get_text(strip=True)
                                        break
                                      

        # Extract Agency
        agency = "no agency"
        for desc in row.find_all("div", class_="list-desc"):
            span = desc.find("span")
            if span and span.get_text(strip=True) == "Agency:":
                                      desc_inner = desc.find("div", class_="list-desc-inner")
                                      if desc_inner:
                                        agency = desc_inner.get_text(strip=True)
                                        break
                                      


        # Only add to the list if title and category are valid
        if title != "No title" and category != "No category":
            tenders.append({"category": category, "title": title, "description": description, "ATM ID": atmid, "agency": agency})

    # Check if there is a "Next" button
    next_button = soup.find("li", class_="next")
    if not next_button or not next_button.find("a"):
        print(f"No 'Next' button found. Assuming page {page} is the last page.")
        break

    # Increment the page number
    page += 1

# Write the results to a CSV file
csv_file = "tenders_with_pagination.csv"
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Category", "Agency", "ATM ID", "Title", "Description"])  # Write header
    for tender in tenders:
        writer.writerow([tender["category"], tender["agency"], tender["ATM ID"], tender["title"], tender["description"]])

print(f"Exported {len(tenders)} tenders to '{csv_file}'")
