import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Filtreleme kriterleri
MIN_YIL = 2015
MAX_KM = 150000
MAX_FIYAT = 1750000  # 1.750.000 TL’den pahalı olamaz
DAYS_LIMIT = 120  # İlan tarihi 120 günden eski olanları almayacak

# Takip edilecek marka ve modeller
MARKALAR_MODELLER = [
    "audi/a3",
    "bmw/3-serisi",
    "ford/focus",
    "honda/civic",
    "hyundai/i20",
    "mercedes-benz/c-serisi",
    "renault/clio",
    "renault/megane",
    "renault/symbol",
    "skoda/octavia",
    "skoda/superb",
    "toyota/corolla",
    "volkswagen/polo",
    "volkswagen/passat",
    "volkswagen/golf"
]

BASE_URL = "https://www.arabam.com/ikinci-el/otomobil/"

st.title("Arabam.com Araç Fiyat Analizi")
st.write("Seçilen marka ve modellere göre ikinci el araç fiyatlarını çekmek için butona basın.")

if st.button("Verileri Çek"):
    ilanlar = []

    for marka_model in MARKALAR_MODELLER:
        url = f"{BASE_URL}{marka_model}?minYear={MIN_YIL}&maxkm={MAX_KM}"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            st.error(f"{marka_model} için veri çekilemedi!")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        ilan_listesi = soup.find_all("tr", class_="listing-item")

        for ilan in ilan_listesi:
            try:
                fiyat = ilan.find("td", class_="listing-price").text.strip()
                fiyat = int(fiyat.replace(".", "").replace("TL", "").strip())

                if fiyat > MAX_FIYAT:
                    continue  # Maksimum fiyatı aşanları alma

                tarih = ilan.find("td", class_="listing-date").text.strip()
                ilan_tarihi = datetime.strptime(tarih, "%d.%m.%Y")

                if ilan_tarihi < datetime.now() - timedelta(days=DAYS_LIMIT):
                    continue  # 120 günden eski ilanları alma
                
                sehir = ilan.find("td", class_="listing-location").text.strip()
                arac_detay = ilan.find("td", class_="listing-modelname").text.strip()
                km = ilan.find("td", class_="listing-km").text.strip()

                ilanlar.append([marka_model, arac_detay, fiyat, km, sehir, ilan_tarihi.strftime("%d-%m-%Y")])

            except Exception as e:
                continue

    # Verileri DataFrame'e çevir
    df = pd.DataFrame(ilanlar, columns=["Marka/Model", "Alt Model", "Fiyat", "KM", "Şehir", "İlan Tarihi"])

    if df.empty:
        st.warning("Belirtilen kriterlere uygun ilan bulunamadı.")
    else:
        # Excel olarak kaydetme
        file_path = "arabam_fiyatlar.xlsx"
        df.to_excel(file_path, index=False)
        st.success("Veriler başarıyla çekildi ve kaydedildi!")
        st.download_button(label="Excel'i İndir", data=open(file_path, "rb"), file_name=file_path, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
