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

def css():
    st.markdown("""
    <style>
    /* Gaya Umum */
    .stApp {
        background-color: #0f172a;  /* Latar belakang gelap */
        color: #e2e8f0;  /* Warna teks terang */
    }
    
    /* Header */
    .header-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .header-container h1 {
        color: #4fd1c5;  /* Warna judul modern */
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .header-container h3 {
        color: #94a3b8;
        font-size: 1rem;
    }
    
    /* Tombol */
    .stButton>button {
        background-color: #4fd1c5 !important;
        color: #0f172a !important;
        border: none;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #2dd4bf !important;
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* File Uploader */
    .stFileUploader>div>div>div {
        background-color: #1e293b;
        border: 2px dashed #4fd1c5;
        border-radius: 15px;
        padding: 1rem;
        color: #94a3b8;
    }
    
    /* Kotak Kode */
    .stCodeBlock {
        background-color: #1e293b !important;
        border-radius: 15px;
        padding: 1rem;
        border: 1px solid #4fd1c5;
    }
    
    /* Animasi */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .animated-container {
        animation: fadeIn 0.5s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)


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
    css()
    
    st.title("Konversi Tangkapan Layar UI Menjadi Kode Website 🖼️➡️💻")
    st.markdown("### Ubah tangkapan layar UI menjadi HTML responsif")

    # Pilih kerangka kerja
    framework = st.selectbox(
        "Pilih Kerangka Kerja CSS", 
        ["Tailwind", "Bootstrap", "Bulma", "Vanilla CSS"]
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

                  # Generate HTML
                st.write("🛠️ Generating website...")
                html_prompt = f"Create an HTML file based on the following UI description, using the UI elements described in the previous response. Include {framework} CSS within the HTML file to style the elements. Make sure the colors used are the same as the original UI. The UI needs to be responsive and mobile-first, matching the original UI as closely as possible. Do not include any explanations or comments. Avoid using ```html. and ``` at the end. ONLY return the HTML code with inline CSS. Here is the refined description: {deskripsi_disempurnakan}"
                initial_html = send_message_to_model(html_prompt, jalur_gambar_sementara)
                st.code(initial_html, language='html')

                # Refine HTML
                st.write("🔧 Refining website...")
                refine_html_prompt = f"Validate the following HTML code based on the UI description and image and provide a refined version of the HTML code with {framework} CSS that improves accuracy, responsiveness, and adherence to the original design. ONLY return the refined HTML code with inline CSS. Avoid using ```html. and ``` at the end. Here is the initial HTML: {initial_html}"
                refined_html = send_message_to_model(refine_html_prompt, jalur_gambar_sementara)
                
                # Buat HTML
                # st.write("🛠️ Membuat website responsif...")
                # prompt_html = f"Buat HTML responsif menggunakan CSS {kerangka_kerja_dipilih}. Cocokkan warna dan tata letak UI asli secara tepat. Tanpa komentar dan penjelasan apa pun hanya berikan output code html saja, jangan pernah mengeluarkan output  ```html diawal dan ``` di akhir. HTML murni dengan CSS inline. Deskripsi: {deskripsi_disempurnakan}"
                # html_awal = kirim_pesan_ke_model(prompt_html, jalur_gambar_sementara)
                
                # Tampilkan kode HTML
                st.code(html_awal, language='html')
                
                # Simpan berkas HTML
                with open("ui_dihasilkan.html", "w", encoding='utf-8') as f:
                    f.write(refined_htm)
                
                # Tombol unduh
                st.download_button(
                    label="Unduh HTML", 
                    data=refined_htm, 
                    file_name="index.html", 
                    mime="text/html"
                )

        except Exception as e:
            logger.error(f"Kesalahan pemrosesan gambar: {e}")
            st.error(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
