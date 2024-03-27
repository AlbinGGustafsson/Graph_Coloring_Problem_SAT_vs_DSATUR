import os

import requests
from bs4 import BeautifulSoup


def download_files_from_urls(url_list):
    if not os.path.exists('download'):
        os.makedirs('download')

    for url in url_list:
        url = url.strip()
        if url:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    filename = url.split('/')[-1]
                    filepath = os.path.join('download', filename)
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {filename}")
                else:
                    print(f"Failed to download {url}. Status code: {response.status_code}")
            except Exception as e:
                print(f"An error occurred: {e}")


url = 'https://mat.tepper.cmu.edu/COLOR02/'

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    filtered_links = []

    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.startswith('INSTANCES/'):
            filtered_links.append(f"https://mat.tepper.cmu.edu/COLOR08/{href}")
        elif href and href.startswith('_INSTANCES/'):
            corrected_href = href.lstrip('_')
            filtered_links.append(f"https://mat.tepper.cmu.edu/COLOR08/{corrected_href}")

    print(filtered_links)

    download_files_from_urls(filtered_links)

else:
    print("Failed to fetch the webpage")
