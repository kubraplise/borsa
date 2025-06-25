from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

hisseler = ["THYAO", "KOZAL", "KOZAA", "BRLSM", "VESTL"]

def kurum_al_sat(hisse):
    url = f"https://bigpara.hurriyet.com.tr/borsa/hisseler/{hisse.lower()}/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    tablo = soup.find("table", class_="dataTable")
    return tablo.prettify() if tablo else "Veri bulunamadı."

@app.route("/", methods=["GET", "POST"])
def index():
    global hisseler
    yeni_hisse = ""
    if request.method == "POST":
        yeni_hisse = request.form.get("hisse")
        if yeni_hisse and yeni_hisse not in hisseler:
            hisseler.append(yeni_hisse)

    analizler = []
    for hisse in hisseler:
        try:
            data = yf.download(hisse + ".IS", period="7d", interval="1d")
            kapanis = data["Close"].dropna()
            rsi = (100 - (100 / (1 + (kapanis.pct_change().add(1).rolling(14).mean())))).iloc[-1]
            macd = kapanis.ewm(span=12).mean().iloc[-1] - kapanis.ewm(span=26).mean().iloc[-1]
            kurum = kurum_al_sat(hisse)
            analizler.append({
                "hisse": hisse,
                "rsi": round(rsi, 2),
                "macd": round(macd, 2),
                "kurum": kurum
            })
        except Exception as e:
            analizler.append({
                "hisse": hisse,
                "rsi": "Veri Yok",
                "macd": "Veri Yok",
                "kurum": "Hata: " + str(e)
            })

    return render_template("index.html", analizler=analizler)

if __name__ == "__main__":
    app.run(debug=True)