# Builds privacy pages (EN + ES), the 404 page, robots.txt and sitemap.xml into public/.
# Run after adding blog posts:  python3 tools/make_static.py
import os, sys, html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blog_content import POSTS

SITE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
BASE = 'https://www.feearmor.com'
UPDATED = {'en': 'October 21, 2026', 'es': '21 de octubre de 2026'}
src = open(os.path.join(SITE, 'index.html')).read()
STYLE = src[src.index('<style>'):src.index('</style>') + len('</style>')]
FAVICON = src[src.index('<link rel="icon"'):src.index('>', src.index('<link rel="icon"')) + 1]
LOGO = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" fill="#1F2937" stroke="#A3E635" stroke-width="2" stroke-linejoin="round"/><path d="M8 11l3 3 5-6" stroke="#A3E635" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'

PRIVACY = {
 'en': ('Privacy Policy', 'How FeeArmor collects, uses and protects your information.', '/privacy', '''
<h1>Privacy Policy</h1>
<p class="muted">Last updated: {updated}</p>
<p>FeeArmor helps people find and remove fees on their monthly bills. This page explains, in plain language, what information we collect and what we do with it.</p>
<h2>What we collect</h2>
<ul>
<li><b>From our signup forms:</b> your first name, email address and preferred language. On our Bill Rescue reader page we also ask which bill bugs you most, and, only if you choose, your mobile number with your consent to receive texts.</li>
<li><b>How you found us:</b> the campaign tags in the link you clicked (for example "utm_source=youtube") and the page you came from.</li>
<li><b>Simple visit counts:</b> we count page views, form submits and signups by campaign. We don't use advertising trackers or tracking cookies, and we don't store your IP address with these counts.</li>
<li><b>When you become a customer:</b> copies of the bills you send us and the details needed to contact your providers. We never ask for your account passwords.</li>
</ul>
<h2>Why we use it</h2>
<ul>
<li>To tell you when FeeArmor opens and when your free bill scan is ready.</li>
<li>To review your bills and contact your providers when you ask us to.</li>
<li>To understand which of our posts and videos bring people to FeeArmor.</li>
</ul>
<h2>What we never do</h2>
<ul>
<li>We never sell your information.</li>
<li>We don't share it with marketing or referral partners.</li>
<li>We never post your name, bill or savings without your written permission.</li>
</ul>
<h2>Who helps us run FeeArmor</h2>
<p>We use a small number of service providers to run this website and store data (for example, our hosting and database provider), and, when we start sending emails, an email delivery service. They may only use your information to provide their service to us.</p>
<h2>Texts</h2>
<p>We send texts only if you checked the box agreeing to them. Up to 4 messages a month. Reply STOP to stop at any time. Consent is not required to use FeeArmor.</p>
<h2>Security and how long we keep it</h2>
<p>Your information is stored with access limited to our team. We delete bill copies 90 days after your account closes or your last fee is paid, unless the law requires us to keep them longer. To prevent abuse, our servers briefly keep the address your signup came from (for up to one hour) to limit repeated submissions.</p>
<h2>Your choices</h2>
<ul>
<li>Unsubscribe from emails using the link in any email.</li>
<li>Ask us to see, correct or delete your information by emailing <a href="mailto:hello@feearmor.com">hello@feearmor.com</a>. We'll reply within 30 days.</li>
</ul>
<h2>Children</h2>
<p>FeeArmor is for adults 18 and older. We don't knowingly collect information from children.</p>
<h2>Changes</h2>
<p>If we change this policy, we'll update the date above. If the change is important, we'll email people on our list.</p>
<h2>Contact</h2>
<p>Questions? Email <a href="mailto:hello@feearmor.com">hello@feearmor.com</a>. Hablamos español: <a href="/es/privacidad">lea esta política en español</a>.</p>
'''),
 'es': ('Política de privacidad', 'Cómo FeeArmor recopila, usa y protege su información.', '/es/privacidad', '''
<h1>Política de privacidad</h1>
<p class="muted">Última actualización: {updated}</p>
<p>FeeArmor ayuda a las personas a encontrar y quitar cargos en sus facturas mensuales. Esta página explica, en palabras sencillas, qué información recopilamos y qué hacemos con ella.</p>
<h2>Qué recopilamos</h2>
<ul>
<li><b>De nuestros formularios:</b> su nombre, su correo electrónico y su idioma preferido. En nuestra página para lectores de Bill Rescue también preguntamos qué factura le molesta más y, solo si usted quiere, su número de celular con su permiso para recibir mensajes de texto.</li>
<li><b>Cómo nos encontró:</b> las etiquetas de campaña del enlace que usó (por ejemplo "utm_source=youtube") y la página de donde venía.</li>
<li><b>Conteos simples de visitas:</b> contamos vistas de página, envíos de formulario y registros por campaña. No usamos rastreadores de publicidad ni cookies de rastreo, y no guardamos su dirección IP con estos conteos.</li>
<li><b>Cuando se hace cliente:</b> copias de las facturas que nos envía y los datos necesarios para contactar a sus compañías. Nunca le pedimos las contraseñas de sus cuentas.</li>
</ul>
<h2>Para qué la usamos</h2>
<ul>
<li>Para avisarle cuando FeeArmor abra y cuando su revisión gratis esté lista.</li>
<li>Para revisar sus facturas y contactar a sus compañías cuando usted nos lo pida.</li>
<li>Para saber cuáles de nuestras publicaciones y videos traen personas a FeeArmor.</li>
</ul>
<h2>Lo que nunca hacemos</h2>
<ul>
<li>Nunca vendemos su información.</li>
<li>No la compartimos con socios de mercadeo ni de referidos.</li>
<li>Nunca publicamos su nombre, su factura ni su ahorro sin su permiso por escrito.</li>
</ul>
<h2>Quién nos ayuda a operar FeeArmor</h2>
<p>Usamos pocos proveedores de servicio para operar este sitio y guardar datos (por ejemplo, nuestro proveedor de hospedaje y base de datos) y, cuando empecemos a enviar correos, un servicio de envío de correo. Solo pueden usar su información para darnos su servicio.</p>
<h2>Mensajes de texto</h2>
<p>Solo enviamos mensajes de texto si usted marcó la casilla para recibirlos. Hasta 4 mensajes al mes. Responda STOP para dejar de recibirlos en cualquier momento. No se necesita este permiso para usar FeeArmor.</p>
<h2>Seguridad y cuánto tiempo la guardamos</h2>
<p>Su información se guarda con acceso limitado a nuestro equipo. Borramos las copias de facturas 90 días después de que se cierre su cuenta o pague su último cargo, a menos que la ley nos pida guardarlas más tiempo. Para evitar abusos, nuestros servidores guardan por poco tiempo (hasta una hora) la dirección desde donde llegó su registro para limitar envíos repetidos.</p>
<h2>Sus opciones</h2>
<ul>
<li>Dese de baja de los correos con el enlace que aparece en cada correo.</li>
<li>Pídanos ver, corregir o borrar su información escribiendo a <a href="mailto:hello@feearmor.com">hello@feearmor.com</a>. Le respondemos en un máximo de 30 días.</li>
</ul>
<h2>Menores de edad</h2>
<p>FeeArmor es para adultos de 18 años o más. No recopilamos a sabiendas información de menores.</p>
<h2>Cambios</h2>
<p>Si cambiamos esta política, actualizaremos la fecha de arriba. Si el cambio es importante, enviaremos un correo a las personas de nuestra lista.</p>
<h2>Contacto</h2>
<p>¿Preguntas? Escriba a <a href="mailto:hello@feearmor.com">hello@feearmor.com</a>. <a href="/privacy" lang="en">Read this policy in English</a>.</p>
'''),
}
NAV = {
 'en': dict(home='/', blog='/blog', other_href='/es', other_lang='es', other_label='Español', cta='Get Early Access', signup='/#signup', privacy='/privacy', privacy_l='Privacy Policy', rights='All rights reserved.'),
 'es': dict(home='/es', blog='/es/blog', other_href='/', other_lang='en', other_label='English', cta='Apuntarme', signup='/es#signup', privacy='/es/privacidad', privacy_l='Política de privacidad', rights='Todos los derechos reservados.'),
}
EXTRA_CSS = '''  .doc h2 { font-size: 22px; margin: 28px 0 10px; }
  .doc ul { padding-left: 22px; }
  .doc li { margin-bottom: 8px; }
  .nav-link { color: var(--text); font-weight: 700; font-size: 15px; text-decoration: none; min-height: 44px; display: inline-flex; align-items: center; }
</style>'''

