// FeeArmor website: static pages + waitlist signup, first-party analytics and admin export.
require('dotenv').config();
const path = require('path');
const crypto = require('crypto');
const express = require('express');
const compression = require('compression');
const { Pool } = require('pg');

const PORT = process.env.PORT || 3000;
const PUBLIC = path.join(__dirname, 'public');
const CANONICAL_HOST = process.env.CANONICAL_HOST || ''; // e.g. www.feearmor.com
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || '';

// Exact consent sentence shown on /rescue; stored with each phone number as the TCPA record.
const SMS_CONSENT_TEXT = "Yes, FeeArmor may send me marketing and account text messages at the number above, including by automated means. Up to 4 msgs/month. Consent isn't a condition of any purchase. Msg & data rates may apply. Reply STOP to opt out, HELP for help.";
const BILLS = ['Internet', 'Mobile phone', 'Cable or satellite TV', 'Electric', 'Gas', 'Water', 'Home security', 'Other'];
const EVENT_KINDS = ['view', 'submit', 'success'];

const pool = process.env.DATABASE_URL
  ? new Pool({ connectionString: process.env.DATABASE_URL, ssl: process.env.PGSSL === 'true' ? { rejectUnauthorized: false } : false })
  : null;

async function initDb() {
  if (!pool) { console.warn('DATABASE_URL not set: signups are disabled.'); return; }
  await pool.query(`CREATE TABLE IF NOT EXISTS waitlist (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT,
    source TEXT,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
  )`);
  await pool.query(`ALTER TABLE waitlist
    ADD COLUMN IF NOT EXISTS preferred_language TEXT,
    ADD COLUMN IF NOT EXISTS biggest_bill TEXT,
    ADD COLUMN IF NOT EXISTS promo_code TEXT,
    ADD COLUMN IF NOT EXISTS phone TEXT,
    ADD COLUMN IF NOT EXISTS sms_consent_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS sms_consent_text TEXT`);
  await pool.query(`CREATE TABLE IF NOT EXISTS page_events (
    id SERIAL PRIMARY KEY,
    kind TEXT NOT NULL,
    page TEXT,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
  )`);
}

// Simple in-memory rate limiter: max `limit` hits per IP per window.
function rateLimiter(limit, windowMs) {
  const hits = new Map();
  setInterval(() => {
    const cutoff = Date.now() - windowMs;
    for (const [ip, times] of hits) {
      const kept = times.filter((t) => t > cutoff);
      if (kept.length) hits.set(ip, kept); else hits.delete(ip);
    }
  }, windowMs).unref();
  return (req, res, next) => {
    const now = Date.now();
    const times = (hits.get(req.ip) || []).filter((t) => t > now - windowMs);
    if (times.length >= limit) return res.status(429).json({ ok: false });
    times.push(now);
    hits.set(req.ip, times);
    next();
  };
}

const clip = (v, n) => (typeof v === 'string' ? v.trim().slice(0, n) : '');

function normalizePhone(raw) {
  const digits = String(raw || '').replace(/\D/g, '');
  if (digits.length === 10) return '+1' + digits;
  if (digits.length === 11 && digits[0] === '1') return '+' + digits;
  return null;
}

function tokenOk(given) {
  if (!ADMIN_TOKEN || typeof given !== 'string') return false;
  const a = crypto.createHash('sha256').update(given).digest();
  const b = crypto.createHash('sha256').update(ADMIN_TOKEN).digest();
  return crypto.timingSafeEqual(a, b);
}

function csvCell(v) {
  if (v === null || v === undefined) return '';
  let s = v instanceof Date ? v.toISOString() : String(v);
  if (/^[=+\-@]/.test(s) && !/^\+\d+$/.test(s)) s = "'" + s; // keep spreadsheet formulas from running (phone numbers are safe)
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}

const app = express();
app.set('trust proxy', 1); // Railway's edge proxy is one hop; the client can't spoof req.ip
app.disable('x-powered-by');
app.use(compression());

