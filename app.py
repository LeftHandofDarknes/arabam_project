import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Arabam.com'dan çekeceğimiz marka ve modeller
TARGET_CARS = {
    "Audi": ["A3"],
    "BMW": ["3 Serisi"],
    "Ford": ["Focus"],
    "Honda": ["Civic"],
    "Hyundai": ["i20"],
    "Mercedes - Benz": ["C Serisi"],
    "Renault": ["Clio", "Megane", "Symbol"],
    "Skoda": ["Octavia", "SüperB"],
    "Toyota": ["Corolla"],
    "Volkswagen": ["Polo", "Passat", "Golf"]
}

# Sabitler
MAX_YAS = 10
MAX_KM = 150000
MAX_FIYAT = 1750000
ILAN_TARIHI_LIMIT = datetime.now() - timedelta(days=120)

st.title("Arabam.com Veri Çekme Uygulaması")

if st.button("Verileri Çek"):
    data = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for marka, modeller in TARGET_CARS.items():
        for model in modeller:
            # URL oluşturuluyor: marka ve model isimleri formatlanıyor
            url = f"https://www.arabam.com/ikinci-el/otomobil/{marka.lower().replace(' ', '-')}-{model.lower().replace(' ', '-')}"
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                st.error(f"Bağlantı hatası: {marka} {model} için veri çekilemedi!")
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            ilanlar = soup.find_all("div", class_="listing-item")
            
            for ilan in ilanlar:
                try:
                    title_tag = ilan.find("h3", class_="listing-title")
                    if title_tag is None:
                        continue
                    ilan_baslik = title_tag.text.strip()

                    price_tag = ilan.find("div", class_="listing-price")
                    if price_tag is None:
                        continue
                    fiyat_str = price_tag.text.strip().replace(" TL", "").replace(".", "")
                    fiyat = int(fiyat_str) if fiyat_str.isdigit() else None

                    detail_tag = ilan.find("div", class_="listing-detail")
                    if detail_tag is None:
                        continue
                    km_str = detail_tag.text.strip().split(" ")[0].replace(".", "")
                    km = int(km_str) if km_str.isdigit() else None

                    # İlan başlığından yıl bilgisi çekiliyor
                    yil_str = ilan_baslik.split(" ")[-1]
                    yil = int(yil_str) if yil_str.isdigit() else None

                    date_tag = ilan.find("span", class_="listing-date")
                    if date_tag is None:
                        continue
                    ilan_tarihi_str = date_tag.text.strip()
                    ilan_tarihi = datetime.strptime(ilan_tarihi_str, "%d.%m.%Y") if ilan_tarihi_str else None

                    location_tag = ilan.find("div", class_="listing-location")
                    sehir_ilce = location_tag.text.strip() if location_tag else ""

                    if yil and km and fiyat and ilan_tarihi:
                        if (yil >= (datetime.now().year - MAX_YAS) and 
                            km <= MAX_KM and 
                            fiyat <= MAX_FIYAT and 
                            ilan_tarihi >= ILAN_TARIHI_LIMIT):
                            data.append([marka, model, ilan_baslik, yil, km, fiyat, ilan_tarihi_str, sehir_ilce])
                except Exception as e:
                    st.write(f"İlan işlenirken hata oluştu: {e}")
                    continue
    
    df = pd.DataFrame(data, columns=["Marka", "Model", "İlan Başlığı", "Yıl", "KM", "Fiyat", "İlan Tarihi", "Şehir/İlçe"])
    if df.empty:
        st.warning("Belirlenen kriterlere uygun ilan bulunamadı!")
    else:
        st.success(f"{len(df)} ilan başarıyla çekildi!")
        df.to_excel("arabam_verileri.xlsx", index=False)
        with open("arabam_verileri.xlsx", "rb") as f:
            st.download_button("Excel Dosyasını İndir", f, file_name="arabam_verileri.xlsx")
