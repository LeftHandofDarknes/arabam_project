import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io

# Arabam.com'dan tüm marka ve modelleri çeken fonksiyon
@st.cache_data
def get_car_brands():
    url = "https://www.arabam.com/ikinci-el/otomobil"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        brand_options = []

        # Marka ve modellerin olduğu yeri bul
        brands = soup.find_all("a", class_="all-brands-list-link")
        for brand in brands:
            brand_name = brand.text.strip()
            brand_url = brand["href"]
            brand_options.append((brand_name, brand_url))

        return brand_options
    else:
        return []

# Marka ve modelleri çek
brand_model_list = get_car_brands()

# Başlık ve Açıklama
st.title("Arabam.com Veri Toplayıcı")
st.write("Belirli kriterlere göre Arabam.com'dan ikinci el araç ilanlarını çekin ve analiz edin.")

# Kullanıcıdan seçim yapmasını istemek
if brand_model_list:
    selected_brand = st.selectbox("Lütfen bir marka seçin:", [b[0] for b in brand_model_list])
    brand_url = dict(brand_model_list)[selected_brand]
else:
    st.error("Arabam.com'dan marka verisi çekilemedi. Lütfen sayfayı yenileyin.")

# Sabit Filtreler
MAX_YAS = 10  # 10 yaşından büyük olamaz
MAX_KM = 150000  # 150.000 km’den fazla olamaz
MAX_FIYAT = 1750000  # 1.750.000 TL’den pahalı olamaz

# "Verileri Çek" butonu
if st.button("Verileri Çek") and brand_url:
    url = f"https://www.arabam.com{brand_url}?minYear=2015&maxkm=150000"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        ilanlar = soup.find_all("div", class_="listing")
        
        veri_listesi = []
        for ilan in ilanlar:
            try:
                ilan_baslik = ilan.find("h2").text.strip()
                yil = int(ilan_baslik.split()[-1])  # Başlıktan yılı çek
                km = int(ilan.find("span", class_="km").text.replace(" km", "").replace(".", ""))
                fiyat = int(ilan.find("span", class_="price").text.replace(" TL", "").replace(".", ""))
                ilan_url = "https://www.arabam.com" + ilan.find("a")["href"]

                # Filtreleme
                if (2025 - yil) <= MAX_YAS and km <= MAX_KM and fiyat <= MAX_FIYAT:
                    veri_listesi.append([ilan_baslik, yil, km, fiyat, ilan_url])

            except Exception as e:
                continue  # Hata olursa atla

        # Veriyi Pandas DataFrame'e çevir
        df = pd.DataFrame(veri_listesi, columns=["İlan Başlığı", "Yıl", "Kilometre", "Fiyat (TL)", "İlan URL"])
        
        if not df.empty:
            st.write(f"{len(df)} ilan bulundu:")
            st.dataframe(df)

            # Excel indirme butonu
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Arabam Verileri")
                writer.close()

            st.download_button(
                label="Excel Olarak İndir",
                data=buffer,
                file_name="arabam_verileri.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:
            st.warning("Filtrelere uygun ilan bulunamadı.")

    else:
        st.error("Veri çekme başarısız. Arabam.com'un yapısını kontrol edin.")
