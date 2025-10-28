# 🖥️ GUI Usage Guide - MJ Solution Kiosk

## 🎉 No More Command Line!

Sekarang Anda bisa menggunakan kiosk dengan **GUI yang user-friendly**!

---

## 🚀 Quick Start with GUI

### 1. Install Dependencies (One Time Only)
```bash
pip install -r requirements.txt
```

### 2. Run GUI
```bash
python kiosk_gui.py
```

**That's it!** 🎉 GUI akan terbuka dengan semua kontrol yang Anda butuhkan.

---

## 📋 GUI Features

### 🎯 **Quick Actions** (Top Section)

| Button | Function |
|--------|----------|
| ▶️ **START KIOSK** | Start/Stop kiosk application |
| 📹 **Detect Cameras** | Scan all cameras and show preview |
| 📏 **Calibrate Distance** | Launch calibration tool |
| 🧪 **Test Components** | Test all components (YOLO, camera, etc) |
| 🎬 **Check Media Files** | Verify all media files exist |
| 📝 **View Logs** | Open log file |

---

### ⚙️ **Settings Sections**

#### 1. Camera Settings
- **Camera Index**: Select camera (0=built-in, 1+=external)
- Auto-detect available cameras with "Detect Cameras" button

#### 2. Distance Calibration
- **FAR (>5m)**: Bbox height threshold
- **NEAR (<5m)**: Bbox height threshold  
- **VERY NEAR (≤0.6m)**: Bbox height threshold
- ⚠️ Use "Calibrate Distance" button first!

#### 3. Timeout Settings
- **Stage 2 Countdown**: When person leaves (5-30s)
- **Stage 3 Timeout**: No response timeout (10-60s)
- **Stage 4 Idle**: No interaction timeout (10-60s)
- **Stage 4 Countdown**: Final countdown before reset (3-20s)

#### 4. Advanced Settings
- **Web URL**: Catalog website URL
- **Fullscreen Mode**: Enable for production
- **Debug Mode**: Show YOLO boxes, FPS, etc.

---

## 📖 Step-by-Step Usage

### 🎬 **First Time Setup**

1. **Launch GUI**
   ```bash
   python kiosk_gui.py
   ```

2. **Detect Cameras**
   - Click "📹 Detect Cameras"
   - Preview semua camera
   - Catat index webcam eksternal (biasanya 1)
   - Update **Camera Index** di GUI

3. **Check Media Files**
   - Click "🎬 Check Media Files"
   - Pastikan semua 4 file ada:
     - ✅ `idle-looping.mp4`
     - ✅ `hand-waving.webm`
     - ✅ `woman-speech.mp3`
     - ✅ `thank-you.mp4` ← **BARU!**

4. **Calibrate Distance**
   - Click "📏 Calibrate Distance"
   - Tool akan terbuka
   - Ikuti instruksi:
     - Berdiri 5m → tekan 's'
     - Berdiri 0.6m → tekan 's'
   - Tool akan kasih recommended values
   - Update nilai di GUI

5. **Test Components**
   - Click "🧪 Test Components"
   - Pastikan semua test PASSED ✅

6. **Save Configuration**
   - Click "💾 Save Configuration"
   - Settings disimpan ke `config/kiosk_config.json`

7. **Start Kiosk!**
   - Click "▶️ START KIOSK"
   - Kiosk akan running!
   - Click "⏹️ STOP KIOSK" untuk stop

---

## 🔄 Updated Flow (dengan Thank You Video)

```
Stage 1: IDLE
  ↓ person detected
Stage 2: DETECTED  
  ↓ distance ≤0.6m
Stage 3: AUDIO
  ↓ confirmed very near
Stage 4: WEB INTERFACE
  ↓ idle timeout + countdown
  ↓ sensor check:
  ├─ Person detected? → Back to Stage 1
  └─ No person? ↓
Stage 5: THANK YOU VIDEO ← NEW!
  ↓ video finished
RESET → Back to Stage 1
```

---

## 🎥 Media Files Required

