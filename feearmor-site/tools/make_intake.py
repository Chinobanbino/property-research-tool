# Builds the customer intake pages: public/intake.html (/intake) and public/es-intake.html (/es/intake).
# Run:  python3 tools/make_intake.py
import os, html

SITE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
BASE = 'https://www.feearmor.com'

# Bill types: (value stored, English label, Spanish label). Keep in sync with INTAKE_BILLS in server.js.
BILLS = [
    ('internet', 'Internet', 'Internet'),
    ('mobile', 'Mobile phone', 'Celular'),
    ('tv', 'Cable or satellite TV', 'TV por cable o satélite'),
    ('home_security', 'Home security', 'Seguridad del hogar'),
    ('electric', 'Electric (fees on the bill)', 'Luz (cargos en la factura)'),
    ('gas', 'Gas (fees on the bill)', 'Gas (cargos en la factura)'),
]
TIMES = [
    ('weekday_morning', 'Weekday mornings (9am–12pm)', 'Mañanas entre semana (9am–12pm)'),
    ('weekday_afternoon', 'Weekday afternoons (12–5pm)', 'Tardes entre semana (12–5pm)'),
    ('weekday_evening', 'Weekday evenings (5–8pm)', 'Noches entre semana (5–8pm)'),
    ('saturday', 'Saturday', 'Sábado'),
]
HEARD = [('', 'Choose one (optional)', 'Elija una (opcional)'), ('youtube', 'YouTube', 'YouTube'), ('instagram', 'Instagram', 'Instagram'),
         ('tiktok', 'TikTok', 'TikTok'), ('facebook', 'Facebook', 'Facebook'), ('friend', 'Friend or family', 'Amigo o familiar'),
         ('bill_rescue', 'Bill Rescue book', 'Libro Bill Rescue'), ('google', 'Google search', 'Búsqueda en Google'), ('other', 'Other', 'Otro')]
# Exact consent sentence; must match SMS_CONSENT_TEXT in server.js (English is the stored record).
SMS_EN = "Yes, FeeArmor may send me marketing and account text messages at the number above, including by automated means. Up to 4 msgs/month. Consent isn't a condition of any purchase. Msg & data rates may apply. Reply STOP to opt out, HELP for help."
SMS_ES = "Sí, FeeArmor puede enviarme mensajes de texto de mercadeo y sobre mi cuenta al número de arriba, incluso por medios automáticos. Hasta 4 mensajes al mes. Este permiso no es condición de ninguna compra. Pueden aplicar tarifas de mensajes y datos. Responda STOP para cancelar, HELP para ayuda."

