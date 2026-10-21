# FeeArmor: Launch (Steps 6 + 7)

## Step 6: Claude in Chrome prompt (Railway + GoDaddy)

Paste this into Claude in Chrome on the Mac where you're logged in to GoDaddy. It does every click itself and stops only for sign-ins and approvals.

```
Set up hosting and the domain for the FeeArmor website. Do every click yourself; stop only for sign-ins, 2FA codes or payment approval, and tell me exactly what you need.

PART A: RAILWAY (railway.com)
1. Sign in to railway.com with GitHub (hand me the sign-in step if needed).
2. New Project → "Deploy from GitHub repo" → choose Chinobanbino/property-research-tool. If Railway asks for access to the repo, grant access to that repo only.
3. Open the new service → Settings:
   - Source → Branch: claude/affectionate-rubin-r5qqv5 (switch to "main" later, once that branch is merged)
   - Source → Root Directory: feearmor-site
   - Name the service "feearmor-web" and the project "feearmor".
4. In the same project: New → Database → Add PostgreSQL.
5. Open feearmor-web → Variables → add:
   - DATABASE_URL = ${{Postgres.DATABASE_URL}}
   - CANONICAL_HOST = www.feearmor.com
   - ADMIN_TOKEN = ${{ secret(48) }}
   Do not copy the ADMIN_TOKEN value into any message, chat or document. I'll read it in Railway myself.
6. Deploy. Wait for the deployment to show "Active". Open Settings → Networking → "Generate Domain", open that *.up.railway.app address, and confirm the FeeArmor home page loads. Also confirm /es, /rescue and /blog load.
7. Settings → Networking → Custom Domain → add www.feearmor.com. Copy the DNS record(s) Railway shows (type, name, value), including any TXT verification record.
Only work inside the new "feearmor" project. Do not open or change any other Railway project.

PART B: GODADDY DNS (godaddy.com, already signed in)
1. My Products → feearmor.com → DNS (Manage DNS).
2. Delete any existing CNAME record named "www". Delete any A record for "@" that points to GoDaddy parking ("Parked").
3. Add exactly the record(s) Railway showed in Part A step 7 (usually a CNAME named "www" pointing to the *.up.railway.app target, plus a TXT verification record if Railway showed one).
4. Go to Forwarding (Domain forwarding) → forward feearmor.com to https://www.feearmor.com, type "Permanent (301)", "Forward only" (no masking). Save.
5. Do not change nameservers, MX records or any other records.
6. Screenshot the final DNS records list and the forwarding setting.

PART C: CHECK
1. Back in Railway → feearmor-web → Custom Domain: wait until www.feearmor.com shows as verified and the certificate is issued (this can take 5–60 minutes; check every 5 minutes, up to 60).
2. Open https://www.feearmor.com and https://feearmor.com. Both should end on https://www.feearmor.com with the padlock.
3. Report back: the Railway *.up.railway.app address, the DNS records you added, the forwarding setting, and whether https://www.feearmor.com loads. Never include the ADMIN_TOKEN.
```

### Email
The site lists **support@feearmor.com** (help@feearmor.com is also mentioned in the privacy pages). Gio is setting up both inboxes. Make sure the email provider's MX and TXT records are added in GoDaddy DNS alongside the Railway records, and don't delete them later.

## Step 7: After it's live (5-minute phone check)

1. **Open www.feearmor.com on your phone.** The page loads with the padlock. Tap "Español" and the Spanish site opens.
2. **Tap "Get Started" and fill out the 3-step form with your own info.** You see "You're armored up, Gio!"
3. **On your laptop, open the export:** `https://www.feearmor.com/admin/intake.csv?token=` plus the ADMIN_TOKEN from Railway → feearmor-web → Variables. Your row is there.
4. **Send the family test link:** `https://www.feearmor.com/intake?code=FAMILY` (Spanish: `/es/intake?code=FAMILY`).

## Launch checklist
- [ ] www.feearmor.com loads over HTTPS, and feearmor.com forwards to it
- [ ] Text the link to yourself in iMessage: the preview shows the FeeArmor image and title
- [ ] /es, /rescue, /blog, /privacy and /es/privacidad all load
- [ ] The intake form works on your phone, and your row is in intake.csv
- [ ] The QR codes in the Bill Rescue PDF open feearmor.com/rescue
- [ ] Your Spanish-speaking VA has read /es and the Spanish blog posts
- [ ] support@feearmor.com and help@feearmor.com receive mail (send a test to each)
- [ ] Add the site to Google Search Console and submit https://www.feearmor.com/sitemap.xml

## UTM links per channel
- YouTube Shorts: `https://www.feearmor.com/?utm_source=youtube&utm_medium=shorts&utm_campaign=launch`
- Instagram bio: `https://www.feearmor.com/?utm_source=instagram&utm_medium=bio&utm_campaign=launch`
- TikTok bio: `https://www.feearmor.com/?utm_source=tiktok&utm_medium=bio&utm_campaign=launch`
- Spanish posts: `https://www.feearmor.com/es?utm_source=facebook&utm_medium=group&utm_campaign=launch_es`
- Signup counts by link: `https://www.feearmor.com/admin/stats?token=` plus your ADMIN_TOKEN
