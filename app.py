import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

def fetch_data():
    url = "https://www.arabam.com/ikinci-el/otomobil"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Arabam.com ile bağlantı kurulamadı. Lütfen tekrar deneyin.")
        return None
    
    # Örnek veri yapısı (Arabam.com'dan gerçek veri çekilecek şekilde güncellenmeli)
    data = [
        {"Marka": "Volkswagen", "Model": "Passat", "Alt Model": "1.6 TDI BlueMotion", "İl": "İstanbul", "İlçe": "Kadıköy", "Fiyat": 1100000, "İlan Tarihi": "2024-01-10"},
        {"Marka": "BMW", "Model": "3 Serisi", "Alt Model": "320d", "İl": "Ankara", "İlçe": "Çankaya", "Fiyat": 1250000, "İlan Tarihi": "2023-12-05"},
        {"Marka": "Mercedes-Benz", "Model": "C Serisi", "Alt Model": "C200", "İl": "İzmir", "İlçe": "Bornova", "Fiyat": 1500000, "İlan Tarihi": "2024-02-15"}
    ]
    
    return pd.DataFrame(data)

def filter_data(df):
    # Tarih filtresi (son 120 gün içinde yayınlanan ilanlar)
    today = datetime.today()
    date_limit = today - timedelta(days=120)
    
    df["İlan Tarihi"] = pd.to_datetime(df["İlan Tarihi"], errors='coerce')
    df = df[df["İlan Tarihi"] >= date_limit]
    
    return df

def main():
    st.title("Arabam.com Veri Çekme Uygulaması")
    
    if st.button("ÇALIŞTIR"):
        st.info("Veriler çekiliyor, lütfen bekleyin...")
        df = fetch_data()
        
        if df is not None:
            df = filter_data(df)
            file_path = "arabam_data.xlsx"
            df.to_excel(file_path, index=False)
            
            st.success("Veri başarıyla çekildi ve kaydedildi!")
            st.download_button(
                label="Excel Dosyasını İndir",
                data=open(file_path, "rb").read(),
                file_name=file_path,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Veri çekme başarısız oldu. Lütfen tekrar deneyin.")

if __name__ == "__main__":
    main()
