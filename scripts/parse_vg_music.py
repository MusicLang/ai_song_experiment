import os
import requests
from bs4 import BeautifulSoup

# Base URL for where the midi files are hosted
BASE_URL = "https://www.vgmusic.com/music/console/sony/ps1/"

# Function to download a file from a URL
def download_file(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)

# Function to create a directory if it doesn't exist
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Fetch the HTML content from the website
response = requests.get(BASE_URL)
html_source = response.text

# Parse the HTML content
soup = BeautifulSoup(html_source, 'html.parser')

# Initialize the current game name as None
current_game_name = None

# Iterate over each row in the table
for row in soup.select('table tr'):
    # Check if the row is a game header
    if 'gameheader' in row.get('class', []):
        # Extract game name from the header and format it
        game_name = row.get_text(strip=True).replace(' ', '_').replace('/', '_')
        current_game_name = game_name
        continue  # Skip to the next row

    # If current_game_name is not set, skip the row as it's before the first game header
    if not current_game_name:
        continue

    # Find the link in the current row
    link = row.find('a', href=True)
    if link and link['href'].endswith('.mid'):
        # We have a valid MIDI file link
        href = link['href']
        file_name = href.split('/')[-1]
        game_directory = os.path.join('data/midi_files', current_game_name)
        ensure_dir(game_directory)
        file_url = BASE_URL + href
        save_path = os.path.join(game_directory, file_name)
        print(f"Downloading {file_name} to {game_directory}...")
        download_file(file_url, save_path)
        print(f"Saved to {save_path}")

print("All MIDI files have been downloaded.")
