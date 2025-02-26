import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Arabam.com'dan almak istediğimiz markalar ve modeller
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

# Filtre kriterleri
MAX_AGE_YEARS = 10  # 10 yaşından büyük olmayacak
MAX_KM = 150000  # 150.000 km üstü olmayacak
MAX_PRICE = 1750000  # 1.750.000 TL üstü olmayacak
DAYS_LIMIT = 120  # Son 120 gün içinde listelenen araçlar

st.title("Arabam.com Araç Fiyat Analizi")

if st.button("Verileri Çek"):
    st.write("Veriler çekiliyor... Lütfen bekleyin.")
    
    base_url = "https://www.arabam.com"
    results = []
    cutoff_date = datetime.now() - timedelta(days=DAYS_LIMIT)
    
    for brand, models in TARGET_CARS.items():
        for model in models:
            search_url = f"{base_url}/ikinci-el/otomobil/{brand.lower()}-{model.lower()}"
            headers = {"User-Agent": "Mozilla/5.0"}
            
            response = requests.get(search_url, headers=headers)
            if response.status_code != 200:
                st.error(f"Bağlantı hatası: {brand} {model} için veriler alınamadı.")
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            listings = soup.find_all("div", class_="listing-item")
            
            for listing in listings:
                try:
                    title = listing.find("h3", class_="listing-title").text.strip()
                    price = listing.find("span", class_="listing-price").text.strip()
                    km = listing.find("li", class_="listing-km").text.strip()
                    year = listing.find("li", class_="listing-year").text.strip()
                    city = listing.find("li", class_="listing-location").text.strip()
                    date = listing.find("li", class_="listing-date").text.strip()
                    
                    price = int(price.replace("TL", "").replace(".", "").strip())
                    km = int(km.replace("km", "").replace(".", "").strip())
                    year = int(year)
                    
                    # 120 gün sınırı
                    ilan_tarihi = datetime.strptime(date, "%d.%m.%Y")
                    if ilan_tarihi < cutoff_date:
                        continue
                    
                    # Filtreleme koşulları
                    if year < (datetime.now().year - MAX_AGE_YEARS) or km > MAX_KM or price > MAX_PRICE:
                        continue
                    
                    results.append([brand, model, title, year, km, price, city, ilan_tarihi.strftime("%d.%m.%Y")])
                except Exception as e:
                    continue
    
    if results:
        df = pd.DataFrame(results, columns=["Marka", "Model", "Başlık", "Yıl", "KM", "Fiyat", "Şehir", "İlan Tarihi"])
        df.to_excel("arabam_scraper.xlsx", index=False)
        st.success("Veriler başarıyla çekildi ve 'arabam_scraper.xlsx' olarak kaydedildi!")
        st.download_button(
            label="Excel Dosyasını İndir",
            data=open("arabam_scraper.xlsx", "rb").read(),
            file_name="arabam_scraper.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Filtrelere uygun veri bulunamadı.")
