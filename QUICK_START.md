# 🚀 Quick Start Guide - MJ Solution Kiosk

Panduan cepat untuk setup dan menjalankan kiosk dalam 5 menit!

---

## ✅ Checklist Sebelum Mulai

- [ ] Python 3.8+ terinstall
- [ ] Webcam tersedia (laptop atau external)
- [ ] File assets sudah ada di folder `assets/`:
  - `idle-looping.mp4`
  - `hand-waving.webm`
  - `woman-speech.mp3`
- [ ] Internet connection (untuk download YOLO model pertama kali)

---

## 📦 Step 1: Install Dependencies (5 menit)

```bash
# 1. Buat virtual environment
python -m venv venv

# 2. Aktivasi venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install packages
pip install -r requirements.txt
```

**⏳ Note:** Instalasi torch bisa memakan waktu 5-10 menit tergantung koneksi internet.

---

## 🎥 Step 2: Test Camera (1 menit)

```bash
python helpers/camera_helper.py
```

Pastikan camera feed muncul. Jika error, coba ubah `CAMERA_INDEX` di `config/settings.py`.

---

## 📏 Step 3: Kalibrasi Distance (5 menit) **PENTING!**

```bash
python calibration_tool.py
```

**Instruksi:**
1. Berdiri di jarak **~5 meter** dari kamera
2. Tekan **'s'** untuk save measurement
3. Berdiri di jarak **~0.6 meter** dari kamera
4. Tekan **'s'** untuk save measurement
5. Tekan **'q'** untuk keluar

Tool akan memberikan **recommended thresholds**. Update di `config/settings.py`:

```python
DISTANCE_FAR = 150        # Ganti dengan nilai recommended
DISTANCE_NEAR = 300       # Ganti dengan nilai recommended
DISTANCE_VERY_NEAR = 500  # Ganti dengan nilai recommended
```

---

## 🎮 Step 4: Test Run (Development Mode)

```bash
python main_refactored.py
```

**Controls:**
- **ESC** atau **Q**: Keluar
- **F11**: Toggle fullscreen (saat di web interface)

**Debug Info** yang akan muncul:
- FPS counter (top-right)
- State info (top-left)
- Distance status
- Bounding box YOLO (hijau/kuning/orange)
- Bbox height (untuk verifikasi kalibrasi)

---

## 🧪 Test Scenarios

### Scenario 1: Idle to Detected
1. Jalankan aplikasi
2. Pastikan video `idle-looping.mp4` muncul
3. Berdiri di depan kamera (>5m)
4. Harus transition ke `hand-waving.webm`

### Scenario 2: Detected to Audio
1. Dari stage 2, mendekat ke kamera (<5m)
2. Video tetap `hand-waving.webm`
3. Mendekat lagi (≤0.6m)
4. Harus play audio `woman-speech.mp3`

### Scenario 3: Audio to Web
1. Dari stage 3, tetap di jarak ≤0.6m
2. Setelah beberapa detik, browser harus terbuka
3. URL: https://mjsolution.co.id/our-product/

### Scenario 4: Web to Reset
1. Dari stage 4, jangan gerakkan mouse
2. Setelah 15 detik, countdown muncul (5 detik)
3. Setelah countdown habis, kembali ke stage 1

### Scenario 5: Stage 2 Timeout
1. Dari stage 2, menjauh dari kamera
2. Countdown 10 detik muncul
3. Setelah habis, kembali ke stage 1

---

## ⚙️ Step 5: Production Setup

### Edit Config untuk Production
```python
# config/settings.py

DEBUG_MODE = False           # Matikan debug info
FULLSCREEN_MODE = True       # Aktifkan fullscreen
SHOW_FPS = False             # Hide FPS counter
```

### Jalankan
```bash
python main_refactored.py
```

---

## 🐛 Troubleshooting

### 1. ❌ "Cannot open camera at index 0"
```python
# Edit config/settings.py
CAMERA_INDEX = 1  # Coba 1, 2, atau 3
```

### 2. ❌ YOLO download gagal
```bash
# Manual download
pip install gdown
gdown https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt
```

### 3. ❌ Video tidak muncul
- Check file ada di `assets/`
- Check path di `config/settings.py`
- Coba format lain (.mp4 atau .avi)

### 4. ❌ Audio tidak keluar
- Check volume sistem
- Test audio file manual: `vlc assets/woman-speech.mp3`
- Coba format lain (.wav atau .ogg)

### 5. ❌ Distance detection tidak akurat
- **KALIBRASI LAGI!** Jalankan `calibration_tool.py`
- Pastikan lighting cukup
- Pastikan background tidak terlalu ramai

### 6. ❌ Web tidak fullscreen
```bash
# Saat browser terbuka, tekan F11 manual
# Atau install browser extension untuk auto-fullscreen
```

### 7. ❌ Aplikasi lambat (low FPS)
```python
# config/settings.py
CAMERA_WIDTH = 640   # Kurangi resolusi
CAMERA_HEIGHT = 480
```

---

## 📊 Performance Tips

### Untuk Laptop Development:
- Gunakan resolusi rendah (640x480)
- YOLO device = "cpu" (default)
- Close aplikasi lain

### Untuk Production (PC/Workstation):
- Gunakan resolusi tinggi (1920x1080)
- Jika punya GPU: `YOLO_DEVICE = "cuda"`
- Install CUDA toolkit untuk GPU acceleration

---

## 🎯 Next Steps

1. ✅ Kalibrasi distance thresholds
2. ✅ Test semua 4 stages
3. ✅ Adjust timeouts sesuai kebutuhan
4. ✅ Setup autostart (lihat README_KIOSK.md)
5. ✅ Deploy ke kiosk box production

---

## 📞 Need Help?

Check detailed documentation di `README_KIOSK.md` atau lihat logs di `kiosk_activity.log`.

**Common Issues:**
- Distance tidak akurat → **KALIBRASI!**
- Video lag → Kurangi resolusi camera
- Audio delay → Gunakan .wav format

---

## 🎉 Selamat!

Jika semua scenario test berhasil, kiosk Anda siap untuk production! 🚀

```
Stage 1 ✅ → Stage 2 ✅ → Stage 3 ✅ → Stage 4 ✅ → Reset ✅
```