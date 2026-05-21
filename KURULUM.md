# Fis Takip — Kurulum (4 Adım)

---

## ADIM 1 — Cloudinary (fotoğraf depolama)

1. https://cloudinary.com → **"Sign Up For Free"**
2. Email + şifre ile kayıt ol, kredi kartı istemiyor
3. Giriş yaptıktan sonra Dashboard açılır:
   - **Cloud Name** → kopyala
   - **API Key** → kopyala
   - **API Secret** → kopyala
4. Bu 3 değeri bir yere kaydet, birazdan lazım

---

## ADIM 2 — Google Apps Script (gider tablosu)

1. **drive.google.com** → Yeni → Google E-Tablolar (boş)
2. Tablonun adını "Gider Takibi" yap
3. Üst menü: **Uzantılar → Apps Script**
4. Soldaki `Code.gs` içindeki her şeyi sil
5. `apps_script.js` dosyasının tüm içeriğini yapıştır
6. Diskete tıklayarak kaydet (Ctrl+S)
7. Mavi **"Deploy"** butonu → **"New deployment"**
   - Type: **Web app**
   - Execute as: **Me**
   - Who has access: **Anyone**
   - **Deploy** → izin ver → **URL'yi kopyala**
8. Bu URL'yi kaydet (`APPS_SCRIPT_URL` olacak)

---

## ADIM 3 — GitHub'a yükle

1. **github.com** → Hesap aç (varsa giriş yap)
2. Sağ üst **"+"** → **"New repository"**
   - Repository name: `fis-takip`
   - **Public** seç
   - **"Create repository"**
3. **"uploading an existing file"** linkine tıkla
4. Şu dosyaları sürükle-bırak yükle:
   - `app.py`
   - `Procfile`
   - `requirements.txt`
   - `.gitignore`
   - `apps_script.js`
5. `templates` klasörü için:
   - Yine "uploading an existing file"
   - Dosyayı sürükle ama ismi `templates/index.html` olarak yaz
6. **"Commit changes"** → bitti

---

## ADIM 4 — Render.com'a deploy

1. **render.com** → **"Get Started"** → GitHub ile giriş yap
2. **"New +"** → **"Web Service"**
3. GitHub reposunu seç (`fis-takip`)
4. Ayarlar:
   - Name: `fis-takip`
   - Region: Frankfurt (Avrupa)
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Aşağıda **"Environment Variables"** bölümü:

| Key | Value |
|-----|-------|
| `ANTHROPIC_API_KEY` | Anthropic'ten aldığın key |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary'den kopyaladığın |
| `CLOUDINARY_API_KEY` | Cloudinary'den kopyaladığın |
| `CLOUDINARY_API_SECRET` | Cloudinary'den kopyaladığın |
| `APPS_SCRIPT_URL` | Apps Script'ten kopyaladığın URL |
| `APPS_SCRIPT_TOKEN` | `fistakip2024` (veya kendi belirlediğin) |

6. **"Create Web Service"** → 2-3 dakika bekle
7. Render sana bir URL verir:
   `https://fis-takip-xxxx.onrender.com`
   
   → Bu URL'yi telefonuna kaydet, tarayıcıdan aç, kullanmaya başla!

---

## Notlar

- Render ücretsiz planda uygulama 15 dk kullanılmazsa uyuyor.
  İlk açılışta 30 sn beklemen gerekebilir.
- Fotoğraflar Cloudinary'de, giderler Google Sheets'te saklanır.
- Google Sheets'i istediğin zaman drive.google.com'dan açabilirsin.
