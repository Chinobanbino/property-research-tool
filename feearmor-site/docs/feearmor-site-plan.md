# FeeArmor Website: Build Plan

Built the same way as the Templ619 waitlist page (7-step Morado HQ web process).
Files that go with this plan:
- `feearmor-index.html`: the finished page (Steps 2 and 4 applied). FORGE builds from this file word for word.
- `feearmor-build-prompt.md`: the Step 5 Claude Code prompt, already reviewed by PROOF.

---

## Step 1: Intake + brief (MAPR)

| Item | Brief |
|---|---|
| **Business + offer** | FeeArmor finds junk fees, expired promos and billing mistakes on US household bills (internet, mobile, TV, utilities, insurance) and fights to get them removed. Performance-based: pay only when it saves money. |
| **Money goal** | **Waitlist signups** (early access). Counted as unique emails in the `waitlist` table. |
| **Audience** | US households, 25–55, tired of rising bills. Traffic from [CONFIRM: Shorts / IG / TikTok / SMS / ads]. Phone-first. |
| **Domain** | feearmor.com [CONFIRM: owned? registrar = GoDaddy?]. Hosting: Railway. |
| **Brand rules** | "FeeArmor": one word, capital F and A, **US spelling "Armor" everywhere (never "Armour")**. Navy `#0B1120` + lime `#A3E635`. Shield-check logo (inline SVG, ready to swap for a real logo file). Tone: on your side, a bit combative toward fees, never toward the customer. Avoid: "guarantee", "bank-grade", "force", savings numbers presented as typical. |
| **Proof available** | None yet. No testimonials, user counts or average savings until real. The hero example is labeled "Illustrative example" and uses no provider brand names. |
| **Data capture** | First name + email. Honeypot. No phone yet (if added later: TCPA consent checkbox, unchecked, with timestamp). Stored in Railway Postgres. |
| **Sitemap** | One page + `/privacy`. Order: Header (wordmark + sticky "Get Early Access") → Hero → What we hunt (fee chips) → How it works (3 steps) → Pricing → Signup → FAQ (accordion) → Footer. Call to action repeated in the header, hero and signup. |
| **Success check (week 1)** | Signups > 0 from each traffic source (by UTM). Submit success rate ≥ 95% of submits. Visit → signup rate tracked from day one; aim ≥ 10% from warm traffic. |

**Calls I made**
- Picked waitlist over a "free audit" signup, because the service isn't live and a free audit button promises something that can't be delivered yet.
- Kept your navy/lime design and the shield-check mark, and dropped Tailwind CDN and Font Awesome to keep the page light and fast.

---

## Step 2: Copy (SITE)

The final copy lives in `feearmor-index.html`. Main lines:

- **Eyebrow:** Defend your wallet against hidden fees
- **H1:** Stop paying fees you never agreed to.
- **Sub:** FeeArmor reads your internet, phone, TV, utility and insurance bills, finds the junk fees, expired promos and billing mistakes, and fights to get them removed.
- **Button (everywhere):** Get Early Access
- **Under button:** Free to join. No card needed. [CONFIRM: You only pay if we save you money.]
- **What we hunt:** "The fees hiding in your monthly bills" + 10 fee chips
- **How it works:** Share your bills → We find the junk → We fight to remove them
- **Pricing:** "You only pay when we win." [CONFIRM: XX]% of first-12-month savings; find nothing, pay $0
- **Signup:** "Be first in line for your free bill scan." + first name, email
- **Success:** "You're on the list, {name}. We'll email you when your free bill scan is ready."
- **FAQ (7):** live yet? / which bills / cost / guarantee (honest no) / passwords / can you lower utility rates (honest: regulated) / data use

**Calls I made**
- Moved the pitch from "we negotiate your rates" to "we find and remove fees." It matches the name, and it's honest about regulated utility rates.
- Removed: "256-Bit Bank-Grade Encryption", "proprietary data to force them", "without lifting a finger", the $842/yr figure, and the Comcast / PG&E / AT&T names. None can be backed up yet, and the brand names implied relationships you don't have.
- Added an FAQ that says plainly "No, we can't guarantee savings."

---

## Step 3: Answer sheet (SITE)

Reply with the number and your answer, or **OK** to take the default.

