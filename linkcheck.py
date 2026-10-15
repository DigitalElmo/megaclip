"""Weekly link check for MegaClip: flags games whose link is dead or now sends you to a different website.
Run: python3 linkcheck.py [games.json path or URL]   (writes linkcheck-report.md next to where you run it; exit code 1 if anything needs a look)"""
import json, sys, urllib.request, urllib.error, concurrent.futures as cf
from urllib.parse import urlparse
from datetime import datetime

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36"
src = sys.argv[1] if len(sys.argv) > 1 else "games.json"
games = json.load(urllib.request.urlopen(src) if src.startswith("http") else open(src))


def site(u):
    h = (urlparse(u).hostname or "").lower()
    return ".".join(h.split(".")[-2:])


def check(g):
    try:
        r = urllib.request.urlopen(urllib.request.Request(g["url"], headers={"User-Agent": UA}), timeout=25)
        final, code = r.geturl(), r.status
    except urllib.error.HTTPError as e:
        final, code = e.geturl() or g["url"], e.code
    except Exception as e:
        return g, "dead", type(e).__name__
    if code in (404, 410) or code >= 500:
        return g, "dead", f"HTTP {code}"
    if site(final) != site(g["url"]):
        return g, "moved", f"now goes to {final}"
    if code >= 400:  # 401/403/429: often bot blocking, not a real problem
        return g, "blocked", f"HTTP {code} (may just be blocking robots)"
    return g, "ok", ""


with cf.ThreadPoolExecutor(24) as ex:
    res = list(ex.map(check, games))
bad = [r for r in res if r[1] in ("dead", "moved")]
soft = [r for r in res if r[1] == "blocked"]
out = [f"# MegaClip link check, {datetime.now():%d %b %Y %H:%M}", "",
       f"{len(games)} games checked: {len(games) - len(bad) - len(soft)} OK, {len(bad)} need a look, {len(soft)} blocked the robot (usually fine).", ""]
for title, rows in (("Need a look (dead, or now go to a different website)", bad), ("Blocked the robot (open them yourself to be sure)", soft)):
    if rows:
        out += [f"## {title}", ""] + [f"- **{g['name']}** ({s}): {why}  \n  {g['url']}" for g, s, why in rows] + [""]
open("linkcheck-report.md", "w").write("\n".join(out))
print(out[2])
sys.exit(1 if bad else 0)
