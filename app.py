import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Uygulama Başlığı
st.set_page_config(page_title="Arabam.com Veri Toplayıcı", page_icon="🚗")
st.title("🚗 Arabam.com Veri Toplayıcı")
st.write("Belirli kriterlere göre Arabam.com'dan ikinci el araç ilanlarını çekin ve analiz edin.")

# Kullanıcının belirlediği marka ve modeller
TARGET_CARS = {
    "Audi": ["A3"],
    "BMW": ["3 Serisi"],
    "Ford": ["Focus"],
    "Honda": ["Civic"],
    "Hyundai": ["i20"],
    "Mercedes-Benz": ["C Serisi"],
    "Renault": ["Clio", "Megane", "Symbol"],
    "Skoda": ["Octavia", "SuperB"],
    "Toyota": ["Corolla"],
    "Volkswagen": ["Polo", "Passat", "Golf"]
}

# Kısıtlayıcı Filtreler
MAX_YEARS_OLD = 10  # Maksimum yaş (Örneğin 2015 ve sonrası)
MAX_KM = 150000  # Maksimum kilometre
MAX_PRICE = 1750000  # Maksimum fiyat (TL)

# Arabam.com URL formatı
BASE_URL = "https://www.arabam.com/ikinci-el/otomobil/{brand}-{model}?maxkm={max_km}&minYear={min_year}&currency=TL&maxPrice={max_price}"

# Kullanıcının araç seçimi
brand = st.selectbox("Lütfen bir marka seçin:", list(TARGET_CARS.keys()))
if brand:
    model = st.selectbox("Lütfen bir model seçin:", TARGET_CARS[brand])

if st.button("Verileri Çek"):
    with st.spinner(f"{brand} {model} için veriler çekiliyor..."):

        # Arabam.com’dan belirlenen filtrelere göre ilanları çek
        url = BASE_URL.format(
            brand=brand.lower().replace(" ", "-"),
            model=model.lower().replace(" ", "-"),
            max_km=MAX_KM,
            min_year=2025 - MAX_YEARS_OLD,
            max_price=MAX_PRICE
        )

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = []

            # Sayfadaki tüm ilanları bul
            for listing in soup.find_all("tr", class_="listing-row"):
                try:
                    alt_model = listing.find("td", class_="model").text.strip()
                    ilan_basligi = listing.find("td", class_="listing-title").text.strip()
                    yil = listing.find("td", class_="year").text.strip()
                    km = listing.find("td", class_="km").text.strip().replace(".", "")
                    renk = listing.find("td", class_="color").text.strip()
                    fiyat = listing.find("td", class_="price").text.strip().replace(".", "").replace("TL", "")
                    tarih = listing.find("td", class_="date").text.strip()
                    il_ilce = listing.find("td", class_="location").text.strip()
                    ilan_url = listing.find("a", class_="listing-link")["href"]

                    # Filtreleme kriterlerine uyan ilanları ekle
                    if int(yil) >= (2025 - MAX_YEARS_OLD) and int(km) <= MAX_KM and int(fiyat) <= MAX_PRICE:
                        listings.append([brand, model, alt_model, ilan_basligi, yil, km, renk, fiyat, tarih, il_ilce, f"https://www.arabam.com{ilan_url}"])

                except Exception as e:
                    continue  # Eğer bir hata olursa geç

            # Eğer ilan bulunduysa tablo göster ve indirilebilir Excel oluştur
            if listings:
                df = pd.DataFrame(listings, columns=["Marka", "Model", "Alt Model", "İlan Başlığı", "Yıl", "Kilometre", "Renk", "Fiyat", "Tarih", "İl/İlçe", "İlan URL"])
                st.success(f"{len(df)} ilan bulundu!")

                # DataFrame'i göster
                st.dataframe(df)

                # Excel olarak indirme seçeneği
                @st.cache_data
                def convert_df(df):
                    return df.to_excel(index=False).encode("utf-8")

                st.download_button(
                    label="📥 Excel İndir",
                    data=convert_df(df),
                    file_name=f"{brand}_{model}_ilanlar.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("⚠️ Filtrelere uygun ilan bulunamadı.")
        else:
            st.error("❌ Arabam.com ile bağlantı kurulamadı. Lütfen tekrar deneyin.")
