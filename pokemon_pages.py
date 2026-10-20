"""Pokémon Fan Games section: /pokemon hub, one page per notable ROM hack or fan game, home strip and search data.
Built from pokemon.json (merged from five hunts; official pages only, never ROM sites). Called from arcade.py."""
import json, re, html
from pages import E, head, crumbs, ld, SITE

KIND = {"rom-hack": "ROM hack", "fan-game": "Fan game"}
STATUS = {"complete": ("Complete", "#2e9e2e"), "beta": ("Beta", "#1f63b8"), "demo": ("Demo", "#8e44ad"),
          "in progress": ("In progress", "#b98900"), "abandoned": ("Abandoned", "#666"), "unknown": ("Status unknown", "#78909c")}
GEN_COL = {"Red/Blue": "#d32f2f", "Red": "#d32f2f", "Blue": "#1e5bd6", "Yellow": "#f2b600", "Green": "#2e7d32",
           "Gold": "#b8860b", "Silver": "#78909c", "Crystal": "#26a6c9",
           "FireRed": "#e2541b", "LeafGreen": "#43a047", "Ruby": "#c2185b", "Sapphire": "#1565c0", "Emerald": "#00897b",
           "Diamond": "#5c6bc0", "Pearl": "#c2799a", "Platinum": "#6d6d7a", "HeartGold": "#c9a227", "SoulSilver": "#8fa3b5",
           "Black": "#333a44", "White": "#7d8a99", "Black 2": "#3a3f4b", "White 2": "#8796a5"}
FAN_COL = "#7b1fa2"
BASE_ORDER = ["Red/Blue", "Yellow", "Gold", "Silver", "Crystal", "Ruby", "Sapphire", "Emerald", "FireRed", "LeafGreen",
              "Diamond", "Pearl", "Platinum", "HeartGold", "SoulSilver", "Black", "White", "Black 2", "White 2"]
PK_CSS = """
.pkhero{margin:8px 12px 12px;border-radius:10px;overflow:hidden;border:2px solid #7a1010;background:linear-gradient(120deg,#b71c1c,#e53935 45%,#ff8f00);color:#fff;padding:12px 14px;position:relative}
.pkhero:after{content:"";position:absolute;right:-40px;top:-40px;width:180px;height:180px;border-radius:50%;background:radial-gradient(circle,#fff 0 18%,#222 18% 22%,transparent 22%),linear-gradient(#ffffff22 50%,#00000022 50%);border:10px solid #ffffff33;pointer-events:none}
.pkhero h1{margin:0;font:900 clamp(24px,4vw,34px)/1 "Arial Rounded MT Bold","Trebuchet MS",Arial;color:#ffeb3b;letter-spacing:-1px;text-shadow:0 2px 0 #8a1c00,2px 2px 0 #000;transform:rotate(-1.5deg);transform-origin:left;position:relative;z-index:1}
.pkhero .pctag{margin:6px 0 8px;font:bold 12px/1.4 Verdana;max-width:62ch;position:relative;z-index:1}
.pkhero .stats{display:flex;flex-wrap:wrap;gap:6px 14px;margin:0 0 9px;position:relative;z-index:1;font:bold 11px Verdana}
.pkhero .stats b{font:900 15px "Trebuchet MS",Arial;color:#ffeb3b;margin-right:3px}
.pkhero .dq{position:relative;z-index:1;margin:0}.pkhero .dq input{font-size:13px;padding:6px 9px;border:2px solid #ffeb3b;border-radius:6px}
.pkhero .dq select{padding:5px;border-radius:6px}
.pkhero .chips2{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;position:relative;z-index:1;font:bold 10px Verdana}
.pkhero .chips2 span{background:rgba(255,255,255,.92);color:#222;border-radius:12px;padding:3px 8px}
#pcount{color:#ffeb3b;font-weight:bold;position:relative;z-index:1;margin:8px 0 0;font-size:11px}
#pres{list-style:none;margin:0 12px 16px;padding:0;display:grid;gap:6px}#pres li{border:1px solid #c9d9ea;border-radius:7px;padding:6px 9px;background:#fff}
.cart .st{display:inline-block;font:bold 9px Verdana;padding:1px 6px;border-radius:8px;background:rgba(255,255,255,.9);color:#222;margin-left:4px}
"""


