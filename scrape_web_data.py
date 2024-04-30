from bs4 import BeautifulSoup
import requests
import re
import mysql.connector

class YgoCardMarketWebScraper:
    def __init__(self, subreddit, sort) -> None:
        self.scrape_url = 'https://old.reddit.com'
        self.url = f'{self.scrape_url}/r/{subreddit}?sort={sort}'
        self.listings = {}
        
        # Connect to database
        self.create_connection()

        # Ensure the table is created
        self.create_table()


    def get_listings(self):
        # Get a response
        response = requests.get(self.url, headers={'User-Agent': 'Mozilla/5.0'})

        # Create a Soup object
        s = BeautifulSoup(response.text, 'html.parser')

        # Define parameters, in this case I want all the reddit posts' titles
        titles = s.find_all('p', class_='title')

        # Cleaning data with RegEx
        for t in titles:
            title = t.text.strip()  # Get the title text
            link = 'https://reddit.com' + t.a['href']  # Get the link URL
            
            # Find all matches of the regex pattern
            matches = re.findall(r'(\[[a-zA-Z][a-zA-Z]\-[a-zA-Z][a-zA-Z]\].*)', title)

            for match in matches:
                self.listings[match] = link

    # Create MySQL connection
    def create_connection(self):
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='mysqlpassword',
            database='reddit'
        )
    
    # Create table if not exists
    def create_table(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reddit_posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            listing VARCHAR(255),
            link VARCHAR(255)
        )
        ''')
        conn.close()

    
    def insert_data(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        self.get_listings()

        for listing, link in self.listings.items():  # Use .items() to iterate over key-value pairs
            cursor.execute('''
            INSERT INTO reddit_posts (listing, link)
            VALUES (%s, %s)
            ''', (listing, link))

        conn.commit()
        conn.close()

    def print_listings(self):
        self.get_listings()

        for listing, link in self.listings.items():  # Use .items() to iterate over key-value pairs
            print("Listing:", listing)
            print("Link:", link)
            print()

web_scraper = YgoCardMarketWebScraper('YGOMarketplace', 'top&t=week')
web_scraper.insert_data()
web_scraper.print_listings()

