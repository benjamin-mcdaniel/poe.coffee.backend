import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote

base_url = "https://www.poewiki.net"
category_url = f"{base_url}/wiki/Category:Amulet_icons"

def get_image_names(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    images = []
    
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            decoded_name = unquote(src.split('/')[-1])
            images.append(decoded_name)

    return images

def get_subcategories(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    subcategories = []

    for subcat in soup.find_all('a', class_='CategoryTreeLabel'):
        href = subcat.get('href')
        if href:
            subcategories.append(f"{base_url}{href}")

    return subcategories

def main():
    image_names = get_image_names(category_url)
    subcategories = get_subcategories(category_url)

    for subcategory in subcategories:
        image_names.extend(get_image_names(subcategory))

    for image in image_names:
        print(image)

if __name__ == "__main__":
    main()
