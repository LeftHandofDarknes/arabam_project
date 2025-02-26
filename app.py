import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Sabitler
MAX_YAS = 10  # 10 yaşından büyük araçlara bakılmayacak
MAX_KM = 150000  # 150.000 KM üzeri araçlara bakılmayacak
MAX_FIYAT = 1750000  # 1.750.000 TL’den pahalı araçlara bakılmayacak

# Arabam.com'dan marka ve model listesini çekme fonksiyonu
def get_brand_model_options():
    url = "https://www.arabam.com/ikinci-el"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return {}, {}
    
    soup = BeautifulSoup(response.text, 'html.parser')
    brands = {}
    
    brand_elements = soup.select(".filter-list a")
    for brand in brand_elements:
        brand_name = brand.text.strip()
        brand_url = brand["href"]
        brands[brand_name] = brand_url
    
    return brands

# Marka ve modelleri al
brands = get_brand_model_options()

st.title("Arabam.com Veri Çekme Uygulaması")

# Marka seçimi
dropdown_brands = list(brands.keys())
selected_brand = st.selectbox("Bir Marka Seçin", dropdown_brands)

# Model ve alt model dinamik olarak seçilecek
if selected_brand:
    brand_url = brands[selected_brand]
    
    # Model seçeneklerini çekelim
    model_url = f"https://www.arabam.com{brand_url}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(model_url, headers=headers)
    
    models = {}
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        model_elements = soup.select(".filter-list a")
        for model in model_elements:
            model_name = model.text.strip()
            model_url = model["href"]
            models[model_name] = model_url
    
    dropdown_models = list(models.keys())
    selected_model = st.selectbox("Bir Model Seçin", dropdown_models)
    
    if selected_model:
        model_url = models[selected_model]
        
        # Alt model çekme işlemi
        alt_model_url = f"https://www.arabam.com{model_url}"
        response = requests.get(alt_model_url, headers=headers)
        
        alt_models = {}
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            alt_model_elements = soup.select(".filter-list a")
            for alt_model in alt_model_elements:
                alt_model_name = alt_model.text.strip()
                alt_model_url = alt_model["href"]
                alt_models[alt_model_name] = alt_model_url
        
        dropdown_alt_models = list(alt_models.keys())
        selected_alt_model = st.selectbox("Bir Alt Model Seçin", dropdown_alt_models)
        
        if selected_alt_model:
            final_url = f"https://www.arabam.com{alt_models[selected_alt_model]}?minYear=2015&maxkm={MAX_KM}"
            st.write(f"Seçilen URL: {final_url}")
            
            if st.button("Verileri Çek"):
                response = requests.get(final_url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    ilanlar = []
                    
                    ilan_elements = soup.select(".listing-item")
                    for ilan in ilan_elements:
                        try:
                            title = ilan.select_one(".listing-title").text.strip()
                            price = ilan.select_one(".listing-price").text.strip().replace("TL", "").replace(".", "").strip()
                            price = int(price) if price.isdigit() else None
                            km = ilan.select_one(".listing-detail-specifications .value").text.strip().replace(" km", "").replace(".", "").strip()
                            km = int(km) if km.isdigit() else None
                            year = ilan.select_one(".listing-model-year").text.strip()
                            year = int(year) if year.isdigit() else None
                            link = f"https://www.arabam.com{ilan.select_one('a')['href']}"
                            
                            if (year and (2025 - year) <= MAX_YAS) and (km and km <= MAX_KM) and (price and price <= MAX_FIYAT):
                                ilanlar.append({
                                    "Başlık": title,
                                    "Fiyat": price,
                                    "KM": km,
                                    "Yıl": year,
                                    "Link": link
                                })
                        except Exception as e:
                            print(f"Hata: {e}")
                    
                    df = pd.DataFrame(ilanlar)
                    if not df.empty:
                        st.dataframe(df)
                        df.to_excel("arabam_veriler.xlsx", index=False)
                        st.success("Veriler başarıyla kaydedildi!")
                    else:
                        st.error("Belirtilen kriterlere uygun ilan bulunamadı.")
