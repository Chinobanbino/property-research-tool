# FeeArmor website

English + Spanish site for FeeArmor (feearmor.com): home pages, Bill Rescue reader page, blog, privacy pages, waitlist signup, simple visit counts and a CSV export.

## Pages

| Address | File |
|---|---|
| `/` | `public/index.html` |
| `/es` | `public/es.html` |
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
Edit the text in `public/index.html` (English) or `public/es.html` (Spanish), commit and push. Railway redeploys automatically.

## Add a blog post
1. Add an entry to `tools/blog_content.py` with the English and Spanish versions.
2. Run `python3 tools/make_blog.py` and `python3 tools/make_static.py` (this updates the sitemap).
3. Commit and push.

## Export signups
- CSV: `https://www.feearmor.com/admin/waitlist.csv?token=ADMIN_TOKEN`
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
- The tables are created with `CREATE TABLE IF NOT EXISTS`. Nothing in this app drops or resets data.
