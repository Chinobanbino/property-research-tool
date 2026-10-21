# Builds the customer intake pages: public/intake.html (/intake) and public/es-intake.html (/es/intake).
# 3-step form (your info, your bills, best time to call) that posts everything at the end to /api/intake.
# Run:  python3 tools/make_intake.py
import os, html, json

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
# Call windows stay inside Texas calling hours (9am-9pm Mon-Sat). Keep in sync with CALL_TIMES in server.js.
TIMES = [
    ('weekday_morning', 'Mornings', '9am–12pm', 'Mañanas', '9am–12pm'),
    ('weekday_afternoon', 'Afternoons', '12–5pm', 'Tardes', '12–5pm'),
    ('weekday_evening', 'Evenings', '5–8pm', 'Noches', '5–8pm'),
    ('saturday', 'Saturday', 'Daytime', 'Sábado', 'De día'),
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
   eyebrow='Free bill review', h1='Start saving on your bills <span class="lime">today.</span>',
   lead='Tell us about your bills in about 2 minutes. Our bilingual team reviews them and calls you with a plan.',
   fee='One-time fee: 40% of your first 12 months of savings. $0 if we don\'t save you money.',
   card_h='Your free bill review', card_p='No charge until you save. You approve every change.',
   steps=['Your info', 'Your bills', 'Best time'], step_of='Step {n} of 3',
   first='First name', last='Last name', email='Email', phone='Mobile phone', phone_hint='We\'ll call this number for your 3-way call with the provider.', zip='ZIP code',
   lang='Preferred language for our call',
   s2='Which bills should we look at?', provider='Provider', provider_ph='e.g. Spectrum', amount='About how much per month?', amount_ph='$',
   s3='Upload your bills (optional, but faster)', s3_hint='A photo or PDF of your latest bill for each provider. Up to 5 files, 10 MB each. Never include passwords or PINs.',
   notes='Anything we should know? (optional)', notes_ph='e.g. My internet bill went up $40 last month.',
   fee_h='How our fee works:', fee_p='We find your savings first. Your fee is a one-time 40% of your first 12 months of savings, payable in 3 interest-free payments if you like. You only pay after the savings show up on your bill.',
   s4='Best time for a 20-minute call', s4_hint='Pick all that work. Texas time.', heard='How did you hear about us?', promo='Promo code (optional)',
   before_h='Before we charge anything:', before_p='We email you a short agreement to e-sign and add a card. Nothing is charged until savings show on your bill. We don\'t contact any provider until you sign, and you approve every change on the call.',
   next='Next', back='Back', submit='Activate My FeeArmor', sending='Sending…',
   fine='By sending, you agree to our <a href="/privacy">Privacy Policy</a>. We never sell your information and never ask for passwords or PINs.',
   pills=['No charge until you save', 'We never sell your info', 'English &amp; Spanish'],
   ok_h='You\'re armored up, {name}!', ok_p='We got your bills. Expect an email from support@feearmor.com within 1 business day.',
   ok_steps=[('We review your bills', 'We look for where you may be overpaying and email you an agreement to e-sign.'),
             ('3-way call with your provider', 'You verify yourself, we negotiate, and you approve every change.'),
             ('You pay only after you save', 'One-time 40% of your first 12 months of savings, once it shows on your bill. $0 if we don\'t save you money.')],
   e_first='Please add your first and last name.', e_email='Please enter a valid email address.', e_phone='Please enter a 10-digit mobile number.', e_zip='Please enter a 5-digit ZIP code.',
   e_bills='Check at least one bill.', e_files='Up to 5 files, each under 10 MB (photo or PDF).', e_time='Pick at least one time that works.',
   e_rate='Too many tries. Please wait a bit and try again.', e_gen='Something went wrong. Please check your connection and try again.',
   sms=SMS_EN, rights='All rights reserved.', privacy_l='Privacy Policy'),
 'es': dict(out='es-intake.html', url='/es/intake', other='/intake', other_lang='en', other_label='English', home='/es', blog='/es/blog', privacy='/es/privacidad',
   title='Empezar', desc='Díganos sus facturas y llamamos a sus compañías para bajarlas. $0 por adelantado. Si no ahorra, no paga.',
   eyebrow='Revisión gratis de facturas', h1='Empiece a <span class="lime">ahorrar</span> en sus facturas hoy.',
   lead='Cuéntenos sobre sus facturas en unos 2 minutos. Nuestro equipo bilingüe las revisa y le llama con un plan.',
   fee='Tarifa única: 40% de sus primeros 12 meses de ahorro. $0 si no le ahorramos dinero.',
   card_h='Su revisión gratis de facturas', card_p='Sin cobro hasta que ahorre. Usted aprueba cada cambio.',
   steps=['Sus datos', 'Sus facturas', 'Mejor hora'], step_of='Paso {n} de 3',
   first='Nombre', last='Apellido', email='Correo electrónico', phone='Celular', phone_hint='Le llamamos a este número para su llamada de 3 personas con la compañía.', zip='Código postal',
   lang='Idioma preferido para la llamada',
   s2='¿Qué facturas revisamos?', provider='Compañía', provider_ph='ej. Spectrum', amount='¿Cuánto paga al mes, más o menos?', amount_ph='$',
   s3='Suba sus facturas (opcional, pero más rápido)', s3_hint='Una foto o PDF de su factura más reciente de cada compañía. Hasta 5 archivos de 10 MB cada uno. Nunca incluya contraseñas ni PIN.',
   notes='¿Algo que debamos saber? (opcional)', notes_ph='ej. Mi factura de internet subió $40 el mes pasado.',
   fee_h='Cómo funciona nuestra tarifa:', fee_p='Primero encontramos su ahorro. Su tarifa es un pago único del 40% de sus primeros 12 meses de ahorro, en 3 pagos sin intereses si prefiere. Solo paga cuando el ahorro aparece en su factura.',
   s4='Mejor horario para una llamada de 20 minutos', s4_hint='Elija todos los que le funcionen. Hora de Texas.', heard='¿Cómo nos conoció?', promo='Código de promoción (opcional)',
   before_h='Antes de cobrar cualquier cosa:', before_p='Le enviamos un acuerdo corto para firmar electrónicamente y agregar una tarjeta. No se cobra nada hasta que el ahorro aparezca en su factura. No contactamos a ninguna compañía hasta que firme, y usted aprueba cada cambio en la llamada.',
   next='Siguiente', back='Atrás', submit='Activar Mi Armadura', sending='Enviando…',
   fine='Al enviar, acepta nuestra <a href="/es/privacidad">Política de privacidad</a>. Nunca vendemos su información ni le pedimos contraseñas o PIN.',
   pills=['Sin cobro hasta que ahorre', 'Nunca vendemos sus datos', 'Español e inglés'],
   ok_h='¡Ya está protegido, {name}!', ok_p='Recibimos sus facturas. Espere un correo de support@feearmor.com en 1 día hábil.',
   ok_steps=[('Revisamos sus facturas', 'Buscamos dónde podría estar pagando de más y le enviamos un acuerdo para firmar.'),
             ('Llamada de 3 personas con su compañía', 'Usted se verifica, nosotros negociamos y usted aprueba cada cambio.'),
             ('Solo paga cuando ahorra', 'Pago único del 40% de sus primeros 12 meses de ahorro, cuando aparece en su factura. $0 si no le ahorramos dinero.')],
   e_first='Por favor escriba su nombre y apellido.', e_email='Por favor escriba un correo electrónico válido.', e_phone='Por favor escriba un celular de 10 dígitos.', e_zip='Por favor escriba un código postal de 5 dígitos.',
   e_bills='Marque al menos una factura.', e_files='Hasta 5 archivos, cada uno de menos de 10 MB (foto o PDF).', e_time='Elija al menos un horario.',
   e_rate='Demasiados intentos. Espere un momento y vuelva a intentarlo.', e_gen='Algo salió mal. Revise su conexión y vuelva a intentarlo.',
   sms=SMS_ES, rights='Todos los derechos reservados.', privacy_l='Política de privacidad'),
}

