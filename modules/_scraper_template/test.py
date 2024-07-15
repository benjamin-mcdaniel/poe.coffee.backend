import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import difflib

base_url = "https://www.poewiki.net"
category_url = f"{base_url}/wiki/Category:Amulet_icons"

expected_images = [
    "Araku_Tiki_inventory_icon.png",
    "Ashes_of_the_Stars_inventory_icon.png",
    "Astramentis_inventory_icon.png",
    "Astramentis_race_season_2_inventory_icon.png",
    "Astrolabe_Amulet_inventory_icon.png",
    "Atziri's_Foible_inventory_icon.png",
    "Atziri's_Foible_pvp_season_2_inventory_icon.png",
    "Atziri's_Foible_race_season_4_inventory_icon.png",
    "Aul's_Uprising_inventory_icon.png",
    "Badge_of_the_Brotherhood_inventory_icon.png"
]

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

    matches = sum(1 for img in image_names if any(difflib.SequenceMatcher(None, img, exp).ratio() > 0.5 for exp in expected_images))
    
    if matches >= len(expected_images) / 2:
        print("Check passed!")
        exit(0)
    else:
        print("Check failed.")
        exit(1)

if __name__ == "__main__":
    main()
