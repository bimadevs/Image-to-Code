import streamlit as st
import pathlib
from PIL import Image
import google.generativeai as genai
import logging

# Konfigurasi pencatatan
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Konfigurasi API key langsung di dalam skrip
API_KEY = 'AIzaSyDvln1q95RRWxaER0fSMlqoaWsA1UU6lvs'  # Silakan ganti dengan API KEY Anda
genai.configure(api_key=API_KEY)

# Konfigurasi generasi
konfigurasi_generasi = {
    "temperature": 0.7,
    "top_p": 0.85,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Pengaturan keamanan
pengaturan_keamanan = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Nama model
NAMA_MODEL = "gemini-1.5-pro-latest"

# Pilihan kerangka kerja
kerangka_kerja = "Tailwind"

# Buat model
model = genai.GenerativeModel(
    model_name=NAMA_MODEL,
    safety_settings=pengaturan_keamanan,
    generation_config=konfigurasi_generasi,
)

# Mulai sesi chat
sesi_chat = model.start_chat(history=[])

# Fungsi untuk mengirim pesan ke model
def kirim_pesan_ke_model(pesan, jalur_gambar):
    try:
        input_gambar = {
            'mime_type': 'image/jpeg',
            'data': pathlib.Path(jalur_gambar).read_bytes()
        }
        respon = sesi_chat.send_message([pesan, input_gambar])
        return respon.text
    except Exception as e:
        logger.error(f"Kesalahan saat mengirim pesan: {e}")
        st.error(f"Terjadi kesalahan saat memproses gambar: {e}")
        return ""

# Aplikasi Streamlit utama
st.set_page_config(
    page_title="Konversi UI ke Kode", 
    page_icon="💻", 
    layout="wide"
)

def main():
    st.title("Konversi Tangkapan Layar UI Menjadi Kode Website 🖼️➡️💻")
    st.markdown("### Ubah tangkapan layar UI menjadi HTML responsif")

    # Pilih kerangka kerja
    kerangka_kerja_dipilih = st.selectbox(
        "Pilih Kerangka Kerja CSS", 
        ["Tailwind", "Bootstrap", "Bulma", "Foundation"]
    )

    # Unggah berkas gambar
    berkas_unggahan = st.file_uploader(
        "Unggah Tangkapan Layar UI", 
        type=["jpg", "jpeg", "png"],
        help="Unggah tangkapan layar UI yang ingin diubah menjadi kode"
    )

    if berkas_unggahan is not None:
        try:
            # Muat dan tampilkan gambar
            gambar = Image.open(berkas_unggahan)
            
            # Konversi ke RGB jika perlu
            if gambar.mode == 'RGBA':
                gambar = gambar.convert('RGB')

            # Simpan gambar sementara
            jalur_gambar_sementara = pathlib.Path("gambar_sementara.jpg")
            gambar.save(jalur_gambar_sementara, format="JPEG")

            # Tampilkan gambar
            st.image(gambar, caption='Gambar Yang Diunggah.', use_column_width=True)

            # Tombol generasi
            if st.button("Buat Kode!"):
                st.write("🧑‍💻 Menganalisis Antarmuka Pengguna...")
                
                # Deskripsi UI
                prompt_deskripsi = "Jelaskan antarmuka pengguna ini secara detail. Sebutkan elemen UI dengan nama dan kotak pembatas dalam format: [nama objek (y_min, x_min, y_max, x_max)]. Jelaskan warna dan tata letak."
                deskripsi = kirim_pesan_ke_model(prompt_deskripsi, jalur_gambar_sementara)
                st.write(deskripsi)

                # Perbaiki deskripsi
                st.write("🔍 Menyempurnakan deskripsi...")
                prompt_perbaikan = f"Validasi dan perbaiki deskripsi antarmuka pengguna ini. Bandingkan dengan gambar asli untuk akurasi: {deskripsi}"
                deskripsi_disempurnakan = kirim_pesan_ke_model(prompt_perbaikan, jalur_gambar_sementara)
                
                # Buat HTML
                st.write("🛠️ Membuat website responsif...")
                prompt_html = f"Buat HTML responsif menggunakan CSS {kerangka_kerja_dipilih}. Cocokkan warna dan tata letak UI asli secara tepat. Tanpa komentar. HTML murni dengan CSS inline. Deskripsi: {deskripsi_disempurnakan}"
                html_awal = kirim_pesan_ke_model(prompt_html, jalur_gambar_sementara)
                
                # Tampilkan kode HTML
                st.code(html_awal, language='html')
                
                # Simpan berkas HTML
                with open("ui_dihasilkan.html", "w", encoding='utf-8') as f:
                    f.write(html_awal)
                
                # Tombol unduh
                st.download_button(
                    label="Unduh HTML", 
                    data=html_awal, 
                    file_name="ui_dihasilkan.html", 
                    mime="text/html"
                )

        except Exception as e:
            logger.error(f"Kesalahan pemrosesan gambar: {e}")
            st.error(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
