const test = require('node:test');
const assert = require('node:assert');
const taxroll = require('../taxroll');

// Synthetic layout to exercise the parser. The real county positions come from
// their published layouts and are not represented here.
const layout = {
  dateFormat: 'YYYYMMDD',
  amountImpliedDecimals: 2,
  fields: {
    account: [1, 8], owner: [9, 12], mailState: [21, 2],
    situsNum: [23, 5], situsStreet: [28, 15], taxYear: [43, 4],
    amountDue: [47, 9], dueDate: [56, 8]
  }
};

function row(account, owner, state, num, street, year, cents, due) {
  return account.padEnd(8) + owner.padEnd(12) + state.padEnd(2) + num.padEnd(5)
    + street.padEnd(15) + year + String(cents).padStart(9, '0') + due;
}

test('addressKey drops directionals, suffixes and punctuation', () => {
  assert.strictEqual(taxroll.addressKey('1234', 'N. Main Street'), '1234 MAIN');
  assert.strictEqual(taxroll.addressKey('01234', 'main st'), '1234 MAIN');
  assert.strictEqual(taxroll.addressKey('', 'Main St'), null);
});

test('buildIndex keeps only past-due balances and folds years per account', async () => {
  const lines = [
    row('A1', 'SMITH JOHN', 'TX', '100', 'N ELM ST', '2023', 150000, '20240131'),
    row('A1', 'SMITH JOHN', 'TX', '100', 'N ELM ST', '2024', 120050, '20250131'),
    row('B2', 'DOE JANE', 'CA', '22', 'OAK AVE', '2024', 50000, '20250131'),
    row('C3', 'PAID UP', 'TX', '9', 'PINE RD', '2024', 0, '20250131'),
    row('D4', 'NOT DUE', 'TX', '7', 'CEDAR LN', '2025', 90000, '20260131')
  ];
  const result = await taxroll.buildIndex(lines, layout, new Date(Date.UTC(2025, 5, 1)));
  assert.strictEqual(result.scanned, 5);
  assert.deepStrictEqual(result.list.map(r => r.account), ['A1', 'B2']);
  const a1 = result.byAddress.get('100 ELM');
  assert.strictEqual(a1.totalOwed, 2700.5);
  assert.deepStrictEqual(a1.years, [2023, 2024]);
  assert.strictEqual(a1.outOfStateOwner, false);
  assert.strictEqual(result.byAddress.get('22 OAK').outOfStateOwner, true);
});

test('next refresh is the coming Monday 20:00 UTC', () => {
  const fri = new Date(Date.UTC(2026, 9, 23, 12));
  assert.strictEqual(taxroll.msUntilNextRefresh(fri), (3 * 24 + 8) * 3600 * 1000);
  const monLate = new Date(Date.UTC(2026, 9, 26, 21));
  assert.strictEqual(taxroll.msUntilNextRefresh(monLate), (7 * 24 - 1) * 3600 * 1000);
});

test('unconfigured counties report why instead of guessing', () => {
  const s = taxroll.status();
  assert.ok(s.dallas && s.tarrant);
  assert.strictEqual(taxroll.lookup('dallas', '1', 'Main').available, false);
});
