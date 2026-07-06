#!/usr/bin/env python3
"""
Check unique du stock — concu pour GitHub Actions.
Les identifiants email viennent des Secrets GitHub (variables d'environnement).
"""

import json
import os
import smtplib
import sys
import urllib.request
import urllib.error
from email.mime.text import MIMEText

PRODUCT_JSON_URL = "https://www.gens-du-monde.com/products/morocco-white-knit.js"
PRODUCT_URL = "https://www.gens-du-monde.com/products/morocco-white-knit"

# Taille voulue : "M", "L"... ou "" pour n'importe quelle taille
TAILLE_VOULUE = ""

# Mets True pour forcer un email de TEST, puis remets False apres.
TEST_MODE = False

# En-tetes navigateur complets pour eviter le blocage 403
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json,text/javascript,*/*;q=0.01",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Referer": PRODUCT_URL,
    "X-Requested-With": "XMLHttpRequest",
}


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


def recuperer_dispo():
    """Retourne la liste des tailles dispo, ou None si le site est inaccessible."""
    try:
        req = urllib.request.Request(PRODUCT_JSON_URL, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
        dispo = [v["title"] for v in data.get("variants", []) if v.get("available")]
        if TAILLE_VOULUE:
            dispo = [t for t in dispo if TAILLE_VOULUE.lower() in t.lower()]
        return dispo
    except urllib.error.HTTPError as e:
        print(f"Site inaccessible (HTTP {e.code}) - on reessaiera au prochain cycle.")
        return None
    except Exception as e:
        print(f"Erreur reseau : {e} - on reessaiera au prochain cycle.")
        return None


def main():
    if TEST_MODE:
        dispo = ["TEST"]
    else:
        dispo = recuperer_dispo()
        if dispo is None:
            # Site bloque/inaccessible : on sort proprement SANS echec.
            print("Aucune verification possible cette fois.")
            sys.exit(0)

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
