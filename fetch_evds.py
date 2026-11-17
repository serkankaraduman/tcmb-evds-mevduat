import csv
import json
import os
import urllib.request
from datetime import datetime, timedelta

API_KEY = os.environ["EVDS_API_KEY"].strip()

end_dt = datetime.utcnow() + timedelta(hours=3)
start_dt = end_dt - timedelta(days=90)

url = (
    "https://evds3.tcmb.gov.tr/igmevdsms-dis/"
    f"series=TP.TRY.MT02-TP.TRY.MT04"
    f"&startDate={start_dt.strftime('%d-%m-%Y')}"
    f"&endDate={end_dt.strftime('%d-%m-%Y')}"
    "&type=json"
)

req = urllib.request.Request(
    url,
    headers={
        "key": API_KEY,
        "User-Agent": "Mozilla/5.0",
    },
)

with urllib.request.urlopen(req, timeout=30) as resp:
    payload = json.loads(resp.read().decode("utf-8"))

items = payload.get("items", [])

def parse_date(row):
    return datetime.strptime(row["Tarih"], "%d-%m-%Y")

# Yalnızca verisi dolu satırları al ve en yeni tarih en üstte olacak şekilde sırala
valid_rows = [
    r for r in items
    if r.get("Tarih") and (r.get("TP_TRY_MT02") is not None or r.get("TP_TRY_MT04") is not None)
]
valid_rows.sort(key=parse_date, reverse=True)

with open("mevduat.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Tarih",
        "3 Aya Kadar Vadeli TL Mevduat (Akım, %)",
        "1 Yıla Kadar Vadeli TL Mevduat (Akım, %)",
    ])
    for r in valid_rows:
        writer.writerow([
            r.get("Tarih", ""),
            r.get("TP_TRY_MT02", ""),
            r.get("TP_TRY_MT04", ""),
        ])
