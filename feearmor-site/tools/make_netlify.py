# Builds a static copy of the site for Netlify (no Node server, no database).
# Forms go to Netlify Forms instead of /api/*, and _redirects recreates the clean URLs.
# Run:  python3 tools/make_netlify.py <output folder>
import os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, 'public')
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'netlify-build'))

def swap(s, old, new, where):
    if old not in s:
        sys.exit(f'make_netlify: expected text not found in {where}: {old[:60]!r}')
    return s.replace(old, new)

ANALYTICS = re.compile(r'<script>\s*\(function \(\) \{(?:(?!</script>).)*?/api/event.*?</script>\s*', re.S)

HIDDEN = lambda name, extra: (f'<input type="hidden" name="form-name" value="{name}">'
                              + ''.join(f'<input type="hidden" name="{k}">' for k in extra))

def intake(s, where):
    s = swap(s, '<form id="intake" novalidate>',
             '<form id="intake" name="intake" method="POST" enctype="multipart/form-data" data-netlify="true" netlify-honeypot="company" novalidate>'
             + HIDDEN('intake', ['call_times', 'sms_consent_text', 'page', 'utm_source', 'utm_medium', 'utm_campaign']), where)
    # Netlify Forms take one file per input and 8 MB per submission.
    s = re.sub(r'<input id="files" name="files" type="file" multiple accept="([^"]+)">',
               r'<input id="files" name="bill_photo_1" type="file" accept="\1">\n              <input id="files2" name="bill_photo_2" type="file" accept="\1" style="margin-top:8px">', s)
    for a, b in [('Up to 5 files, 10 MB each.', 'Up to 2 files, 8 MB total.'),
                 ('Hasta 5 archivos de 10 MB cada uno.', 'Hasta 2 archivos, 8 MB en total.'),
                 ('Up to 5 files, each under 10 MB (photo or PDF).', 'Up to 2 files, 8 MB total (photo or PDF).'),
                 ('Hasta 5 archivos, cada uno de menos de 10 MB (foto o PDF).', 'Hasta 2 archivos, 8 MB en total (foto o PDF).')]:
        s = s.replace(a, b)
    s = swap(s, '''      var files = f.files.files;
      if (files.length > 5) return fail(M.e_files, f.files);
      for (var i = 0; i < files.length; i++) if (files[i].size > 10 * 1024 * 1024) return fail(M.e_files, f.files);''',
             '''      var total = 0;
      [f.files, f.files2].forEach(function (inp) { if (inp.files[0]) total += inp.files[0].size; });
      if (total > 7.5 * 1024 * 1024) return fail(M.e_files, f.files);''', where)
    s = swap(s, '''    var data = new FormData(f);
    ['utm_source', 'utm_medium', 'utm_campaign'].forEach(function (k) { data.append(k, q.get(k) || ''); });
    data.append('page', location.pathname);''',
             '''    ['utm_source', 'utm_medium', 'utm_campaign'].forEach(function (k) { f[k].value = q.get(k) || ''; });
    f.page.value = location.pathname;
    f.call_times.value = [].map.call(f.querySelectorAll('input[name=call_time]:checked'), function (x) { return x.value; }).join(', ');
    f.sms_consent_text.value = f.sms_consent.checked ? f.querySelector('label.consent span').textContent : '';
    var data = new FormData(f);''', where)
    return swap(s, "fetch('/api/intake', {", "fetch('/', {", where)

def rescue(s):
    w = 'rescue.html'
    s = swap(s, '<form id="waitlist" novalidate>',
             '<form id="waitlist" name="rescue" method="POST" data-netlify="true" netlify-honeypot="company" novalidate>'
             + HIDDEN('rescue', ['sms_consent_text', 'promo_code', 'utm_source', 'utm_medium', 'utm_campaign']), w)
    a = s.index("fetch('/api/waitlist'")
    b = s.index('}).then(function (res) {', a)
    body = '''fetch('/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        'form-name': 'rescue', first_name: firstName, email: email, biggest_bill: bill, preferred_language: form.preferred_language.value,
        phone: smsConsent ? phone : '', sms_consent: smsConsent ? 'yes' : '',
        sms_consent_text: smsConsent ? form.querySelector('label.consent span').textContent : '',
        promo_code: 'RESCUE', company: form.company.value,
        utm_source: params.get('utm_source') || 'billrescue',
        utm_medium: params.get('utm_medium') || 'typed-url',
        utm_campaign: params.get('utm_campaign') || 'lastpage'
      }).toString()
    '''
    return s[:a] + body + s[b:]

REDIRECTS = '''# Old .html addresses -> clean ones
/es.html               /es             301!
/es-intake.html        /es/intake      301!
/es-privacidad.html    /es/privacidad  301!
/blog/es/index.html    /es/blog        301!

# Clean addresses -> files
/es                    /es.html                 200
/es/intake             /es-intake.html          200
/es/privacidad         /es-privacidad.html      200
/es/blog               /blog/es/index.html      200
/es/blog/:slug         /blog/es/:slug.html      200
'''

if os.path.exists(OUT):
    shutil.rmtree(OUT)
shutil.copytree(PUBLIC, OUT)
for dirpath, _, files in os.walk(OUT):
    for name in files:
        if not name.endswith('.html'):
            continue
        p = os.path.join(dirpath, name)
        rel = os.path.relpath(p, OUT)
        s = ANALYTICS.sub('', open(p).read())
        if rel in ('intake.html', 'es-intake.html'):
            s = intake(s, rel)
        elif rel == 'rescue.html':
            s = rescue(s)
        if '/api/' in s:
            sys.exit(f'make_netlify: {rel} still calls /api/')
        open(p, 'w').write(s)
open(os.path.join(OUT, '_redirects'), 'w').write(REDIRECTS)
print('built Netlify site in', OUT)
