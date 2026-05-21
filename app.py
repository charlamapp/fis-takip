import os
import json
from datetime import datetime

import anthropic
import requests
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY")
APPS_SCRIPT_URL    = os.getenv("APPS_SCRIPT_URL")
APPS_SCRIPT_TOKEN  = os.getenv("APPS_SCRIPT_TOKEN", "fistakip2024")

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key    = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure     = True,
)


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data    = request.get_json()
    img_b64 = data.get("image", "").split(",")[-1]

    if not img_b64:
        return jsonify({"error": "Görüntü bulunamadı"}), 400
    if not ANTHROPIC_API_KEY:
        return jsonify({"error": "ANTHROPIC_API_KEY eksik"}), 500

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64},
                },
                {
                    "type": "text",
                    "text": (
                        "Bu fiş görüntüsünü analiz et. "
                        "SADECE şu JSON formatını döndür:\n"
                        '{"tarih":"GG.AA.YYYY","magaza":"mağaza adı",'
                        '"toplam":"sadece rakam örn 125.50",'
                        '"kategori":"Market|Restoran/Kafe|Akaryakıt|Eczane|Giyim|Elektronik|Ulaşım|Eğlence|Diğer",'
                        '"notlar":"varsa önemli not max 60 karakter"}\n'
                        "Tarih bulunamazsa bugünün tarihini kullan."
                    ),
                },
            ],
        }],
    )

    text = msg.content[0].text.strip()
    if "```" in text:
        text = text.split("```")[1].lstrip("json").strip()
    try:
        result = json.loads(text)
    except Exception:
        result = {
            "tarih"    : datetime.now().strftime("%d.%m.%Y"),
            "magaza"   : "",
            "toplam"   : "",
            "kategori" : "Diğer",
            "notlar"   : "Otomatik okuma başarısız, manuel girin",
        }
    return jsonify(result)


@app.route("/save", methods=["POST"])
def save():
    data    = request.get_json()
    receipt = data.get("receipt", {})
    img_b64 = data.get("image", "").split(",")[-1]

    if not img_b64:
        return jsonify({"error": "Görüntü yok"}), 400

    # 1. Cloudinary'e yükle
    tarih_safe  = receipt.get("tarih", datetime.now().strftime("%d.%m.%Y")).replace(".", "-")
    magaza_safe = receipt.get("magaza", "fis")[:20].replace(" ", "_").replace("/", "-")
    ts          = datetime.now().strftime("%H%M%S")
    public_id   = f"fislerim/fis_{tarih_safe}_{magaza_safe}_{ts}"

    try:
        upload  = cloudinary.uploader.upload(
            "data:image/jpeg;base64," + img_b64,
            public_id = public_id,
        )
        foto_url = upload["secure_url"]
    except Exception as e:
        return jsonify({"error": f"Cloudinary hatası: {e}"}), 500

    # 2. Apps Script'e gönder → Sheets'e yazar
    if not APPS_SCRIPT_URL:
        return jsonify({"error": "APPS_SCRIPT_URL tanımlı değil"}), 500

    try:
        resp = requests.post(
            APPS_SCRIPT_URL,
            json={
                "token"   : APPS_SCRIPT_TOKEN,
                "tarih"   : receipt.get("tarih", ""),
                "magaza"  : receipt.get("magaza", ""),
                "toplam"  : receipt.get("toplam", ""),
                "kategori": receipt.get("kategori", ""),
                "notlar"  : receipt.get("notlar", ""),
                "foto"    : foto_url,
                "eklenme" : datetime.now().strftime("%d.%m.%Y %H:%M"),
            },
            timeout=10,
        )
    except Exception as e:
        return jsonify({"error": f"Sheets hatası: {e}"}), 500

    return jsonify({"success": True, "link": foto_url})


@app.route("/expenses")
def expenses():
    if not APPS_SCRIPT_URL:
        return jsonify({"items": [], "total": 0})
    try:
        res  = requests.get(
            APPS_SCRIPT_URL,
            params={"token": APPS_SCRIPT_TOKEN},
            timeout=10,
        )
        rows = res.json()
        if isinstance(rows, list):
            rows.reverse()
        else:
            rows = []
    except Exception:
        rows = []

    total = sum(_parse(r.get("toplam", "0")) for r in rows)
    return jsonify({"items": rows, "total": round(total, 2)})


def _parse(s):
    try:
        return float(str(s).replace(",", ".").replace(" ", ""))
    except Exception:
        return 0.0


if __name__ == "__main__":
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close()
    except Exception:
        ip = "localhost"
    print(f"\n  Fis Takip → http://{ip}:8080\n")
    app.run(host="0.0.0.0", port=8080, debug=False)