def tagline(o):
    """PokéCommunity-only entries have listing notes like 'FireRed hack; thread title: "X"; 11M views...'; keep just the tagline."""
    n = o.get("note") or ""
    m = re.search(r'thread title: "([^"]+)"', n)
    if m: return m.group(1)
    if re.match(r"^\w[\w/ ]* hack; ", n) or n.startswith("ROM hack;"): return ""
    return n


def fmt_views(v):
    return f"{v / 1e6:.1f}M".replace(".0M", "M") if v >= 1e6 else f"{v // 1000}K" if v >= 1000 else str(v)


def colour(o):
    return FAN_COL if o["kind"] == "fan-game" else GEN_COL.get(o["base"], "#546e7a")


def pk_cart(o, mini=False):
    st, _ = STATUS[o["status"]]
    con = o["base"] if o["kind"] == "rom-hack" and o["base"] else KIND[o["kind"]]
    desc = "" if mini else tagline(o)
    desc = desc if len(desc) <= 96 else desc[:93].rsplit(" ", 1)[0] + "..."
    meta = "" if mini else " &middot; ".join(x for x in [f"#{o['rank']} most popular" if o["rank"] else "",
                                                        f"&#9733; {o['stars']:,}" if o["stars"] else "",
                                                        f"{fmt_views(o['views'])} views" if o["views"] else ""] if x)
    href = f'/pokemon/{o["slug"]}' if o["page"] else E(o["links"][0]["url"])
    ext = "" if o["page"] else ' target="_blank" rel="noopener noreferrer"'
    get = "" if mini else f'<a class="get" href="{E(o["links"][0]["url"])}" target="_blank" rel="noopener noreferrer">Official page &#9656;</a>'
    return (f'<div class="cart{" mini" if mini else ""}" style="--c:{colour(o)}"><a class="lbl" href="{href}"{ext}>'
            f'<span class="con">{E(con)}{"" if mini else f"<span class=st>{st}</span>"}</span><span class="ct">{E(o["title"])}</span>'
            + (f'<p class="cd">{E(desc)}</p>' if desc else "") + (f'<span class="cm">{meta}</span>' if meta else "") + f"</a>{get}</div>")


def home_strip(poke):
    picks = [o for o in poke if o["rank"]][:8]
    return (f'<section class="pcban" id="pokemon" style="background:linear-gradient(120deg,#b71c1c,#e53935 55%,#ff8f00);border-color:#7a1010"><div class="hd">'
            f'<h2 style="color:#ffeb3b">&#9889; NEW! POK&Eacute;MON FAN GAMES</h2>'
            f'<p>{len(poke):,} fan-made Pok&eacute;mon games and ROM hacks: Radical Red, Unbound, Infinite Fusion and loads more.</p>'
            f'<a class="go" href="/pokemon">Browse all &#9656;</a></div><div class="row">{"".join(pk_cart(o, True) for o in picks)}</div></section>')


