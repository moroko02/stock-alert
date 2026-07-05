#!/usr/bin/env python3
"""
Check unique du stock — conçu pour GitHub Actions.
Les identifiants email viennent des Secrets GitHub (variables d'environnement).
"""

import json
import os
import smtplib
import urllib.request
from email.mime.text import MIMEText

PRODUCT_JSON_URL = "https://www.gens-du-monde.com/products/morocco-white-knit.js"
PRODUCT_URL = "https://www.gens-du-monde.com/products/morocco-white-knit"

# Taille voulue : "M", "L"... ou "" pour n'importe quelle taille
TAILLE_VOULUE = ""

# Mets True pour forcer un email de TEST, puis remets False apres.
TEST_MODE = True

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def envoyer_email(sujet: str, corps: str):
    exp = os.environ["EMAIL_FROM"]
    pwd = os.environ["EMAIL_PASS"].replace(" ", "")
    dest = os.environ.get("EMAIL_TO", exp)
    msg = MIMEText(corps, "plain", "utf-8")
    msg["Subject"] = sujet
    msg["From"] = exp
    msg["To"] = dest
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(exp, pwd)
        server.send_message(msg)
    print("Email envoye !")


def main():
    if TEST_MODE:
        dispo = ["TEST"]
    else:
        req = urllib.request.Request(PRODUCT_JSON_URL, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
        dispo = [v["title"] for v in data.get("variants", []) if v.get("available")]
        if TAILLE_VOULUE:
            dispo = [t for t in dispo if TAILLE_VOULUE.lower() in t.lower()]

    found = bool(dispo)
    if found:
        tailles = ", ".join(dispo)
        print(f"DISPONIBLE : {tailles}")
        envoyer_email(
            f"Morocco White Knit de retour en stock ({tailles}) !",
            f"Le tshirt est de nouveau disponible en : {tailles}\n\nFonce : {PRODUCT_URL}",
        )
    else:
        print("Toujours en rupture.")

    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a") as f:
            f.write(f"found={'true' if found else 'false'}\n")


if __name__ == "__main__":
    main()
