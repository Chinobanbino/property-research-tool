// Staff dashboard for Gio and Jaime: intake pipeline, call appointments, and Twilio texts to staff phones.
// Customers are never texted from here; only the numbers listed in STAFF.
const path = require('path');
const crypto = require('crypto');
const express = require('express');

const TZ = 'America/Chicago';
const STATUSES = ['new', 'contacted', 'booked', 'signed', 'called', 'saved', 'paid', 'reviewed', 'no_savings', 'no_show', 'lost'];
const COOKIE = 'fa_staff';
const SESSION_DAYS = 30;

// STAFF="Gio:+12145550100,Jaime:+15555550100"
function parseStaff(raw) {
  return String(raw || '').split(',').map((s) => s.trim()).filter(Boolean).map((s) => {
    const i = s.lastIndexOf(':');
    return { name: s.slice(0, i).trim(), phone: s.slice(i + 1).trim() };
  }).filter((s) => s.name && /^\+\d{8,15}$/.test(s.phone));
}

// "2026-10-23T10:00" read as Central Time -> Date (UTC).
function centralToDate(naive) {
  const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/.exec(naive || '');
  if (!m) return null;
  const asUtc = Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5]);
  const offset = (d) => {
    const p = Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone: TZ, hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
      .formatToParts(d).map((x) => [x.type, x.value]));
    return Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute) - d.getTime();
  };
  let t = asUtc - offset(new Date(asUtc));
  t = asUtc - offset(new Date(t)); // second pass settles DST edges
  return new Date(t);
}

const fmtCentral = (d, opts) => new Intl.DateTimeFormat('en-US', { timeZone: TZ, ...opts }).format(d);
const whenText = (d) => `${fmtCentral(d, { weekday: 'short', month: 'short', day: 'numeric' })} ${fmtCentral(d, { hour: 'numeric', minute: '2-digit' })} CT`;
const billsText = (bills) => (bills || []).map((b) => `${b.type}${b.provider ? ' ' + b.provider : ''}${b.monthly ? ' $' + b.monthly : ''}`).join(', ');

