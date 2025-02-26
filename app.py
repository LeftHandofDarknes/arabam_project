import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Kullanıcı arayüzü başlığı
st.title("🚗 Arabam.com Veri Toplayıcı")
st.write("Belirli kriterlere göre Arabam.com'dan ikinci el araç ilanlarını çekin ve analiz edin.")

# Kullanıcıdan almak istediğimiz markalar
MARKALAR_MODELLER = {
    "Audi": "A3",
    "BMW": "3 Serisi",
    "Ford": "Focus",
    "Honda": "Civic",
    "Hyundai": "i20",
    "Mercedes-Benz": "C Serisi",
    "Renault": ["Clio", "Megane", "Symbol"],
    "Skoda": ["Octavia", "SuperB"],
    "Toyota": "Corolla",
    "Volkswagen": ["Polo", "Passat", "Golf"]
}

# Filtreler
MAX_YAS = 10
MAX_KM = 150000
MAX_FIYAT = 1750000  # 1.750.000 TL’den pahalı olamaz

# Kullanıcı seçimi
selected_brand = st.selectbox("Lütfen bir marka seçin:", list(MARKALAR_MODELLER.keys()))
selected_model = st.selectbox("Lütfen bir model seçin:", MARKALAR_MODELLER[selected_brand] if isinstance(MARKALAR_MODELLER[selected_brand], list) else [MARKALAR_MODELLER[selected_brand]])

# Veriyi çekmek için buton
temp_message = st.empty()
if st.button("Verileri Çek"):
    temp_message.info(f"'{selected_brand} {selected_model}' için veriler çekiliyor...")
    
    base_url = f"https://www.arabam.com/ikinci-el/{selected_brand.lower()}-{selected_model.lower()}"
    params = {"maxPrice": MAX_FIYAT, "minYear": 2025 - MAX_YAS, "maxkm": MAX_KM}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
    
    response = requests.get(base_url, params=params, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        ilanlar = []

        for ilan in soup.find_all("tr", class_="listing-item"):  # Arabam.com'un güncel yapısına bakarak güncellenebilir
            try:
                model = ilan.find("td", class_="listing-model").text.strip()
                ilan_baslik = ilan.find("td", class_="listing-title").text.strip()
                yil = int(ilan.find("td", class_="listing-year").text.strip())
                km = int(ilan.find("td", class_="listing-km").text.replace(".", "").strip())
                renk = ilan.find("td", class_="listing-color").text.strip()
                fiyat = int(ilan.find("td", class_="listing-price").text.replace(" TL", "").replace(".", "").strip())
                tarih = ilan.find("td", class_="listing-date").text.strip()
                il_ilce = ilan.find("td", class_="listing-location").text.strip()
                ilan_url = ilan.find("a", class_="listing-link")["href"]
                ilan_url = f"https://www.arabam.com{ilan_url}"
                
                if yil >= (2025 - MAX_YAS) and km <= MAX_KM and fiyat <= MAX_FIYAT:
                    ilanlar.append([model, ilan_baslik, yil, km, renk, fiyat, tarih, il_ilce, ilan_url])
            except Exception as e:
                print(f"Hata oluştu: {e}")
                continue
    
        if ilanlar:
            df = pd.DataFrame(ilanlar, columns=["Model", "İlan Başlığı", "Yıl", "Kilometre", "Renk", "Fiyat", "Tarih", "İl / İlçe", "İlan URL"])
            st.success("Veriler başarıyla çekildi!")
            st.dataframe(df)
            df.to_excel("arabam_verileri.xlsx", index=False)
            st.download_button("Excel İndir", data=open("arabam_verileri.xlsx", "rb"), file_name="arabam_verileri.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.warning("Filtrelere uygun ilan bulunamadı.")
    else:
        st.error("Arabam.com ile bağlantı kurulamadı. Lütfen tekrar deneyin.")