**Part 1: Blanks**
| # | Question | Suggested default | Your answer |
|---|---|---|---|
| 1 | Is the service live, or is this a pre-launch waitlist? | Waitlist | |
| 2 | Launch month | [none] | |
| 3 | Launch area: nationwide or first states? | Nationwide | |
| 4 | Fee: % of savings, and over what period? ⚠️ blocks launch | 40% of first 12 months | **Decided Oct 21: one-time 40% of first-year savings, billed after savings post, 3-payment split** |
| 5 | Billing terms (charged upfront, monthly, or as savings show up?) | Monthly as savings show up | |
| 6 | How customers share bills: upload PDF/photo, or connect accounts? | Upload PDF or photo | |
| 7 | Who contacts providers: your team, or do you give the customer a script? | Our team, with customer permission | |
| 8 | Do you ever need account passwords? | No | |
| 9 | Bill types at launch | Internet, mobile, TV, electric, gas, home/auto insurance | |
| 10 | Contact email | hello@feearmor.com | |
| 11 | Legal entity name for the footer | [none] | |
| 12 | Instagram URL | [none; remove link if none] | |
| 13 | TikTok URL | [none; remove link if none] | |

**Part 2: Choices**
| # | Question | Suggested default | Your answer |
|---|---|---|---|
| 14 | Email provider for the welcome email (Resend, Mailchimp, ConvertKit, none yet) | Resend | |
| 15 | Is feearmor.com bought? Registrar? | GoDaddy | |
| 16 | GitHub account/org for the repo | Same as your other sites | |

**Part 3: Keep or swap**
| # | Question | Suggested default | Your answer |
|---|---|---|---|
| 17 | Keep the H1 "Stop paying fees you never agreed to."? | Keep | |
| 18 | Keep the 4 example rows in the hero card? | Keep | |

⚠️ **Launch blockers:** #4 (pricing must be accurate before the page goes live). Privacy page is built by FORGE, so you only review it. If you pick an email provider (#14), its sending domain must be verified (DNS records go to HOST).

---

## Step 4: Design + layout spec (PIXL)

**Colors**
| Token | Hex | Use |
|---|---|---|
| bg | `#0B1120` | Page background, inputs |
| surface | `#111827` | Cards |
| border | `#273244` | Card/section borders |
| text | `#F9FAFB` | Headings, body |
| muted | `#9CA3AF` | Secondary text (7.6:1 on bg, passes AA) |
| lime | `#A3E635` | Buttons, highlights, eyebrows |
| lime-hover | `#BEF264` | Button hover |
| on-lime | `#0B1120` | Button text (12:1, passes AA) |
| error | `#F87171` | Inline form errors |

**Type:** system font stack. Body 17px / 1.6. H1 34–54px (fluid), H2 26–36px, weight 800.
**Spacing:** 56px between sections, 24px side padding, content max 720px (hero 1120px, 2 columns at ≥960px).
**Buttons:** lime, 52px tall, full width on phones, 12px radius. Header button 44px.

**Layout**
1. **Header:** sticky, wordmark left, "Get Early Access" right. No hamburger (one page, nothing to hide).
2. **Hero:** copy + button; "Illustrative example" fee card below on phones, beside it on desktop (the old page hid it on phones).
3. **What we hunt:** fee chips that wrap.
4. **How it works:** 3 cards, stacked on phones, 3 across on desktop.
5. **Pricing:** one card with a lime border.
6. **Signup:** card with first name, email, hidden honeypot, button, small print.
7. **FAQ:** `<details>` accordion (works without JS).
8. **Footer:** wordmark, Privacy / Contact / socials, ©.

**States:** button shows "Joining…" while sending → success message replaces the form and gets focus → inline red error with retry for network errors or 429 → a duplicate email shows success.

**Build checklist** (✅ = already true in `feearmor-index.html`)
- ✅ Tap targets ≥ 44px, inputs 17px (no zoom on iPhone)
- ✅ One H1, title tag (50 chars), meta description (152 chars)
- ✅ Open Graph + Twitter tags, canonical, inline SVG favicon
- ✅ No sideways scroll at 320 / 375 / 1280 (tested)
- ✅ Visible focus styles, reduced-motion respected
- ⬜ `og-image.png` (1200×630) to be generated by FORGE
- ⬜ `/privacy` page to be built by FORGE

