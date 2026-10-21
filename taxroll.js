const fetch = require('node-fetch');
const readline = require('readline');
const unzipper = require('unzipper');

// Each county posts a weekly zip whose filename changes every week, so the
// current link is scraped from the county's tax roll page unless overridden.
//
// Field positions (0-based offsets below) come from the county layouts, checked
// against the 10/2026 files:
//   Dallas:  TRW-02 "2026 Tax Roll (TRW) File Layout". One row per account/year/jurisdiction.
//   Tarrant: "Taxroll Record Definition" (10/2017). Master.dat has grown to 782 bytes since
//            then, so everything after the owner name sits 40-50 bytes later than published.
const COUNTIES = {
  dallas: {
    name: 'Dallas County',
    pageUrl: 'https://www.dallascounty.org/departments/tax/tax-roll.php',
    linkPattern: /[^"'\s]*trwfile\.\d+\.zip/i,
    url: process.env.DALLAS_TRW_URL || null,
    amountNote: 'Total due incl. penalty & interest',
    createParser: createDallasParser
  },
  tarrant: {
    name: 'Tarrant County',
    pageUrl: 'https://www.tarrantcountytx.gov/en/tax/property-tax/tarrant-county-tax-roll.html',
    linkPattern: /[^"'\s]*TaxRoll\d{8}\.zip/i,
    url: process.env.TARRANT_ROLL_URL || null,
    amountNote: 'Base tax due, before penalty & interest',
    createParser: createTarrantParser
  }
};

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
// A leading directional and trailing street suffix are dropped because counties
// and OSM disagree on them, but never the last remaining word ("101 East Pl" -> "101 EAST").
function addressKey(houseNumber, street) {
  const num = String(houseNumber || '').trim().replace(/^0+/, '').toUpperCase();
  const words = String(street || '')
    .toUpperCase()
    .replace(/[.,#]/g, ' ')
    .split(/\s+/)
    .filter(Boolean);
  while (words.length > 1 && SUFFIXES[words[words.length - 1]]) words.pop();
  if (words.length > 1 && DIRECTIONS[words[0]]) words.shift();
  if (!num || words.length === 0) return null;
  return num + ' ' + words.join(' ');
}

// V8 keeps a substring pointing at its whole parent line, so values that are
// stored copy into a fresh string; otherwise every kept field pins a 500-800 byte row.
function cut(line, start, length) {
  return Buffer.from(line.substr(start, length).trim(), 'latin1').toString('latin1');
}

function joinParts(parts) {
  return parts.filter(Boolean).join(' ').replace(/\s+/g, ' ').trim();
}

// MM/DD/YYYY -> YYYYMMDD so dates compare as strings.
function mdyToYmd(raw) {
  const m = raw.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  return m ? m[3] + m[1] + m[2] : '';
}

function ymd(date) {
  return date.toISOString().slice(0, 10).replace(/-/g, '');
}

function newLead(account) {
  return {
    account: account,
    owner: '',
    mailingAddress: '',
    mailCity: '',
    mailState: '',
    mailZip: '',
    propertyAddress: '',
    key: null,
    totalOwed: 0,
    years: [],
    taxSuit: false,
    deferral: false
  };
}

function addYear(lead, year) {
  if (year && !lead.years.includes(year)) lead.years.push(year);
}

// Dallas TRW: delinquent when DUE-DATE has passed and TOT_AMT_DUE is still owed.
// Only real property, commercial and mobile home rolls; business personal property is not a house lead.
function createDallasParser(today) {
  const todayYmd = ymd(today);
  const leads = new Map();
  return {
    entries: [{
      match: /flat404/i,
      onLine: function(line) {
        if ('RCM'.indexOf(line.charAt(439)) === -1) return;
        if (cut(line, 100, 8) >= todayYmd) return;
        const owed = (parseInt(line.substr(489, 11), 10) || 0) / 100;
        if (owed <= 0) return;
        const account = cut(line, 0, 34);
        let lead = leads.get(account);
        if (!lead) {
          lead = newLead(account);
          const num = cut(line, 440, 8);
          // PARCEL NAME is "STREET, CITY-CODE" (e.g. "BROOKVIEW DR, DA").
          const street = cut(line, 448, 40).replace(/,[^,]*$/, '').trim();
          lead.owner = cut(line, 225, 40);
          lead.mailingAddress = joinParts([cut(line, 265, 40), cut(line, 305, 40), cut(line, 345, 40)]);
          lead.mailCity = cut(line, 385, 40);
          lead.mailState = cut(line, 425, 2);
          lead.mailZip = cut(line, 427, 12).slice(0, 5);
          lead.propertyAddress = joinParts([num, street]);
          lead.key = addressKey(num, street);
          leads.set(account, lead);
        }
        lead.totalOwed += owed;
        addYear(lead, parseInt(line.substr(34, 4), 10));
        if (line.charAt(121) !== ' ') lead.taxSuit = true;
        if (line.charAt(218) === 'D') lead.deferral = true;
      }
    }],
    finish: function() { return Array.from(leads.values()); }
  };
}

// Tarrant: Rec.DAT (one row per account/year/unit/charge) says what is past due;
// Master.dat (one row per account) supplies owner and property address.
// The zip stores Rec.DAT first, so delinquent accounts are known before Master is read.
function createTarrantParser(today) {
  const todayYmd = ymd(today);
  const leads = new Map();
  let recSeen = false;
  return {
    entries: [{
      match: /^rec\.dat$/i,
      onLine: function(line) {
        recSeen = true;
        const due = parseFloat(line.substr(78, 12)) || 0;
        if (due <= 0) return;
        const delinquent = mdyToYmd(cut(line, 90, 10));
        if (!delinquent || delinquent > todayYmd) return;
        const account = cut(line, 0, 11);
        let lead = leads.get(account);
        if (!lead) {
          lead = newLead(account);
          leads.set(account, lead);
        }
        lead.totalOwed += due;
        addYear(lead, parseInt(line.substr(30, 4), 10));
        if (cut(line, 120, 18) || mdyToYmd(cut(line, 110, 10)) < '99990101') lead.taxSuit = true;
      }
    }, {
      match: /^master\.dat$/i,
      onLine: function(line) {
        if (!recSeen) throw new Error('Tarrant zip: Master.dat came before Rec.DAT');
        const lead = leads.get(cut(line, 0, 11));
        if (!lead) return;
        const num = cut(line, 223, 7).replace(/^0+/, '');
        const street = cut(line, 198, 25);
        lead.owner = cut(line, 326, 50);
        lead.mailingAddress = joinParts([cut(line, 376, 50), cut(line, 426, 60)]);
        lead.mailCity = cut(line, 486, 30);
        lead.mailState = cut(line, 516, 20);
        lead.mailZip = cut(line, 536, 18).slice(0, 5);
        lead.propertyAddress = joinParts([num, street]);
        lead.key = addressKey(num, street);
        // Over-65/disabled deferral: start date set, end date open or in the future.
        const deferStart = cut(line, 554, 10);
        const deferEnd = mdyToYmd(cut(line, 564, 10));
        if (deferStart !== '01/01/9999' && (deferEnd === '99990101' || deferEnd > todayYmd)) lead.deferral = true;
      }
    }],
    finish: function() { return Array.from(leads.values()); }
  };
}

// Accounts without a property address (mineral interests, business personal
// property) are not house leads, so they are left out.
function indexLeads(leads) {
  const list = [];
  const byAddress = new Map();
  for (const lead of leads) {
    if (!lead.propertyAddress) continue;
    lead.totalOwed = Math.round(lead.totalOwed * 100) / 100;
    lead.years.sort();
    lead.yearsOwed = lead.years.length;
    lead.outOfStateOwner = Boolean(lead.mailState) && !/^(TX|TEXAS)$/i.test(lead.mailState);
    list.push(lead);
    if (lead.key) byAddress.set(lead.key, lead);
  }
  list.sort(function(a, b) { return b.totalOwed - a.totalOwed; });
  return { list: list, byAddress: byAddress };
}

// Feeds every line of each matching zip entry to its parser; other entries are skipped.
async function parseZipStream(stream, parser) {
  let scanned = 0;
  const zip = stream.pipe(unzipper.Parse({ forceStream: true }));
  for await (const entry of zip) {
    const name = entry.path.split('/').pop();
    const handler = parser.entries.find(function(e) { return e.match.test(name); });
    if (!handler) { entry.autodrain(); continue; }
    const lines = readline.createInterface({ input: entry, crlfDelay: Infinity });
    for await (const line of lines) {
      if (!line) continue;
      scanned++;
      handler.onLine(line);
    }
  }
  return scanned;
}

async function resolveUrl(county) {
  if (county.url) return county.url;
  const response = await fetch(county.pageUrl);
  if (!response.ok) throw new Error('Tax roll page: HTTP ' + response.status);
  const match = (await response.text()).match(county.linkPattern);
  if (!match) throw new Error('No tax roll download link found on ' + county.pageUrl);
  return new URL(match[0].replace(/^href=/i, ''), county.pageUrl).toString();
}

const state = {};
for (const key of Object.keys(COUNTIES)) {
  state[key] = { loadedAt: null, sourceUrl: null, scanned: 0, list: [], byAddress: new Map(), error: null, loading: false };
}

async function loadCounty(key) {
  const county = COUNTIES[key];
  const s = state[key];
  if (s.loading) return;
  s.loading = true;
  try {
    const url = await resolveUrl(county);
    const response = await fetch(url);
    if (!response.ok) throw new Error('Download failed: HTTP ' + response.status);
    const parser = county.createParser(new Date());
    const scanned = await parseZipStream(response.body, parser);
    const result = indexLeads(parser.finish());
    // Swap in only after a full successful parse, so a failed refresh keeps the last good data.
    s.list = result.list;
    s.byAddress = result.byAddress;
    s.scanned = scanned;
    s.sourceUrl = url;
    s.loadedAt = new Date();
    s.error = null;
    console.log(county.name + ' tax roll loaded: ' + result.list.length + ' delinquent accounts from ' + scanned + ' rows');
  } catch (error) {
    s.error = error.message;
    console.error(county.name + ' tax roll error:', error);
  } finally {
    s.loading = false;
  }
}

// Load one county at a time to keep peak memory and bandwidth down on small hosts.
async function loadAll() {
  for (const key of Object.keys(COUNTIES)) await loadCounty(key);
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
  if (process.env.TAXROLL_DISABLED === '1') return;
  loadAll();
  scheduleRefresh();
}

function isSupported(key) {
  return Boolean(COUNTIES[key]);
}

function lookup(key, houseNumber, street) {
  const s = state[key];
  if (!s) return null;
  const base = { county: COUNTIES[key].name, dataAsOf: s.loadedAt, amountNote: COUNTIES[key].amountNote };
  if (!s.loadedAt) {
    return Object.assign(base, { available: false, reason: s.error || 'Tax roll still loading' });
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
    // Neither county file carries a property zip, so this filters on the owner's mailing zip.
    if (opts.zip && !String(r.mailZip).startsWith(opts.zip)) return false;
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
      sourceUrl: s.sourceUrl,
      rowsScanned: s.scanned,
      delinquentAccounts: s.list.length,
      amountNote: COUNTIES[key].amountNote,
      loading: s.loading,
      error: s.error
    };
  }
  return out;
}

module.exports = {
  COUNTIES: COUNTIES,
  addressKey: addressKey,
  createDallasParser: createDallasParser,
  createTarrantParser: createTarrantParser,
  indexLeads: indexLeads,
  parseZipStream: parseZipStream,
  msUntilNextRefresh: msUntilNextRefresh,
  start: start,
  isSupported: isSupported,
  lookup: lookup,
  filterLeads: filterLeads,
  status: status
};
