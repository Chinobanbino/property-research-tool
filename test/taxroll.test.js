const test = require('node:test');
const assert = require('node:assert');
const taxroll = require('../taxroll');

// Builds a fixed-width row from { offset: value } pairs (0-based offsets, as in taxroll.js).
function row(width, fields) {
  const chars = Array(width).fill(' ');
  for (const [offset, value] of Object.entries(fields)) {
    String(value).split('').forEach(function(c, i) { chars[+offset + i] = c; });
  }
  return chars.join('');
}

function dallasRow(o) {
  return row(534, {
    0: o.account, 34: o.year, 100: o.due, 121: o.suit || ' ', 218: o.defer || ' ',
    225: o.owner, 265: o.mail, 385: o.city, 425: o.state, 427: o.zip,
    439: o.roll || 'R', 440: o.num, 448: o.street, 489: String(o.cents).padStart(11, '0')
  });
}

function feed(parser, entryName, lines) {
  const handler = parser.entries.find(function(e) { return e.match.test(entryName); });
  lines.forEach(function(l) { handler.onLine(l); });
}

const TODAY = new Date(Date.UTC(2026, 9, 21));

test('addressKey drops directionals and suffixes but keeps the street name', () => {
  assert.strictEqual(taxroll.addressKey('1234', 'N. Main Street'), '1234 MAIN');
  assert.strictEqual(taxroll.addressKey('01234', 'main st'), '1234 MAIN');
  assert.strictEqual(taxroll.addressKey('101', 'EAST PL'), '101 EAST');
  assert.strictEqual(taxroll.addressKey('10101', 'E NORTHWEST HWY'), taxroll.addressKey('10101', 'East Northwest Highway'));
  assert.strictEqual(taxroll.addressKey('', 'Main St'), null);
});

test('Dallas: sums past-due rows per account and skips current, paid and personal property', () => {
  const base = { account: '00000000001000000', owner: 'DOE JANE', mail: 'PO BOX 1', city: 'AUSTIN', state: 'TX', zip: '787010000', num: '100', street: 'ELM ST, DA' };
  const p = taxroll.createDallasParser(TODAY);
  feed(p, 'flat404.DALLASCOUNTY.20261019.1', [
    dallasRow(Object.assign({}, base, { year: '2024', due: '20250201', cents: 150000 })),
    dallasRow(Object.assign({}, base, { year: '2025', due: '20260201', cents: 120050, suit: 'J' })),
    dallasRow(Object.assign({}, base, { year: '2026', due: '20270201', cents: 99999 })),
    dallasRow(Object.assign({}, base, { account: '2', year: '2025', due: '20260201', cents: 0 })),
    dallasRow(Object.assign({}, base, { account: '3', year: '2025', due: '20260201', cents: 5000, roll: 'P' })),
    dallasRow(Object.assign({}, base, { account: '4', year: '2025', due: '20260201', cents: 7000, state: 'CA', defer: 'D', num: '9', street: 'OAK AVE, GP' }))
  ]);
  const { list, byAddress } = taxroll.indexLeads(p.finish());
  assert.deepStrictEqual(list.map(r => r.account), ['00000000001000000', '4']);
  const elm = byAddress.get('100 ELM');
  assert.strictEqual(elm.totalOwed, 2700.5);
  assert.deepStrictEqual(elm.years, [2024, 2025]);
  assert.strictEqual(elm.propertyAddress, '100 ELM ST');
  assert.strictEqual(elm.mailZip, '78701');
  assert.strictEqual(elm.taxSuit, true);
  assert.strictEqual(elm.outOfStateOwner, false);
  const oak = byAddress.get('9 OAK');
  assert.strictEqual(oak.deferral, true);
  assert.strictEqual(oak.outOfStateOwner, true);
});

test('Tarrant: receivables decide delinquency, master supplies address; no-address accounts dropped', () => {
  const rec = (acct, year, due, delq, suit) => row(268, { 0: acct, 30: year, 78: due, 90: delq, 110: '01/01/9999', 120: suit || '' });
  const master = (acct, num, street, owner, state) => row(782, {
    0: acct, 198: street, 223: num, 326: owner, 426: '1 MAIN ST', 486: 'FORT WORTH', 516: state, 536: '761020000',
    554: '01/01/9999', 564: '01/01/9999'
  });
  const p = taxroll.createTarrantParser(TODAY);
  feed(p, 'Rec.DAT', [
    rec('00000000001', '2024', '000000100.25', '02/01/2025'),
    rec('00000000001', '2025', '000000200.50', '02/01/2026', 'TX-22-1'),
    rec('00000000001', '2026', '000000999.00', '02/01/2027'),
    rec('00000000002', '2025', '000000000.00', '02/01/2026'),
    rec('00000000003', '2025', '000000050.00', '02/01/2026')
  ]);
  feed(p, 'Master.dat', [
    master('00000000001', '0001312', 'DONNA LN', 'ROE RICHARD', 'OK'),
    master('00000000002', '0000010', 'PINE RD', 'PAID UP', 'TX'),
    master('00000000003', '0000000', '', 'MINERAL OWNER', 'TX')
  ]);
  const { list, byAddress } = taxroll.indexLeads(p.finish());
  assert.deepStrictEqual(list.map(r => r.account), ['00000000001']);
  const lead = byAddress.get('1312 DONNA');
  assert.strictEqual(lead.totalOwed, 300.75);
  assert.deepStrictEqual(lead.years, [2024, 2025]);
  assert.strictEqual(lead.taxSuit, true);
  assert.strictEqual(lead.outOfStateOwner, true);
  assert.strictEqual(lead.mailZip, '76102');
});

test('Tarrant: refuses a zip where Master.dat precedes Rec.DAT', () => {
  const p = taxroll.createTarrantParser(TODAY);
  assert.throws(() => feed(p, 'Master.dat', [row(782, { 0: '1' })]), /Master\.dat came before Rec\.DAT/);
});

test('next refresh is the coming Monday 20:00 UTC', () => {
  const fri = new Date(Date.UTC(2026, 9, 23, 12));
  assert.strictEqual(taxroll.msUntilNextRefresh(fri), (3 * 24 + 8) * 3600 * 1000);
  const monLate = new Date(Date.UTC(2026, 9, 26, 21));
  assert.strictEqual(taxroll.msUntilNextRefresh(monLate), (7 * 24 - 1) * 3600 * 1000);
});

test('lookup reports the county is still loading before data arrives', () => {
  const r = taxroll.lookup('dallas', '1', 'Main');
  assert.strictEqual(r.available, false);
  assert.match(r.reason, /loading/);
});