T = {
 'en': dict(out='intake.html', url='/intake', other='/es/intake', other_lang='es', other_label='Español', home='/', blog='/blog', privacy='/privacy',
   title='Get Started', desc='Tell us your bills and we\'ll call your providers to lower them. $0 upfront. No savings, no fee.',
   eyebrow='Get started', h1='Tell us your bills.', lead='About 2 minutes. No charge until you save. Nothing changes on your accounts without your YES.',
   s1='About you', first='First name', last='Last name', email='Email', phone='Mobile phone', phone_hint='For your 3-way call with the provider', zip='ZIP code',
   lang='Preferred language', s2='Your bills', s2_hint='Check every bill you\'d like us to look at.', provider='Provider', provider_ph='e.g. Spectrum', amount='About how much per month?', amount_ph='$',
   s3='Upload your bills (optional, but faster)', s3_hint='A photo or PDF of your latest bill for each provider. Up to 5 files, 10 MB each. Never include passwords or PINs.',
   s4='Best time for a 20-minute call', s4_hint='Pick all that work. We\'ll confirm by email.', heard='How did you hear about us?', notes='Anything we should know? (optional)', promo='Promo code (optional)',
   next_h='What happens next', next=['We email you within one business day.', 'You e-sign a short service agreement and authorization. We don\'t contact any provider until you sign.', 'We set up a 3-way call. You verify yourself with the provider and approve every change.', 'You pay only after the savings show up on your bill.'],
   submit='Send My Bills', sending='Sending…', fine='By sending, you agree to our <a href="/privacy">Privacy Policy</a>. We never ask for your passwords or PINs.',
   ok_h='Got it, {name}.', ok_p='We\'ll email you within one business day with your agreement to e-sign and a time for your call. Questions? support@feearmor.com',
   e_first='Please add your first and last name.', e_email='Please enter a valid email address.', e_phone='Please enter a 10-digit mobile number.', e_zip='Please enter a 5-digit ZIP code.',
   e_bills='Check at least one bill.', e_files='Up to 5 files, each under 10 MB (photo or PDF).', e_rate='Too many tries. Please wait a bit and try again.', e_gen='Something went wrong. Please check your connection and try again.',
   sms=SMS_EN, cta='Get Started', rights='All rights reserved.', privacy_l='Privacy Policy'),
 'es': dict(out='es-intake.html', url='/es/intake', other='/intake', other_lang='en', other_label='English', home='/es', blog='/es/blog', privacy='/es/privacidad',
   title='Empezar', desc='Díganos sus facturas y llamamos a sus compañías para bajarlas. $0 por adelantado. Si no ahorra, no paga.',
   eyebrow='Empezar', h1='Díganos sus facturas.', lead='Unos 2 minutos. Sin cobro hasta que usted ahorre. Nada cambia en sus cuentas sin su SÍ.',
   s1='Sus datos', first='Nombre', last='Apellido', email='Correo electrónico', phone='Celular', phone_hint='Para su llamada de 3 personas con la compañía', zip='Código postal',
   lang='Idioma preferido', s2='Sus facturas', s2_hint='Marque cada factura que quiere que revisemos.', provider='Compañía', provider_ph='ej. Spectrum', amount='¿Cuánto paga al mes, más o menos?', amount_ph='$',
   s3='Suba sus facturas (opcional, pero más rápido)', s3_hint='Una foto o PDF de su factura más reciente de cada compañía. Hasta 5 archivos de 10 MB cada uno. Nunca incluya contraseñas ni PIN.',
   s4='Mejor horario para una llamada de 20 minutos', s4_hint='Elija todos los que le funcionen. Le confirmamos por correo.', heard='¿Cómo nos conoció?', notes='¿Algo que debamos saber? (opcional)', promo='Código de promoción (opcional)',
   next_h='Lo que sigue', next=['Le escribimos en un día hábil.', 'Usted firma electrónicamente un acuerdo de servicio corto y una autorización. No contactamos a ninguna compañía hasta que firme.', 'Hacemos una llamada de 3 personas. Usted se verifica con la compañía y aprueba cada cambio.', 'Solo paga cuando el ahorro aparece en su factura.'],
   submit='Enviar Mis Facturas', sending='Enviando…', fine='Al enviar, acepta nuestra <a href="/es/privacidad">Política de privacidad</a>. Nunca le pedimos contraseñas ni PIN.',
   ok_h='Recibido, {name}.', ok_p='Le escribimos en un día hábil con su acuerdo para firmar y un horario para su llamada. ¿Preguntas? support@feearmor.com',
   e_first='Por favor escriba su nombre y apellido.', e_email='Por favor escriba un correo electrónico válido.', e_phone='Por favor escriba un celular de 10 dígitos.', e_zip='Por favor escriba un código postal de 5 dígitos.',
   e_bills='Marque al menos una factura.', e_files='Hasta 5 archivos, cada uno de menos de 10 MB (foto o PDF).', e_rate='Demasiados intentos. Espere un momento y vuelva a intentarlo.', e_gen='Algo salió mal. Revise su conexión y vuelva a intentarlo.',
   sms=SMS_ES, cta='Empezar', rights='Todos los derechos reservados.', privacy_l='Política de privacidad'),
}