ON = ' class="on"'
CHECK = '<svg viewBox="0 0 8 8" width="8" height="8" fill="none" aria-hidden="true"><path d="M1 4l2 2 4-3" stroke="#0D1B2A" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'

EXTRA_CSS = '''<style>
  .strip { background: linear-gradient(160deg, #0D1B2A 0%, #162640 100%); padding: 48px 0 76px; text-align: center; }
  .strip .pill-top { display: inline-block; background: rgba(78,201,76,.1); border: 1px solid rgba(78,201,76,.25); color: var(--green); font-size: 12px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; padding: 6px 16px; border-radius: 20px; margin-bottom: 18px; }
  .strip h1 { font-size: clamp(28px, 6vw, 40px); max-width: 640px; margin: 0 auto 12px; }
  .strip h1 .lime { color: var(--green); }
  .strip p { color: #A9B6C6; max-width: 500px; margin: 0 auto 14px; }
  .strip .fee-badge { display: inline-block; background: rgba(78,201,76,.1); border: 1px solid rgba(78,201,76,.25); color: var(--green); font-size: 14px; font-weight: 700; padding: 8px 18px; border-radius: 8px; max-width: 100%; }
  .wizard-wrap { max-width: 660px; margin: -44px auto 60px; padding: 0 16px; position: relative; }
  .wcard { scroll-margin-top: 84px; background: #fff; color: #1A2332; border-radius: 16px; box-shadow: 0 8px 40px rgba(13,27,42,.14); overflow: hidden; }
  .wcard-head { background: var(--navy); color: #fff; padding: 20px 28px; display: flex; gap: 12px; align-items: center; }
  .wcard-head img { width: 30px; height: 30px; }
  .wcard-head h2 { font-size: 18px; margin: 0; color: #fff; }
  .wcard-head p { font-size: 13px; color: #A9B6C6; margin: 2px 0 0; }
  .wbody { padding: 28px; }
  .prog-labels { display: flex; justify-content: space-between; margin-bottom: 8px; gap: 8px; }
  .prog-labels span { font-size: 12px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
  .prog-labels span.on { color: var(--accent); }
  .prog-track { height: 4px; background: var(--border); border-radius: 4px; overflow: hidden; margin-bottom: 26px; }
  .prog-fill { height: 100%; background: var(--green); border-radius: 4px; transition: width .4s ease; }
  .step-page[hidden] { display: none; }
  .field { margin-bottom: 18px; }
  .grid2 { display: grid; gap: 0 14px; }
  @media (min-width: 560px) { .grid2 { grid-template-columns: 1fr 1fr; } }
  .hint { font-size: 13px; color: var(--muted); margin: 6px 0 0; }
  .q { font-size: 16px; font-weight: 800; margin-bottom: 10px; display: block; }
  .bill { border: 1.5px solid var(--border); border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; background: #F5F7FA; transition: .15s; }
  .bill > label { display: flex; align-items: center; gap: 10px; margin: 0; font-weight: 700; min-height: 30px; cursor: pointer; }
  .bill input[type=checkbox] { width: 20px; height: 20px; accent-color: #2E7D32; }
  .bill .more { display: none; margin-top: 12px; }
  .bill.on { border-color: var(--green); background: #EBF9EB; }
  .bill.on .more { display: grid; }
  .opt-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .opt-grid label { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; min-height: 64px; padding: 10px 8px; margin: 0; background: #F5F7FA; border: 1.5px solid var(--border); border-radius: 10px; cursor: pointer; font-weight: 700; font-size: 15px; position: relative; transition: .15s; }
  .opt-grid label small { font-weight: 500; color: var(--muted); font-size: 13px; }
  .opt-grid input { position: absolute; opacity: 0; pointer-events: none; }
  .opt-grid label:has(input:checked) { background: #EBF9EB; border-color: var(--green); }
  .opt-grid label:has(input:focus-visible) { outline: 3px solid var(--green); outline-offset: 2px; }
  input[type=file] { width: 100%; padding: 12px; border: 1.5px dashed #9FB0C3; border-radius: 10px; background: #F5F7FA; font: inherit; font-size: 15px; }
  textarea { width: 100%; min-height: 90px; padding: 12px 16px; border: 1.5px solid #CBD6E2; border-radius: 10px; font: inherit; font-size: 17px; resize: vertical; }
  .fee-note { background: #EBF9EB; border: 1px solid rgba(78,201,76,.35); border-radius: 8px; padding: 14px 16px; font-size: 14px; line-height: 1.6; margin: 0 0 18px; }
  .fee-note strong { color: #1a6e19; }
  .btn-row { display: flex; gap: 12px; margin-top: 22px; }
  .btn-row .btn { flex: 1; }
  .btn-back { min-height: 54px; padding: 0 20px; background: #F5F7FA; color: var(--muted); border: 1.5px solid var(--border); border-radius: 10px; font: inherit; font-weight: 700; cursor: pointer; }
  .btn-back:hover { color: #1A2332; border-color: #1A2332; }
  .wbody .form-error { margin-top: 14px; }
  .pills { display: flex; flex-wrap: wrap; gap: 10px 18px; margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border); }
  .pills span { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; color: var(--muted); }
  .pills i { width: 16px; height: 16px; background: var(--green); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; flex: none; }
  .ty { padding: 44px 28px; text-align: center; }
  .ty h2 { font-size: 26px; margin: 0 0 10px; }
  .ty > p { color: var(--muted); max-width: 420px; margin: 0 auto 24px; }
  .ty-steps { background: #F5F7FA; border-radius: 12px; padding: 22px; text-align: left; counter-reset: n; list-style: none; margin: 0; }
  .ty-steps li { counter-increment: n; position: relative; padding-left: 42px; margin-bottom: 16px; }
  .ty-steps li:last-child { margin-bottom: 0; }
  .ty-steps li::before { content: counter(n); position: absolute; left: 0; top: 2px; width: 28px; height: 28px; border-radius: 50%; background: var(--navy); color: var(--green); font-weight: 900; font-size: 13px; display: flex; align-items: center; justify-content: center; }
  .ty-steps h3 { font-size: 15px; margin: 0 0 3px; }
  .ty-steps p { font-size: 14px; color: var(--muted); margin: 0; }
  @media (max-width: 480px) { .wbody { padding: 22px 18px; } .wcard-head { padding: 18px; } .prog-labels span { font-size: 11px; letter-spacing: .03em; } }
  @media (prefers-reduced-motion: reduce) { .prog-fill { transition: none; } }
</style>'''

