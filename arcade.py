"""Build index.html from games.json in a mid-2000s web-games-portal style.
Run: python3 arcade.py  (then vercel deploy --prod --yes)"""
import json, html
from datetime import date

E = html.escape
CATS = [  # key, label, icon colour
    ("new", "New Games!", "#ff3d00"),
    ("shoot", "Shoot 'em Up", "#d81b1b"),
    ("action", "Action & Driving", "#ff8a00"),
    ("sports", "Sports", "#2e9e2e"),
    ("adventure", "Adventure & RPG", "#8e44ad"),
    ("strategy", "Strategy", "#1565c0"),
    ("puzzle", "Puzzles & Daily", "#00acc1"),
    ("pokemon", "Pokémon & Friends", "#f4c20d"),
    ("party", "Party & Family", "#e91e63"),
    ("multi", "Multiplayer", "#00897b"),
    ("indie", "Fresh & Original", "#43a047"),
    ("retro", "Retro Classics", "#6d4c41"),
    ("official", "Official & Free", "#0097a7"),
    ("zones", "Game Zones", "#455a64"),
]
LABEL = {k: l for k, l, _ in CATS}
COL = {k: c for k, _, c in CATS}

games = json.load(open("games.json"))
newest = max(g["added"] for g in games)
for g in games:
    g["is_new"] = g["added"] == newest


def thumb(g):
    note = f'<i>{E(g["note"])}</i>' if g["note"] else ""
    new = '<em class="nb">NEW!</em>' if g["is_new"] else ""
    m = g.get("mobile", "maybe")
    why = E(g.get("mobile_why", ""))
    mob = {"yes": f'<em class="mb y" title="{why}">&#128241; Phone OK</em>',
           "no": f'<em class="mb n" title="{why}">&#128187; Computer only</em>',
           "maybe": f'<em class="mb m" title="{why}">&#128241;? Not sure</em>'}[m]
    return (f'<a class="g" href="{E(g["url"])}" target="_blank" rel="noopener noreferrer" '
            f'data-m="{m}" data-s="{E((g["name"] + " " + g["host"] + " " + LABEL[g["cat"]]).lower())}">'
            f'<span class="t"><img src="{E(g["img"])}" alt="" loading="lazy">{new}{mob}</span>'
            f'<b>{E(g["name"])}</b>{note}</a>')


def box(key, title, items, colour):
    return (f'<section class="box" id="{key}"><h2 style="--c:{colour}"><span class="ic"></span>{E(title)}'
            f'<small>{len(items)} games</small></h2><div class="grid">{"".join(map(thumb, items))}</div>'
            f'<a class="top" href="#">&#9650; back to top</a></section>')


by = {k: [g for g in games if g["cat"] == k] for k, _, _ in CATS}
by["new"] = [g for g in games if g["is_new"]]
cats = [(k, l, c) for k, l, c in CATS if by[k]]

side = "".join(f'<li><a href="#{k}"><span class="ic" style="--c:{c}"></span>{E(l)}</a> <small>({len(by[k])})</small></li>'
               for k, l, c in cats)
top10 = [g for g in games if g.get("top")][:10]
toplist = "".join(f'<li><a href="{E(g["url"])}" target="_blank" rel="noopener noreferrer">{E(g["name"])}</a></li>' for g in top10)
feat = next((g for g in games if g.get("featured")), top10[0])
fresh = by["new"][:8] or games[-8:]
freshlist = "".join(f'<li><a href="{E(g["url"])}" target="_blank" rel="noopener noreferrer">{E(g["name"])}</a></li>' for g in fresh)
ticker = " &nbsp;&#9733;&nbsp; ".join(E(g["name"]) for g in (by["new"] or games[-12:])[:14])
boxes = "".join(box(k, l, by[k], c) for k, l, c in cats)
viral = sorted((g for g in games if g.get("viral")), key=lambda g: g["viral"])
viralbox = (f'<section class="box viral" id="viral"><h2 style="--c:#e53935"><span class="ic"></span>&#128293; THE VIRAL {len(viral)}: every game from the list that blew up on X'
            f'<small>{len(viral)} games</small></h2><p class="vsub">Black Ops zombies, Halo, GTA, Skate 3 and more, all in a browser tab. Start here!</p>'
            f'<div class="grid">{"".join(map(thumb, viral))}</div><a class="top" href="#">&#9650; back to top</a></section>') if viral else ""
updated = date.fromisoformat(newest).strftime("%-d %B %Y")

