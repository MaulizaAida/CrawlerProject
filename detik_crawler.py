import requests
from bs4 import BeautifulSoup
import csv

# URL of the Detik.com homepage
url = 'https://news.detik.com/'

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the page content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all article elements
    articles = soup.find_all('article', class_='list-content__item', limit=10)  # Limit to 10 articles

    # Create a list to store the titles and URLs
    news_data = []

    # Loop through the articles and extract the title and link
    for article in articles:
        title_tag = article.find('h2', class_='media__title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag.find('a')['href']  # Extract the link from the anchor tag
            news_data.append({'Title': title, 'Link': link})

    # Write the titles and links to a CSV file
    with open('detik_news_titles.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()  # Write header
        for data in news_data:
            writer.writerow(data)  # Write each title and link

    print("Successfully saved the news titles and links to detik_news_titles.csv")
else:
    print(f"Failed to retrieve the page: {response.status_code}")
