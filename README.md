# Tokocrypto Trading Bot on Vercel (Serverless)

Bot trading otomatis gratis untuk Tokocrypto yang berjalan tanpa server terus-menerus (*serverless*). Menggunakan **Vercel Cron Jobs** untuk bangun setiap 15 menit, memeriksa pasar menggunakan indikator **RSI (Relative Strength Index)**, dan melakukan eksekusi order secara aman via API Tokocrypto.

---

## Fitur Utama
* **100% Gratis:** Berjalan di Vercel Free Tier dan GitHub gratis.
* **Keamanan Kredensial:** API Key disimpan aman di Environment Variables Vercel, bukan di kode GitHub.
* **Mode Simulasi (Dry Run):** Bot dapat disetel untuk berjalan secara virtual untuk menguji strategi tanpa uang asli.
* **Tanpa Setup Server Rumit:** Tidak perlu menyewa VPS atau membiarkan PC Anda menyala 24/7.

---

## Persiapan Sebelum Memulai

### 1. Dapatkan API Key Tokocrypto
1. Masuk ke akun Tokocrypto Anda.
2. Buka menu **Manajemen API** (API Management).
3. Buat API Key baru (misal diberi nama "Vercel Bot").
4. **PENTING (KEAMANAN):**
   * Centang **Enable Reading** (Wajib).
   * Centang **Enable Spot & Margin Trading** (Wajib untuk eksekusi trade).
   * **JANGAN centang** `Enable Withdrawals` (Demi keamanan dana Anda).
   * Karena Vercel menggunakan IP dinamis, pilih opsi **"Unrestricted (Less Secure)"** untuk akses IP.
5. Catat `API Key` dan `Secret Key` yang diberikan.

---

## Langkah 1: Simpan Kode di GitHub (Private Repository)
Sangat penting untuk menyimpan kode ini di repositori **Private** agar tidak ada orang lain yang melihat struktur Anda.

1. Masuk ke akun [GitHub](https://github.com/) Anda.
2. Buat repositori baru dengan mengklik **New**:
   * Nama Repositori: `tokocrypto-bot-vercel`
   * Pilih opsi **Private** (Sangat Wajib!).
   * Jangan centang "Add a README file" atau lainnya, biarkan kosong.
3. Hubungkan folder lokal Anda dan unggah kodenya menggunakan Git:
   ```bash
   cd C:\Users\lenovo\.gemini\antigravity\scratch\tokocrypto-bot-vercel
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin git@github.com:USERNAME_ANDA/tokocrypto-bot-vercel.git
   git push -u origin main
   ```

---

## Langkah 2: Deploy ke Vercel (Gratis)

1. Masuk ke akun [Vercel](https://vercel.com/) Anda (gunakan akun GitHub Anda agar mudah terintegrasi).
2. Klik tombol **Add New** lalu pilih **Project**.
3. Cari repositori **`tokocrypto-bot-vercel`** yang baru Anda buat di GitHub, lalu klik **Import**.
4. Pada bagian **Environment Variables**, masukkan variabel-variabel berikut (lihat `.env.example` sebagai acuan):
   * `TOKO_API_KEY` = *[API Key Tokocrypto Anda]*
   * `TOKO_SECRET_KEY` = *[Secret Key Tokocrypto Anda]*
   * `SYMBOL` = `BTC/BIDR` (atau koin lain pilihan Anda)
   * `TRADE_AMOUNT` = `0.0001` (jumlah koin yang ingin ditransaksikan per sinyal)
   * `DRY_RUN` = `True` (Ubah ke `False` jika Anda sudah yakin ingin menggunakan uang asli)
5. Klik **Deploy** dan tunggu proses selesai.

---

## Langkah 3: Mengaktifkan Jadwal Otomatis (Cron Job)

Vercel akan mendeteksi file `vercel.json` dan mendaftarkan Cron Job secara otomatis setelah deployment berhasil.
1. Masuk ke Dashboard Proyek Anda di Vercel.
2. Buka tab **Settings** -> **Cron Jobs**.
3. Anda akan melihat Cron Job terdaftar untuk mengarah ke `/api/cron` setiap 15 menit.
4. Anda bisa mengklik tombol **"Run"** secara manual pada baris cron tersebut untuk mengujinya secara instan.
5. Hasil log transaksi dapat dilihat langsung pada tab **Logs** di Vercel.

---

## Cara Menjalankan & Menguji Secara Lokal

Sebelum Anda deploy ke Vercel, Anda dapat menguji bot ini di komputer Anda sendiri:

1. Buat salinan file `.env.example` dan ubah namanya menjadi `.env`:
   ```bash
   cp .env.example .env
   ```
2. Isi `TOKO_API_KEY` dan `TOKO_SECRET_KEY` di file `.env` tersebut.
3. Instal dependensi library yang dibutuhkan:
   ```bash
   pip install ccxt python-dotenv
   ```
4. Jalankan script bot secara lokal:
   ```bash
   python api/cron.py
   ```
   *Anda akan melihat log output dari pembacaan harga, perhitungan RSI, dan simulasi order langsung di terminal Anda.*
