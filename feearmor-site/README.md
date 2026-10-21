# FeeArmor website

English + Spanish site for FeeArmor (feearmor.com): home pages, Bill Rescue reader page, blog, privacy pages, waitlist signup, simple visit counts and a CSV export.

## Pages

| Address | File |
|---|---|
| `/` | `public/index.html` |
| `/es` | `public/es.html` |
| `/intake`, `/es/intake` (customer intake: bills, uploads, call times) | built by `tools/make_intake.py` |
| `/rescue` (Bill Rescue readers, hidden from Google) | `public/rescue.html` |
| `/privacy`, `/es/privacidad` | built by `tools/make_static.py` |
| `/blog`, `/es/blog`, `/blog/<post>`, `/es/blog/<post>` | built by `tools/make_blog.py` |

## Run it locally

```
npm install
cp .env.example .env   # fill in DATABASE_URL and ADMIN_TOKEN
npm start              # http://localhost:3000
```

## Edit the copy
- Home pages: edit `public/index.html` (English) or `public/es.html` (Spanish).
- Styles for every page: `public/site.css`.
- Intake form: edit `tools/make_intake.py`, then run `python3 tools/make_intake.py`.

Commit and push, and Railway redeploys automatically.

## Add a blog post
1. Add an entry to `tools/blog_content.py` with the English and Spanish versions.
2. Run `python3 tools/make_blog.py` and `python3 tools/make_static.py` (this updates the sitemap).
3. Commit and push.

## Export signups and intake requests
- Intake requests (new customers): `https://www.feearmor.com/admin/intake.csv?token=ADMIN_TOKEN`
  - Each row lists file links. Replace `TOKEN` in a link with your ADMIN_TOKEN to download that bill.
  - Bills contain account numbers. Download them only to the VA system, never to personal devices or chats.
- Bill Rescue reader signups: `https://www.feearmor.com/admin/waitlist.csv?token=ADMIN_TOKEN`
- Visit and signup counts: `https://www.feearmor.com/admin/stats?token=ADMIN_TOKEN`

The token is the `ADMIN_TOKEN` variable in Railway. Never share it or post it anywhere. A wrong token shows "Not found."

## Environment variables

| Name | What it is |
|---|---|
| `DATABASE_URL` | Postgres connection (Railway sets it) |
| `CANONICAL_HOST` | `www.feearmor.com`; any other feearmor.com host redirects there |
| `ADMIN_TOKEN` | Secret for the admin links |
| `PGSSL` | `true` only if the database needs SSL from outside Railway |

## Rollback
Railway → the FeeArmor service → Deployments → pick the last good one → Redeploy.

## Data rules
- Duplicate emails are treated as success and never overwrite what's stored.
- Phone numbers are saved only with the text-consent box checked, along with the time and exact consent wording.
- Intake uploads: photos and PDFs only, up to 5 files of 10 MB each. They're stored in Postgres and downloadable only with the admin token.
- The tables are created with `CREATE TABLE IF NOT EXISTS`. Nothing in this app drops or resets data.
