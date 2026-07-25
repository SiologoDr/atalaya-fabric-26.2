#!/usr/bin/env python3
"""
dev.py - Prepara y sirve el resource pack para el servidor de pruebas.

Que hace:
  1. Empaqueta la carpeta resourcepack/ en run/pack-host/atalaya.zip
  2. Calcula el SHA1 y configura run/server.properties (para el auto-envio)
  3. Acepta el EULA en run/eula.txt
  4. Sirve el pack en http://127.0.0.1:8765

Uso:
  python dev.py           # empaqueta, configura y SIRVE el pack (deja esta terminal abierta)
  python dev.py --build   # solo empaqueta y configura (no sirve)

Flujo de desarrollo tipico:
  Terminal 1:  python dev.py            <- sirve el pack (dejar abierta)
  Terminal 2:  ./gradlew runServer      <- compila el plugin y arranca el server
  Conectate a  localhost  y acepta el pack.

Cada vez que cambies texturas del pack: vuelve a correr 'python dev.py'
(regenera el zip y el SHA1) y reinicia el servidor.

Nota: esto es para DESARROLLO (localhost). En un servidor real, hostea el pack
en una URL publica y pon resource-pack + resource-pack-sha1 en server.properties.
"""
import hashlib
import http.server
import os
import socketserver
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "resourcepack")
RUN = os.path.join(ROOT, "run")
HOST_DIR = os.path.join(RUN, "pack-host")
ZIP = os.path.join(HOST_DIR, "atalaya.zip")
PORT = 8765
URL = f"http://127.0.0.1:{PORT}/atalaya.zip"


def build_pack():
    if not os.path.isdir(SRC):
        sys.exit(f"[dev] No existe la carpeta '{SRC}'.")
    os.makedirs(HOST_DIR, exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(SRC):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, SRC))
    sha1 = hashlib.sha1(open(ZIP, "rb").read()).hexdigest()
    print(f"[dev] Pack empaquetado -> {ZIP}")
    print(f"[dev] SHA1: {sha1}")
    return sha1


def set_prop(lines, key, value):
    prefix = key + "="
    for i, line in enumerate(lines):
        if line.startswith(prefix):
            lines[i] = prefix + value
            return
    lines.append(prefix + value)


def configure(sha1):
    os.makedirs(RUN, exist_ok=True)
    # Acepta el EULA de Minecraft (necesario para correr el servidor).
    with open(os.path.join(RUN, "eula.txt"), "w", encoding="utf-8") as f:
        f.write("eula=true\n")

    sp = os.path.join(RUN, "server.properties")
    if not os.path.exists(sp):
        print("[dev] Aun no existe run/server.properties.")
        print("[dev] Corre './gradlew runServer' una vez, detenlo, y vuelve a correr 'python dev.py'.")
        return

    lines = open(sp, encoding="utf-8").read().splitlines()
    set_prop(lines, "resource-pack", URL)
    set_prop(lines, "resource-pack-sha1", sha1)
    set_prop(lines, "resource-pack-id", "11111111-2222-3333-4444-555555555555")
    set_prop(lines, "require-resource-pack", "false")
    set_prop(lines, "resource-pack-prompt",
             '{"text":"Instala el pack para ver el contenido de Atalaya"}')
    open(sp, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("[dev] run/server.properties configurado con el resource pack.")


def serve():
    os.chdir(HOST_DIR)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        print(f"[dev] Sirviendo el pack en {URL}")
        print("[dev] Deja esta terminal abierta. Ctrl+C para detener.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[dev] Host detenido.")


def main():
    sha1 = build_pack()
    configure(sha1)
    if "--build" in sys.argv:
        return
    serve()


if __name__ == "__main__":
    main()