EXTRA_CSS = '''<style>
  .intake h1 { font-size: clamp(32px, 7vw, 46px); }
  .intake fieldset.box { background: var(--surface); border: 1.5px solid var(--border); border-radius: var(--radius); padding: 20px; margin: 0 0 18px; }
  .intake fieldset.box > legend { font-size: 18px; font-weight: 800; padding: 0 6px; }
  .grid2 { display: grid; gap: 14px; }
  @media (min-width: 560px) { .grid2 { grid-template-columns: 1fr 1fr; } }
  .hint { font-size: 14px; color: var(--muted); margin: -2px 0 12px; }
  .bill { border: 1.5px solid var(--border); border-radius: 12px; padding: 12px 14px; margin-bottom: 10px; background: var(--bg); }
  .bill > label { display: flex; align-items: center; gap: 10px; margin: 0; font-weight: 700; min-height: 32px; cursor: pointer; }
  .bill input[type=checkbox], .times input { width: 20px; height: 20px; accent-color: #2E7D32; }
  .bill .more { display: none; margin-top: 12px; }
  .bill.on { border-color: var(--green); }
  .bill.on .more { display: grid; }
  .times { display: grid; gap: 8px; }
  .times label { display: flex; align-items: center; gap: 10px; font-weight: 500; margin: 0; min-height: 40px; }
  input[type=file] { width: 100%; padding: 12px; border: 1.5px dashed #9FB0C3; border-radius: 10px; background: var(--bg); font: inherit; font-size: 15px; }
  textarea { width: 100%; min-height: 90px; padding: 12px 16px; border: 1.5px solid #CBD6E2; border-radius: 10px; font: inherit; font-size: 17px; resize: vertical; }
  .next { counter-reset: n; list-style: none; padding: 0; margin: 0; }
  .next li { counter-increment: n; position: relative; padding-left: 38px; margin-bottom: 12px; }
  .next li::before { content: counter(n); position: absolute; left: 0; top: 0; width: 26px; height: 26px; border-radius: 50%; background: var(--navy); color: var(--green); font-weight: 900; font-size: 14px; display: flex; align-items: center; justify-content: center; }
</style>'''

def esc(x): return html.escape(x, quote=True)

def page(lang):
    t = T[lang]; i = 1 if lang == 'en' else 2
    bills = '\n'.join(f'''          <div class="bill" data-bill="{v}">
            <label><input type="checkbox" name="bill_{v}" value="1"> {esc(b[i])}</label>
            <div class="more grid2">
              <div><label for="prov_{v}">{t['provider']}</label><input id="prov_{v}" name="provider_{v}" type="text" maxlength="60" placeholder="{t['provider_ph']}"></div>
              <div><label for="amt_{v}">{t['amount']}</label><input id="amt_{v}" name="amount_{v}" type="text" inputmode="decimal" maxlength="8" placeholder="{t['amount_ph']}"></div>
            </div>
          </div>''' for b in BILLS for v in [b[0]])
    times = '\n'.join(f'            <label><input type="checkbox" name="call_time" value="{v}"> {esc(x[i])}</label>' for x in TIMES for v in [x[0]])
    heard = '\n'.join(f'              <option value="{x[0]}">{esc(x[i])}</option>' for x in HEARD)
    nxt = '\n'.join(f'          <li>{esc(x)}</li>' for x in t['next'])
    msgs = {k: t[k] for k in ['e_first', 'e_email', 'e_phone', 'e_zip', 'e_bills', 'e_files', 'e_rate', 'e_gen', 'sending', 'submit', 'ok_h']}
    import json
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t['title'])} | FeeArmor</title>
<meta name="description" content="{esc(t['desc'])}">
<link rel="canonical" href="{BASE}{t['url']}">
<link rel="alternate" hreflang="en" href="{BASE}/intake">
<link rel="alternate" hreflang="es" href="{BASE}/es/intake">
<meta property="og:title" content="FeeArmor | {esc(t['title'])}">
<meta property="og:description" content="{esc(t['desc'])}">
<meta property="og:image" content="{BASE}/og-image.png">
<meta name="theme-color" content="#0D1B2A">
<link rel="icon" href="/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="/site.css">
{EXTRA_CSS}
</head>
<body>
<header>
  <div class="wrap">
    <a class="wordmark" href="{t['home']}" aria-label="FeeArmor"><img src="/logo.svg" alt="" width="34" height="34"><span>Fee<span class="lime">Armor</span></span></a>
    <div class="head-right">
      <a class="nav-link hide-xs" href="{t['blog']}">Blog</a>
      <a class="lang-link" href="{t['other']}" hreflang="{t['other_lang']}" lang="{t['other_lang']}">{t['other_label']}</a>
    </div>
  </div>
