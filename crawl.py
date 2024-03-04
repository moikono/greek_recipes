import json

from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import Optional, NoReturn
import pandas as pd
import requests

from config import (BASE_URL, NUM_PAGES, DATA_DIR)
from utils import text_to_minutes


class Crawler:

    def __init__(self):
        self.num_pages = NUM_PAGES
        self.base_url = BASE_URL

    def get_image(self, soup) -> Optional[str]:
        image = soup.find('link', attrs={'as': 'image'})['href']
        if image:
            return image
        return None

    def get_ingredients(self, soup) -> Optional[str]:
        ingredients = soup.find('ul', class_='dr-unordered-list')
        if ingredients:
            return ingredients.text.replace("\n", "").strip()
        return None

    def get_procedure(self, soup) -> Optional[str]:
        procedure = soup.find('ol', class_='dr-ordered-list')
        if procedure:
            return procedure.text.strip()
        return None

    def get_tags(self, soup) -> Optional[list]:
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            json_content = script_tag.string

            data = json.loads(json_content)

            keywords = data.get('keywords')
            recipe_category = data.get('recipeCategory')

            if recipe_category and keywords:
                return keywords.split(',') + recipe_category.split(',')
            elif keywords:
                return keywords.split(',')
            elif recipe_category:
                recipe_category.split(',')
        return None

    def get_time(self, soup) -> Optional[int]:
        cooking_time = soup.find_all(class_='nx-time-wrapper')
        if cooking_time:
            return text_to_minutes(cooking_time[-1].get_text(strip=True).split(':')[-1])
        return None

    def get_all_recipes(self, base_url, num_pages) -> dict:

        d = {}
        links = []
        tags = []
        procedures = []
        ingredients = []
        images = []
        cooking_time = []

        pbar = tqdm(range(1, num_pages + 1))

        for page_num in pbar:
            pbar.set_description(f"Crawling Page {page_num}")
            url = f"{base_url}/page/{page_num}/"

            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding="iso-8859-1")

            hrefs = soup.find_all('a', class_='post-thumbnail', href=True)

            for href in hrefs:
                response = requests.get(href['href'])
                soup = BeautifulSoup(response.content, 'html.parser')

                links.append(href['href'])
                tags.append(self.get_tags(soup))
                procedures.append(self.get_procedure(soup))
                ingredients.append(self.get_ingredients(soup))
                images.append(self.get_image(soup))
                cooking_time.append(self.get_time(soup))

        d['recipe_link'] = links
        d['ingredients'] = ingredients
        d['procedure'] = procedures
        d['image'] = images
        d['tags'] = tags
        d['cooking_time'] = cooking_time

        return d

    def export(self) -> NoReturn:
        recipes_dict = self.get_all_recipes(self.base_url, self.num_pages)
        df = pd.DataFrame.from_dict(recipes_dict, orient='index').T
        df.to_csv(DATA_DIR.joinpath('gastronomos_dataset1.csv'), index=False)


def main():
    crawler = Crawler()
    crawler.export()


if __name__ == "__main__":
    main()
