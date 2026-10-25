"""Build index.html from games.json in a mid-2000s web-games-portal style.
Run: python3 arcade.py  (then vercel deploy --prod --yes)"""
import json, html, re
from datetime import date

E = html.escape
KOFI = "https://ko-fi.com/digitalelmo"
# Email address is never in the HTML: the script assembles it only when someone taps a mail button (stops address-harvesting bots)
MAILJS = """<script>
const EMR='em.notorp@omle_latigid',SUB={s:['MegaClip game suggestion','Game name:\\nLink where you play it:\\nDid you make it? (yes/no):\\nDoes it work on a phone? (yes/no/not sure):\\nAnything else:\\n'],f:['MegaClip: remove or fix a game','Which game:\\nWhat should happen (remove / change link / change name or picture / broken link):\\nIs it your game? (yes/no):\\nDetails:\\n']};
const em=()=>EMR.split('').reverse().join('');
document.querySelectorAll('[data-reveal]').forEach(b=>b.addEventListener('click',()=>{const k=b.dataset.reveal,box=document.getElementById('mail-'+k),m=em();
box.querySelector('.addr').textContent=m;box.querySelector('.open').href='mailto:'+m+'?subject='+encodeURIComponent(SUB[k][0])+'&body='+encodeURIComponent(SUB[k][1]);box.hidden=!box.hidden;if(!box.hidden)box.scrollIntoView({block:'nearest',behavior:'smooth'})}));
document.querySelectorAll('.copy').forEach(b=>b.addEventListener('click',()=>{navigator.clipboard.writeText(em()).then(()=>{b.textContent='Copied!'})}));
</script>"""
MAILCSS = """.strip{display:flex;gap:6px;flex:0 0 auto}.sm{display:none}
.strip a,.strip button{font:900 12px "Trebuchet MS",Arial,sans-serif;color:#fff;text-decoration:none;padding:4px 14px;border-radius:14px;cursor:pointer;border:1px solid;box-shadow:0 1px 0 rgba(0,0,0,.35);text-shadow:1px 1px 0 rgba(0,0,0,.3);white-space:nowrap}
.strip .s1{background:linear-gradient(#ff8a7a,#e8473b);border-color:#a8261d}.strip .s2{background:linear-gradient(#5aa2ec,#1f63b8);border-color:#0b3466}.strip .s3{background:linear-gradient(#7ee05a,#2f9e17);border-color:#1f6e0e}
.strip a:hover,.strip button:hover{filter:brightness(1.12)}
.mailbox{margin:10px auto;max-width:560px;border:2px solid #1f63b8;border-radius:9px;background:#f2f8ff;padding:10px 14px;text-align:center;font-size:12px}
.mailbox .addr{font-size:15px;color:#0b3466;word-break:break-all}.mailbox p{margin:4px 0 8px}
.mailbox .open{display:inline-block;font:900 13px "Trebuchet MS",Arial;color:#fff;text-decoration:none;padding:6px 14px;border-radius:18px;background:linear-gradient(#5aa2ec,#1f63b8);border:2px solid #0b3466;margin:2px}
.mailbox .copy{font:bold 12px Verdana;padding:5px 12px;border-radius:18px;background:linear-gradient(#fff,#ddd);border:2px solid #999;cursor:pointer;margin:2px}
[hidden]{display:none!important}
@media (max-width:820px){.lg{display:none}.sm{display:inline}
 header{height:84px}header:before{bottom:-72px}.logo{font-size:32px!important;top:12px;left:14px}.slogan{top:56px;left:16px;font-size:9px!important;right:84px}
 .badge{width:58px!important;height:58px!important;font-size:9px!important;top:12px;right:12px}
 nav{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;padding:5px 6px 0}nav::-webkit-scrollbar{display:none}nav a{flex:0 0 auto;font-size:11px;padding:6px 10px 5px}
 .bar{flex-wrap:wrap;gap:6px;padding:5px 8px}.bar input{flex:1 1 0;min-width:0}.bar button{padding:3px 8px}.ph{font-size:10px}
 .strip{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;flex:1 1 100%;padding:2px 0 1px}.strip a,.strip button{padding:5px 4px;font-size:12px;text-align:center}
 .mailbox{margin:8px}}"""
def MAILBOX(k, intro):
    return (f'<div class="mailbox" id="mail-{k}" hidden><p>{intro}</p><p>&#128231; <b class="addr"></b></p>'
            '<a class="open" href="#">&#9993; Open my email app</a> <button type="button" class="copy">Copy address</button></div>')