---

## Step 6: Domain + launch (HOST)

**DNS (GoDaddy → Railway):** FORGE prints the exact records Railway shows after adding the domains. Expect:
| Type | Name | Value |
|---|---|---|
| CNAME (or ALIAS/ANAME, or GoDaddy forwarding if apex CNAME isn't supported) | `@` | `<value Railway shows>` |
| CNAME | `www` | `<value Railway shows>` |
| TXT | `_railway-verify` (if shown) | `<value Railway shows>` |

GoDaddy doesn't support CNAME on the bare domain. If Railway shows only a CNAME for `@`, either move DNS to Cloudflare (free, supports CNAME flattening) or use `www.feearmor.com` as the main address and forward the bare domain to it in GoDaddy. **Default: `www` main + forward the bare domain**, the fewest moving parts.

**Claude in Chrome prompt (run after FORGE prints the records):**
```
Open godaddy.com and sign in (hand me only the sign-in/2FA step).
Go to My Products → feearmor.com → DNS.
1. Delete any existing A record for "@" that points to GoDaddy parking, and any existing CNAME for "www".
2. Add these records exactly: [PASTE RECORDS FROM FORGE RECAP].
3. Go to Forwarding → add domain forwarding from feearmor.com to https://www.feearmor.com, type 301 permanent, "forward only".
4. Save. Screenshot the final DNS table and the forwarding setting, and report back.
Do not change MX, TXT or nameserver records other than the ones listed.
```

**Launch checklist**
- [ ] https://feearmor.com and https://www.feearmor.com both load over HTTPS and end on the same URL
- [ ] Favicon shows in a browser tab
- [ ] Text the link to yourself in iMessage: preview shows title, description and image
- [ ] Sign up from your phone and see the success message
- [ ] /privacy loads
- [ ] CSV export downloads with your test row
- [ ] UTM links ready (use www, since bare-domain forwarding can drop the ?utm part):
  - `https://www.feearmor.com/?utm_source=youtube&utm_medium=shorts&utm_campaign=launch`
  - `https://www.feearmor.com/?utm_source=instagram&utm_medium=bio&utm_campaign=launch`
  - `https://www.feearmor.com/?utm_source=tiktok&utm_medium=bio&utm_campaign=launch`
  - `https://www.feearmor.com/?utm_source=sms&utm_medium=text&utm_campaign=launch`

---

## Step 7: QA + SEO (PROOF + RANKR)

**PROOF before the run:** done. Changes already made to the build prompt:
- Fresh Railway project only; explicit ban on touching `fortunate-ambition` or any other project
- Table creation is `CREATE TABLE IF NOT EXISTS`. No drop, truncate or reset anywhere.
- Test rows use `+feearmortest` emails and only those get deleted
- Admin token printed in terminal only; `.env` is gitignored before the first commit
- No step waits on Gio except GoDaddy DNS, which goes to HOST

**PROOF after launch** (run on the live site):
1. Any `[CONFIRM` text still on the page (blocks launch)
2. Form: valid / empty / bad email / duplicate / honeypot / offline
3. Lighthouse mobile ≥ 90 Performance, ≥ 95 Accessibility, ≥ 90 SEO
4. Broken links (social links pointing to placeholders)
5. Ranked fix list, signup blockers first

**RANKR on-page SEO** (already in the HTML)
- Title: `FeeArmor | Stop Paying Hidden Fees on Your Bills` (50 chars)
- Meta: `FeeArmor finds junk fees, expired promos and billing mistakes on your internet, phone, TV, utility and insurance bills, and fights to get them removed.` (152 chars)
- One H1, H2s in order, Organization schema. FORGE adds FAQPage schema once the FAQ answers are final, plus sitemap.xml and robots.txt.

**Search phrases to target:**
1. hidden fees on bills
2. junk fees internet bill
3. how to remove fees from cable bill
4. lower my internet bill service
5. bill negotiation service
6. modem rental fee refund
7. broadcast TV fee remove
8. late fee reversal utility
9. promo price expired internet bill
10. bill audit service

**Calls I made**
- Kept `www` as the main address, because of GoDaddy's limit on CNAME records for the bare domain.
- Left FAQPage schema out of the HTML until the FAQ answers are confirmed, because schema shouldn't contain placeholders.
