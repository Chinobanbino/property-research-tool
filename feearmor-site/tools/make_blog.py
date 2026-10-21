import os, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blog_content import POSTS
# Reads the site's look from public/index.html and writes pages into public/blog
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
src = open(os.path.join(ROOT, 'index.html')).read()
style = '<link rel="stylesheet" href="/site.css">\n<style>\n</style>'
style = style.replace('</style>', '''  .nav-link { color: var(--text); font-weight: 700; font-size: 15px; text-decoration: none; min-height: 44px; display: inline-flex; align-items: center; }
  .nav-link:hover { color: var(--lime); }
  .crumb { font-size: 14px; color: var(--muted); margin-bottom: 12px; }
  .crumb a { color: var(--muted); }
  .byline { color: var(--muted); font-size: 15px; margin-bottom: 28px; }
  article h2 { font-size: 24px; margin: 32px 0 12px; }
  article ul { padding-left: 22px; margin: 0 0 16px; }
  article li { margin-bottom: 8px; }
  .callout { background: var(--surface); border-left: 4px solid var(--lime); border-radius: 10px; padding: 16px 18px; margin: 24px 0; }
  .cta-box { border: 2px solid var(--lime); border-radius: var(--radius); padding: 24px; margin-top: 40px; background: rgba(163,230,53,.06); }
  .cta-box h2 { margin-top: 0; }
  .post-list { display: grid; gap: 16px; margin-top: 24px; }
  .post-card { display: block; text-decoration: none; color: var(--text); }
  .post-card:hover { border-color: var(--lime); }
  .post-card h2 { font-size: 21px; margin-bottom: 8px; }
  .post-card p { color: var(--muted); margin: 0; }
  .post-card .more { color: var(--lime); font-weight: 700; margin-top: 10px; display: inline-block; }
  @media (max-width: 400px) { .hide-xs { display: none; } }
</style>''')
FAVICON = '<link rel="icon" href="/logo.svg" type="image/svg+xml">'
LOGO = '<img src="/logo.svg" alt="" width="34" height="34">'
DATE_ISO, DATE = '2026-10-21', {'en': 'October 21, 2026', 'es': '21 de octubre de 2026'}
BASE = 'https://www.feearmor.com'
T = {
 'en': dict(home='/', blog='/blog', other='English', other_lang='es', other_label='Español', cta='Get Started', signup='/#signup',
            blog_title='The FeeArmor Blog', blog_sub='Plain-English guides to the fees hiding in your monthly bills.',
            blog_desc='Guides to removing junk fees, expired promos and billing mistakes from your internet, phone and TV bills.',
            by='By Giovanni Morado', read='Read the guide →',
            box_h='Rather not make the call?', box_p='FeeArmor makes these calls for you, in English or Spanish. $0 upfront: no savings, no fee.',
            privacy='/privacy', privacy_l='Privacy Policy', footer='All rights reserved.', entity='FeeArmor'),
 'es': dict(home='/es', blog='/es/blog', other='Español', other_lang='en', other_label='English', cta='Empezar', signup='/es#signup',
            blog_title='El blog de FeeArmor', blog_sub='Guías sencillas sobre los cargos escondidos en sus facturas.',
            blog_desc='Guías para quitar cargos basura, promociones vencidas y errores de cobro de sus facturas de internet, teléfono y TV.',
            by='Por Giovanni Morado', read='Leer la guía →',
            box_h='¿Prefiere no hacer la llamada?', box_p='FeeArmor hace estas llamadas por usted, en español. $0 por adelantado: si no ahorra, no paga.',
            privacy='/es/privacidad', privacy_l='Política de privacidad', footer='Todos los derechos reservados.', entity='FeeArmor'),
}
def other_url(lang, path_en, path_es):
    return path_es if lang == 'en' else path_en