</header>
<main class="intake">
  <section class="off">
    <div class="wrap">
      <div id="intake-body">
        <p class="eyebrow">{t['eyebrow']}</p>
        <h1>{t['h1']}</h1>
        <p class="muted">{t['lead']}</p>
        <form id="intake" novalidate>
          <fieldset class="box">
            <legend>{t['s1']}</legend>
            <div class="grid2">
              <div><label for="first_name">{t['first']}</label><input id="first_name" name="first_name" type="text" autocomplete="given-name" required maxlength="60"></div>
              <div><label for="last_name">{t['last']}</label><input id="last_name" name="last_name" type="text" autocomplete="family-name" required maxlength="60"></div>
              <div><label for="email">{t['email']}</label><input id="email" name="email" type="email" autocomplete="email" inputmode="email" required maxlength="254"></div>
              <div><label for="phone">{t['phone']}</label><input id="phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required maxlength="20"><p class="hint" style="margin:6px 0 0">{t['phone_hint']}</p></div>
              <div><label for="zip">{t['zip']}</label><input id="zip" name="zip" type="text" autocomplete="postal-code" inputmode="numeric" required maxlength="10"></div>
              <fieldset>
                <legend>{t['lang']}</legend>
                <div class="lang-choice">
                  <label><input type="radio" name="preferred_language" value="en"{' checked' if lang == 'en' else ''}> English</label>
                  <label lang="es"><input type="radio" name="preferred_language" value="es"{' checked' if lang == 'es' else ''}> Español</label>
                </div>
              </fieldset>
            </div>
          </fieldset>

          <fieldset class="box">
            <legend>{t['s2']}</legend>
            <p class="hint">{t['s2_hint']}</p>
{bills}
          </fieldset>

          <fieldset class="box">
            <legend>{t['s3']}</legend>
            <p class="hint">{t['s3_hint']}</p>
            <input id="files" name="files" type="file" multiple accept="image/jpeg,image/png,image/webp,image/heic,image/heif,application/pdf">
          </fieldset>

          <fieldset class="box">
            <legend>{t['s4']}</legend>
            <p class="hint">{t['s4_hint']}</p>
            <div class="times">
{times}
            </div>
            <div style="margin-top:14px"><label for="heard_from">{t['heard']}</label>
              <select id="heard_from" name="heard_from">
{heard}
              </select>
            </div>
            <div style="margin-top:14px"><label for="notes">{t['notes']}</label><textarea id="notes" name="notes" maxlength="500"></textarea></div>
            <div style="margin-top:14px"><label for="promo_code">{t['promo']}</label><input id="promo_code" name="promo_code" type="text" maxlength="20" autocapitalize="characters"></div>
          </fieldset>

          <label class="consent" for="sms_consent"><input id="sms_consent" name="sms_consent" type="checkbox" value="1"><span>{esc(t['sms'])}</span></label>
          <div class="hp" aria-hidden="true"><label for="company">Company</label><input id="company" name="company" type="text" tabindex="-1" autocomplete="off"></div>

          <div class="card" style="margin-top:6px">
            <h3 style="margin-bottom:12px">{t['next_h']}</h3>
            <ol class="next">
{nxt}
            </ol>
          </div>

          <p class="form-error" id="form-error" role="alert" hidden></p>
          <button class="btn btn-block" type="submit" id="submit-btn">{t['submit']}</button>
          <p class="small" style="margin:0">{t['fine']}</p>
        </form>
      </div>
      <div class="card success" id="success" hidden tabindex="-1">
        <div class="check"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12l5 5 9-10" stroke="#2E7D32" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
        <h2 id="success-title"></h2>
        <p class="muted">{t['ok_p']}</p>
      </div>
    </div>
  </section>
