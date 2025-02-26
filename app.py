import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Sabitler (Filtreler)
MAX_AGE = 10  # Maksimum yaş (10 yıldan eski araçları gösterme)
MAX_KM = 150000  # Maksimum kilometre (150.000 km üzerini gösterme)
MAX_PRICE = 1750000  # Maksimum fiyat (1.750.000 TL üzerini gösterme)

# Arabam.com'dan marka listesini çeken fonksiyon
def get_car_brands():
    url = "https://www.arabam.com/ikinci-el/otomobil"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        brand_options = []

        brands = soup.select("a[href*='/ikinci-el/otomobil']")
        for brand in brands:
            brand_name = brand.text.strip()
            brand_url = brand["href"]
            if brand_name and "?" not in brand_url:
                brand_options.append((brand_name, brand_url))

        return brand_options if brand_options else None
    else:
        return None

# Arabam.com'dan ilanları çeken fonksiyon
def fetch_car_listings(brand_url):
    url = f"https://www.arabam.com{brand_url}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    listings = []
    
    cars = soup.select(".listing-text")  # Arabam.com'un ilan başlıklarını çekiyoruz
    
    for car in cars:
        try:
            title = car.text.strip()
            link = car.find("a")["href"]
            price = int(car.find_next(".listing-price").text.replace("TL", "").replace(".", "").strip())
            year = int(car.find_next(".listing-year").text.strip())
            km = int(car.find_next(".listing-km").text.replace("km", "").replace(".", "").strip())
            location = car.find_next(".listing-location").text.strip()
            
            # Filtreleri uygula
            if (2025 - year) > MAX_AGE or km > MAX_KM or price > MAX_PRICE:
                continue
            
            listings.append({
                "Model": title,
                "Yıl": year,
                "Kilometre": km,
                "Fiyat": price,
                "İl / İlçe": location,
                "İlan URL": f"https://www.arabam.com{link}"
            })
        except Exception:
            continue  # Eğer bir hata alırsak, ilanı atla
    
    return listings

# Streamlit Arayüzü
st.title("🚗 Arabam.com Veri Toplayıcı")
st.write("Belirli kriterlere göre Arabam.com'dan ikinci el araç ilanlarını çekin ve analiz edin.")

brand_model_list = get_car_brands()

if brand_model_list:
    selected_brand = st.selectbox("Lütfen bir marka seçin:", [b[0] for b in brand_model_list])
    brand_url = dict(brand_model_list).get(selected_brand, None)
    fetch_button = st.button("Verileri Çek")
else:
    st.error("Arabam.com'dan marka verisi çekilemedi. Lütfen sayfayı yenileyin.")
    fetch_button = None  # Butonu devre dışı bırak

if fetch_button and brand_url:
    st.info(f"'{selected_brand}' için veriler çekiliyor...")
    listings = fetch_car_listings(brand_url)
    
    if listings:
        df = pd.DataFrame(listings)
        st.dataframe(df)
        st.download_button("📥 Excel Olarak İndir", df.to_csv(index=False), "ilanlar.csv", "text/csv")
    else:
        st.warning("Filtrelere uygun ilan bulunamadı.")
