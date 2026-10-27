"""Build a static academic website. Run from any directory."""
from pathlib import Path
import json
import shutil
import re
import html
from datetime import date
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
    return f'<div class="links"><a href="contact.html">Contact ↗</a><a href="{e(C["github"])}">GitHub ↗</a><a href="{e(C["linkedin"])}">LinkedIn ↗</a><a href="assets/Yentl-Collin-CV.pdf">CV ↗</a></div>'


def page(title, body, filename, active='Home', description=None):
    description = description or 'Yentl Collin — research in generative modeling, efficient foundation models, and interpretable time-series learning.'
    nav = ''.join(f'<a href="{url}"'+(' aria-current="page"' if active == label else '')+f'>{label}</a>' for label, url in [('Home','index.html'),('Publications','publications.html'),('Notes & writing','notes.html'),('Contact','contact.html')])
    # All generated pages live at the root; this also works on project Pages URLs.
    doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} — Yentl Collin</title><meta name="description" content="{e(description)}"><meta name="theme-color" content="#faf9f6"><link rel="canonical" href="{e(C['site_url'])}/{filename}"><meta property="og:title" content="{e(title)} — Yentl Collin"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website"><link rel="stylesheet" href="assets/style.css"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"></head>
<body><a class="skip" href="#main">Skip to content</a><header><nav class="nav" aria-label="Main navigation"><a class="brand" href="index.html">Yentl Collin</a><div class="navlinks">{nav}<a class="cv" href="assets/Yentl-Collin-CV.pdf">CV ↗</a></div></nav></header><main id="main">{body}</main><footer><span>© {date.today().year} Yentl Collin</span><span><a href="{e(C['github'])}">GitHub</a> &nbsp; / &nbsp; <a href="{e(C['linkedin'])}">LinkedIn</a> &nbsp; / &nbsp; <a href="mailto:{e(C['email'])}">Email</a></span></footer></body></html>'''
    (OUT / filename).write_text(doc)


def papers():
    result = ''
    for p in C['publications']:
        code = f'<a href="{e(p["code"])}">Code ↗</a>' if p.get('code') else ''
        result += f'''<article class="paper"><div class="year">{e(p['year'])}</div><div><h3><a href="{e(p['paper'])}">{e(p['title'])}</a></h3><div class="venue">{e(p['venue'])} &nbsp; · &nbsp; {e(p['context'])}</div><p>{e(p['description'])}</p><div class="links"><a href="{e(p['paper'])}">Paper ↗</a>{code}</div></div></article>'''
    return result


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
    portrait_html = f'<img src="{e(portrait)}" alt="Portrait of Yentl Collin" width="500" height="625">'
else:
    portrait_html = '<div class="portrait-placeholder" role="img" aria-label="Yentl Collin — portrait to come"><span>YC</span><small>Portrait to come</small></div>'
research = ''.join(f'<div><h3>{e(i["title"])}</h3><p>{e(i["text"])}</p></div>' for i in C['interests'])
if notes:
    latest = notes[0]
    note_teaser = f'<p class="subtle">{e(latest["date"])}</p><h3><a href="{latest["url"]}">{e(latest["title"])}</a></h3><p>{e(latest.get("summary", ""))}</p>'
else:
    note_teaser = '<div class="empty-note"><p>A space for research notes, ideas, and things I find interesting.</p><p>First notes coming soon.</p></div>'
page('Home', f'''<div class="hero"><div class="hero-copy"><p class="kicker">Machine learning · Research</p><h1>{e(C['name'])}</h1><p class="role">{e(C['role'])}</p><div class="intro">{''.join('<p>'+e(p)+'</p>' for p in C['intro'])}</div>{links()}</div><figure class="portrait">{portrait_html}</figure></div>
<section aria-labelledby="research-title"><div class="section-head"><h2 id="research-title">Research interests</h2></div><div class="research-grid">{research}</div></section>
<section aria-labelledby="papers-title"><div class="section-head"><h2 id="papers-title">Selected publications</h2><a href="publications.html">All publications ↗</a></div>{papers()}</section>
<div class="bottom-grid"><section><h2>Notes & writing</h2>{note_teaser}<a class="arrow-link" href="notes.html">Explore the notebook ↗</a></section><section><h2>A little beyond research</h2><p>{e(C['outside'])}</p><a class="arrow-link" href="contact.html">Get in touch ↗</a></section></div>''', 'index.html')
page('Publications', f'<div class="page-intro"><p class="kicker">Research</p><h1>Publications</h1><p>My work on generative modeling and interpretable time-series learning.</p></div>{papers()}', 'publications.html', 'Publications')
listing = ''.join(f'<a class="note-row" href="{n["url"]}"><span class="subtle">{e(n["date"])}</span><h2>{e(n["title"])}</h2><p>{e(n.get("summary", ""))}</p></a>' for n in notes)
page('Notes & writing', f'<div class="page-intro"><p class="kicker">Notebook</p><h1>Notes & writing</h1><p>Research notes, ideas in progress, and things I find interesting.</p></div>'+(listing or '<section class="empty-note"><h2>First notes coming soon.</h2><p class="subtle" style="margin-top:16px">This space will grow with readings, experiments, and questions along the way.</p></section>'), 'notes.html', 'Notes & writing')
contacts = [('Email',f'mailto:{C["email"]}',C['email']),('GitHub',C['github'],'github.com/YentlCollin'),('LinkedIn',C['linkedin'],'Yentl Collin'),('Phone','tel:'+re.sub(r'\s','',C['phone']),C['phone'])]
contact_html = ''.join(f'<div class="contact-item"><dt>{e(label)}</dt><dd><a href="{e(url)}">{e(text)}</a></dd></div>' for label,url,text in contacts)
page('Contact', f'<div class="page-intro"><p class="kicker">Say hello</p><h1>Contact</h1><p>For research discussions, collaborations, or a conversation about shared interests, feel free to get in touch.</p></div><dl class="contact-grid">{contact_html}</dl>', 'contact.html', 'Contact')
page('Page not found', '<div class="page-intro"><p class="kicker">404</p><h1>Page not found.</h1><p>This page may have moved.</p><a href="index.html">Back to the homepage ↗</a></div>', '404.html', '')
(OUT / '.nojekyll').touch()
(OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {C["site_url"]}/sitemap.xml\n')
urls = ['index.html','publications.html','notes.html','contact.html']+[n['url'] for n in notes]
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{e(C["site_url"])}/{u}</loc></url>' for u in urls)+'</urlset>')
print(f'Built {len(urls)} pages in {OUT}')
