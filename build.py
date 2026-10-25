"""Build wealth-manager.html from template.html + data.json + india_min.json.

Usage:
  python build.py                      # uses existing data.json
  python build.py path/to/Tracker.xlsm # re-extracts data.json from the workbook first

The Investments tab is password protected: investment rows (Type or Category Investment) are taken out of the
page data and encrypted (AES-256-GCM, key from PBKDF2-SHA256). The password comes
from the WM_PASSWORD environment variable, or the first line of .wm_password, and must be
digits only (the page unlocks with a number pad that submits once all digits are in).
"""
import base64, json, os, secrets, subprocess, sys, pathlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

here = pathlib.Path(__file__).parent
ITERATIONS = 310_000

def password():
    pw = os.environ.get("WM_PASSWORD")
    f = here / ".wm_password"
    if not pw and f.exists():
        lines = f.read_text(encoding="utf-8").splitlines()
        pw = lines[0].strip() if lines else ""
    if not pw:
        sys.exit("No password set. Put it in .wm_password (one line) or set WM_PASSWORD, then run again.")
    if not pw.isdigit():
        sys.exit("The password must be digits only: the Investments tab unlocks with a number pad.")
    return pw

def seal(obj, pw):
    salt, iv = secrets.token_bytes(16), secrets.token_bytes(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS).derive(pw.encode())
    ct = AESGCM(key).encrypt(iv, json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode(), None)
    b64 = lambda b: base64.b64encode(b).decode()
    return {"s": b64(salt), "i": b64(iv), "c": b64(ct), "n": ITERATIONS, "l": len(pw), "k": len(obj["log"])}

if len(sys.argv) > 1:
    subprocess.check_call([sys.executable, str(here / "extract.py"), sys.argv[1], str(here / "data.json")])
pw = password()
data = json.loads((here / "data.json").read_text(encoding="utf-8"))
private = lambda x: x["t"] == "Investment" or x["c"] == "Investment"  # keep in step with isPrivate in template.html
secret = {"log": [x for x in data["log"] if private(x)], "inv": data["inv"]}
data["log"] = [x for x in data["log"] if not private(x)]
data["inv"] = []

t = (here / "template.html").read_text(encoding="utf-8")
html = t.replace("__DATA__", json.dumps(data, separators=(",", ":"), ensure_ascii=False)) \
        .replace("__VAULT__", json.dumps(seal(secret, pw))) \
        .replace("__MAP__", (here / "india_min.json").read_text(encoding="utf-8"))
# Standalone page: add the document shell the Artifact host normally supplies.
page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style></head><body>'
        + html + '</body></html>')
(here / "wealth-manager.html").write_text(page, encoding="utf-8")
print(f"Wrote wealth-manager.html ({len(secret['log'])} investment rows encrypted)")
