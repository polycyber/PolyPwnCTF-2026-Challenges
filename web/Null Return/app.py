from flask import Flask, request, jsonify, render_template
import subprocess
import os
from datetime import datetime

app = Flask(__name__)

# Restricted env: only cat, ls, grep are available via PATH
RESTRICTED_ENV = {
    "PATH": "/usr/local/restricted",
    "HOME": "/tmp",
}

# Whitelist of allowed "NeuralOS" commands mapped to real linux commands
COMMANDS = {
    "help": None,
    "status": None,
    "date": None,
    "list": None,
    "read": None,
    "search": None,
    "clear": None,
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/terminal", methods=["POST"])
def terminal():
    data = request.get_json()
    user_input = data.get("command", "").strip()

    if not user_input:
        return jsonify({"output": "ERR: AUCUN SIGNAL D'ENTRÉE DÉTECTÉ"})

    parts = user_input.split(None, 1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if command == "aide" or command == "help":
        output = (
            "══════════════════════════════════════════════════\n"
            "       NeuralOS v0.2.1 - MENU D'AIDE\n"
            "══════════════════════════════════════════════════\n"
            "  aide           - Afficher ce message\n"
            "  statut         - Diagnostics systeme\n"
            "  date           - Horodatage actuel\n"
            "  liste          - Lister les dossiers du labo\n"
            "  lire <fich>    - Lire un dossier du labo\n"
            "  chercher <q>   - Chercher un mot dans les logs\n"
            "  effacer        - Effacer le terminal\n"
            "══════════════════════════════════════════════════"
        )

    elif command == "statut" or command == "status":
        output = (
            "DIAGNOSTICS SYSTÈME\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Cœur Neural ........... HORS LIGNE\n"
            "Banques Mémoire ....... 43% CORROMPUES\n"
            "Réseau ................ ISOLÉ\n"
            "Accès Labo 7 .......... SCELLÉ\n"
            "Dr. Voss .............. STATUT INCONNU\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠ ANOMALIE CRITIQUE DÉTECTÉE — SECTEUR 7"
        )

    elif command == "date":
        future = datetime.now().replace(year=datetime.now().year + 10)
        output = f"HORODATAGE: {future.strftime('%Y-%m-%d %H:%M:%S')} UTC+2"

    elif command == "liste" or command == "list":
        # Run ls on the records directory
        try:
            result = subprocess.run(
                ["ls", "-1", "/app/records"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            files = result.stdout.strip()
            output = "DOSSIERS DU LABORATOIRE DISPONIBLES\n" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for i, f in enumerate(files.splitlines(), 1):
                output += f"[{i:03d}] {f}\n"
        except Exception:
            output = "ERR: IMPOSSIBLE D'ACCÉDER AU STOCKAGE"

    elif command == "lire" or command == "read":
        if not args:
            output = "USAGE: lire <fichier>\nLire un dossier du laboratoire."
        else:
            # Direct cat with user input — vulnerable to command injection!
            try:
                result = subprocess.run(
                    f"cat /app/records/{args}",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    env=RESTRICTED_ENV,
                )
                stdout = result.stdout.strip()
                stderr = result.stderr.strip()
                if stdout:
                    output = stdout
                elif stderr:
                    output = f"ERR: {stderr}"
                else:
                    output = "ERR: DOSSIER INTROUVABLE OU VIDE"
            except subprocess.TimeoutExpired:
                output = "ERR: OPÉRATION EXPIRÉE"
            except Exception:
                output = "ERR: DYSFONCTIONNEMENT SYSTÈME"

    elif command == "chercher" or command == "search":
        if not args:
            output = "USAGE: chercher <mot-clé>\nRechercher dans les dossiers du labo."
        else:
            # grep with user input — also vulnerable to command injection!
            try:
                result = subprocess.run(
                    f'grep -ri "{args}" /app/records/',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    env=RESTRICTED_ENV,
                )
                stdout = result.stdout.strip()
                if stdout:
                    if len(stdout) > 4096:
                        stdout = stdout[:4096] + "\n[SORTIE TRONQUÉE]"
                    output = stdout
                else:
                    output = f'AUCUN DOSSIER CORRESPONDANT À "{args}"'
            except subprocess.TimeoutExpired:
                output = "ERR: RECHERCHE EXPIRÉE"
            except Exception:
                output = "ERR: DYSFONCTIONNEMENT SYSTÈME"

    elif command == "effacer" or command == "clear":
        output = "__CLEAR__"

    else:
        output = (
            f'ERR: COMMANDE INCONNUE "{command.upper()}"\n'
            'Tapez "aide" pour les commandes disponibles.'
        )

    return jsonify({"output": output})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