def build(poke, games, write, shell):
    """write(path, html) and shell(head_html, body) come from pages.build so every page shares the same frame."""
    pg = [o for o in poke if o["page"]]
    by_base = {}
    for o in pg:
        by_base.setdefault(o["base"] if o["kind"] == "rom-hack" and o["base"] in GEN_COL else ("Fan games" if o["kind"] == "fan-game" else "Other ROM hacks"), []).append(o)
    norm = lambda t: re.sub(r"[^a-z0-9]+", " ", re.sub(r"pok[eé]mon", "", (t or "").lower())).strip()
    mc = {}
    for g in games:
        mc.setdefault(norm(g["name"]), g)

    # ---- one page per notable game ----
    for o in pg:
        st, stc = STATUS[o["status"]]
        kind = KIND[o["kind"]]
        what = f'{o["base"]} {kind}' if o["kind"] == "rom-hack" and o["base"] else kind
        desc_txt = tagline(o)
        meta_desc = (f'{o["title"]}: a fan-made Pokémon {what.lower()}' + (f' by {o["author"]}' if o["author"] else "") +
                     f'. {st}.' + (f' {desc_txt}' if desc_txt else "") + " Official page link on MegaClip.")[:300]
        title = f'{o["title"]} ({what}) :: MegaClip'
        cr, cr_ld = crumbs([("MegaClip", "/"), ("Pokémon Fan Games", "/pokemon"), (o["title"], None)])
        facts = [f'<li><b>Type</b> {E(what)}</li>', f'<li><b>Status</b> <span class="pill" style="--c:{stc}">{st}</span></li>']
        if o["platform"]: facts.append(f'<li><b>Plays on</b> {E(o["platform"])}{" (via your own copy of the game)" if o["kind"] == "rom-hack" else ""}</li>')
        if o["author"]: facts.append(f'<li><b>Made by</b> {E(o["author"])}</li>')
        if o["updated"]: facts.append(f'<li><b>Last activity</b> {E(o["updated"])}</li>')
        if o["rank"]: facts.append(f'<li><b>Popularity</b> #{o["rank"]} most popular Pokémon fan game right now</li>')
        if o["views"]: facts.append(f'<li><b>Forum views</b> {fmt_views(o["views"])} on PokéCommunity</li>')
        if o["stars"]: facts.append(f'<li><b>GitHub stars</b> &#9733; {o["stars"]:,}</li>')
        bare = lambda u: re.sub(r"^https?://(www\.)?", "", u)[:80]
        links = "".join(f'<li><a class="pn" href="{E(l["url"])}" target="_blank" rel="noopener noreferrer">{E(l["label"])} &#9656;</a>'
                        f'<div class="pm">{E(bare(l["url"]))}</div></li>' for l in o["links"])
        how = ("<b>How to play:</b> ROM hacks are shared as a patch. Download the patch from the official page and apply it to <b>your own copy</b> of the original game. MegaClip never links to game files."
               if o["kind"] == "rom-hack" else "<b>How to play:</b> download it from the official page above. It's a free, fan-made game.")
        same = [x for x in by_base.get(o["base"] if o["kind"] == "rom-hack" and o["base"] in GEN_COL else ("Fan games" if o["kind"] == "fan-game" else "Other ROM hacks"), []) if x is not o][:10]
        rel = "".join(f'<li><a href="/pokemon/{x["slug"]}">{E(x["title"])}</a> <small>{STATUS[x["status"]][0]}</small></li>' for x in same)
        play = mc.get(norm(o["title"]))
        playh = (f'<div class="note">&#127918; <b>Play a version in your browser:</b> <a href="/game/{play["slug"]}">{E(play["name"])}</a> is on MegaClip.</div>' if play else "")
        game_ld = ld({"@context": "https://schema.org", "@type": "VideoGame", "name": o["title"], "url": f'{SITE}/pokemon/{o["slug"]}',
                      "description": meta_desc, "genre": "Role-playing", **({"author": {"@type": "Person", "name": o["author"]}} if o["author"] else {}),
                      "sameAs": o["links"][0]["url"]})
        body = (f'{cr}<div class="doc2"><h1 style="font:bold 24px/1.15 Trebuchet MS,Verdana;color:#c43e00;margin:6px 0">{E(o["title"])}</h1>'
                f'<p><span class="pill" style="--c:{colour(o)}">{E(what)}</span><span class="pill" style="--c:{stc}">{st}</span></p>'
                + (f'<p style="font-size:14px">{E(desc_txt)}</p>' if desc_txt else "")
                + f'<ul class="facts">{"".join(facts)}</ul><h2 style="font:bold 15px Trebuchet MS,Verdana;margin:14px 0 6px">Official page{"s" if len(o["links"]) > 1 else ""}</h2>'
                f'<ul class="proj">{links}</ul><div class="note">{how}</div>'
                f'<div class="warn">&#128737; <b>Stay safe:</b> only download from the official page. Sites offering "pre-patched ROMs" or "free downloads" of these games are often fake or carry malware.</div>'
                f'{playh}<h2 style="font:bold 15px Trebuchet MS,Verdana;margin:16px 0 4px">More like this</h2><ul class="dlist" style="border-top:1px solid #c9d9ea;border-radius:7px">{rel}</ul></div>')
        write(f'/pokemon/{o["slug"]}', shell(head(title, meta_desc, f'/pokemon/{o["slug"]}', None, cr_ld + game_ld), body))

    # ---- hub ----
    top = [o for o in poke if o["rank"]]
    done = [o for o in pg if o["kind"] == "rom-hack" and o["status"] == "complete" and not o["rank"]]
    done.sort(key=lambda o: -(o["views"] + o["stars"] * 500)); done = done[:24]
    fans = [o for o in pg if o["kind"] == "fan-game" and not o["rank"] and o["status"] in ("complete", "beta", "demo")][:24]
    shown = {o["slug"] for o in top + done + fans}
    fresh = sorted([o for o in pg if o["slug"] not in shown and o["updated"] >= "2026" and o["status"] in ("complete", "beta", "demo")],
                   key=lambda o: o["updated"], reverse=True)[:12]
    def shelf(t, sub, items, c, anchor):
        return (f'<section class="box" id="{anchor}" style="margin:0 12px 16px"><h2 style="--c:{c};font-size:16px;padding:9px 11px"><span class="ic"></span>{t}<small>{len(items)} games</small></h2>'
                f'<p class="vsub" style="margin:0;padding:7px 11px;background:#fff3e0;font-weight:bold;color:#7a3b00;border:1px solid #c9d9ea;border-top:0">{sub}</p>'
                f'<div class="carts">{"".join(pk_cart(o) for o in items)}</div></section>')
    order = [b for b in BASE_ORDER if b in by_base] + [b for b in ("Fan games", "Other ROM hacks") if b in by_base]
    gid = lambda b: "base-" + re.sub(r"[^a-z0-9]+", "-", b.lower()).strip("-")
    tiles = "".join(f'<a class="tile" href="#{gid(b)}" style="--c:{FAN_COL if b == "Fan games" else GEN_COL.get(b, "#546e7a")}"><b>{E(b)}</b><span>{len(by_base[b])} games</span></a>' for b in order)
    lists = "".join(f'<section class="box" id="{gid(b)}"><h2 style="--c:{FAN_COL if b == "Fan games" else GEN_COL.get(b, "#546e7a")}"><span class="ic"></span>{E(b)}<small>{len(by_base[b])} games</small></h2><ul class="dlist">'
                    + "".join(f'<li><a href="/pokemon/{o["slug"]}">{E(o["title"])}</a> <small>{STATUS[o["status"]][0]}</small></li>' for o in sorted(by_base[b], key=lambda o: o["title"].lower()))
                    + "</ul></section>" for b in order)
    hacks = sum(1 for o in poke if o["kind"] == "rom-hack"); fg = len(poke) - hacks
    cr, cr_ld = crumbs([("MegaClip", "/"), ("Pokémon Fan Games", None)])
    desc = f'{len(poke):,} fan-made Pokémon games and ROM hacks, from Radical Red and Unbound to Infinite Fusion and PokéRogue. Official pages only.'
    bases = "".join(f'<option value="{E(b)}">{E(b)}</option>' for b in BASE_ORDER if any(o["base"] == b for o in poke))
    hub_css = """<style>.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px;margin:0 12px 16px}
.tile{display:block;text-decoration:none;color:#fff;border-radius:10px;padding:9px 11px;background:linear-gradient(color-mix(in srgb,var(--c) 75%,#fff),var(--c));border:2px solid color-mix(in srgb,var(--c) 60%,#000);box-shadow:0 2px 0 color-mix(in srgb,var(--c) 60%,#000);text-shadow:1px 1px 0 rgba(0,0,0,.35)}
.tile b{display:block;font:900 13px "Trebuchet MS",Arial}.tile span{font:bold 10px Verdana;opacity:.9}.tile:hover{filter:brightness(1.1)}</style>"""
    body = (f'{hub_css}<style>{PK_CSS}</style>{cr}<div class="pkhero"><h1>&#9889; POK&Eacute;MON FAN GAMES</h1>'
            f'<p class="pctag">Every fan-made Pok&eacute;mon game we could find: ROM hacks that remix the classics, and brand-new games built from scratch by fans.</p>'
            f'<div class="stats"><span><b>{len(poke):,}</b>games</span><span><b>{hacks:,}</b>ROM hacks</span><span><b>{fg:,}</b>fan games</span>'
            f'<span><b>{sum(1 for o in poke if o["status"] == "complete"):,}</b>complete</span></div>'
            f'<div class="dq"><input id="pq" type="search" placeholder="Search {len(poke):,} games... try Radical Red, Emerald, Fusion" aria-label="Search Pokémon fan games">'
            f'<select id="pk" aria-label="Type"><option value="">Hacks and fan games</option><option value="rom-hack">ROM hacks</option><option value="fan-game">Fan games</option></select>'
            f'<select id="pb" aria-label="Base game"><option value="">Any base game</option>{bases}</select>'
            f'<select id="ps" aria-label="Status"><option value="">Any status</option><option value="complete">Complete</option><option value="playable">Playable now (complete, beta, demo)</option></select></div>'
            f'<p id="pcount"></p><div class="chips2"><span>&#128279; Official pages only</span><span>&#128191; ROM hacks need your own copy of the game</span><span>&#128737; Never download pre-patched ROMs</span></div></div>'
            f'<ul id="pres" hidden></ul><div id="pall"><div class="tiles">{tiles}</div>'
            + shelf("&#128293; The most popular right now", "The fan games everyone is playing, ranked by forum views, coverage, the 2025 community awards and Reddit buzz.", top, "#e53935", "top")
            + shelf("&#9989; Best completed ROM hacks", "Finished from start to end. Grab the patch, apply it to your own copy, play.", done, "#2e9e2e", "complete")
            + shelf("&#127918; Fan games you can download", "Brand-new Pok&eacute;mon games made from scratch by fans. No original game needed.", fans, FAN_COL, "fangames")
            + (shelf("&#9889; New this year", "Released or updated in 2026.", fresh, "#1f63b8", "fresh") if fresh else "")
            + f'<div style="padding:0 12px"><h2 style="font:900 18px Trebuchet MS,Arial;color:#c43e00;margin:4px 0 8px">Every Pok&eacute;mon fan game, by base game</h2>{lists}</div></div>')
    write("/pokemon", fn="pokemon/index.html", page=shell(head(f'Pokémon Fan Games & ROM Hacks: {len(poke):,} Fan-Made Games :: MegaClip', desc, "/pokemon", None, cr_ld), body))

    # ---- search data: [slug or "", title, kind, base, status, url] ----
    json.dump([[o["slug"] if o["page"] else "", o["title"], o["kind"], o["base"], o["status"], "" if o["page"] else o["links"][0]["url"]] for o in poke],
              open("search-pokemon.json", "w"), ensure_ascii=False, separators=(",", ":"))
