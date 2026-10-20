"""Per-game pages, category pages, the PC Ports (decomps) section, search data and the sitemap.
Called from arcade.py after index.html is built; returns the HTML of every page so arcade.py can hash inline scripts."""
import json, html, os, re, unicodedata

E = html.escape
SITE = "https://megaclip.games"
VA = "<script>window.va=window.va||function(){(window.vaq=window.vaq||[]).push(arguments)};</script><script defer src=\"/_vercel/insights/script.js\"></script>"
PHONE = {"yes": ("y", "&#128241; Works on a phone"), "no": ("n", "&#128187; Needs a computer"), "maybe": ("m", "&#128241;? Might work on a phone")}
STATUS = {"easy": ("Easy install", "#2e9e2e", "A ready-made PC version with a simple installer or launcher."),
          "play": ("PC version", "#1f63b8", "Fans have made a PC version. Some are still early, so read the project page first."),
          "code": ("Code only", "#666", "The rebuilt code is public, but you'd have to build the game yourself."),
          "wip": ("In progress", "#b98900", "Fans are still working on it.")}
PAGE_CSS = """
.crumbs{padding:8px 12px 0;font-size:11px;color:#555}.crumbs a{color:#0645ad}
.gp{display:grid;grid-template-columns:minmax(0,420px) minmax(0,1fr);gap:16px;padding:10px 12px 14px}
.gp .shot{width:100%;aspect-ratio:4/3;object-fit:cover;border:3px solid #fff;box-shadow:0 0 0 1px #9cb6d2,2px 2px 0 #c9d9ea;background:#dde}
.gp h1{margin:0 0 6px;font:bold 24px/1.15 "Trebuchet MS",Verdana;color:#c43e00}
.gp .lead{font-size:14px;line-height:1.5;margin:0 0 10px}
.facts{margin:10px 0;padding:0;list-style:none;border:1px solid #9cc0e6;border-radius:7px;background:#f2f8ff}
.facts li{padding:5px 9px;border-bottom:1px dotted #b9d3ee}.facts li:last-child{border:0}.facts b{display:inline-block;min-width:96px;color:#0b3466}
.pill{display:inline-block;font:bold 10px Verdana;color:#fff;padding:2px 7px;border-radius:9px;margin:1px 2px 1px 0;background:var(--c,#1f63b8)}
.tag{display:inline-block;font-size:11px;background:#ffefc2;border:1px solid #e3b44b;border-radius:9px;padding:1px 7px;margin:2px 3px 2px 0}
.note{border:2px solid #ff9a00;border-radius:9px;background:linear-gradient(#fff8e1,#ffe9a8);padding:9px 12px;margin:10px 0;font-size:12px}
.warn{border:2px solid #e53935;border-radius:9px;background:#fff3f2;padding:9px 12px;margin:10px 0;font-size:12px}
.proj{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.proj li{border:1px solid #9cc0e6;border-radius:7px;background:#fff;padding:8px 10px}
.proj a.pn{font:bold 14px "Trebuchet MS",Verdana}.proj .pd{margin:3px 0 0;color:#444}.proj .pm{font-size:10px;color:#777;margin-top:3px}
.related{padding:0 12px 14px}
.dlist{columns:4 220px;column-gap:18px;padding:8px 10px;border:1px solid #c9d9ea;border-top:0;border-radius:0 0 7px 7px;margin:0 0 14px;list-style:none}
.dlist li{break-inside:avoid;padding:2px 0;font-size:12px}.dlist small{color:#888}
.dq{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:8px 0}.dq input{flex:1 1 240px;font:13px Verdana;padding:5px 7px;border:2px inset #ccc;min-width:0}
.dq select{font:12px Verdana;padding:4px}
#dres{list-style:none;margin:0 0 14px;padding:0;display:grid;gap:6px}
#dres li{border:1px solid #c9d9ea;border-radius:7px;padding:6px 9px;background:#fff}
.doc2{padding:4px 12px 16px;font-size:13px;line-height:1.55}
@media (max-width:820px){.gp{grid-template-columns:minmax(0,1fr)}.gp h1{font-size:20px}}
"""


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    t = re.sub(r"\(.*?\)", " ", t)
    t = re.sub(r"\b(the|a|an|online|browser|web|port|remake|fan|edition|hd|3d|game|free)\b", " ", t)
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def head(title, desc, path, img=None, extra=""):
    og_img = f'<meta property="og:image" content="{SITE}/{E(img)}">' if img else ""
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="description" content="{E(desc)}"><link rel="canonical" href="{SITE}{path}">'
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="MegaClip"><meta property="og:title" content="{E(title)}">'
            f'<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{SITE}{path}">{og_img}'
            f'<meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/apple-touch-icon.png">'
            f'<meta name="theme-color" content="#1e63b5">{VA}{extra}<title>{E(title)}</title>')


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def crumbs(items):
    """items: [(label, path or None)]"""
    html_ = " &rsaquo; ".join(f'<a href="{p}">{E(l)}</a>' if p else E(l) for l, p in items)
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": l, **({"item": SITE + p} if p else {})} for i, (l, p) in enumerate(items)]}
    return f'<div class="crumbs">{html_}</div>', ld(data)


