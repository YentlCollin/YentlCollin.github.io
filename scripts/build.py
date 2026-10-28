"""Build a static academic website. Run from any directory."""
from pathlib import Path
import json
import shutil
import re
import html
from datetime import date
from calendar import month_abbr
import markdown

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
C = json.loads((ROOT / 'content.json').read_text())
e = html.escape
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
shutil.copytree(ROOT / 'assets', OUT / 'assets')


def links():
    return f'<div class="links"><a href="mailto:{e(C["email"])}">Email</a><a href="{e(C["github"])}">GitHub</a><a href="{e(C["linkedin"])}">LinkedIn</a><a href="assets/Yentl-Collin-CV.pdf">CV <span aria-hidden="true">↗</span></a></div>'


def page(title, body, filename, active='Home', description=None):
    description = description or 'Yentl Collin — research in generative modeling, efficient foundation models, and interpretable time-series learning.'
    nav = ''.join(f'<a href="{url}"'+(' aria-current="page"' if active == label else '')+f'>{label}</a>' for label, url in [('Home','index.html'),('Publications','publications.html'),('Notes & writing','notes.html'),('Contact','contact.html')])
    doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} — Yentl Collin</title><meta name="description" content="{e(description)}"><meta name="theme-color" content="#faf9f5"><link rel="canonical" href="{e(C['site_url'])}/{filename}"><meta property="og:title" content="{e(title)} — Yentl Collin"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website"><link rel="preload" href="assets/fonts/font-4.ttf" as="font" type="font/ttf" crossorigin><link rel="stylesheet" href="assets/style.css?v=4"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"></head>