| File | Stage | Description |
|------|-------|-------------|
| `idle-looping.mp4` | Stage 1 | Loop saat idle (>5m) |
| `hand-waving.webm` | Stage 2 | Attract attention (<5m) |
| `woman-speech.mp3` | Stage 3 | Audio prompt (≤0.6m) |
| `thank-you.mp4` | Stage 5 | **NEW!** Thank you sebelum reset |

**Semua file harus ada di folder `assets/`**

---

## 💡 Tips

### Development Mode
```
✅ Debug Mode: ON
✅ Fullscreen: OFF
```
- Lihat YOLO boxes
- Lihat FPS
- Lihat distance info
- Easy untuk testing

### Production Mode
```
❌ Debug Mode: OFF
✅ Fullscreen: ON
```
- Clean display
- No technical info
- Fullscreen web
- Professional look

---

## 🐛 Troubleshooting

### ❌ GUI tidak muncul
```bash
# Install tkinter
# Ubuntu/Debian:
sudo apt-get install python3-tk

# Windows: Biasanya sudah include
```

### ❌ Camera tidak detect
- Click "📹 Detect Cameras"
- Pastikan webcam terpasang
- Close aplikasi lain yang pakai camera (Zoom, Teams)

### ❌ YOLO error
- Click "🧪 Test Components"
- Lihat error message
- Run: `python -m utility.fix_yolo_install`

### ❌ Media files missing
- Click "🎬 Check Media Files"
- Lihat file mana yang missing
- Add file ke `assets/` folder

### ❌ Distance tidak akurat
- Click "📏 Calibrate Distance"
- Kalibrasi ulang dengan teliti
- Update nilai di GUI
- Click "💾 Save Configuration"

---

## 📁 Configuration File

Settings disimpan di: `config/kiosk_config.json`

Example:
```json
{
    "camera_index": 1,
    "distance_far": 150,
    "distance_near": 300,
    "distance_very_near": 500,
    "stage2_countdown": 10,
    "stage3_timeout": 15,
    "stage4_idle_timeout": 15,
    "stage4_countdown": 5,
    "web_url": "https://mjsolution.co.id/our-product/",
    "fullscreen": true,
    "debug_mode": false
}
```

---

## 🎯 Keyboard Shortcuts (saat kiosk running)

| Key | Action |
|-----|--------|
| **ESC** | Stop kiosk |
| **Q** | Stop kiosk |
| **F11** | Toggle fullscreen (di web) |

---

## 🚀 Production Deployment

### 1. Setup
- Install semua dependencies
- Add semua media files
- Calibrate distance
- Test semua stages

### 2. Configure
- Set **Fullscreen Mode**: ON
- Set **Debug Mode**: OFF
- Set correct **Camera Index**
- Save configuration

### 3. Run
```bash
python kiosk_gui.py
```
- Click "▶️ START KIOSK"
- Minimize GUI window
- Kiosk fullscreen di monitor utama

### 4. Autostart (Optional)
Create shortcut/batch file:

**Windows:** `start_kiosk.bat`
```batch
@echo off
cd C:\path\to\kiosk-motion-detector
python kiosk_gui.py
```

**Linux:** `start_kiosk.sh`
```bash
#!/bin/bash
cd /path/to/kiosk-motion-detector
python kiosk_gui.py
```

Add to startup folder/crontab

---

## ✅ Checklist Before Production

- [ ] All media files ada (4 files)
- [ ] Camera detected (correct index)
- [ ] Distance calibrated
- [ ] All components tested (passed)
- [ ] Web URL correct
- [ ] Fullscreen mode ON
- [ ] Debug mode OFF
- [ ] Test all 5 stages manually
- [ ] Autostart configured

---

## 🎉 Advantages of GUI

✅ **No command line** - User friendly  
✅ **Visual configuration** - Easy to adjust  
✅ **One-click actions** - Fast testing  
✅ **Real-time status** - See what's happening  
✅ **Built-in tools** - All tools integrated  
✅ **Save/Load config** - Persistent settings  
✅ **Error messages** - Clear feedback  

---

## 📞 Need Help?

1. Click "📝 View Logs" untuk lihat error
2. Click "🧪 Test Components" untuk diagnostic
3. Check `kiosk_activity.log` file
4. Contact developer with:
   - Screenshot GUI
   - Log file
   - Error message

---

**Enjoy your user-friendly kiosk! 🎉**