def shell(lang, title, desc, canon, alt, body, robots=''):
    n = NAV[lang]
    alt_links = ''
    if alt:
        alt_links = (f'<link rel="alternate" hreflang="en" href="{BASE}{alt[0]}">\n'
                     f'<link rel="alternate" hreflang="es" href="{BASE}{alt[1]}">\n')
    canon_link = f'<link rel="canonical" href="{BASE}{canon}">\n' if canon else ''
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | FeeArmor</title>
<meta name="description" content="{html.escape(desc)}">
{robots}{canon_link}{alt_links}<meta name="theme-color" content="#0B1120">
{FAVICON}
{STYLE.replace('</style>', EXTRA_CSS)}
</head>
<body>
<header>
  <div class="wrap">
    <a class="wordmark" href="{n['home']}" aria-label="FeeArmor">{LOGO}<span>Fee<span class="lime">Armor</span></span></a>
    <div class="head-right">
      <a class="lang-link" href="{n['other_href']}" hreflang="{n['other_lang']}" lang="{n['other_lang']}">{n['other_label']}</a>
      <a class="btn btn-sm" href="{n['signup']}">{n['cta']}</a>
    </div>
  </div>
</header>
<main>
  <section>
    <div class="wrap doc">
{body}
    </div>
  </section>