def build(games, decomps, css, header, bar, footer, thumb, cats, label):
    """Write every extra page. Returns (list of page html, list of sitemap paths)."""
    out, paths = [], []

    def write(path, page):
        fn = "index.html" if path == "/" else path.strip("/") + ".html"
        os.makedirs(os.path.dirname(fn) or ".", exist_ok=True)
        open(fn, "w").write(page)
        out.append(page)
        paths.append(path)

    open("site.css", "w").write(css + PAGE_CSS)  # one shared stylesheet, cached across all these pages

    def shell(hd, body):
        return f'{hd}<link rel="stylesheet" href="/site.css"></head><body><div class="wrap">{header}{bar}{body}{footer}</div><script src="/search.js" defer></script></body></html>'

    # cross-links between browser games and PC ports
    dec_page = [d for d in decomps if d["page"]]
    dec_by_norm = {}
    for d in dec_page:
        dec_by_norm.setdefault(norm(d["title"]), d)
    game_by_norm = {}
    for g in games:
        for key in (g.get("based_on"), g["name"]):
            if key and norm(key):
                game_by_norm.setdefault(norm(key), []).append(g)
    for g in games:
        g["_decomp"] = next((dec_by_norm[norm(k)] for k in (g.get("based_on"), g["name"]) if k and norm(k) in dec_by_norm), None)

    # ---- game pages ----
    for g in games:
        tags = set(g.get("tags") or [])
        def score(o):
            return (3 * (o["cat"] == g["cat"]) + len(tags & set(o.get("tags") or [])) + 2 * (bool(g.get("based_on")) and o.get("based_on") == g.get("based_on")))
        rel = sorted((o for o in games if o is not g), key=lambda o: (-score(o), o["name"]))[:8]
        ph_cls, ph_txt = PHONE[g.get("mobile", "maybe")]
        desc = g.get("desc") or f'{g["name"]}: a {label[g["cat"]].lower()} game you can play in your web browser.'
        title = f'{g["name"]}: Play Online in Your Browser :: MegaClip'
        cr, cr_ld = crumbs([("MegaClip", "/"), (label[g["cat"]], f'/category/{g["cat"]}'), (g["name"], None)])
        game_ld = ld({"@context": "https://schema.org", "@type": "VideoGame", "name": g["name"], "url": f'{SITE}/game/{g["slug"]}',
                      "image": f'{SITE}/{g["img"]}', "description": desc, "genre": label[g["cat"]], "gamePlatform": "Web browser",
                      "playMode": "SinglePlayer" if "multiplayer" not in tags else "MultiPlayer", "sameAs": g["url"]})
        facts = [f'<li><b>Category</b> <a href="/category/{g["cat"]}">{E(label[g["cat"]])}</a></li>',
                 f'<li><b>Phone?</b> <span class="mb {ph_cls}" style="position:static;display:inline-block">{ph_txt}</span> {E(g.get("mobile_why", ""))}</li>',
                 f'<li><b>Plays on</b> {E(g["host"])}</li>']
        if g.get("based_on"):
            facts.append(f'<li><b>Based on</b> {E(g["based_on"])}</li>')
        if g["note"]:
            facts.append(f'<li><b>Heads up</b> {E(g["note"])}</li>')
        tagh = "".join(f'<span class="tag">{E(t)}</span>' for t in sorted(tags))
        dlink = (f'<div class="note">&#128187; <b>Want the full version on PC?</b> Fans have rebuilt <a href="/decomp/{g["_decomp"]["slug"]}">{E(g["_decomp"]["title"])}</a> as a PC port. You need your own copy of the original game.</div>'
                 if g["_decomp"] else "")
        body = (f'{cr}<div class="gp"><div><a href="{E(g["url"])}" target="_blank" rel="noopener noreferrer"><img class="shot" src="/{E(g["img"])}" alt="{E(g["name"])} screenshot"></a></div>'
                f'<div><h1>{E(g["name"])}</h1><p class="lead">{E(desc)}</p>'
                f'<a class="play" href="{E(g["url"])}" target="_blank" rel="noopener noreferrer">&#9654; PLAY NOW!</a>'
                f'<ul class="facts">{"".join(facts)}</ul><div>{tagh}</div>{dlink}'
                f'<p style="font-size:11px;color:#666">The game opens on its maker\'s website in a new tab. MegaClip just points you there.</p></div></div>'
                f'<section class="box related"><h2 style="--c:#ff8a00"><span class="ic"></span>More games like {E(g["name"])}<small>{len(rel)} games</small></h2>'
                f'<div class="grid">{"".join(thumb(o) for o in rel)}</div></section>')
        write(f'/game/{g["slug"]}', shell(head(title, desc, f'/game/{g["slug"]}', g["img"], cr_ld + game_ld), body))

    # ---- category pages ----
    for k, l, c in cats:
        items = [g for g in games if g["cat"] == k] if k != "new" else [g for g in games if g["is_new"]]
        if k == "new" or not items:
            continue
        cr, cr_ld = crumbs([("MegaClip", "/"), (l, None)])
        desc = f'{len(items)} free {l.lower()} games you can play in your browser, no downloads. Hand-picked on MegaClip.'
        body = (f'{cr}<div class="doc2"><h1 style="font:bold 22px Trebuchet MS,Verdana;color:#c43e00;margin:6px 0">{E(l)} Games</h1><p>{E(desc)}</p></div>'
                f'<section class="box" style="padding:0 12px"><h2 style="--c:{c}"><span class="ic"></span>{E(l)}<small>{len(items)} games</small></h2>'
                f'<div class="grid">{"".join(thumb(g) for g in items)}</div></section>')
        write(f'/category/{k}', shell(head(f'{l} Games: Play Free Online :: MegaClip', desc, f'/category/{k}', items[0]["img"], cr_ld), body))

    # ---- decomp pages ----
    fam_rank = {}
    for d in dec_page:
        fam_rank.setdefault(d["fam"], []).append(d)
    for d in dec_page:
        st, col, st_txt = STATUS[d["status"]]
        plat = f' ({d["platform"]})' if d["platform"] else ""
        n = len(d["links"])
        desc = (f'{d["title"]}{plat} rebuilt by fans for PC. {n} fan project{"s" if n > 1 else ""} '
                f'{"with an easy installer" if d["status"] == "easy" else "with a PC version"}. Bring your own copy of the game.')
        title = f'{d["title"]} PC Port & Decomp{plat} :: MegaClip'
        cr, cr_ld = crumbs([("MegaClip", "/"), ("PC Ports", "/decomps"), (d["title"], None)])
        projs = "".join(
            f'<li><a class="pn" href="{E(l["url"])}" target="_blank" rel="noopener noreferrer">{"&#9733; " if l["pick"] else ""}{E(l["label"])}</a>'
            + (f'<p class="pd">{E(l["desc"])}</p>' if l["desc"] else "")
            + '<div class="pm">' + " &middot; ".join(x for x in [
                E(re.sub(r"^https?://(www\.)?", "", l["url"]).split("?")[0][:70]),
                f'&#9733; {l["stars"]:,} stars' if l.get("stars") else "",
                f'last updated {l["updated"]}' if l.get("updated") else "",
                "archived (no longer updated)" if l.get("archived") else "",
                "recommended" if l["pick"] else ""] if x) + "</div></li>" for l in d["links"])
        same = [o for o in fam_rank[d["fam"]] if o is not d]
        same.sort(key=lambda o: (o["platform"] != d["platform"], -len(o["links"]), o["title"]))
        rel = "".join(f'<li><a href="/decomp/{o["slug"]}">{E(o["title"])}</a> <small>{E(o["platform"])}</small></li>' for o in same[:10])
        plat_pill = f'<span class="pill" style="--c:#555">{E(d["platform"])}</span>' if d["platform"] else ""
        prog_pill = f'<span class="pill" style="--c:#8e44ad">{E(d["progress"])}</span>' if d["progress"] else ""
        play = [g for g in game_by_norm.get(norm(d["title"]), [])][:3]
        playh = ("<div class=\"note\">&#127918; <b>No copy of the game? Play in your browser instead:</b> "
                 + ", ".join(f'<a href="/game/{g["slug"]}">{E(g["name"])}</a>' for g in play) + "</div>") if play else ""
        body = (f'{cr}<div class="doc2"><h1 style="font:bold 24px/1.15 Trebuchet MS,Verdana;color:#c43e00;margin:6px 0">{E(d["title"])} on PC</h1>'
                f'<p><span class="pill" style="--c:{col}">{st}</span>{plat_pill}{prog_pill} {st_txt}</p>'
                f'<p>Fans took {E(d["title"])} apart and rebuilt it so it runs natively on a computer, often with widescreen, higher frame rates and mods. '
                f'{"Here is the project" if n == 1 else f"Here are the {n} projects"} we know about:</p>'
                f'<ul class="proj">{projs}</ul>'
                f'<div class="note">&#128191; <b>Bring your own game.</b> These projects share code only, not the game itself. You need your own copy of the original game to play.</div>'
                f'<div class="warn">&#128737; <b>Stay safe:</b> only download from the project\'s own page linked above. Fake "PC port" downloads on other sites can carry malware.</div>'
                f'{playh}<h2 style="font:bold 15px Trebuchet MS,Verdana;margin:16px 0 4px">More {E(d["fam"])} PC ports</h2><ul class="dlist" style="border-top:1px solid #c9d9ea;border-radius:7px">{rel}</ul></div>')
        write(f'/decomp/{d["slug"]}', shell(head(title, desc, f'/decomp/{d["slug"]}', None, cr_ld), body))

    # ---- decomps hub ----
    groups = {}
    for d in sorted(dec_page, key=lambda d: d["title"].lower()):
        groups.setdefault(d["fam"], []).append(d)
    order = ["Nintendo", "PlayStation", "Xbox", "SEGA", "PC and DOS", "Arcade", "Old home computers", "Phones", "Other"]
    lists = "".join(
        f'<section class="box"><h2 style="--c:#1f63b8"><span class="ic"></span>{E(f)}<small>{len(groups[f])} games</small></h2><ul class="dlist">'
        + "".join(f'<li><a href="/decomp/{d["slug"]}">{E(d["title"])}</a> <small>{E(d["platform"])}</small></li>' for d in groups[f]) + "</ul></section>"
        for f in order if f in groups)
    cr, cr_ld = crumbs([("MegaClip", "/"), ("PC Ports", None)])
    desc = f'{len(decomps):,} classic console games rebuilt by fans to run on PC: decompilations, recompilations and fan ports. Bring your own copy of the game.'
    fams = "".join(f'<option value="{E(f)}">{E(f)}</option>' for f in order if any(d["fam"] == f for d in decomps))
    body = (f'{cr}<div class="doc2"><h1 style="font:bold 24px Trebuchet MS,Verdana;color:#c43e00;margin:6px 0">PC Ports: classic games rebuilt by fans</h1>'
            f'<p>Fans have taken {len(decomps):,} console and classic games apart and rebuilt their code so they run natively on a computer. '
            f'These are <b>downloads, not browser games</b>, and every one needs <b>your own copy of the original game</b>. '
            f'{len(dec_page):,} of them have a PC version you can use today.</p>'
            f'<div class="warn">&#128737; <b>Stay safe:</b> only download from each project\'s own page. Fake "PC port" downloads elsewhere can carry malware.</div>'
            f'<div class="dq"><input id="dq" type="search" placeholder="Search all {len(decomps):,} games..." aria-label="Search PC ports">'
            f'<select id="df" aria-label="Console"><option value="">All consoles</option>{fams}</select>'
            f'<select id="ds" aria-label="Status"><option value="pc">Has a PC version</option><option value="">Everything</option><option value="easy">Easy install only</option></select></div>'
            f'<p id="dcount" style="font-size:11px;color:#666"></p><ul id="dres" hidden></ul></div><div id="dall" style="padding:0 12px">{lists}</div>')
    write("/decomps", shell(head(f'PC Ports: {len(decomps):,} Classic Games Rebuilt by Fans :: MegaClip', desc, "/decomps", None, cr_ld), body))

    # ---- search data (loaded only when someone searches) ----
    json.dump([[d["slug"] if d["page"] else "", d["title"], d["platform"], d["fam"], d["status"],
                "" if d["page"] else d["links"][0]["url"]] for d in decomps],
              open("search-decomps.json", "w"), ensure_ascii=False, separators=(",", ":"))
    return out, paths