def page(lang, title, desc, canon, alt_en, alt_es, body, jsonld):
    t = T[lang]
    other = T[t['other_lang']]
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title) if 'FeeArmor' in title else html.escape(title) + ' | FeeArmor'}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{BASE}{canon}">
<link rel="alternate" hreflang="en" href="{BASE}{alt_en}">
<link rel="alternate" hreflang="es" href="{BASE}{alt_es}">
<link rel="alternate" hreflang="x-default" href="{BASE}{alt_en}">
<meta property="og:type" content="article">
<meta property="og:url" content="{BASE}{canon}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{BASE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B1120">
{FAVICON}
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
{style}
</head>
<body>
<header>
  <div class="wrap">
    <a class="wordmark" href="{t['home']}" aria-label="FeeArmor">{LOGO}<span>Fee<span class="lime">Armor</span></span></a>
    <div class="head-right">
      <a class="nav-link hide-xs" href="{t['blog']}">Blog</a>
      <a class="lang-link" href="{alt_es if lang == 'en' else alt_en}" hreflang="{t['other_lang']}" lang="{t['other_lang']}">{t['other_label']}</a>
      <a class="btn btn-sm" href="{t['signup']}">{t['cta']}</a>
    </div>
  </div>
</header>
<main>
  <section class="light">
    <div class="wrap">
{body}
    </div>
  </section>
</main>
<footer>
  <div class="wrap">
    <nav aria-label="Footer">
      <a href="{t['home']}">FeeArmor</a>
      <a href="{t['blog']}">Blog</a>
      <a href="{t['privacy']}">{t['privacy_l']}</a>
    </nav>
    <p style="margin:0">&copy; 2026 {t['entity']}. {t['footer']}</p>
  </div>
</footer>
</body>
</html>
'''
def cta(lang):
    t = T[lang]
    return f'''      <div class="cta-box">
        <h2>{t['box_h']}</h2>
        <p>{t['box_p']}</p>
        <a class="btn" href="{t['signup']}">{t['cta']}</a>
      </div>'''
os.makedirs(os.path.join(ROOT, 'blog', 'es'), exist_ok=True)
for lang in ('en', 'es'):
    t = T[lang]
    cards = []
    for p in POSTS:
        c = p[lang]
        slug = p['slug'] if lang == 'en' else p['es_slug']
        url_en, url_es = f"/blog/{p['slug']}", f"/es/blog/{p['es_slug']}"
        canon = url_en if lang == 'en' else url_es
        ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": c['title'], "description": c['desc'],
              "inLanguage": lang, "datePublished": DATE_ISO, "dateModified": DATE_ISO,
              "author": {"@type": "Person", "name": "Giovanni Morado"},
              "publisher": {"@type": "Organization", "name": "FeeArmor", "url": BASE + "/"},
              "mainEntityOfPage": BASE + canon}
        body = f'''      <article>
        <p class="crumb"><a href="{t['blog']}">Blog</a></p>
        <h1 style="font-size:clamp(30px,7vw,44px)">{html.escape(c['title'])}</h1>
        <p class="byline">{t['by']} · {DATE[lang]}</p>
{c['body']}
{cta(lang)}
      </article>'''
        out = os.path.join(ROOT, 'blog', 'es' if lang == 'es' else '', slug + '.html')
        open(out, 'w').write(page(lang, c['title'], c['desc'], canon, url_en, url_es, body, ld))
        cards.append(f'''        <a class="card post-card" href="{canon}">
          <h2>{html.escape(c['title'])}</h2>
          <p>{html.escape(c['summary'])}</p>
          <span class="more">{t['read']}</span>
        </a>''')
    idx_body = f'''      <p class="eyebrow">Blog</p>
      <h1 style="font-size:clamp(32px,7vw,48px)">{t['blog_title']}</h1>
      <p class="muted">{t['blog_sub']}</p>
      <div class="post-list">
{chr(10).join(cards)}
      </div>
{cta(lang)}'''
    ld = {"@context": "https://schema.org", "@type": "Blog", "name": t['blog_title'], "inLanguage": lang, "url": BASE + t['blog']}
    out = os.path.join(ROOT, 'blog', 'es' if lang == 'es' else '', 'index.html')
    open(out, 'w').write(page(lang, t['blog_title'], t['blog_desc'], t['blog'], '/blog', '/es/blog', idx_body, ld))
print('built', sorted(os.path.relpath(os.path.join(d, f), ROOT) for d, _, fs in os.walk(os.path.join(ROOT, 'blog')) for f in fs))
