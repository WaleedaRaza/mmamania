from dotenv import load_dotenv
import os
load_dotenv('.env')
import requests
from bs4 import BeautifulSoup

response = requests.get('https://en.wikipedia.org/wiki/UFC_on_ESPN:_Taira_vs._Park')
soup = BeautifulSoup(response.content, 'html.parser')
tables = soup.find_all('table')

print(f'Found {len(tables)} tables')

for i, table in enumerate(tables):
    rows = table.find_all('tr')
    print(f'Table {i}: {len(rows)} rows')
    
    for row in rows[:3]:
        cells = row.find_all('td')
        print(f'  Row cells: {len(cells)}')
        if len(cells) >= 7:
            print(f'    Cell 2 text: "{cells[2].get_text(strip=True)}"')
