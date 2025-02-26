import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Kullanıcı filtreleri
MAX_KM = 150000
MAX_PRICE = 1750000
MAX_AGE = 10
CURRENT_YEAR = 2025

# Arabam.com'dan marka ve model bilgilerini çek
@st.cache_data
def get_brands():
    url = "https://www.arabam.com/ikinci-el/otomobil"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    brands = [a.text.strip() for a in soup.select(".filter-list a")]
    return brands

@st.cache_data
def get_models(brand):
    url = f"https://www.arabam.com/ikinci-el/{brand.lower().replace(' ', '-')}-modelleri"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    models = [a.text.strip() for a in soup.select(".filter-list a")]
    return models

@st.cache_data
def get_submodels(brand, model):
    url = f"https://www.arabam.com/ikinci-el/{brand.lower().replace(' ', '-')}/{model.lower().replace(' ', '-')}-modelleri"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    submodels = [a.text.strip() for a in soup.select(".filter-list a")]
    return submodels

# Belirtilen sayfadan ilanları çekme fonksiyonu
def get_listings(brand, model, submodel):
    url = f"https://www.arabam.com/ikinci-el/{brand.lower().replace(' ', '-')}/{model.lower().replace(' ', '-')}/{submodel.lower().replace(' ', '-')}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    listings = []

    for row in soup.select(".listing-item"):  # Arabam.com'daki her ilanı seç
        try:
            year = int(row.select_one(".year").text.strip())
            km = int(row.select_one(".km").text.strip().replace(".", ""))
            price = int(row.select_one(".price").text.strip().replace(" TL", "").replace(".", ""))
            title = row.select_one(".title").text.strip()
            location = row.select_one(".location").text.strip()
            link = "https://www.arabam.com" + row.select_one("a")["href"]
            
            # Kullanıcı kriterlerine göre filtreleme
            if (CURRENT_YEAR - year) <= MAX_AGE and km <= MAX_KM and price <= MAX_PRICE:
                listings.append({
                    "Model": model,
                    "İlan Başlığı": title,
                    "Yıl": year,
                    "Kilometre": km,
                    "Fiyat": price,
                    "İl / İlçe": location,
                    "İlan URL": link
                })
        except:
            continue

    return listings

# Streamlit UI
def main():
    st.set_page_config(page_title="Arabam.com Veri Toplayıcı", page_icon="🚗", layout="wide")
    st.title("🚗 Arabam.com Veri Toplayıcı")
    st.write("Belirli kriterlere göre Arabam.com'dan ikinci el araç ilanlarını çekin ve analiz edin.")

    # Marka Seçimi
    brands = get_brands()
    brand = st.selectbox("Lütfen bir marka seçin:", brands)

    if brand:
        models = get_models(brand)
        model = st.selectbox("Lütfen bir model seçin:", models)
        
        if model:
            submodels = get_submodels(brand, model)
            submodel = st.selectbox("Lütfen bir alt model seçin:", submodels)

            if st.button("Verileri Çek"):
                st.info(f"'{brand} {model} {submodel}' için veriler çekiliyor...")
                listings = get_listings(brand, model, submodel)
                
                if listings:
                    df = pd.DataFrame(listings)
                    st.dataframe(df)
                    
                    # Excel dosyası olarak indir
                    output_file = "arabam_data.xlsx"
                    df.to_excel(output_file, index=False)
                    with open(output_file, "rb") as f:
                        st.download_button("Verileri İndir", f, file_name=output_file)
                else:
                    st.warning("Filtrelere uygun ilan bulunamadı.")

if __name__ == "__main__":
    main()
