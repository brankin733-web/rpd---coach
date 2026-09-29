#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
BUILD="2026-09-29-1645"
CACHE=f"rpd-coach-v1-2-0-{BUILD}"

def p(rel):
    q=ROOT/rel
    if not q.exists():
        raise SystemExit(f"Cache refresh patch missing: {q}")
    return q

# Force Chrome/PWA to recognise this as a new app shell and remove old caches.
sw=p("public/sw.js")
text=sw.read_text()
import re
text=re.sub(r'const CACHE="[^"]+";', f'const CACHE="{CACHE}";', text, count=1)
sw.write_text(text)

# Force a service-worker script URL change so an already-installed Chromebook PWA
# cannot remain pinned to the old v1.2 worker.
reg=p("components/ServiceWorkerRegistration.tsx")
text=reg.read_text()
text=text.replace(
    'navigator.serviceWorker.register("/sw.js", { updateViaCache: "none" }).catch(() => undefined);',
    f'''navigator.serviceWorker.register("/sw.js?v={BUILD}", {{ updateViaCache: "none" }}).then(async registration => {{
        await registration.update();
        if ("caches" in window) {{
          const keys=await caches.keys();
          await Promise.all(keys.filter(key=>key.startsWith("rpd-coach-")&&key!=="{CACHE}").map(key=>caches.delete(key)));
        }}
      }}).catch(() => undefined);'''
)
reg.write_text(text)

# Put an unmistakable build marker in the home UI so the current version can
# be visually verified instead of guessing from the appearance.
home=p("components/app/HomeScreen.tsx")
text=home.read_text()
marker='<span className="rpd-build-stamp">BUILD 29 SEP 2026 · LIVE</span>'
if marker not in text:
    text=text.replace(
        '<div className="app-wordmark home-brand"><b>RPD</b><span>COACH</span></div>',
        '<div><div className="app-wordmark home-brand"><b>RPD</b><span>COACH</span></div>'+marker+'</div>',
        1
    )
home.write_text(text)

css=p("app/globals.css")
text=css.read_text()
if "/* RPD current build stamp */" not in text:
    text += r'''

/* RPD current build stamp */
.rpd-build-stamp{display:block;margin-top:3px;font-size:7px;line-height:1;font-weight:950;letter-spacing:.9px;color:#ff5960;opacity:.9}
'''
    css.write_text(text)

print(f"RPD cache refresh applied: {CACHE}")
