import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Arabam.com ana URL'si
BASE_URL = "https://www.arabam.com"

# Sabit filtreler
MAX_YAS = 10  # 10 yaşından büyük araçları almaz
MAX_KM = 150000  # 150.000 km üstü araçları almaz
MAX_FIYAT = 1750000  # 1.750.000 TL’den pahalı araçları almaz

st.title("Arabam.com Araç Veri Çekme Uygulaması 🚗")

@st.cache_data
def get_brands():
    """Arabam.com'dan marka listesini çeker."""
    url = f"{BASE_URL}/ikinci-el/otomobil"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    brand_list = []
    for brand in soup.select("ul.category-list a"):
        brand_name = brand.text.strip()
        brand_url = brand["href"]
        brand_list.append((brand_name, brand_url))

    return brand_list

@st.cache_data
def get_models(brand_url):
    """Seçilen markaya göre model listesini çeker."""
    url = f"{BASE_URL}{brand_url}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    model_list = []
    for model in soup.select("ul.category-list a"):
        model_name = model.text.strip()
        model_url = model["href"]
        model_list.append((model_name, model_url))

    return model_list

@st.cache_data
def get_submodels(model_url):
    """Seçilen modele göre alt model listesini çeker."""
    url = f"{BASE_URL}{model_url}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    submodel_list = []
    for submodel in soup.select("ul.category-list a"):
        submodel_name = submodel.text.strip()
        submodel_url = submodel["href"]
        submodel_list.append((submodel_name, submodel_url))

    return submodel_list

def scrape_data(selected_url):
    """Seçilen alt model için araç verilerini çeker ve filtreler uygular."""
    url = f"{BASE_URL}{selected_url}?minYear=2015&maxkm=150000"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    car_data = []
    for listing in soup.select(".listing-item"):
        try:
            title = listing.select_one(".listing-title").text.strip()
            price = listing.select_one(".listing-price").text.strip().replace(" TL", "").replace(".", "")
            price = int(price) if price.isdigit() else None
            details = listing.select(".listing-detail-line")
            km = int(details[0].text.strip().replace(" km", "").replace(".", ""))
            year = int(details[1].text.strip())
            link = BASE_URL + listing.select_one("a")["href"]

            # Filtreleri uygulayalım
            if price and price <= MAX_FIYAT and km <= MAX_KM and (2025 - year) <= MAX_YAS:
                car_data.append([title, price, km, year, link])
        except Exception as e:
            print(f"Hata: {e}")

    df = pd.DataFrame(car_data, columns=["Başlık", "Fiyat (TL)", "Kilometre", "Yıl", "Link"])
    return df

# Dropdown menüleri oluştur
brands = get_brands()
brand_names = [b[0] for b in brands]
selected_brand = st.selectbox("Marka Seçiniz", brand_names)

if selected_brand:
    brand_url = dict(brands)[selected_brand]
    models = get_models(brand_url)
    model_names = [m[0] for m in models]
    selected_model = st.selectbox("Model Seçiniz", model_names)

    if selected_model:
        model_url = dict(models)[selected_model]
        submodels = get_submodels(model_url)
        submodel_names = [s[0] for s in submodels]
        selected_submodel = st.selectbox("Alt Model Seçiniz", submodel_names)

        if selected_submodel:
            submodel_url = dict(submodels)[selected_submodel]

            if st.button("Verileri Çek"):
                df = scrape_data(submodel_url)
                if not df.empty:
                    st.dataframe(df)

                    # Excel olarak indirilebilir hale getirelim
                    excel_filename = "arabam_verileri.xlsx"
                    df.to_excel(excel_filename, index=False)
                    with open(excel_filename, "rb") as f:
                        st.download_button("Excel olarak indir", f, file_name=excel_filename)
                else:
                    st.warning("Hiçbir veri bulunamadı!")
