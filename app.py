import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Sabitler
MAX_YAS = 10  # 10 yaşından büyük araçları almayacağız
MAX_KM = 150000  # 150.000 km’den fazla olanları almayacağız
MAX_FIYAT = 1750000  # 1.750.000 TL’den pahalı olanları almayacağız
BASE_URL = "https://www.arabam.com"

# Sayfa Başlığı ve Açıklama
st.set_page_config(page_title="🚗 Arabam.com Veri Toplayıcı", layout="wide")
st.title("🚗 Arabam.com Veri Toplayıcı")
st.write("Belirli kriterlere göre Arabam.com'dan ikinci el araç ilanlarını çekin ve analiz edin.")

# Marka Listesini Çekme Fonksiyonu
@st.cache_data
def get_brands():
    url = f"{BASE_URL}/ikinci-el/otomobil"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    brand_elements = soup.select(".all-category-list a")  # Marka linkleri
    brands = {el.text.strip(): el["href"] for el in brand_elements if "href" in el.attrs}
    
    return brands

# Seçilen markaya göre model verisini çekme
def get_models(brand_url):
    url = f"{BASE_URL}{brand_url}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    model_elements = soup.select(".all-category-list a")  # Model linkleri
    models = {el.text.strip(): el["href"] for el in model_elements if "href" in el.attrs}
    
    return models

# **1. Adım: Marka Seçimi**
brands = get_brands()

if brands:
    selected_brand = st.selectbox("Lütfen bir marka seçin:", options=list(brands.keys()))
    brand_url = brands[selected_brand]
else:
    st.error("Arabam.com'dan marka verisi çekilemedi. Lütfen sayfayı yenileyin.")
    st.stop()

# **2. Adım: Model Seçimi**
models = get_models(brand_url)
if models:
    selected_model = st.selectbox("Lütfen bir model seçin:", options=list(models.keys()))
    model_url = models[selected_model]
else:
    st.error(f"{selected_brand} markasına ait modeller çekilemedi.")
    st.stop()

# **Verileri Çek Butonu**
if st.button("Verileri Çek"):
    st.info(f"'{selected_brand} {selected_model}' için veriler çekiliyor...")

    # İlanları çekme fonksiyonu
    def scrape_listings(url):
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        listings = []
        
        # Her ilan satırını seçiyoruz
        car_elements = soup.select("tr[data-id]")  # Arabam.com ilan satırları

        for car in car_elements:
            try:
                model = car.select_one("td:nth-of-type(1)").text.strip()
                title = car.select_one("td:nth-of-type(2)").text.strip()
                year = int(car.select_one("td:nth-of-type(3)").text.strip())
                km = int(car.select_one("td:nth-of-type(4)").text.replace(".", "").strip())
                color = car.select_one("td:nth-of-type(5)").text.strip()
                price_text = car.select_one("td:nth-of-type(6)").text.strip().replace(" TL", "").replace(".", "")
                price = int(price_text) if price_text.isnumeric() else 0
                date = car.select_one("td:nth-of-type(7)").text.strip()
                location = car.select_one("td:nth-of-type(8)").text.strip()
                link = BASE_URL + car.select_one("td:nth-of-type(2) a")["href"]

                # **Filtreleme**
                if (2025 - year <= MAX_YAS) and (km <= MAX_KM) and (price <= MAX_FIYAT):
                    listings.append([model, title, year, km, color, price, date, location, link])
            except Exception as e:
                continue  # Hatalı ilanları atla

        return listings

    # **İlanları Çekme İşlemi**
    data = scrape_listings(f"{BASE_URL}{model_url}?minYear=2015&maxkm=150000")

    # **Sonuçları Göster**
    if data:
        df = pd.DataFrame(data, columns=["Model", "İlan Başlığı", "Yıl", "Kilometre", "Renk", "Fiyat", "Tarih", "İl/İlçe", "İlan URL"])
        st.dataframe(df)
        
        # **Excel Olarak İndir**
        st.download_button("Excel Olarak İndir", df.to_csv(index=False).encode("utf-8"), "arabam_verileri.csv", "text/csv")
    else:
        st.warning("Filtrelere uygun ilan bulunamadı.")
