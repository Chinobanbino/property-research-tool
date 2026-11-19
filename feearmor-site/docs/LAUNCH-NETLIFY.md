# FeeArmor: publish on Netlify (Claude in Chrome prompt)

Paste the block below into Claude in Chrome. No zip file is needed: Netlify builds the site straight from GitHub using `netlify.toml`.

```
Publish the FeeArmor website on Netlify and connect feearmor.com. Do every click yourself; stop only for sign-ins, 2FA codes or payment screens, and tell me exactly what you need.

PART 0: CANCEL THE RAILWAY RETRY
If you scheduled a Railway retry for FeeArmor earlier today, cancel it. Do not change anything in Railway.

PART A: NETLIFY (netlify.com)
1. Sign up or sign in with GitHub (Free plan; never pick a paid plan).
2. Add new project → Import an existing project → GitHub → repository Chinobanbino/property-research-tool. If GitHub asks, grant access to that repository only.
3. Branch to deploy: claude/affectionate-rubin-r5qqv5. Leave base directory, build command and publish directory as Netlify fills them from netlify.toml (base feearmor-site, command python3 tools/make_netlify.py netlify-build, publish netlify-build). Click Deploy.
4. Wait for "Published". Open the *.netlify.app address and confirm these load: /, /es, /intake, /es/intake, /blog, /privacy.
5. Project configuration → Forms → Enable form detection. Then Deploys → Trigger deploy → Deploy site, and wait for "Published" again.
6. Forms tab: confirm forms named "intake" and "rescue" are listed. Then Forms → Form notifications → Add notification → Email notification → help@feearmor.com, once for "intake" and once for "rescue".
7. Test: open https://<address>.netlify.app/intake?code=FAMILY, fill all 3 steps with first name "Test", last name "Gio", email help@feearmor.com, phone 2145550100, ZIP 75201, check Internet, pick a call time, leave the text box unchecked, and submit. Confirm "You're armored up, Test!" and that the submission appears under Forms → intake.

PART B: CONNECT THE DOMAIN
1. Netlify → Domain management → Add a domain → www.feearmor.com. If Netlify offers to add feearmor.com too, accept, and make www.feearmor.com the primary domain. Do NOT switch to Netlify DNS or change nameservers.
2. GoDaddy (already signed in) → My Products → feearmor.com → DNS:
   - Edit the CNAME named "www" so it points to <address>.netlify.app
   - Delete the A record "@" that points to Parked
   - Do not touch MX, TXT or any email records, and do not change nameservers
3. GoDaddy → Forwarding → forward feearmor.com to https://www.feearmor.com, Permanent (301), forward only (no masking).
4. Back in Netlify → Domain management: wait until www.feearmor.com is verified and HTTPS is provisioned (check every 5 minutes, up to 60).

PART C: REPORT
Report: the *.netlify.app address, whether the test submission arrived, the DNS changes you made, and whether https://www.feearmor.com and https://feearmor.com both load the site with the padlock.
```
