"""Capturas de tela do site em 1280px e 390px, com erros de console."""
import sys, threading, http.server, functools, socketserver
from pathlib import Path
from playwright.sync_api import sync_playwright

import os
PUB = Path(os.environ.get("SITE_DIR") or Path(__file__).resolve().parent.parent / "public")
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/capturas")
OUT.mkdir(parents=True, exist_ok=True)
PAGINAS = sys.argv[2].split(",") if len(sys.argv) > 2 else [
    "index.html", "obras/esquina.html", "obras/turbina.html", "obras/mar-sobre-mar.html",
    "radio.html", "indice.html", "exposicoes.html", "textos.html", "sobre.html"]

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(PUB))
Handler.log_message = lambda *a: None
srv = socketserver.TCPServer(("127.0.0.1", 0), Handler)
porta = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as p:
    b = p.chromium.launch()
    for nome, vp in [("desk", {"width": 1280, "height": 860}), ("mob", {"width": 390, "height": 844})]:
        ctx = b.new_context(viewport=vp, device_scale_factor=1)
        ctx.route("**/*", lambda r: r.abort() if not r.request.url.startswith(f"http://127.0.0.1:{porta}") else r.continue_())
        for pg in PAGINAS:
            page = ctx.new_page()
            erros = []
            page.on("pageerror", lambda e: erros.append(str(e)))
            page.on("console", lambda m: erros.append(m.text) if m.type == "error" and "ERR_FAILED" not in m.text else None)
            page.goto(f"http://127.0.0.1:{porta}/{pg}")
            page.wait_for_timeout(500)
            arq = OUT / f"{nome}-{pg.replace('/', '_').replace('.html', '')}.png"
            page.screenshot(path=str(arq), full_page=True)
            larg = page.evaluate("document.documentElement.scrollWidth")
            print(nome, pg, "scrollWidth", larg, "erros:", [x for x in erros if "Failed to load resource" not in x])
            page.close()
        ctx.close()
    b.close()
srv.shutdown()
