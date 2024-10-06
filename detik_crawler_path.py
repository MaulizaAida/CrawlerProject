import requests
from bs4 import BeautifulSoup

# URL you want to scrape
url = 'https://news.detik.com'

# Send a GET request to the webpage
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the page content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Use the specified CSS selector to find the desired content
    content = soup.select_one('body > div.container > div > div.column-8 > div.section.nhl > div.list-content')
    
    if content:
        print(content.text)  # Or process the content as needed
    else:
        print("No content found at the specified path.")
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