SUGBOX = MAILBOX("s", "Send us the <b>game name</b>, the <b>link</b>, whether <b>you made it</b> and if it <b>works on a phone</b>:")
FIXBOX = MAILBOX("f", "Tell us <b>which game</b> and what should happen (remove it, change the link, or fix the name or picture):")
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
import unicodedata
def slugify(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:70] or "game"
used = {g["slug"] for g in games if g.get("slug")}
for g in games:  # each game keeps its page address forever once given one
    if not g.get("slug"):
        s, i = slugify(g["name"]), 2
        while s in used: s, i = f"{slugify(g['name'])}-{i}", i + 1
        g["slug"] = s; used.add(s)
json.dump(games, open("games.json", "w"), ensure_ascii=False, indent=1)
decomps = json.load(open("decomps.json"))
poke = json.load(open("pokemon.json"))
import pages, pokemon_pages
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
    search = " ".join([g["name"], g["host"], LABEL[g["cat"]], g.get("based_on", ""), " ".join(g.get("tags", []))]).lower()
    return (f'<div class="c" data-m="{m}" data-s="{E(search)}"><a class="g" href="{E(g["url"])}" target="_blank" rel="noopener noreferrer">'
            f'<span class="t"><img src="/{E(g["img"])}" alt="" loading="lazy">{new}{mob}</span>'
            f'<b>{E(g["name"])}</b>{note}</a><a class="inf" href="/game/{g["slug"]}">&#9432; info</a></div>')


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
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="MegaClip: free browser games, no downloads. Hand-picked new web games, retro classics and fan projects you can play in a tab."><link rel="canonical" href="https://megaclip.games/"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><meta name="theme-color" content="#1e63b5"><script>window.va=window.va||function(){{(window.vaq=window.vaq||[]).push(arguments)}};</script><script defer src="/_vercel/insights/script.js"></script>
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
.g{{text-decoration:none;color:#0645ad;display:block}}.c{{min-width:0}}.inf{{font-size:10px;color:#777;text-decoration:none}}.inf:hover{{color:#e65100;text-decoration:underline}}
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
.kofi{{display:block;margin:8px 0 2px;text-align:center;font:900 13px "Trebuchet MS",Arial;color:#fff!important;text-decoration:none;padding:8px 10px;border-radius:20px;background:linear-gradient(#ff8a7a,#e8473b);border:2px solid #a8261d;text-shadow:1px 1px 0 #a8261d;box-shadow:0 2px 0 #a8261d}}.kofi:hover{{background:linear-gradient(#ffa597,#f25a4e)}}
.viral{{border:3px solid #e53935;border-radius:10px;padding:0;box-shadow:0 0 0 3px #ffcc80}} .viral h2{{font-size:17px;padding:9px 11px;border-radius:7px 7px 0 0}}
.viral .vsub{{margin:0;padding:7px 11px;background:#fff3e0;font-weight:bold;color:#b71c1c;border-bottom:1px solid #ffcc80}}
.viral .grid{{grid-template-columns:repeat(auto-fill,minmax(170px,1fr));border:0;background:#fffaf2}} .viral .g b{{font-size:12px}}
nav a.hot{{background:linear-gradient(#ff6b5b,#d81b1b);border-color:#8e0000;text-shadow:1px 1px 0 #7f0000}}
@media (max-width:820px){{.cols{{grid-template-columns:minmax(0,1fr)}}main{{min-width:0}}.slogan{{font-size:10px;right:90px}}.feat img{{max-width:320px}}.grid{{grid-template-columns:repeat(auto-fill,minmax(96px,1fr))}}.side,.right{{order:2}}.feat{{grid-template-columns:1fr}}.logo{{font-size:38px}}.badge{{width:70px;height:70px;font-size:11px}}marquee{{display:none}}.viral .grid{{grid-template-columns:repeat(auto-fill,minmax(130px,1fr))}}.viral h2{{font-size:14px}}.bar{{flex-wrap:wrap}}}}
{MAILCSS}
{pages.CART_CSS}
</style></head><body><div class="wrap">
<header><div class="cloud" style="left:38%;top:24px;width:70px"></div><div class="cloud" style="left:62%;top:44px;width:56px"></div><div class="cloud" style="left:52%;top:12px;width:44px"></div>
<div class="logo">Mega<span>Clip</span></div><div class="slogan">Free online games! No downloads, no Flash Player needed!</div>
<div class="badge">{len(games)}<br>FREE<br>GAMES!</div></header>
<nav><a class="hot" href="#viral">&#128293; Viral {len(viral)}</a><a class="hot" href="/decomps">&#128190; PC Ports</a><a class="hot" href="/pokemon">&#9889; Pok&eacute;mon</a>{"".join(f'<a href="#{k}">{E(l)}</a>' for k, l, _ in cats[:8])}</nav>
<div class="bar"><input id="q" type="search" placeholder="Search games..." aria-label="Search games"><button id="go">Search</button>
<label class="ph"><input type="checkbox" id="ph"> &#128241; Phone-friendly<span class="lg"> only</span></label><marquee scrollamount="4">&#9733; NEW GAMES ADDED! &#9733; {ticker} &#9733;</marquee><div class="strip"><a class="s1" href="{KOFI}" target="_blank" rel="noopener noreferrer">&#9749; Support<span class="lg"> MegaClip</span></a><button type="button" class="s2" data-reveal="s">&#128236; Suggest<span class="lg"> a game</span></button><a class="s3" href="/about">&#128737; <span class="lg">Is it safe?</span><span class="sm">Safe?</span></a></div></div>
{SUGBOX}
<div class="cols">
<aside class="side"><h3>Game Categories</h3><ul><li><a href="#viral"><span class="ic" style="--c:#e53935"></span>&#128293; The Viral {len(viral)}</a> <small>({len(viral)})</small></li>{side}<li><a href="/decomps"><span class="ic" style="--c:#0b3466"></span>&#128190; PC Ports</a> <small>({len(decomps):,})</small></li><li><a href="/pokemon"><span class="ic" style="--c:#e53935"></span>&#9889; Pok&eacute;mon Fan Games</a> <small>({len(poke):,})</small></li></ul>
<div class="panel" style="margin-top:10px"><div class="flash"><b>Play them while you can!</b>Some of these games get taken down by the big publishers, so if one stops working, try another.</div></div></aside>
<main id="home">
{viralbox}
{pages.home_banner(decomps)}
{pokemon_pages.home_strip(poke)}
<div class="feat"><img src="/{E(feat["img"])}" alt=""><div><h2>Featured Game: {E(feat["name"])}</h2>
<p>{E(feat.get("blurb","The one that started it all. Black Ops zombies, running right in your web browser. No install, no disc, just click and play."))}</p>
<a class="play" href="{E(feat["url"])}" target="_blank" rel="noopener noreferrer">&#9654; PLAY NOW!</a></div></div>
<p id="nores" class="hide" style="padding:10px;background:#ffefc2">No games found. Try another word!</p>
{boxes}
<section class="box" id="dbox" hidden><h2 style="--c:#0b3466"><span class="ic"></span>&#128190; PC Ports: download, bring your own copy of the game<small id="dn"></small></h2><ul class="dlist" id="dl"></ul></section>
<section class="box" id="pbox" hidden><h2 style="--c:#e53935"><span class="ic"></span>&#9889; Pok&eacute;mon fan games and ROM hacks<small id="pn"></small></h2><ul class="dlist" id="pl"></ul></section></main>
<aside class="right"><div class="panel"><h3>&#9749; Keep MegaClip running</h3><ul><li>MegaClip is free and staying free. No ads, ever. If it gave you a new favourite game, you can buy me a coffee.<a class="kofi" href="https://ko-fi.com/digitalelmo" target="_blank" rel="noopener noreferrer">&#9749; Support on Ko-fi</a></li></ul></div><div class="panel"><h3>&#9733; Top 10 Games</h3><ol>{toplist}</ol></div>
<div class="panel"><h3>New This Week</h3><ul>{freshlist}</ul></div>
<div class="panel"><div class="flash"><b>Tips</b>Green &#128241; = works on a phone. Grey &#128187; = needs a computer. Games work best in Chrome. Some ask for files from a game you own: skip those. Big games can take a minute to load, so wait for the bar!</div></div></aside>
</div>
<footer>MegaClip &middot; last updated {updated} &middot; Games belong to their makers and are linked, not hosted here. &middot; <a href="/about" style="color:#fff">About &amp; Safety</a> &middot; <a href="https://ko-fi.com/digitalelmo" target="_blank" rel="noopener noreferrer" style="color:#fff">&#9749; Support MegaClip</a> &middot; <a href="https://github.com/DigitalElmo/megaclip" target="_blank" rel="noopener noreferrer" style="color:#fff">View the code on GitHub</a></footer></div>
<script src="/search.js" defer></script>{MAILJS}</body></html>'''
open("index.html", "w").write(page)

css = re.search(r"<style>(.*?)</style>", page, re.S).group(1)
head = page.split("<title>")[0].replace('<link rel="canonical" href="https://megaclip.games/">', '<link rel="canonical" href="https://megaclip.games/about">').replace(
    'content="MegaClip: free browser games, no downloads. Hand-picked new web games, retro classics and fan projects you can play in a tab."',
    'content="How MegaClip works, why it is safe, and how to suggest a game or ask for one to be removed."')
gh = "https://github.com/DigitalElmo/megaclip"
about = f'''{head}<title>About &amp; Safety :: MegaClip</title><style>{css}
.doc{{max-width:820px;margin:0 auto;padding:16px 14px 24px;font-size:13px;line-height:1.55}}.doc .panel ul{{list-style:disc;padding-left:26px}}.doc .panel li{{padding:3px 0}}
.linkbtn{{background:none;border:0;padding:0;color:#0645ad;text-decoration:underline;cursor:pointer;font:inherit}}.doc h1{{font:bold 22px "Trebuchet MS",Verdana;color:#c43e00;margin:0 0 6px}}.doc p.lead{{margin:0 0 14px}}</style></head><body><div class="wrap">
<header><div class="cloud" style="left:38%;top:24px;width:70px"></div><div class="cloud" style="left:62%;top:44px;width:56px"></div>
<a href="/" style="text-decoration:none"><div class="logo">Mega<span>Clip</span></div></a><div class="slogan">Free online games! No downloads, no Flash Player needed!</div>
<div class="badge">{len(games)}<br>FREE<br>GAMES!</div></header>
<nav><a class="hot" href="/">&#9664; Back to the games</a></nav>
<div class="doc"><h1>About &amp; Safety</h1>
<p class="lead">MegaClip is a hand-picked list of {len(games)} games you can play straight in your browser. It's like a giant bookmarks page: every game runs on its maker's own website, and MegaClip just points you there.</p>
<div class="panel"><h3>What MegaClip does NOT do</h3><ul>
<li>No downloads. MegaClip never gives you a file to install or run.</li>
<li>No game files. Nothing is hosted here except this page and the little thumbnail pictures.</li>
<li>No ads, no cookies, no accounts, no logins, no tracking pixels.</li>
<li>We only count visits (Vercel Web Analytics, which uses no cookies and doesn't identify you).</li></ul></div>
<div class="panel"><h3>Don't take our word for it: check it yourself</h3><ul>
<li><a href="https://developer.mozilla.org/en-US/observatory/analyze?host=megaclip.games" target="_blank" rel="noopener noreferrer"><b>Mozilla Observatory</b></a>: the security grade for this site (it scores A+).</li>
<li><a href="https://transparencyreport.google.com/safe-browsing/search?url=megaclip.games" target="_blank" rel="noopener noreferrer"><b>Google Safe Browsing</b></a>: Google's check for unsafe sites.</li>
<li><a href="https://www.virustotal.com/gui/search/megaclip.games" target="_blank" rel="noopener noreferrer"><b>VirusTotal</b></a>: dozens of antivirus scanners at once.</li>
<li><a href="{gh}" target="_blank" rel="noopener noreferrer"><b>The code on GitHub</b></a>: every line of this site is public, so anyone can read exactly what it does.</li></ul></div>
<div class="panel"><h3>How we keep the links healthy</h3><ul>
<li>Every link is checked by a robot once a week. Dead links, and links that suddenly send you to a different website, get fixed or removed.</li>
<li>Games open in a new tab, walled off from this page, so a game's site can't touch MegaClip.</li>
<li>Remember: once you click a game, you're on someone else's website. Never type a password or card number into a game you don't trust.</li></ul></div>
<div class="panel"><h3>&#9749; Who pays for it?</h3><ul><li>MegaClip is free and has no ads. It's run by Digital Elmo, and kept going by people who chip in for a coffee. <a href="https://ko-fi.com/digitalelmo" target="_blank" rel="noopener noreferrer"><b>Support MegaClip on Ko-fi</b></a>. Totally optional: every game stays free either way.</li></ul></div><div class="panel"><h3>&#128236; Suggest a game</h3><ul>
<li>Made a browser game, or found one we're missing? <button type="button" class="linkbtn" data-reveal="s"><b>Tap here to email us</b></button>, or <a href="{gh}/issues/new?template=suggest-game.yml" target="_blank" rel="noopener noreferrer">post it on GitHub</a>.</li></ul>{SUGBOX}</div>
<div class="panel"><h3>Made a game that's listed here?</h3><ul>
<li>All games, names and pictures belong to the people who made them.</li>
<li>Want it removed, renamed, or the link changed? <button type="button" class="linkbtn" data-reveal="f"><b>Tap here to email us</b></button> (or <a href="{gh}/issues/new?template=remove-or-fix.yml" target="_blank" rel="noopener noreferrer">use GitHub</a>) and it'll be done quickly.</li></ul>{FIXBOX}</div>
</div>
<footer>MegaClip &middot; last updated {updated} &middot; <a href="/" style="color:#fff">All games</a> &middot; <a href="{gh}" target="_blank" rel="noopener noreferrer" style="color:#fff">View the code on GitHub</a></footer></div>{MAILJS}</body></html>'''
open("about.html", "w").write(about)
# Game pages, category pages, PC Ports section, search data (pages.py)
sub_header = (f'<header><div class="cloud" style="left:38%;top:24px;width:70px"></div><div class="cloud" style="left:62%;top:44px;width:56px"></div>'
              f'<a href="/" style="text-decoration:none"><div class="logo">Mega<span>Clip</span></div></a><div class="slogan">Free online games! No downloads, no Flash Player needed!</div>'
              f'<div class="badge">{len(games)}<br>FREE<br>GAMES!</div></header>'
              '<nav><a class="hot" href="/">&#9664; All games</a><a class="hot" href="/decomps">&#128190; PC Ports</a><a class="hot" href="/pokemon">&#9889; Pok&eacute;mon</a>'
              + "".join(f'<a href="/category/{k}">{E(l)}</a>' for k, l, _ in cats if k != "new") + '</nav>')
sub_bar = (f'<div class="bar"><input id="q" type="search" placeholder="Search games..." aria-label="Search games"><button id="go">Search</button>'
           f'<div class="strip" style="margin-left:auto"><a class="s1" href="{KOFI}" target="_blank" rel="noopener noreferrer">&#9749; Support<span class="lg"> MegaClip</span></a><a class="s3" href="/about">&#128737; <span class="lg">Is it safe?</span><span class="sm">Safe?</span></a></div></div>')
sub_footer = (f'<footer>MegaClip &middot; last updated {updated} &middot; Games belong to their makers and are linked, not hosted here. &middot; '
              f'<a href="/" style="color:#fff">All games</a> &middot; <a href="/decomps" style="color:#fff">PC Ports</a> &middot; <a href="/pokemon" style="color:#fff">Pok&eacute;mon Fan Games</a> &middot; <a href="/about" style="color:#fff">About &amp; Safety</a></footer>')
extra, paths = pages.build(games, decomps, css, sub_header, sub_bar, sub_footer, thumb, CATS, LABEL, poke)
for g in games:
    g.pop("_decomp", None)
# Sitemap: home, about, and every generated page
open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"<url><loc>https://megaclip.games{p}</loc></url>\n" for p in ["/", "/about"] + paths) + "</urlset>\n")
# Security headers: allow only these pages' own inline scripts (by hash), no 'unsafe-inline' for scripts
import re, hashlib, base64
hashes = " ".join("'sha256-" + base64.b64encode(hashlib.sha256(m.encode()).digest()).decode() + "'"
                  for m in dict.fromkeys(re.findall(r"<script>(.*?)</script>", page + about + "".join(extra), re.S)))
csp = ("default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' " + hashes +
       "; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'; object-src 'none'; upgrade-insecure-requests")
hdr = [("Content-Security-Policy", csp), ("X-Frame-Options", "DENY"), ("X-Content-Type-Options", "nosniff"),
       ("Referrer-Policy", "strict-origin-when-cross-origin"), ("Cross-Origin-Resource-Policy", "same-origin"),
       ("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()"),
       ("Strict-Transport-Security", "max-age=63072000; includeSubDomains")]
# Old game URLs that were renamed: send visitors (and Google) to the new page
REDIRECTS = [("/game/inxanitylabs-com-75-games-includes-paid-games-skip-those", "/game/inxanity-labs"),
             ("/game/bolt-pit", "/category/shoot")]
json.dump({"$schema": "https://openapi.vercel.sh/vercel.json", "cleanUrls": True,
           "redirects": [{"source": a, "destination": b, "permanent": True} for a, b in REDIRECTS],
           "headers": [{"source": "/(.*)", "headers": [{"key": k, "value": v} for k, v in hdr]}]},
          open("vercel.json", "w"), indent=1)
print("ok", len(games), "games,", len(cats), "categories,", len(paths), "extra pages")
