"""Decodifica a saída salva de download_file_content (JSON com base64) para um arquivo."""
import json, base64, sys, pathlib
src, dest = sys.argv[1], pathlib.Path(sys.argv[2])
d = json.load(open(src))
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_bytes(base64.b64decode(d["content"]))
print(dest, d.get("mimeType"), dest.stat().st_size)