module.exports = function staff(app, { pool, clip, rateLimiter, siteUrl }) {
  const SECRET = process.env.SESSION_SECRET || process.env.ADMIN_TOKEN || '';
  const PASSWORD = process.env.DASHBOARD_PASSWORD || '';
  const STAFF = parseStaff(process.env.STAFF);
  const TW = { sid: process.env.TWILIO_ACCOUNT_SID, token: process.env.TWILIO_AUTH_TOKEN, from: process.env.TWILIO_FROM, service: process.env.TWILIO_MESSAGING_SERVICE_SID };
  const enabled = Boolean(SECRET && PASSWORD && STAFF.length && pool);
  if (!enabled) console.warn('Staff dashboard disabled: set DASHBOARD_PASSWORD, STAFF, ADMIN_TOKEN and DATABASE_URL.');

  async function sms(to, body) {
    if (!TW.sid || !TW.token || !(TW.from || TW.service)) { console.log(`[sms not sent, Twilio not set] to ${to}: ${body}`); return false; }
    const form = new URLSearchParams({ To: to, Body: body });
    if (TW.service) form.set('MessagingServiceSid', TW.service); else form.set('From', TW.from);
    try {
      const r = await fetch(`https://api.twilio.com/2010-04-01/Accounts/${TW.sid}/Messages.json`, {
        method: 'POST',
        headers: { Authorization: 'Basic ' + Buffer.from(`${TW.sid}:${TW.token}`).toString('base64'), 'Content-Type': 'application/x-www-form-urlencoded' },
        body: form,
        signal: AbortSignal.timeout(10000),
      });
      if (!r.ok) console.error('twilio send failed:', r.status);
      return r.ok;
    } catch (e) {
      console.error('twilio send failed:', e.message);
      return false;
    }
  }
  const staffByName = (n) => STAFF.find((s) => s.name === n);
  const textStaff = (names, body) => Promise.all(STAFF.filter((s) => !names || names.includes(s.name)).map((s) => sms(s.phone, body)));

  // ---- sessions: signed cookie "name|expires|hmac" ----
  const sign = (v) => crypto.createHmac('sha256', SECRET).update(v).digest('base64url');
  function session(req) {
    if (!enabled) return null;
    const raw = (req.headers.cookie || '').split(/;\s*/).find((c) => c.startsWith(COOKIE + '='));
    if (!raw) return null;
    const [name, exp, mac] = decodeURIComponent(raw.slice(COOKIE.length + 1)).split('|');
    if (!name || !exp || !mac || Date.now() > +exp) return null;
    const want = Buffer.from(sign(`${name}|${exp}`)); const got = Buffer.from(mac);
    if (want.length !== got.length || !crypto.timingSafeEqual(want, got)) return null;
    return staffByName(name) ? name : null;
  }
  const need = (req, res, next) => { const who = session(req); if (!who) return res.status(401).json({ ok: false }); req.staff = who; next(); };
  const page = (file) => (req, res) => { res.set('Cache-Control', 'no-store'); res.set('X-Robots-Tag', 'noindex'); res.sendFile(path.join(__dirname, 'views', file)); };

  app.get('/dashboard', (req, res, next) => (session(req) ? page('dashboard.html')(req, res, next) : res.redirect(302, '/dashboard/login')));
  app.get('/dashboard/login', page('login.html'));
  app.post('/dashboard/login', rateLimiter(10, 15 * 60 * 1000), express.urlencoded({ extended: false, limit: '2kb' }), (req, res) => {
    const who = staffByName(clip(req.body.name, 40));
    const a = crypto.createHash('sha256').update(String(req.body.password || '')).digest();
    const b = crypto.createHash('sha256').update(PASSWORD).digest();
    if (!enabled || !who || !crypto.timingSafeEqual(a, b)) return res.redirect(303, '/dashboard/login?bad=1');
    const exp = String(Date.now() + SESSION_DAYS * 864e5);
    const secure = req.secure ? '; Secure' : '';
    res.set('Set-Cookie', `${COOKIE}=${encodeURIComponent(`${who.name}|${exp}|${sign(`${who.name}|${exp}`)}`)}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${SESSION_DAYS * 86400}${secure}`);
    res.redirect(303, '/dashboard');
  });
  app.post('/dashboard/logout', (req, res) => { res.set('Set-Cookie', `${COOKIE}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0`); res.redirect(303, '/dashboard/login'); });

  app.get('/api/staff/me', need, (req, res) => res.json({ name: req.staff, staff: STAFF.map((s) => s.name), statuses: STATUSES, twilio: Boolean(TW.sid) }));

  app.get('/api/staff/requests', need, async (req, res) => {
    const { rows } = await pool.query(
      `SELECT r.id, r.created_at, r.status, r.first_name, r.last_name, r.email, r.phone, r.zip, r.preferred_language, r.bills, r.call_times,
              r.heard_from, r.notes, r.promo_code, r.sms_consent_at, r.assigned_to, r.appointment_at, r.old_monthly, r.new_monthly,
              r.confirmation, r.staff_notes, r.updated_at,
              COALESCE(json_agg(json_build_object('id', f.id, 'name', f.filename)) FILTER (WHERE f.id IS NOT NULL), '[]') AS files
         FROM intake_requests r LEFT JOIN intake_files f ON f.intake_id = r.id
        GROUP BY r.id ORDER BY r.appointment_at NULLS LAST, r.id DESC LIMIT 500`);
    res.set('Cache-Control', 'no-store');
    res.json(rows);
  });

  app.patch('/api/staff/requests/:id', need, express.json({ limit: '10kb' }), async (req, res) => {
    if (!/^\d+$/.test(req.params.id)) return res.status(404).json({ ok: false });
    const b = req.body || {};
    const sets = []; const vals = [];
    const put = (col, v) => { vals.push(v); sets.push(`${col} = $${vals.length}`); };
    if ('status' in b) { if (!STATUSES.includes(b.status)) return res.status(400).json({ ok: false }); put('status', b.status); }
    if ('assigned_to' in b) { if (b.assigned_to && !staffByName(b.assigned_to)) return res.status(400).json({ ok: false }); put('assigned_to', b.assigned_to || null); }
    let when;
    if ('appointment' in b) {
      when = b.appointment ? centralToDate(b.appointment) : null;
      if (b.appointment && !when) return res.status(400).json({ ok: false });
      put('appointment_at', when);
      put('reminded_at', null);
    }
    for (const col of ['old_monthly', 'new_monthly']) {
      if (col in b) {
        const n = b[col] === '' || b[col] === null ? null : Number(b[col]);
        if (n !== null && !(n >= 0 && n < 100000)) return res.status(400).json({ ok: false });
        put(col, n);
      }
    }
    if ('confirmation' in b) put('confirmation', clip(b.confirmation, 80) || null);
    if ('staff_notes' in b) put('staff_notes', clip(b.staff_notes, 2000) || null);
    if (!sets.length) return res.status(400).json({ ok: false });
    put('updated_at', new Date());
    vals.push(req.params.id);
    const { rows: before } = await pool.query('SELECT assigned_to, appointment_at FROM intake_requests WHERE id = $1', [req.params.id]);
    if (!before.length) return res.status(404).json({ ok: false });
    const { rows } = await pool.query(`UPDATE intake_requests SET ${sets.join(', ')} WHERE id = $${vals.length} RETURNING *`, vals);
    const r = rows[0];
    // Text whoever owns the call when it's newly booked, moved, or handed to them.
    const moved = r.appointment_at && (!before[0].appointment_at || +before[0].appointment_at !== +r.appointment_at);
    const handed = r.assigned_to && r.assigned_to !== before[0].assigned_to;
    if (r.appointment_at && r.assigned_to && (moved || handed)) {
      textStaff([r.assigned_to], `FeeArmor call: ${r.first_name} ${r.last_name[0]}. (${r.preferred_language === 'es' ? 'Spanish' : 'English'}) ${whenText(r.appointment_at)}. ${billsText(r.bills)}. Set by ${req.staff}. ${siteUrl}/dashboard`);
    }
    res.json({ ok: true });
  });

  app.get('/dashboard/file/:id', async (req, res) => {
    if (!session(req) || !/^\d+$/.test(req.params.id)) return res.status(404).send('Not found');
    const { rows } = await pool.query('SELECT filename, mime, data FROM intake_files WHERE id = $1', [req.params.id]);
    if (!rows.length) return res.status(404).send('Not found');
    res.set('Content-Type', rows[0].mime);
    res.set('Content-Disposition', `attachment; filename="${(rows[0].filename || 'bill').replace(/[^\w.\- ]/g, '_')}"`);
    res.set('Cache-Control', 'no-store');
    res.send(rows[0].data);
  });

  // ---- reminders: 60 minutes before each call, and an 8am CT list of the day's calls ----
  let lastDigest = '';
  async function tick() {
    if (!enabled) return;
    try {
      const { rows } = await pool.query(
        `UPDATE intake_requests SET reminded_at = now()
          WHERE appointment_at BETWEEN now() AND now() + interval '60 minutes' AND reminded_at IS NULL AND assigned_to IS NOT NULL
            AND status NOT IN ('called','saved','paid','reviewed','no_savings','lost')
        RETURNING first_name, last_name, phone, preferred_language, bills, appointment_at, assigned_to`);
      for (const r of rows) {
        await textStaff([r.assigned_to], `Reminder: FeeArmor call at ${whenText(r.appointment_at)} with ${r.first_name} ${r.last_name[0]}. (${r.preferred_language === 'es' ? 'Spanish' : 'English'}) ${r.phone}. ${billsText(r.bills)}`);
      }
      const now = new Date();
      const day = fmtCentral(now, { year: 'numeric', month: '2-digit', day: '2-digit' });
      if (fmtCentral(now, { hour: 'numeric', hourCycle: 'h23' }) === '8' && lastDigest !== day) {
        lastDigest = day;
        const start = centralToDate(`${day.slice(6)}-${day.slice(0, 2)}-${day.slice(3, 5)}T00:00`);
        const { rows: today } = await pool.query(
          `SELECT first_name, last_name, appointment_at, assigned_to FROM intake_requests
            WHERE appointment_at >= $1 AND appointment_at < $1::timestamptz + interval '1 day' ORDER BY appointment_at`, [start]);
        for (const s of STAFF) {
          const mine = today.filter((r) => r.assigned_to === s.name);
          if (mine.length) await sms(s.phone, `FeeArmor today (${mine.length}): ` + mine.map((r) => `${fmtCentral(r.appointment_at, { hour: 'numeric', minute: '2-digit' })} ${r.first_name} ${r.last_name[0]}.`).join(', '));
        }
      }
    } catch (e) {
      console.error('reminder tick failed:', e.message);
    }
  }
  setInterval(tick, 60 * 1000).unref();

  return {
    // Called after a new intake is saved.
    newIntake(r) {
      if (!enabled) return;
      textStaff(null, `New FeeArmor signup: ${r.first_name} ${r.last_name[0]}. (${r.preferred_language === 'es' ? 'Spanish' : 'English'}), ${billsText(r.bills)}. Book the call: ${siteUrl}/dashboard`);
    },
  };
};

module.exports.centralToDate = centralToDate;