</main>
<footer>
  <div class="wrap">
    <nav aria-label="Footer">
      <a href="{n['home']}">FeeArmor</a>
      <a href="{n['blog']}">Blog</a>
      <a href="{n['privacy']}">{n['privacy_l']}</a>
    </nav>
    <p style="margin:0">&copy; 2026 FeeArmor. {n['rights']}</p>
  </div>
</footer>
</body>
</html>
'''

for lang, (title, desc, url, body) in PRIVACY.items():
    out = 'privacy.html' if lang == 'en' else 'es-privacidad.html'
    open(os.path.join(SITE, out), 'w').write(shell(lang, title, desc, url, ('/privacy', '/es/privacidad'), body.format(updated=UPDATED[lang])))

notfound = '''<h1>Page not found</h1>
<p>That page doesn't exist. <a href="/">Go to the FeeArmor home page</a>.</p>
<p lang="es">Esa página no existe. <a href="/es">Ir a la página de FeeArmor en español</a>.</p>'''
open(os.path.join(SITE, '404.html'), 'w').write(shell('en', 'Page not found', 'Page not found', '', None, notfound, '<meta name="robots" content="noindex">\n'))

open(os.path.join(SITE, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/\n\nSitemap: {BASE}/sitemap.xml\n')

# Sitemap: home + privacy + blog pairs, each English/Spanish pair linked with hreflang.
pairs = [('/', '/es'), ('/privacy', '/es/privacidad'), ('/blog', '/es/blog')]
pairs += [(f"/blog/{p['slug']}", f"/es/blog/{p['es_slug']}") for p in POSTS]
urls = []
for en, es in pairs:
    for loc in (en, es):
        urls.append(f'''  <url>
    <loc>{BASE}{loc}</loc>
    <xhtml:link rel="alternate" hreflang="en" href="{BASE}{en}"/>
    <xhtml:link rel="alternate" hreflang="es" href="{BASE}{es}"/>
  </url>''')
open(os.path.join(SITE, 'sitemap.xml'), 'w').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    + '\n'.join(urls) + '\n</urlset>\n')
print('built privacy.html, es-privacidad.html, 404.html, robots.txt, sitemap.xml (%d urls)' % len(urls))
