import csv
import html
import json
import os
import shutil
import urllib.request
from datetime import datetime, timedelta

API_KEY = os.environ["EVDS_API_KEY"].strip()

end_dt = datetime.utcnow() + timedelta(hours=3)
start_dt = end_dt - timedelta(days=90)

url = (
    "https://evds3.tcmb.gov.tr/igmevdsms-dis/"
    "series=TP.TRY.MT02-TP.TRY.MT04"
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

valid_rows = [
    r for r in items
    if r.get("Tarih") and (r.get("TP_TRY_MT02") is not None or r.get("TP_TRY_MT04") is not None)
]
valid_rows.sort(key=parse_date, reverse=True)

headers = [
    "Tarih",
    "3 Aya Kadar Vadeli TL Mevduat (Akım, %)",
    "1 Yıla Kadar Vadeli TL Mevduat (Akım, %)",
]

with open("mevduat.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    for r in valid_rows:
        writer.writerow([
            r.get("Tarih", ""),
            r.get("TP_TRY_MT02", ""),
            r.get("TP_TRY_MT04", ""),
        ])

os.makedirs("_site", exist_ok=True)
shutil.copy("mevduat.csv", "_site/mevduat.csv")

rows_html = "\n".join(
    f"<tr><td>{html.escape(str(r.get('Tarih', '')))}</td>"
    f"<td>{html.escape(str(r.get('TP_TRY_MT02', '')))}</td>"
    f"<td>{html.escape(str(r.get('TP_TRY_MT04', '')))}</td></tr>"
    for r in valid_rows
)

html_doc = f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>TCMB EVDS Mevduat Faiz Oranları</title>
</head>
<body>
  <h1>TCMB EVDS TL Mevduat Faiz Oranları (Akım, %)</h1>
  <table border="1" cellpadding="6" cellspacing="0">
    <thead>
      <tr>
        <th>{headers[0]}</th>
        <th>{headers[1]}</th>
        <th>{headers[2]}</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</body>
</html>
"""

with open("_site/index.html", "w", encoding="utf-8") as f:
    f.write(html_doc)