</main>
<footer>
  <div class="wrap">
    <nav aria-label="Footer"><a href="{t['home']}">FeeArmor</a><a href="{t['blog']}">Blog</a><a href="{t['privacy']}">{t['privacy_l']}</a><a href="mailto:support@feearmor.com">support@feearmor.com</a></nav>
    <p style="margin:0">&copy; 2026 FeeArmor. {t['rights']}</p>
  </div>
</footer>
<script>
(function () {{
  var M = {json.dumps(msgs, ensure_ascii=False)};
  var form = document.getElementById('intake');
  var btn = document.getElementById('submit-btn');
  var err = document.getElementById('form-error');
  var q = new URLSearchParams(location.search);
  if (q.get('code')) form.promo_code.value = q.get('code').toUpperCase().slice(0, 20);
  document.querySelectorAll('.bill input[type=checkbox]').forEach(function (cb) {{
    cb.addEventListener('change', function () {{ cb.closest('.bill').classList.toggle('on', cb.checked); }});
  }});
  function fail(msg, el) {{ err.textContent = msg; err.hidden = false; if (el) el.focus(); }}
  function ev(kind) {{ if (window.faEvent) window.faEvent(kind); }}
  form.addEventListener('submit', function (e) {{
    e.preventDefault(); err.hidden = true;
    var f = form;
    if (!f.first_name.value.trim() || !f.last_name.value.trim()) return fail(M.e_first, f.first_name);
    if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(f.email.value.trim())) return fail(M.e_email, f.email);
    var digits = f.phone.value.replace(/\\D/g, '');
    if (!(digits.length === 10 || (digits.length === 11 && digits[0] === '1'))) return fail(M.e_phone, f.phone);
    if (!/^\\d{{5}}(-\\d{{4}})?$/.test(f.zip.value.trim())) return fail(M.e_zip, f.zip);
    if (!f.querySelector('.bill input[type=checkbox]:checked')) return fail(M.e_bills, f.querySelector('.bill input'));
    var files = f.files.files;
    if (files.length > 5) return fail(M.e_files, f.files);
    for (var i = 0; i < files.length; i++) if (files[i].size > 10 * 1024 * 1024) return fail(M.e_files, f.files);
    var data = new FormData(f);
    ['utm_source', 'utm_medium', 'utm_campaign'].forEach(function (k) {{ data.append(k, q.get(k) || ''); }});
    data.append('page', location.pathname);
    ev('submit');
    btn.disabled = true; btn.textContent = M.sending;
    fetch('/api/intake', {{ method: 'POST', body: data }}).then(function (res) {{
      if (res.status === 429) throw new Error('rate');
      if (res.status === 413 || res.status === 415) throw new Error('files');
      if (!res.ok) throw new Error('fail');
      ev('success');
      document.getElementById('success-title').textContent = M.ok_h.replace('{{name}}', f.first_name.value.trim());
      document.getElementById('intake-body').hidden = true;
      var s = document.getElementById('success'); s.hidden = false; s.focus(); window.scrollTo(0, 0);
    }}).catch(function (e2) {{
      fail(e2.message === 'rate' ? M.e_rate : e2.message === 'files' ? M.e_files : M.e_gen);
      btn.disabled = false; btn.textContent = M.submit;
    }});
  }});
}})();
</script>
<script>
(function () {{
  var q = new URLSearchParams(location.search);
  function ev(kind) {{
    try {{
      var d = JSON.stringify({{ kind: kind, page: location.pathname, utm_source: q.get('utm_source') || '', utm_medium: q.get('utm_medium') || '', utm_campaign: q.get('utm_campaign') || '' }});
      if (navigator.sendBeacon) navigator.sendBeacon('/api/event', new Blob([d], {{ type: 'application/json' }}));
      else fetch('/api/event', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: d, keepalive: true }});
    }} catch (e) {{}}
  }}
  window.faEvent = ev;
  ev('view');
}})();
</script>
</body>
</html>
'''

for lang, t in T.items():
    open(os.path.join(SITE, t['out']), 'w').write(page(lang))
print('built intake.html, es-intake.html')