<body><a class="skip" href="#main">Skip to content</a><header class="site-header"><nav class="nav" aria-label="Main navigation"><a class="brand" href="index.html">Yentl Collin<span style="color:#7f946e">.</span></a><div class="navlinks">{nav}<a class="cv" href="assets/Yentl-Collin-CV.pdf">CV ↗</a></div></nav></header><main id="main">{body}</main><footer><span>© {date.today().year} Yentl Collin</span><div class="footer-links"><a href="{e(C['github'])}">GitHub</a><a href="{e(C['linkedin'])}">LinkedIn</a><a href="mailto:{e(C['email'])}">Email</a></div></footer></body></html>'''
    (OUT / filename).write_text(doc)


def papers():
    result = ''
    for p in C['publications']:
        code = f'<a href="{e(p["code"])}">Code <span aria-hidden="true">↗</span></a>' if p.get('code') else ''
        authors = e(p.get('authors', '')).replace('Yentl Collin', '<strong>Yentl Collin</strong>')
        image_class = ' ssm' if p.get('image','').endswith('ssm-cgm.png') else ''
        result += f'''<article class="paper"><a class="paper-figure{image_class}" href="{e(p['paper'])}" tabindex="-1" aria-hidden="true"><img src="{e(p['image'])}" alt="" width="640" height="400" loading="lazy"></a><div><div class="paper-meta"><span>{e(p['year'])}</span><span aria-hidden="true">/</span><span class="venue">{e(p['venue'])}</span></div><h3><a href="{e(p['paper'])}">{e(p['title'])}</a></h3><p class="authors">{authors}</p><p class="paper-description">{e(p['description'])}</p><div class="links"><a href="{e(p['paper'])}">Paper <span aria-hidden="true">↗</span></a>{code}</div></div></article>'''
    return result


def news_section():
    items = sorted(C.get('news', []), key=lambda n: n['date'], reverse=True)
    if not items:
        return ''
    rows = []
    for item in items:
        raw_date = item['date']
        if not re.fullmatch(r'\d{4}-\d{2}(?:-\d{2})?', raw_date):
            raise ValueError('News dates must use YYYY-MM or YYYY-MM-DD')
        parsed_date = date.fromisoformat(raw_date + '-01' if len(raw_date) == 7 else raw_date)
        label = f'{month_abbr[parsed_date.month]} {parsed_date.year}'
        category = item.get('category', '')
        category_class = ' contribution' if category == 'Contribution' else ''
        rows.append(f'''<li class="news-item"><time datetime="{e(raw_date)}">{label}</time><div class="news-copy"><div class="news-heading"><h3><a href="{e(item['url'])}">{e(item['title'])} <span aria-hidden="true">↗</span></a></h3><span class="news-category{category_class}">{e(category)}</span></div><p>{e(item['description'])}</p></div></li>''')
    return '<section class="news-section" id="news" aria-labelledby="news-title"><div class="section-head"><h2 id="news-title">News &amp; releases</h2></div><ul class="news-list">' + ''.join(rows) + '</ul></section>'


notes = []
for path in (ROOT / 'notes').glob('*.md'):
    raw = path.read_text()
    if not raw.startswith('---\n'):
        raise ValueError(f'{path.name}: expected YAML-style metadata between --- lines')
    _, metadata, body = raw.split('---', 2)
    meta = dict(line.split(':', 1) for line in metadata.strip().splitlines() if ':' in line)
    meta = {k.strip(): v.strip().strip('"') for k,v in meta.items()}
    if meta.get('draft', 'false').lower() == 'true':
        continue
    if not meta.get('title') or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', meta.get('date', '')):
        raise ValueError(f'{path.name}: title and YYYY-MM-DD date are required')
    slug = path.stem
    if not re.fullmatch('[a-z0-9-]+', slug):
        raise ValueError(f'{path.name}: use lowercase letters, numbers, and hyphens')
    filename = f'note-{slug}.html'
    rendered = markdown.markdown(body, extensions=['fenced_code','tables','sane_lists'])
    page(meta['title'], f'<div class="page-intro"><a href="notes.html">← All notes</a><p class="kicker" style="margin-top:28px">{e(meta["date"])}</p><h1>{e(meta["title"])}</h1><p>{e(meta.get("summary", ""))}</p></div><article class="prose">{rendered}</article>', filename, 'Notes & writing', meta.get('summary'))
    notes.append({**meta, 'url': filename})
notes.sort(key=lambda n:n['date'], reverse=True)

portrait = C.get('portrait')
if portrait:
    if not (ROOT / portrait).is_file() or not portrait.startswith('assets/'):
        raise ValueError('portrait must point to an existing file in assets/')
    hero_image = f'<figure class="hero-art portrait"><div class="art-frame"><img src="{e(portrait)}" alt="Portrait of Yentl Collin" width="1122" height="1402" fetchpriority="high"></div></figure>'
else:
    hero_image = '<figure class="hero-art"><div class="art-frame"><img src="assets/research/flow-map.svg" alt="Conceptual illustration of a teacher trajectory and a learned flow map" width="640" height="400"></div><figcaption>Flow matching & generative modeling</figcaption></figure>'
research = ''.join(f'<span>{e(i["title"])}</span>' for i in C['interests'])
if notes:
    latest = notes[0]
    note_teaser = f'<p class="kicker">{e(latest["date"])}</p><h3><a href="{latest["url"]}">{e(latest["title"])}</a></h3><p>{e(latest.get("summary", ""))}</p>'
else:
    note_teaser = '<div class="empty-note"><p>A notebook for ideas worth keeping.</p><p class="subtle">Research notes, readings, and occasional detours.<br>First entries coming soon.</p></div>'
page('Home', f'''<div class="hero"><div class="hero-copy"><p class="kicker">Machine learning research</p><h1>{e(C['name'])}</h1><p class="role">{e(C['role'])}</p><div class="intro">{''.join('<p>'+e(p)+'</p>' for p in C['intro'])}</div>{links()}</div>{hero_image}</div>
<div class="research-line"><h2>Research interests</h2><div class="topics">{research}</div></div>
{news_section()}
<section class="publications-section" aria-labelledby="papers-title"><div class="section-head"><h2 id="papers-title">Selected publications</h2><a href="publications.html">All publications <span aria-hidden="true">↗</span></a></div>{papers()}</section>
<div class="lower-grid"><section><h2>Notes & writing</h2>{note_teaser}</section></div>
<div class="contact-strip"><p>Always happy to talk research.</p><a href="mailto:{e(C['email'])}">{e(C['email'])} &nbsp; ↗</a></div>''', 'index.html')
page('Publications', f'<div class="page-intro"><p class="kicker">Research</p><h1>Publications</h1><p>Selected work on generative models, efficient inference, and interpretable time-series learning.</p></div>{papers()}<p class="authors" style="margin-top:25px">* Equal contribution.</p>', 'publications.html', 'Publications')
listing = ''.join(f'<a class="note-row" href="{n["url"]}"><time datetime="{e(n["date"])}">{e(n["date"])}</time><div><h2>{e(n["title"])}</h2><p>{e(n.get("summary", ""))}</p></div></a>' for n in notes)
page('Notes & writing', f'<div class="page-intro"><p class="kicker">The notebook</p><h1>Notes & writing</h1><p>A place for research notes, useful intuitions, and things I find interesting.</p></div>'+(listing or '<section class="writing-empty"><h2>A few thoughts, soon.</h2><p>This notebook is still taking shape. It will collect readings, experiments, and ideas along the way.</p><a href="index.html">Back to the homepage ↗</a></section>'), 'notes.html', 'Notes & writing')
contacts = [('Email',f'mailto:{C["email"]}',C['email']),('GitHub',C['github'],'YentlCollin ↗'),('LinkedIn',C['linkedin'],'Yentl Collin ↗'),('Phone','tel:'+re.sub(r'\s','',C['phone']),C['phone'])]
contact_html = ''.join(f'<div class="contact-item"><dt>{e(label)}</dt><dd><a href="{e(url)}">{e(text)}</a></dd></div>' for label,url,text in contacts)
page('Contact', f'<div class="page-intro"><p class="kicker">Get in touch</p><h1>Let’s talk.</h1><p>For research discussions, collaborations, or simply a shared interest.</p></div><div class="contact-layout"><dl class="contact-grid">{contact_html}</dl></div>', 'contact.html', 'Contact')
page('Page not found', '<div class="page-intro"><p class="kicker">404</p><h1>A wrong turn.</h1><p>This page may have moved.</p><a href="index.html">Back to the homepage ↗</a></div>', '404.html', '')
(OUT / '.nojekyll').touch()
(OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {C["site_url"]}/sitemap.xml\n')
urls = ['index.html','publications.html','notes.html','contact.html']+[n['url'] for n in notes]
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{e(C["site_url"])}/{u}</loc></url>' for u in urls)+'</urlset>')
print(f'Built {len(urls)} pages in {OUT}')
