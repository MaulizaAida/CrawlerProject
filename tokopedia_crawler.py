import requests
import json
import pandas as pd
import sqlite3
from datetime import datetime
from tqdm import tqdm

# List of Indonesian cities with their respective latitude and longitude
city_coordinates = {
    "Jakarta": {"lat": -6.2088, "long": 106.8456},
    "Bandung": {"lat": -6.9175, "long": 107.6191},
    "Surabaya": {"lat": -7.2504, "long": 112.7688},
    "Medan": {"lat": 3.5952, "long": 98.6722},
    "Semarang": {"lat": -6.9939, "long": 110.4203},
    "Yogyakarta": {"lat": -7.7956, "long": 110.3695},
    "Makassar": {"lat": -5.1472, "long": 119.4328},
    "Palembang": {"lat": -2.9977, "long": 104.7750},
    "Denpasar": {"lat": -8.4095, "long": 115.1889},
    "Batam": {"lat": 1.1218, "long": 104.3990}
}

def fetch_data(product_name, user_lat, user_long):
    # Define the URL for the GraphQL query
    url = 'https://gql.tokopedia.com/graphql/TopadsHeadlineQuery'
    
    # Define the headers as per the curl command
    headers = {
        'sec-ch-ua-platform': 'Linux',
        'X-Version': '71280f3',
        'Referer': 'https://www.tokopedia.com/search?st=&q=laptop&srp_component_id=02.01.00.00&srp_page_id=&srp_page_title=&navsource=',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'iris_session_id': 'd3d3LnRva29wZWRpYS5jb20=.8821bf1371c4f4d91889b0e8a2021b50.1728117143823',
        'X-Source': 'tokopedia-lite',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'X-Tkpd-Lite-Service': 'zeus'
    }
    
    # Define the payload for the POST request
    payload = [
        {
            "operationName": "TopadsHeadlineQuery",
            "variables": {
                "displayParams": f"navsource=&q={product_name}&srp_component_id=02.01.00.00&srp_page_id=&srp_page_title=&st=&user_addressId=&user_lat={user_lat}&user_long={user_long}&user_postCode=&user_warehouseId=0&warehouses=&dep_id=&device=desktop&ep=cpm&page=1&product_id=&src=search&template_id=3&headline_product_count=3&item=1&user_id=0"
            },
            "query": """query TopadsHeadlineQuery($displayParams: String!) {
                displayAdsV3(displayParams: $displayParams) {
                    data {
                        id
                        headline {
                            shop {
                                name
                                products: product {
                                    name
                                    priceStr: price_format
                                    ratingAverage: rating_average
                                    url: uri
                                    __typename
                                }
                                __typename
                            }
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
            }"""
        }
    ]
    
    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    # Check the response
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return None

def extract_data(response, product_name, city_name):
    # Prepare a list to store the data
    data_to_save = []

    # Current timestamp
    inserted_at = datetime.now().isoformat()

    # Extracting important data
    for item in response[0]['data']['displayAdsV3']['data']:
        shop_name = item['headline']['shop']['name']
        for product in item['headline']['shop']['products']:
            product_info = {
                'Product Name': product['name'],
                'Price': product['priceStr'],
                'Rating': product['ratingAverage'],
                'URL': product['url'],
                'Shop Name': shop_name,
                'Inserted At': inserted_at,
                'Search Keyword': product_name,  # Add the search keyword here
                'City': city_name  # Add the city here
            }
            data_to_save.append(product_info)

    return data_to_save

def save_to_sqlite(data):
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            price TEXT,
            rating REAL,
            url TEXT,
            shop_name TEXT,
            inserted_at TEXT,
            search_keyword TEXT,
            city TEXT
        )
    ''')

    # Insert data into the table
    for product in data:
        cursor.execute('''
            INSERT INTO Products (product_name, price, rating, url, shop_name, inserted_at, search_keyword, city) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product['Product Name'], product['Price'], product['Rating'], product['URL'], product['Shop Name'], product['Inserted At'], product['Search Keyword'], product['City']))

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("Data saved to products.db")

def main():
    # List of product names to search
    products_to_search = [
        "Smartwatch", "Wireless earbuds", "Electric scooter", "Gaming laptop",
        "Portable projector", "Fitness tracker", "Air fryer", "Robot vacuum",
        "Electric toothbrush", "Drone with camera", "Home security camera",
        "Instant pot", "Virtual reality headset", "Noise-canceling headphones",
        "4K TV", "Smart thermostat", "E-reader", "Bluetooth speaker",
        "Streaming device", "Digital photo frame", "Smart light bulbs",
        "Massage gun", "Hair straightener", "Air purifier", "Electric kettle",
        "Bicycle", "DSLR camera", "Tablet", "3D printer", "Action camera",
        "Kitchen scale", "Waterproof speaker", "Portable charger",
        "Wi-Fi range extender", "Robot mop", "Electric grill", "Soundbar",
        "Coffee maker", "Pet camera", "Home gym equipment", "LED strip lights",
        "Digital thermometer", "Smart fridge", "Smart lock", "Multi-cooker",
        "Fitness bike", "Smartwatch for kids", "Cordless vacuum", "Bluetooth tracker",
        "Wireless charging pad", "LED desk lamp", "Plant-based protein powder",
        "Organic skincare", "Camping hammock", "Waterproof phone case",
        "Yoga mat", "Instant camera", "Portable air conditioner", "Smart mirror",
        "Subscription box for snacks", "Handmade jewelry", "Organic tea",
        "Essential oil diffuser", "Craft beer brewing kit", "Electric bike",
        "Gaming chair", "Home brewing equipment", "Makeup brushes set",
        "Baby monitor", "Memory foam pillow", "Home theater system",
        "Fitness resistance bands", "Vintage vinyl records", "Pet grooming kit",
        "Eco-friendly tote bags", "Art supplies set", "Smart scale",
        "Electric blanket", "Inflatable paddle board", "Food dehydrator",
        "Customizable sneakers", "High-quality chef's knife", "Leather wallet",
        "Compact mirror", "Reusable water bottle", "Wireless security system",
        "Personalized photo book", "Natural cleaning products", "Car phone mount",
        "Yoga wheel", "Meditation cushion", "Smart garden kit",
        "Meal prep containers", "Travel backpack", "Fitness meal plan subscription",
        "Vintage camera", "Home office furniture", "Unique board games",
        "Solar power bank", "DIY craft kit"
    ]

    all_data = []

    for city, coords in city_coordinates.items():
        user_lat = coords["lat"]
        user_long = coords["long"]
        for product in tqdm(products_to_search, desc=f"Processing in {city}"):
            response = fetch_data(product, user_lat, user_long)  # Pass latitude and longitude
            if response:
                extracted_data = extract_data(response, product, city)  # Pass the city name here.
                all_data.extend(extracted_data)

    if all_data:
        save_to_sqlite(all_data)

if __name__ == "__main__":
    main()