app.use((req, res, next) => {
  res.set('X-Content-Type-Options', 'nosniff');
  res.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.set('X-Frame-Options', 'DENY');
  // Send the bare domain (and any other host) to the canonical www host, keeping path + query.
  if (CANONICAL_HOST && req.hostname !== CANONICAL_HOST && req.hostname.endsWith('feearmor.com')) {
    return res.redirect(301, 'https://' + CANONICAL_HOST + req.originalUrl);
  }
  next();
});

app.get('/healthz', (req, res) => res.json({ ok: true }));

// ---- API ----
app.use('/api', express.json({ limit: '10kb', type: ['application/json', 'text/plain'] }));

app.post('/api/waitlist', rateLimiter(5, 60 * 60 * 1000), async (req, res) => {
  const b = req.body || {};
  if (clip(b.company, 200)) return res.json({ ok: true }); // honeypot: pretend success, store nothing

  const email = clip(b.email, 254).toLowerCase();
  const firstName = clip(b.first_name, 60);
  if (!firstName || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return res.status(400).json({ ok: false });
  if (!pool) return res.status(503).json({ ok: false });

  const lang = b.preferred_language === 'es' ? 'es' : 'en';
  const bill = BILLS.includes(b.biggest_bill) ? b.biggest_bill : null;
  const promo = b.promo_code === 'RESCUE' ? 'RESCUE' : null;
  const phone = b.sms_consent === true ? normalizePhone(b.phone) : null;

  try {
    // Duplicates return success and only fill in fields that were empty (never overwrite).
    await pool.query(
      `INSERT INTO waitlist (email, first_name, source, utm_source, utm_medium, utm_campaign,
         preferred_language, biggest_bill, promo_code, phone, sms_consent_at, sms_consent_text)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,
         CASE WHEN $10::text IS NULL THEN NULL ELSE now() END,
         CASE WHEN $10::text IS NULL THEN NULL ELSE $11 END)
       ON CONFLICT (email) DO UPDATE SET
         preferred_language = COALESCE(waitlist.preferred_language, EXCLUDED.preferred_language),
         biggest_bill = COALESCE(waitlist.biggest_bill, EXCLUDED.biggest_bill),
         promo_code = COALESCE(waitlist.promo_code, EXCLUDED.promo_code),
         sms_consent_at = CASE WHEN waitlist.phone IS NULL THEN EXCLUDED.sms_consent_at ELSE waitlist.sms_consent_at END,
         sms_consent_text = CASE WHEN waitlist.phone IS NULL THEN EXCLUDED.sms_consent_text ELSE waitlist.sms_consent_text END,
         phone = COALESCE(waitlist.phone, EXCLUDED.phone)`,
      [email, firstName, clip(b.source, 200), clip(b.utm_source, 100), clip(b.utm_medium, 100), clip(b.utm_campaign, 100),
       lang, bill, promo, phone, SMS_CONSENT_TEXT]
    );
    res.json({ ok: true });
  } catch (err) {
    console.error('waitlist insert failed:', err.message);
    res.status(500).json({ ok: false });
  }
});

app.post('/api/event', rateLimiter(300, 60 * 60 * 1000), async (req, res) => {
  const b = req.body || {};
  if (!pool || !EVENT_KINDS.includes(b.kind)) return res.status(204).end();
  try {
    await pool.query('INSERT INTO page_events (kind, page, utm_source, utm_medium, utm_campaign) VALUES ($1,$2,$3,$4,$5)',
      [b.kind, clip(b.page, 100), clip(b.utm_source, 100), clip(b.utm_medium, 100), clip(b.utm_campaign, 100)]);
  } catch (err) {
    console.error('event insert failed:', err.message);
  }
  res.status(204).end();
});

// ---- Admin (token in ?token=, stored as the ADMIN_TOKEN variable) ----
app.get('/admin/waitlist.csv', async (req, res) => {
  if (!tokenOk(req.query.token) || !pool) return res.status(404).send('Not found');
  const cols = ['id', 'email', 'first_name', 'preferred_language', 'biggest_bill', 'promo_code', 'phone', 'sms_consent_at',
    'source', 'utm_source', 'utm_medium', 'utm_campaign', 'created_at'];
  const { rows } = await pool.query(`SELECT ${cols.join(', ')} FROM waitlist ORDER BY id`);
  const csv = [cols.join(',')].concat(rows.map((r) => cols.map((c) => csvCell(r[c])).join(','))).join('\n');
  res.set('Content-Type', 'text/csv; charset=utf-8');
  res.set('Content-Disposition', 'attachment; filename="feearmor-waitlist.csv"');
  res.set('Cache-Control', 'no-store');
  res.send(csv);
});

app.get('/admin/stats', async (req, res) => {
  if (!tokenOk(req.query.token) || !pool) return res.status(404).send('Not found');
  const q = (days) => pool.query(
    `SELECT COALESCE(NULLIF(utm_source, ''), '(none)') AS source, kind, COUNT(*)::int AS n
       FROM page_events WHERE created_at > now() - ($1 || ' days')::interval
      GROUP BY 1, 2 ORDER BY 1, 2`, [String(days)]);
  const [d7, d30, total] = await Promise.all([q(7), q(30), pool.query('SELECT COUNT(*)::int AS n FROM waitlist')]);
  res.set('Cache-Control', 'no-store');
  res.json({ signups_total: total.rows[0].n, last_7_days: d7.rows, last_30_days: d30.rows });
});

// ---- Pages (clean URLs) ----
const PAGES = {
  '/': 'index.html',
  '/es': 'es.html',
  '/rescue': 'rescue.html',
  '/privacy': 'privacy.html',
  '/es/privacidad': 'es-privacidad.html',
  '/blog': 'blog/index.html',
  '/es/blog': 'blog/es/index.html',
};
const sendPage = (res, file) => {
  res.set('Cache-Control', 'no-cache');
  res.sendFile(path.join(PUBLIC, file), (err) => { if (err) notFound(res); });
};
const notFound = (res) => { res.status(404); res.set('Cache-Control', 'no-cache'); res.sendFile(path.join(PUBLIC, '404.html')); };

// Old-style .html addresses go to the clean URL.
const CLEAN = Object.fromEntries(Object.entries(PAGES).map(([route, file]) => ['/' + file, route]));
app.get(/\.html$/, (req, res, next) => {
  const p = req.path;
  let target = CLEAN[p];
  if (!target && /^\/blog\/es\/[a-z0-9-]+\.html$/.test(p)) target = '/es/blog/' + p.slice(9, -5);
  else if (!target && /^\/blog\/[a-z0-9-]+\.html$/.test(p)) target = p.slice(0, -5);
  if (!target) return next();
  const qs = req.originalUrl.slice(req.path.length);
  res.redirect(301, target + qs);
});

Object.entries(PAGES).forEach(([route, file]) => app.get(route, (req, res) => sendPage(res, file)));
app.get('/blog/:slug', (req, res) => (/^[a-z0-9-]+$/.test(req.params.slug) ? sendPage(res, `blog/${req.params.slug}.html`) : notFound(res)));
app.get('/es/blog/:slug', (req, res) => (/^[a-z0-9-]+$/.test(req.params.slug) ? sendPage(res, `blog/es/${req.params.slug}.html`) : notFound(res)));

app.use(express.static(PUBLIC, {
  index: false,
  extensions: false,
  setHeaders: (res, file) => {
    if (/\.(png|jpg|svg|ico|webp)$/.test(file)) res.set('Cache-Control', 'public, max-age=604800');
    else res.set('Cache-Control', 'no-cache');
  },
}));

app.use((req, res) => notFound(res));

initDb()
  .then(() => app.listen(PORT, () => console.log(`FeeArmor listening on ${PORT}`)))
  .catch((err) => { console.error('Database setup failed:', err.message); process.exit(1); });
