const fetch = require('node-fetch');
const readline = require('readline');
const unzipper = require('unzipper');

// Field positions are 1-based [start, length], copied from each county's
// published record layout. A county stays disabled until its layout is filled
// in -- guessed positions would silently produce wrong leads.
//   Dallas:  TRW-02 "Tax Roll (TRW) File Layout" (dallascounty.org/departments/tax/tax-roll.php)
//   Tarrant: "Tax Roll Record Definition Layout" (tarrantcountytx.gov tax roll page)
// Required fields: account, taxYear, amountDue, dueDate, situsNum, situsStreet.
// Optional: owner, mail1, mail2, mailCity, mailState, mailZip, situsZip.
const COUNTIES = {
  dallas: {
    name: 'Dallas County',
    url: process.env.DALLAS_TRW_URL || null,
    layout: null
  },
  tarrant: {
    name: 'Tarrant County',
    url: process.env.TARRANT_ROLL_URL || null,
    layout: null
  }
};

const REQUIRED_FIELDS = ['account', 'taxYear', 'amountDue', 'dueDate', 'situsNum', 'situsStreet'];

const SUFFIXES = {
  STREET: 'ST', ST: 'ST', AVENUE: 'AVE', AVE: 'AVE', AV: 'AVE', ROAD: 'RD', RD: 'RD',
  DRIVE: 'DR', DR: 'DR', LANE: 'LN', LN: 'LN', BOULEVARD: 'BLVD', BLVD: 'BLVD',
  COURT: 'CT', CT: 'CT', CIRCLE: 'CIR', CIR: 'CIR', PLACE: 'PL', PL: 'PL',
  PARKWAY: 'PKWY', PKWY: 'PKWY', HIGHWAY: 'HWY', HWY: 'HWY', TRAIL: 'TRL', TRL: 'TRL',
  TERRACE: 'TER', TER: 'TER', WAY: 'WAY', LOOP: 'LOOP', FREEWAY: 'FWY', FWY: 'FWY'
};
const DIRECTIONS = {
  NORTH: 'N', N: 'N', SOUTH: 'S', S: 'S', EAST: 'E', E: 'E', WEST: 'W', W: 'W',
  NORTHEAST: 'NE', NE: 'NE', NORTHWEST: 'NW', NW: 'NW', SOUTHEAST: 'SE', SE: 'SE', SOUTHWEST: 'SW', SW: 'SW'
};

