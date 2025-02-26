import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO

# Belirlenen araç marka ve modelleri
MARKA_MODELLER = {
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

BASE_URL = "https://www.arabam.com/ikinci-el"

# Arabam.com için sabit filtreler
MIN_YIL = 2015
MAX_KM = 150000
MAX_FIYAT = 1750000  # 1.750.000 TL’den pahalı olanlar alınmayacak

st.title("🚗 Arabam.com Veri Toplayıcı")
st.write("Belirli kriterlere göre Arabam.com'dan ikinci el araç ilanlarını çekin ve analiz edin.")

# Kullanıcıdan araç marka seçimi
marka_secim = st.selectbox("Lütfen bir marka seçin:", list(MARKA_MODELLER.keys()))

# Seçilen markanın modellerini listeleme
model_secim = st.selectbox("Lütfen bir model seçin:", MARKA_MODELLER[marka_secim])

# Veri çekme butonu
if st.button("Verileri Çek"):
    with st.spinner(f"{marka_secim} {model_secim} için veriler çekiliyor..."):
        try:
            # Arabam.com için uygun URL oluşturma
            url = f"{BASE_URL}/{marka_secim.lower()}-{model_secim.lower()}?minYear={MIN_YIL}&maxkm={MAX_KM}&maxPrice={MAX_FIYAT}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                st.error("Arabam.com ile bağlantı kurulamadı. Lütfen tekrar deneyin.")
            else:
                # Sayfa kaynağını işle
                soup = BeautifulSoup(response.text, "html.parser")
                ilanlar = []
                
                # İlanları çekme
                for ilan in soup.find_all("tr", class_="listing-item"):
                    try:
                        model = ilan.find("td", class_="listing-modelname").text.strip()
                        ilan_baslik = ilan.find("td", class_="listing-title").text.strip()
                        yil = ilan.find("td", class_="listing-year").text.strip()
                        km = ilan.find("td", class_="listing-km").text.strip().replace(".", "")
                        fiyat = ilan.find("td", class_="listing-price").text.strip().replace(" TL", "").replace(".", "")
                        il_ilce = ilan.find("td", class_="listing-location").text.strip()
                        ilan_url = "https://www.arabam.com" + ilan.find("a")["href"]

                        ilanlar.append([model, ilan_baslik, yil, km, fiyat, il_ilce, ilan_url])
                    except:
                        continue
                
                # Eğer ilan yoksa hata göster
                if not ilanlar:
                    st.warning("Filtrelere uygun ilan bulunamadı.")
                else:
                    # Veriyi tablo halinde göster
                    df = pd.DataFrame(ilanlar, columns=["Model", "İlan Başlığı", "Yıl", "Kilometre", "Fiyat", "İl/İlçe", "İlan URL"])
                    st.dataframe(df)
                    
                    # Excel dosyası olarak indirme butonu
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name="Arabam İlanları")
                    output.seek(0)
                    st.download_button(
                        label="📥 Verileri Excel olarak indir",
                        data=output,
                        file_name=f"{marka_secim}_{model_secim}_ilanlar.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