page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="MegaClip: free browser games, no downloads. Hand-picked new web games, retro classics and fan projects you can play in a tab."><link rel="canonical" href="https://megaclip.games/"><script>window.va=window.va||function(){{(window.vaq=window.vaq||[]).push(arguments)}};</script><script defer src="/_vercel/insights/script.js"></script>
<title>MegaClip :: Free Online Games!</title><style>
*{{box-sizing:border-box}}
body{{margin:0;background:#1d4f8c url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='8' height='8'%3E%3Cpath d='M0 0h4v4H0zM4 4h4v4H4z' fill='%23ffffff' fill-opacity='.04'/%3E%3C/svg%3E");
 font:12px/1.35 Verdana,Tahoma,Geneva,sans-serif;color:#222}}
a{{color:#0645ad}}
.wrap{{max-width:1440px;margin:0 auto;background:#fff;border:1px solid #0b2f5c;box-shadow:0 0 0 4px #3f7cc8}}
header{{position:relative;height:118px;background:linear-gradient(#7fc4ff,#2b7fd8 70%,#1e63b5);overflow:hidden;border-bottom:3px solid #ff9a00}}
header:before{{content:"";position:absolute;left:-40px;right:-40px;bottom:-60px;height:110px;background:radial-gradient(ellipse at 30% 0,#7bd34a,#3f9b1f 70%);border-radius:50%}}
.cloud{{position:absolute;background:#fff;border-radius:40px;opacity:.85;height:18px}}
.cloud:before,.cloud:after{{content:"";position:absolute;background:#fff;border-radius:50%}}
.cloud:before{{width:26px;height:26px;top:-12px;left:10px}}.cloud:after{{width:34px;height:34px;top:-18px;left:28px}}
.logo{{position:absolute;left:22px;top:16px;font:900 52px/1 "Arial Rounded MT Bold","Trebuchet MS",Arial,sans-serif;color:#ffb300;letter-spacing:-1px;
 text-shadow:0 3px 0 #e65100,0 0 0 #fff,-2px -2px 0 #0b3d7a,2px -2px 0 #0b3d7a,-2px 2px 0 #0b3d7a,2px 2px 0 #0b3d7a,0 7px 10px rgba(0,0,0,.35);transform:rotate(-3deg)}}
.logo span{{color:#fff}}
.slogan{{position:absolute;left:30px;top:82px;color:#fff;font:bold 13px Verdana;text-shadow:1px 1px 0 #0b3d7a}}
.badge{{position:absolute;right:22px;top:20px;width:92px;height:92px;border-radius:50%;background:radial-gradient(#fff36b,#ffc400);color:#c62828;font:900 14px/1.05 "Trebuchet MS",Arial;
 display:flex;align-items:center;justify-content:center;text-align:center;transform:rotate(12deg);box-shadow:0 3px 0 #e65100,0 6px 10px rgba(0,0,0,.3);border:3px dashed #ff6f00}}
nav{{display:flex;flex-wrap:wrap;gap:2px;padding:6px 8px 0;background:linear-gradient(#0f4a8f,#0b3466)}}
nav a{{color:#fff;text-decoration:none;font:bold 12px Verdana;padding:7px 12px 6px;border-radius:8px 8px 0 0;background:linear-gradient(#ffb43d,#ff7b00);border:1px solid #c45a00;border-bottom:0;text-shadow:1px 1px 0 #a34a00}}
nav a:hover{{background:linear-gradient(#ffe066,#ffb000)}}
.bar{{display:flex;align-items:center;gap:10px;background:#ffefc2;border-bottom:1px solid #e3b44b;padding:6px 10px}}
.bar input{{flex:0 1 260px;font:12px Verdana;padding:3px 5px;border:2px inset #ccc}}
.bar button{{font:bold 11px Verdana;padding:3px 10px;background:linear-gradient(#fff,#ddd);border:2px outset #ddd;cursor:pointer}}
marquee{{flex:1;color:#b71c1c;font-weight:bold}}
.cols{{display:grid;grid-template-columns:200px 1fr 220px;gap:14px;padding:12px}}
.side h3,.box h2,.panel h3{{margin:0;color:#fff;font:bold 13px Verdana;padding:6px 9px;border-radius:7px 7px 0 0;background:linear-gradient(#5aa2ec,#1f63b8);text-shadow:1px 1px 0 #0b3466}}
.side ul,.panel ul,.panel ol{{margin:0;padding:6px 8px 8px 8px;list-style:none;border:1px solid #9cc0e6;border-top:0;background:#f2f8ff;border-radius:0 0 7px 7px}}
.panel ol{{list-style:decimal;padding-left:28px}}
.side li{{padding:3px 0;border-bottom:1px dotted #b9d3ee}} .side li a{{font-weight:bold;text-decoration:none}}
.side li a:hover,.panel a:hover{{text-decoration:underline;color:#e65100}}
.side small{{color:#777}}
.ic{{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:6px;background:var(--c);vertical-align:-1px;box-shadow:inset 0 -3px 0 rgba(0,0,0,.25),0 0 0 1px rgba(0,0,0,.25)}}
.panel{{margin-bottom:10px}} .panel li{{padding:2px 0}}
.feat{{border:2px solid #ff9a00;border-radius:9px;background:linear-gradient(#fff8e1,#ffe9a8);padding:12px;display:grid;grid-template-columns:300px 1fr;gap:12px;margin-bottom:12px}}
.feat img{{width:100%;aspect-ratio:4/3;object-fit:cover;border:3px solid #fff;box-shadow:0 0 0 1px #c98a00}}
.feat h2{{margin:0 0 4px;font:bold 20px "Trebuchet MS",Verdana;color:#c43e00}}
.play{{display:inline-block;margin-top:8px;font:900 15px "Trebuchet MS",Arial;color:#fff;text-decoration:none;padding:7px 18px;border-radius:20px;
 background:linear-gradient(#7ee05a,#2f9e17);border:2px solid #1f6e0e;text-shadow:1px 1px 0 #1f6e0e;box-shadow:0 2px 0 #1f6e0e}}
.play:hover{{background:linear-gradient(#a6f27c,#3cb81e)}}
.box{{margin-bottom:14px}} .box h2{{--c:#1f63b8;font-size:14px;background:linear-gradient(color-mix(in srgb,var(--c) 55%,#fff),var(--c))}}
.box h2 small{{float:right;font:normal 11px Verdana;opacity:.9}}
.box h2 .ic{{background:#fff}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px 10px;border:1px solid #c9d9ea;border-top:0;padding:10px;border-radius:0 0 7px 7px;background:#fff}}
.g{{text-decoration:none;color:#0645ad;display:block}}
.t{{display:block;position:relative;border:1px solid #9cb6d2;padding:2px;background:#fff;box-shadow:1px 1px 0 #c9d9ea}}
.t img{{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;background:#dde}}
.g:hover .t{{border-color:#ff8a00;box-shadow:0 0 0 2px #ffcc66}}
.g b{{display:block;margin-top:4px;font-size:11px;text-decoration:underline}} .g:hover b{{color:#e65100}}
.g i{{display:block;font-style:normal;font-size:10px;color:#666}}
.nb{{position:absolute;top:-6px;right:-6px;background:#e53935;color:#fff;font:bold 9px Verdana;font-style:normal;padding:2px 4px;border-radius:3px;transform:rotate(8deg);box-shadow:1px 1px 0 #7f0000}}
.mb{{position:absolute;left:4px;bottom:4px;font:bold 9px Verdana;font-style:normal;padding:2px 5px;border-radius:9px;color:#fff;box-shadow:0 1px 0 rgba(0,0,0,.4)}}.mb.y{{background:#2e9e2e}}.mb.n{{background:#555}}.mb.m{{background:#b98900}}
.ph{{font:bold 11px Verdana;white-space:nowrap;cursor:pointer}}
.top{{display:block;text-align:right;font-size:10px;margin-top:3px}}
.flash{{border:1px solid #ccc;background:#fafafa;padding:8px;font-size:11px;color:#555;text-align:center}}
.flash b{{display:block;color:#c62828;font-size:12px;margin-bottom:3px}}
footer{{background:#0b3466;color:#bcd3f0;font-size:10px;text-align:center;padding:10px}}
.hide{{display:none!important}}
.viral{{border:3px solid #e53935;border-radius:10px;padding:0;box-shadow:0 0 0 3px #ffcc80}} .viral h2{{font-size:17px;padding:9px 11px;border-radius:7px 7px 0 0}}
.viral .vsub{{margin:0;padding:7px 11px;background:#fff3e0;font-weight:bold;color:#b71c1c;border-bottom:1px solid #ffcc80}}
.viral .grid{{grid-template-columns:repeat(auto-fill,minmax(170px,1fr));border:0;background:#fffaf2}} .viral .g b{{font-size:12px}}
nav a.hot{{background:linear-gradient(#ff6b5b,#d81b1b);border-color:#8e0000;text-shadow:1px 1px 0 #7f0000}}
@media (max-width:820px){{.cols{{grid-template-columns:minmax(0,1fr)}}main{{min-width:0}}.slogan{{font-size:10px;right:90px}}.feat img{{max-width:320px}}.grid{{grid-template-columns:repeat(auto-fill,minmax(96px,1fr))}}.side,.right{{order:2}}.feat{{grid-template-columns:1fr}}.logo{{font-size:38px}}.badge{{width:70px;height:70px;font-size:11px}}marquee{{display:none}}.viral .grid{{grid-template-columns:repeat(auto-fill,minmax(130px,1fr))}}.viral h2{{font-size:14px}}.bar{{flex-wrap:wrap}}}}
</style></head><body><div class="wrap">
<header><div class="cloud" style="left:38%;top:24px;width:70px"></div><div class="cloud" style="left:62%;top:44px;width:56px"></div><div class="cloud" style="left:52%;top:12px;width:44px"></div>
<div class="logo">Mega<span>Clip</span></div><div class="slogan">Free online games! No downloads, no Flash Player needed!</div>
<div class="badge">{len(games)}<br>FREE<br>GAMES!</div></header>
<nav><a class="hot" href="#viral">&#128293; Viral {len(viral)}</a>{"".join(f'<a href="#{k}">{E(l)}</a>' for k, l, _ in cats[:8])}</nav>
<div class="bar"><input id="q" type="search" placeholder="Search games..." aria-label="Search games"><button id="go">Search</button>
<label class="ph"><input type="checkbox" id="ph"> &#128241; Phone-friendly only</label><marquee scrollamount="4">&#9733; NEW GAMES ADDED! &#9733; {ticker} &#9733;</marquee></div>
<div class="cols">
<aside class="side"><h3>Game Categories</h3><ul><li><a href="#viral"><span class="ic" style="--c:#e53935"></span>&#128293; The Viral {len(viral)}</a> <small>({len(viral)})</small></li>{side}</ul>
<div class="panel" style="margin-top:10px"><div class="flash"><b>Play them while you can!</b>Some of these games get taken down by the big publishers, so if one stops working, try another.</div></div></aside>
<main>
{viralbox}
<div class="feat"><img src="{E(feat["img"])}" alt=""><div><h2>Featured Game: {E(feat["name"])}</h2>
<p>{E(feat.get("blurb","The one that started it all. Black Ops zombies, running right in your web browser. No install, no disc, just click and play."))}</p>
<a class="play" href="{E(feat["url"])}" target="_blank" rel="noopener noreferrer">&#9654; PLAY NOW!</a></div></div>
<p id="nores" class="hide" style="padding:10px;background:#ffefc2">No games found. Try another word!</p>
{boxes}</main>
<aside class="right"><div class="panel"><h3>&#9733; Top 10 Games</h3><ol>{toplist}</ol></div>
<div class="panel"><h3>New This Week</h3><ul>{freshlist}</ul></div>
<div class="panel"><div class="flash"><b>Tips</b>Green &#128241; = works on a phone. Grey &#128187; = needs a computer. Games work best in Chrome. Some ask for files from a game you own: skip those. Big games can take a minute to load, so wait for the bar!</div></div></aside>
</div>
<footer>MegaClip &middot; last updated {updated} &middot; Games belong to their makers and are linked, not hosted here.</footer></div>
<script>
const q=document.getElementById('q'),cards=[...document.querySelectorAll('.g')],boxes=[...document.querySelectorAll('.box')],nr=document.getElementById('nores');
const ph=document.getElementById('ph');
function f(){{const v=q.value.trim().toLowerCase(),po=ph.checked;let any=0;cards.forEach(c=>c.classList.toggle('hide',(!!v&&!c.dataset.s.includes(v))||(po&&c.dataset.m!=='yes')));
boxes.forEach(b=>{{const n=b.querySelectorAll('.g:not(.hide)').length;b.classList.toggle('hide',!n);any+=n}});nr.classList.toggle('hide',!!any||!(v||po))}}
ph.addEventListener('change',f);
q.addEventListener('input',f);document.getElementById('go').onclick=f;
</script></body></html>'''
open("index.html", "w").write(page)
# Security headers: allow only this page's own inline scripts (by hash), no 'unsafe-inline' for scripts
import re, hashlib, base64
hashes = " ".join("'sha256-" + base64.b64encode(hashlib.sha256(m.encode()).digest()).decode() + "'"
                  for m in re.findall(r"<script>(.*?)</script>", page, re.S))
csp = ("default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' " + hashes +
       "; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'; object-src 'none'; upgrade-insecure-requests")
hdr = [("Content-Security-Policy", csp), ("X-Frame-Options", "DENY"), ("X-Content-Type-Options", "nosniff"),
       ("Referrer-Policy", "strict-origin-when-cross-origin"), ("Cross-Origin-Resource-Policy", "same-origin"),
       ("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()"),
       ("Strict-Transport-Security", "max-age=63072000; includeSubDomains")]
json.dump({"$schema": "https://openapi.vercel.sh/vercel.json",
           "headers": [{"source": "/(.*)", "headers": [{"key": k, "value": v} for k, v in hdr]}]},
          open("vercel.json", "w"), indent=1)
print("ok", len(games), "games,", len(cats), "categories")