// "1234 N. Main Street" and "1234 MAIN ST" both become "1234 MAIN".
// Directionals and suffixes are dropped because counties and OSM disagree on them.
function addressKey(houseNumber, street) {
  const num = String(houseNumber || '').trim().replace(/^0+/, '').toUpperCase();
  const words = String(street || '')
    .toUpperCase()
    .replace(/[.,#]/g, ' ')
    .split(/\s+/)
    .filter(Boolean)
    .filter(function(w) { return !DIRECTIONS[w] && !SUFFIXES[w]; });
  if (!num || words.length === 0) return null;
  return num + ' ' + words.join(' ');
}

function field(line, layout, name) {
  const pos = layout.fields[name];
  if (!pos) return '';
  return line.substr(pos[0] - 1, pos[1]).trim();
}

function parseDate(raw, format) {
  const digits = raw.replace(/\D/g, '');
  if (digits.length !== 8 || /^0+$/.test(digits)) return null;
  let y, m, d;
  if (format === 'MMDDYYYY') {
    m = digits.slice(0, 2); d = digits.slice(2, 4); y = digits.slice(4);
  } else {
    y = digits.slice(0, 4); m = digits.slice(4, 6); d = digits.slice(6);
  }
  const date = new Date(Date.UTC(+y, +m - 1, +d));
  return isNaN(date) ? null : date;
}

function parseAmount(raw, impliedDecimals) {
  const negative = /-/.test(raw);
  const cleaned = raw.replace(/[^\d.]/g, '');
  if (!cleaned) return 0;
  let value = cleaned.includes('.') ? parseFloat(cleaned) : parseInt(cleaned, 10) / Math.pow(10, impliedDecimals || 0);
  return negative ? -value : value;
}

function parseLine(line, layout) {
  return {
    account: field(line, layout, 'account'),
    owner: field(line, layout, 'owner'),
    mail1: field(line, layout, 'mail1'),
    mail2: field(line, layout, 'mail2'),
    mailCity: field(line, layout, 'mailCity'),
    mailState: field(line, layout, 'mailState'),
    mailZip: field(line, layout, 'mailZip'),
    situsNum: field(line, layout, 'situsNum'),
    situsStreet: field(line, layout, 'situsStreet'),
    situsZip: field(line, layout, 'situsZip'),
    taxYear: parseInt(field(line, layout, 'taxYear'), 10) || null,
    amountDue: parseAmount(field(line, layout, 'amountDue'), layout.amountImpliedDecimals),
    dueDate: parseDate(field(line, layout, 'dueDate'), layout.dateFormat)
  };
}

function isDelinquent(row, today) {
  return row.amountDue > 0 && row.dueDate !== null && row.dueDate < today;
}

// Folds delinquent rows (one per account per tax year) into one lead per account.
function createAccumulator() {
  const accounts = new Map();
  return {
    add: function(row) {
      let acct = accounts.get(row.account);
      if (!acct) {
        acct = {
          account: row.account,
          owner: row.owner,
          mailingAddress: [row.mail1, row.mail2].filter(Boolean).join(' '),
          mailCity: row.mailCity,
          mailState: row.mailState,
          mailZip: row.mailZip,
          propertyAddress: [row.situsNum, row.situsStreet].filter(Boolean).join(' '),
          propertyZip: row.situsZip,
          key: addressKey(row.situsNum, row.situsStreet),
          totalOwed: 0,
          years: []
        };
        accounts.set(row.account, acct);
      }
      acct.totalOwed += row.amountDue;
      if (row.taxYear && !acct.years.includes(row.taxYear)) acct.years.push(row.taxYear);
    },
    finish: function() {
      const list = [];
      const byAddress = new Map();
      for (const acct of accounts.values()) {
        acct.totalOwed = Math.round(acct.totalOwed * 100) / 100;
        acct.years.sort();
        acct.yearsOwed = acct.years.length;
        acct.outOfStateOwner = Boolean(acct.mailState) && acct.mailState.toUpperCase() !== 'TX';
        list.push(acct);
        if (acct.key) byAddress.set(acct.key, acct);
      }
      list.sort(function(a, b) { return b.totalOwed - a.totalOwed; });
      return { list: list, byAddress: byAddress };
    }
  };
}

async function openLineStream(url, isZip) {
  const response = await fetch(url);
  if (!response.ok) throw new Error('Download failed: HTTP ' + response.status);
  let stream = response.body;
  if (isZip) stream = response.body.pipe(unzipper.ParseOne());
  return readline.createInterface({ input: stream, crlfDelay: Infinity });
}

// Builds a delinquent-only index from any async iterable of lines.
async function buildIndex(lines, layout, today) {
  const acc = createAccumulator();
  let scanned = 0;
  for await (const line of lines) {
    if (!line.trim()) continue;
    scanned++;
    const row = parseLine(line, layout);
    if (row.account && isDelinquent(row, today)) acc.add(row);
  }
  const result = acc.finish();
  result.scanned = scanned;
  return result;
}

const state = {};
for (const key of Object.keys(COUNTIES)) {
  state[key] = { loadedAt: null, scanned: 0, list: [], byAddress: new Map(), error: null, loading: false };
}

function configProblem(county) {
  if (!county.layout) return 'Record layout not configured yet';
  const missing = REQUIRED_FIELDS.filter(function(f) { return !county.layout.fields[f]; });
  if (missing.length) return 'Layout missing fields: ' + missing.join(', ');
  if (!county.url) return 'Download URL not configured';
  return null;
}

async function loadCounty(key) {
  const county = COUNTIES[key];
  const s = state[key];
  const problem = configProblem(county);
  if (problem) { s.error = problem; return; }
  if (s.loading) return;
  s.loading = true;
  try {
    const isZip = county.layout.zip || /\.zip(\?|$)/i.test(county.url);
    const lines = await openLineStream(county.url, isZip);
    const result = await buildIndex(lines, county.layout, new Date());
    // Swap in only after a full successful parse, so a failed refresh keeps the last good data.
    s.list = result.list;
    s.byAddress = result.byAddress;
    s.scanned = result.scanned;
    s.loadedAt = new Date();
    s.error = null;
    console.log(county.name + ' tax roll loaded: ' + result.list.length + ' delinquent accounts of ' + result.scanned + ' rows');
  } catch (error) {
    s.error = error.message;
    console.error(county.name + ' tax roll error:', error);
  } finally {
    s.loading = false;
  }
}

function loadAll() {
  return Promise.all(Object.keys(COUNTIES).map(loadCounty));
}

// Rolls are posted Monday after the Friday build; refresh Monday 3pm Central (20:00 UTC).
function msUntilNextRefresh(now) {
  const next = new Date(now);
  next.setUTCHours(20, 0, 0, 0);
  const daysAhead = (1 - next.getUTCDay() + 7) % 7;
  next.setUTCDate(next.getUTCDate() + daysAhead);
  if (next <= now) next.setUTCDate(next.getUTCDate() + 7);
  return next - now;
}

function scheduleRefresh() {
  setTimeout(function() {
    loadAll().finally(scheduleRefresh);
  }, msUntilNextRefresh(new Date()));
}

function start() {
  loadAll();
  scheduleRefresh();
}

function isSupported(key) {
  return Boolean(COUNTIES[key]);
}

function lookup(key, houseNumber, street) {
  const s = state[key];
  if (!s) return null;
  const base = { county: COUNTIES[key].name, dataAsOf: s.loadedAt };
  if (!s.loadedAt) {
    return Object.assign(base, { available: false, reason: s.error || configProblem(COUNTIES[key]) || 'Tax roll still loading' });
  }
  const k = addressKey(houseNumber, street);
  if (!k) {
    return Object.assign(base, { available: true, matchAttempted: false, reason: 'No house number from geocoder' });
  }
  const hit = s.byAddress.get(k);
  if (!hit) return Object.assign(base, { available: true, matchAttempted: true, delinquent: false });
  return Object.assign(base, { available: true, matchAttempted: true, delinquent: true, record: hit });
}

function filterLeads(key, opts) {
  const s = state[key];
  if (!s) return [];
  const minOwed = opts.minOwed || 0;
  const minYears = opts.minYears || 0;
  return s.list.filter(function(r) {
    if (r.totalOwed < minOwed) return false;
    if (r.yearsOwed < minYears) return false;
    if (opts.zip && !String(r.propertyZip).startsWith(opts.zip)) return false;
    return true;
  });
}

function status() {
  const out = {};
  for (const key of Object.keys(COUNTIES)) {
    const s = state[key];
    out[key] = {
      county: COUNTIES[key].name,
      loadedAt: s.loadedAt,
      rowsScanned: s.scanned,
      delinquentAccounts: s.list.length,
      loading: s.loading,
      error: s.error
    };
  }
  return out;
}

module.exports = {
  COUNTIES: COUNTIES,
  addressKey: addressKey,
  parseLine: parseLine,
  isDelinquent: isDelinquent,
  buildIndex: buildIndex,
  msUntilNextRefresh: msUntilNextRefresh,
  start: start,
  isSupported: isSupported,
  lookup: lookup,
  filterLeads: filterLeads,
  status: status
};