def esc(x): return html.escape(x, quote=True)

def page(lang):
    t = T[lang]; i = 1 if lang == 'en' else 2
    bills = '\n'.join(f'''              <div class="bill" data-bill="{v}">
                <label><input type="checkbox" name="bill_{v}" value="1"> {esc(b[i])}</label>
                <div class="more grid2">
                  <div class="field"><label for="prov_{v}">{t['provider']}</label><input id="prov_{v}" name="provider_{v}" type="text" maxlength="60" placeholder="{t['provider_ph']}"></div>
                  <div class="field"><label for="amt_{v}">{t['amount']}</label><input id="amt_{v}" name="amount_{v}" type="text" inputmode="decimal" maxlength="8" placeholder="{t['amount_ph']}"></div>
                </div>
              </div>''' for b in BILLS for v in [b[0]])
    j = 1 if lang == 'en' else 3
    times = '\n'.join(f'                <label><input type="checkbox" name="call_time" value="{x[0]}">{esc(x[j])}<small>{esc(x[j + 1])}</small></label>' for x in TIMES)
    heard = '\n'.join(f'                <option value="{x[0]}">{esc(x[i])}</option>' for x in HEARD)
    labels = '\n'.join(f'          <span id="pl{n}"{ON if n == 1 else ""}>{esc(s)}</span>' for n, s in enumerate(t['steps'], 1))
    pills = '\n'.join(f'            <span><i>{CHECK}</i>{p}</span>' for p in t['pills'])
    oks = '\n'.join(f'          <li><h3>{esc(h)}</h3><p>{esc(p)}</p></li>' for h, p in t['ok_steps'])
    msgs = {k: t[k] for k in ['e_first', 'e_email', 'e_phone', 'e_zip', 'e_bills', 'e_files', 'e_time', 'e_rate', 'e_gen', 'sending', 'submit', 'ok_h', 'step_of']}
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
<main>
  <section class="strip">
    <div class="wrap">
      <p class="pill-top">{t['eyebrow']}</p>
      <h1>{t['h1']}</h1>
      <p>{t['lead']}</p>
      <p class="fee-badge">{esc(t['fee'])}</p>
    </div>
  </section>
  <div class="wizard-wrap off">
    <div class="wcard" id="main-card">
      <div class="wcard-head">
        <img src="/logo.svg" alt="" width="30" height="30">
        <div><h2>{t['card_h']}</h2><p>{t['card_p']}</p></div>
      </div>
      <div class="wbody">
        <div class="prog-labels" aria-hidden="true">
{labels}
        </div>
        <div class="prog-track" role="progressbar" aria-valuemin="1" aria-valuemax="3" aria-valuenow="1" aria-label="{esc(t['step_of'].format(n=1))}" id="prog-bar"><div class="prog-fill" id="prog" style="width:33%"></div></div>

        <form id="intake" novalidate>
          <div class="step-page" id="s1">
            <div class="grid2">
              <div class="field"><label for="first_name">{t['first']}</label><input id="first_name" name="first_name" type="text" autocomplete="given-name" required maxlength="60"></div>
              <div class="field"><label for="last_name">{t['last']}</label><input id="last_name" name="last_name" type="text" autocomplete="family-name" required maxlength="60"></div>
            </div>
            <div class="field"><label for="phone">{t['phone']}</label><input id="phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required maxlength="20" placeholder="(555) 000-0000"><p class="hint">{t['phone_hint']}</p></div>
            <div class="grid2">
              <div class="field"><label for="email">{t['email']}</label><input id="email" name="email" type="email" autocomplete="email" inputmode="email" required maxlength="254"></div>
              <div class="field"><label for="zip">{t['zip']}</label><input id="zip" name="zip" type="text" autocomplete="postal-code" inputmode="numeric" required maxlength="10"></div>
            </div>
            <fieldset class="field">
              <legend>{t['lang']}</legend>
              <div class="lang-choice">
                <label><input type="radio" name="preferred_language" value="en"{' checked' if lang == 'en' else ''}> English</label>
                <label lang="es"><input type="radio" name="preferred_language" value="es"{' checked' if lang == 'es' else ''}> Español</label>
              </div>
            </fieldset>
          </div>

          <div class="step-page" id="s2" hidden>
            <fieldset class="field">
              <legend class="q">{t['s2']}</legend>
{bills}
            </fieldset>
            <div class="field"><label for="files">{t['s3']}</label>
              <input id="files" name="files" type="file" multiple accept="image/jpeg,image/png,image/webp,image/heic,image/heif,application/pdf">
              <p class="hint">{t['s3_hint']}</p>
            </div>
            <p class="fee-note"><strong>{t['fee_h']}</strong> {esc(t['fee_p'])}</p>
            <div class="field"><label for="notes">{t['notes']}</label><textarea id="notes" name="notes" maxlength="500" placeholder="{esc(t['notes_ph'])}"></textarea></div>
          </div>

          <div class="step-page" id="s3" hidden>
            <fieldset class="field">
              <legend class="q">{t['s4']}</legend>
              <p class="hint" style="margin:-4px 0 10px">{t['s4_hint']}</p>
              <div class="opt-grid">
{times}
              </div>
            </fieldset>
            <div class="grid2">
              <div class="field"><label for="heard_from">{t['heard']}</label>
                <select id="heard_from" name="heard_from">
{heard}
                </select>
              </div>
              <div class="field"><label for="promo_code">{t['promo']}</label><input id="promo_code" name="promo_code" type="text" maxlength="20" autocapitalize="characters"></div>
            </div>
            <label class="consent field" for="sms_consent"><input id="sms_consent" name="sms_consent" type="checkbox" value="1"><span>{esc(t['sms'])}</span></label>
            <p class="fee-note"><strong>{t['before_h']}</strong> {esc(t['before_p'])}</p>
          </div>

          <div class="hp" aria-hidden="true"><label for="company">Company</label><input id="company" name="company" type="text" tabindex="-1" autocomplete="off"></div>
          <p class="form-error" id="form-error" role="alert" hidden></p>
          <div class="btn-row">
            <button class="btn-back" type="button" id="back-btn" hidden>&larr; {t['back']}</button>
            <button class="btn" type="submit" id="submit-btn">{t['next']} &rarr;</button>
          </div>
          <p class="small" id="fine" style="margin:14px 0 0;text-align:center" hidden>{t['fine']}</p>
          <div class="pills">
{pills}
          </div>
        </form>
      </div>
    </div>

    <div class="wcard" id="success" hidden tabindex="-1">
      <div class="ty">
        <div class="success"><div class="check"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12l5 5 9-10" stroke="#2E7D32" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></div></div>
        <h2 id="success-title"></h2>
        <p>{esc(t['ok_p'])}</p>
        <ol class="ty-steps">
{oks}
        </ol>
      </div>
    </div>
  </div>
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
  var NEXT = {json.dumps(t['next'] + ' →', ensure_ascii=False)};
  var form = document.getElementById('intake');
  var btn = document.getElementById('submit-btn');
  var back = document.getElementById('back-btn');
  var err = document.getElementById('form-error');
  var cur = 1;
  var q = new URLSearchParams(location.search);
  if (q.get('code')) form.promo_code.value = q.get('code').toUpperCase().slice(0, 20);
  document.querySelectorAll('.bill input[type=checkbox]').forEach(function (cb) {{
    cb.addEventListener('change', function () {{ cb.closest('.bill').classList.toggle('on', cb.checked); }});
  }});
  function fail(msg, el) {{ err.textContent = msg; err.hidden = false; if (el) el.focus(); return false; }}
  function ev(kind) {{ if (window.faEvent) window.faEvent(kind); }}
  function check(step) {{
    var f = form;
    if (step === 1) {{
      if (!f.first_name.value.trim() || !f.last_name.value.trim()) return fail(M.e_first, f.first_name.value.trim() ? f.last_name : f.first_name);
      var digits = f.phone.value.replace(/\\D/g, '');
      if (!(digits.length === 10 || (digits.length === 11 && digits[0] === '1'))) return fail(M.e_phone, f.phone);
      if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(f.email.value.trim())) return fail(M.e_email, f.email);
      if (!/^\\d{{5}}(-\\d{{4}})?$/.test(f.zip.value.trim())) return fail(M.e_zip, f.zip);
    }}
    if (step === 2) {{
      if (!f.querySelector('.bill input[type=checkbox]:checked')) return fail(M.e_bills, f.querySelector('.bill input'));
      var files = f.files.files;
      if (files.length > 5) return fail(M.e_files, f.files);
      for (var i = 0; i < files.length; i++) if (files[i].size > 10 * 1024 * 1024) return fail(M.e_files, f.files);
    }}
    if (step === 3) {{
      if (!f.querySelector('input[name=call_time]:checked')) return fail(M.e_time, f.querySelector('input[name=call_time]'));
    }}
    return true;
  }}
  function go(n) {{
    document.getElementById('s' + cur).hidden = true;
    cur = n;
    var page = document.getElementById('s' + n);
    page.hidden = false;
    document.getElementById('prog').style.width = [33, 66, 100][n - 1] + '%';
    var bar = document.getElementById('prog-bar');
    bar.setAttribute('aria-valuenow', n); bar.setAttribute('aria-label', M.step_of.replace('{{n}}', n));
    for (var k = 1; k <= 3; k++) document.getElementById('pl' + k).classList.toggle('on', k <= n);
    back.hidden = n === 1;
    document.getElementById('fine').hidden = n !== 3;
    btn.textContent = n === 3 ? M.submit : NEXT;
    err.hidden = true;
    document.getElementById('main-card').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    var first = page.querySelector('input:not([type=hidden])');
    if (first) first.focus({{ preventScroll: true }});
  }}
  form.addEventListener('change', function () {{ err.hidden = true; }});
  back.addEventListener('click', function () {{ if (cur > 1) go(cur - 1); }});
  form.addEventListener('submit', function (e) {{
    e.preventDefault(); err.hidden = true;
    if (!check(cur)) return;
    if (cur < 3) return go(cur + 1);
    var f = form;
    var data = new FormData(f);
    ['utm_source', 'utm_medium', 'utm_campaign'].forEach(function (k) {{ data.append(k, q.get(k) || ''); }});
    data.append('page', location.pathname);
    ev('submit');
    btn.disabled = true; back.disabled = true; btn.textContent = M.sending;
    fetch('/api/intake', {{ method: 'POST', body: data }}).then(function (res) {{
      if (res.status === 429) throw new Error('rate');
      if (res.status === 413 || res.status === 415) throw new Error('files');
      if (!res.ok) throw new Error('fail');
      ev('success');
      document.getElementById('success-title').textContent = M.ok_h.replace('{{name}}', f.first_name.value.trim());
      document.getElementById('main-card').hidden = true;
      var s = document.getElementById('success'); s.hidden = false; s.focus(); s.scrollIntoView({{ block: 'start' }});
    }}).catch(function (e2) {{
      if (e2.message === 'files') {{ go(2); fail(M.e_files, f.files); }}
      else fail(e2.message === 'rate' ? M.e_rate : M.e_gen);
      btn.disabled = false; back.disabled = false; btn.textContent = cur === 3 ? M.submit : NEXT;
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
