import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Arabam.com URL'leri
BASE_URL = "https://www.arabam.com"
MARKA_URL = f"{BASE_URL}/arabalar"

# Kullanıcı filtreleri
MAX_YAS = 10  # 10 yaşından büyük olmayacak
MAX_KM = 150000  # 150.000 km’den fazla olmayacak
MAX_FIYAT = 1750000  # 1.750.000 TL’den pahalı olmayacak

# Header bilgisi (Bot engellemeyi aşmak için)
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Arabam.com'dan markaları al
@st.cache_data
def get_brands():
    response = requests.get(MARKA_URL, headers=HEADERS)
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    brands = {item.text.strip(): item["href"] for item in soup.select(".brand-item a")}
    return brands

# Seçilen markaya göre modelleri al
@st.cache_data
def get_models(brand_url):
    response = requests.get(BASE_URL + brand_url, headers=HEADERS)
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    models = {item.text.strip(): item["href"] for item in soup.select(".model-item a")}
    return models

# Seçilen modele göre alt modelleri al
@st.cache_data
def get_submodels(model_url):
    response = requests.get(BASE_URL + model_url, headers=HEADERS)
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    submodels = {item.text.strip(): item["href"] for item in soup.select(".submodel-item a")}
    return submodels

# Sayfa başlığı
st.title("Arabam.com Veri Çekme Uygulaması")

# Marka seçimi
brands = get_brands()
brand_name = st.selectbox("Marka Seçin", ["Seçiniz"] + list(brands.keys()))

# Model seçimi (Eğer marka seçilmişse)
if brand_name != "Seçiniz":
    models = get_models(brands[brand_name])
    model_name = st.selectbox("Model Seçin", ["Seçiniz"] + list(models.keys()))
else:
    model_name = "Seçiniz"

# Alt model seçimi (Eğer model seçilmişse)
if model_name != "Seçiniz":
    submodels = get_submodels(models[model_name])
    submodel_name = st.selectbox("Alt Model Seçin", ["Seçiniz"] + list(submodels.keys()))
else:
    submodel_name = "Seçiniz"

# "Verileri Çek" butonu (Eğer her şey seçilmişse aktif olur)
if submodel_name != "Seçiniz":
    if st.button("Verileri Çek"):
        ilan_url = f"{BASE_URL}{submodels[submodel_name]}?minYear=2015&maxkm=150000"
        response = requests.get(ilan_url, headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            ilanlar = []
            for ilan in soup.select(".listing-item"):
                try:
                    fiyat = ilan.select_one(".listing-price").text.strip().replace("TL", "").replace(".", "").strip()
                    fiyat = int(fiyat) if fiyat.isdigit() else 0
                    model_yili = int(ilan.select_one(".listing-model-year").text.strip())
                    km = int(ilan.select_one(".listing-km").text.strip().replace("km", "").replace(".", "").strip())
                    link = BASE_URL + ilan.select_one(".listing-item a")["href"]

                    # Filtreleri uygula
                    if model_yili >= (2025 - MAX_YAS) and km <= MAX_KM and fiyat <= MAX_FIYAT:
                        ilanlar.append({
                            "Fiyat": fiyat,
                            "Model Yılı": model_yili,
                            "Kilometre": km,
                            "Link": link
                        })
                except Exception as e:
                    print("Hata:", e)

            # Verileri DataFrame'e çevir ve göster
            if ilanlar:
                df = pd.DataFrame(ilanlar)
                st.write(df)
                df.to_excel("arabam_verileri.xlsx", index=False)
                st.success("Veriler başarıyla çekildi ve arabam_verileri.xlsx olarak kaydedildi!")
            else:
                st.warning("Belirtilen kriterlere uygun ilan bulunamadı!")
