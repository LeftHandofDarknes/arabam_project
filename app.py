import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io

# Streamlit başlık ve açıklama
st.title("Arabam.com Veri Toplayıcı")
st.write("Belirli kriterlere göre Arabam.com'dan ikinci el araç ilanlarını çekin ve analiz edin.")

# Kullanıcıdan araç seçimi
marka_model = st.text_input("Hangi marka/modeli aramak istersiniz?", "Volkswagen Passat 1.6 TDi BlueMotion")

# Sabit filtreler
MAX_YAS = 10  # 10 yaşından büyük olamaz
MAX_KM = 150000  # 150.000 km’den fazla olamaz
MAX_FIYAT = 1750000  # 1.750.000 TL’den pahalı olamaz

# Kullanıcı "Verileri Çek" butonuna basınca çalışacak kısım
if st.button("Verileri Çek"):
    # Arabam.com'da arama için uygun URL formatı
    query = marka_model.replace(" ", "-").lower()
    url = f"https://www.arabam.com/ikinci-el/otomobil/{query}?minYear=2015&maxkm=150000"

    # Web scraping (Sayfa isteği)
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Arabam.com’da ilanları çeken kod (XPath veya HTML yapısı değişebilir)
        ilanlar = soup.find_all("div", class_="listing")
        
        # Boş liste oluştur
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
        
        # Eğer ilan varsa ekrana yazdır
        if not df.empty:
            st.write(f"{len(df)} ilan bulundu:")
            st.dataframe(df)

            # Excel olarak indirme butonu
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

