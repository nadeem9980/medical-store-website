import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import time

base_url = "https://dwatson.pk/medicines.html"
headers = {
    "User-Agent": "Mozilla/5.0"
}

filename = "products_scraped.csv"
fields = [
    "name", "details", "link", "group", "brand",
    "batch_no", "expiry_date", "created_at", "added_by_id",
    "image", "price"
]

default_group = "Medicine"
default_added_by_id = 1

with open(filename, mode="w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    page = 1
    while True:
        params = {
            "p": page,
            "product_list_limit": 12  # keep default 12 per page, or increase if it works
        }
        print(f"Fetching page {page} ...")
        response = requests.get(base_url, headers=headers, params=params)
        time.sleep(2)  # polite delay
        soup = BeautifulSoup(response.content, 'html.parser')

        products = soup.find_all('li', class_='item product product-item')
        if not products:
            print("No more products found, stopping.")
            break

        for product in products:
            try:
                name_tag = product.find('a', class_='product-item-link')
                name = name_tag.get_text(strip=True) if name_tag else ""

                link_tag = product.find('a', class_='product photo product-item-photo')
                link = link_tag['href'] if link_tag else ""

                img_tag = product.find('img', class_='product-image-photo')
                image = img_tag['src'] if img_tag else ""

                brand_tag = product.find('p', class_='manufacturer-link manufacturer-name')
                brand = brand_tag.get_text(strip=True) if brand_tag else ""

                price_tag = product.find('span', class_='price')
                price = price_tag.get_text(strip=True).replace("Rs.", "").replace(",", "").strip() if price_tag else "0"

                detail_tag = product.find('p', class_='manufacturer-link')
                details = detail_tag.get_text(strip=True) if detail_tag else ""

                batch_no = "N/A"
                expiry_date = ""
                created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                added_by_id = default_added_by_id
                group = default_group

                writer.writerow({
                    "name": name,
                    "details": details,
                    "link": link,
                    "group": group,
                    "brand": brand,
                    "batch_no": batch_no,
                    "expiry_date": expiry_date,
                    "created_at": created_at,
                    "added_by_id": added_by_id,
                    "image": image,
                    "price": price
                })

                print(f"Saved: {name}")

            except Exception as e:
                print(f"Error saving product: {e}")

        page += 1
