# FeeArmor growth playbook: steps 1–4 (compliant version)

Rule for the whole funnel: **we only auto-text people who asked to hear from us** (texted our keyword, checked the text box on the site, or signed up on /rescue). Everything before that is mail, ads, community and referrals.

---

## Step 1: Who we target

**Primary customer:** Texas household, **Spanish-preferred, ages 45–75, homeowner or long-term renter, paying for 2+ services** (internet + TV and/or 2+ mobile lines).

Why them:
- **Biggest bills, biggest fee.** Bundles (internet + TV + phones) often run $200+/month, and long-time customers are most likely to be past their promo pricing. More savings means a bigger 40% fee for the same 45-minute call.
- **Least served.** Few bill-negotiation services offer full Spanish service, and many providers' retention lines are hard to reach in Spanish. That's our edge.
- **They trust a person, not an app.** The 3-way call with a Spanish-speaking VA fits them better than a "give us your login" app.
- **They pay.** Homeowners and stable households have cards on file and steady bills, so savings show up and fees get collected.

**Secondary:** English-speaking households 55+ with cable + internet bundles (same math, more competition).

**Not targeted by category:** we don't buy or use lists of people by disability, income, benefits or family status. Those are sensitive-data lists, and the Texas consumer-protection law (DTPA) adds penalties of up to $250,000 when people 65+ are harmed. We target **bill profile + language + area**, which reaches the same households legally.

## Step 2: Where the people come from

| Channel | What we use | Cost (rough) | Legal notes |
|---|---|---|---|
| **Direct mail** (main paid channel) | PropStream owner-occupied homeowners in Texas ZIP codes with large Spanish-speaking populations, owned 5+ years. Or a consumer list from Data Axle / Melissa / AccuData with a "Spanish language preference" select. | List: a few cents a record. Postcard printed + mailed: about $0.50–$0.80 each. | **Legal without consent.** Bilingual postcard → QR code to `/es/intake?code=MAIL1` and "Text AHORRO to (number)". |
| **Facebook / Instagram ads in Spanish** | Texas, ages 45+, Spanish language. Send to `/es/intake?utm_source=facebook`. | Test $10–20/day | Ads are fine. The text box on our form is unchecked by default (consent). |
| **Community** | Churches, community centers, Spanish radio call-ins, local Facebook groups. Free "Bill Rescue" talks + the Bill Rescue guide. | Time + printing | Flyers carry the keyword and QR code. |
| **Bill Rescue guide** | Free guide → last page sends readers to `/rescue`. | $0 | Already built. |
| **Referrals** | Every saved customer gets a referral link (step 7). | Referral reward | Best leads: a friend already trusts us. |
| **Keyword texting** | "Text **AHORRO** (Spanish) or **SAVE** (English) to (our number)". | ClickSend per message | The person texting first **is** their opt-in for our replies. |

**PropStream:** use it for **mail lists only**. Skip-traced phone numbers from PropStream are for calls/texts *with* consent; cold-texting them is the part we're not doing (Texas SB 140 registration + $10k bond, both Do Not Call lists, carrier 10DLC rules, and the lawyer sign-off would all be needed first).

**Track every source:** each postcard batch, ad and flyer gets its own `?code=` or `utm_source`, so the dashboard and stats show which channel brings paying customers.

## Step 3: The SMS campaign (opt-in only)

Setup before the first text:
1. **ClickSend:** register the brand and a **10DLC campaign** ("Customer care + marketing to opted-in customers"). Describe the opt-in: keyword text, website checkbox, /rescue form. Paste our consent wording.
2. **Keywords:** AHORRO and SAVE → auto-reply #1. STOP, PARAR, CANCELAR → unsubscribe. HELP, AYUDA → help reply.
3. **Quiet hours (Texas):** send only **Mon–Sat 9am–9pm, Sun noon–9pm** (customer's local time).
4. **Max 4 marketing texts/month** (matches our consent wording).
5. **Spanish accents:** a text with á/é/ñ is sent as a "Unicode" message, which allows ~70 characters per segment instead of 160, so it can cost 2–3x. Keep accents (they matter for trust) but keep Spanish texts short.

### The scripts

Psychology used (all honest; no fake urgency, no fake reviews):
- **Reciprocity:** a free bill review first.
- **Tiny first yes:** reply YES, nothing else.
- **Loss framing that's true:** "you may be paying for fees you never agreed to."
- **Remove risk:** "$0 unless you save" in every pitch.
- **Ease:** "2 minutes, no bills needed yet."
- **Commitment:** they pick their own call time.
- **Specific social proof:** only real numbers once we have them ("Our last 20 customers saved an average of $X/mo"). Never invent them.

| # | When | English | Spanish |
|---|---|---|---|
| 1 | They text SAVE / AHORRO | FeeArmor: Thanks for reaching out! We call your internet, phone & cable companies and lower your bill. $0 unless you save. Reply YES for a free bill review. Up to 4 msgs/mo. Reply STOP to opt out. | FeeArmor: ¡Gracias por escribirnos! Llamamos a sus compañías de internet, celular y cable para bajar su factura. $0 si no ahorra. Responda SI para una revisión gratis. Hasta 4 msjs/mes. STOP para salir. |
| 2 | They reply YES / SI | Great! It takes 2 min and you don't need your bills yet: feearmor.com/intake?code=SMS. Tell us your provider and about what you pay, and we'll text you an estimate. | ¡Excelente! Toma 2 minutos y no necesita sus facturas todavía: feearmor.com/es/intake?code=SMS. Díganos su compañía y cuánto paga más o menos, y le enviamos un estimado. |
| 3 | No form after 2 days (once only) | Still paying too much for {provider}? Your free review is 2 minutes: feearmor.com/intake?code=SMS. Reply STOP to opt out. | ¿Sigue pagando de más? Su revisión gratis toma 2 minutos: feearmor.com/es/intake?code=SMS. STOP para salir. |
| 4 | Form submitted | Thanks {name}! Based on what you told us, people with similar bills often save about ${low}–${high}/mo (estimate, not a promise). Pick a time for your call: {booking link} | ¡Gracias {name}! Según lo que nos dijo, personas con facturas parecidas suelen ahorrar unos ${low}–${high} al mes (estimado, no garantizado). Elija la hora de su llamada: {enlace} |
| 5 | Call booked | You're set for {day} at {time}. Before then, sign your agreement here: {link}. Your card is saved, not charged. You only pay after savings show on your bill. | Su llamada es el {día} a las {hora}. Antes, firme su acuerdo aquí: {enlace}. Su tarjeta se guarda, no se cobra. Solo paga cuando el ahorro aparece en su factura. |
| 6 | 24 hours before | Reminder: your FeeArmor call is tomorrow at {time}, about 45 min (mostly on hold). Have your latest {provider} bill handy, or send a photo: {link}. Reply C to confirm, R to reschedule. | Recordatorio: su llamada es mañana a las {hora}, unos 45 min (casi todo en espera). Tenga a la mano su factura de {compañía} o envíe una foto: {enlace}. Responda C para confirmar o R para cambiar. |
| 7 | 1 hour before | We'll call you at {time} from {number}. See you soon! Reply R if you need a new time. | Le llamamos a las {hora} desde el {número}. ¡Hasta pronto! Responda R si necesita otra hora. |
| 8 | No-show | We missed you today, {name}. No problem, pick a new time here: {link} | No pudimos comunicarnos hoy, {name}. No hay problema, elija otra hora aquí: {enlace} |
| 9 | After a successful call | Done! {provider} lowered your bill from ${old} to ${new}/mo (confirmation #{conf}). When your next bill shows it, text us a photo and we'll wrap up. | ¡Listo! {compañía} bajó su factura de ${old} a ${new} al mes (confirmación #{conf}). Cuando llegue su próxima factura con el cambio, envíenos una foto y terminamos. |
| 10 | Savings verified + charged | Your savings are on your bill! Fee: ${fee} (40% of 12 months of savings){or 3 payments of $x}. Receipt: {link}. Thank you for trusting us! | ¡Su ahorro ya aparece en su factura! Tarifa: ${fee} (40% de 12 meses de ahorro){o 3 pagos de $x}. Recibo: {enlace}. ¡Gracias por su confianza! |
| 11 | 2 days later | Would you leave a quick review? It takes 30 seconds and helps other families find us: {google link} | ¿Nos deja una reseña rápida? Toma 30 segundos y ayuda a otras familias a encontrarnos: {enlace} |
| 12 | 1 week later | Know someone paying too much? Send them feearmor.com/r/{code}. When they save, you get ${reward}. | ¿Conoce a alguien que paga de más? Envíele feearmor.com/es/r/{code}. Cuando ahorre, usted recibe ${reward}. |
| HELP | HELP / AYUDA | FeeArmor: help@feearmor.com. Msg & data rates may apply. Up to 4 msgs/mo. Reply STOP to opt out. | FeeArmor: help@feearmor.com. Pueden aplicar tarifas. Hasta 4 msjs/mes. Responda STOP para salir. |
| STOP | STOP / PARAR | FeeArmor: You're unsubscribed and won't get more texts. | FeeArmor: Se dio de baja y no recibirá más mensajes. |

Notes:
- Messages 4–10 are account messages for a service they asked for; they still respect STOP and quiet hours.
- Message 4's ranges come from the savings calculator (to be built on substantiated numbers).
- Referral reward amount and the `/r/{code}` links are decisions for Gio; the links need building.

## Step 4: They reply YES → sign-up without friction

- The link opens the existing 3-step form (`/intake` or `/es/intake`). **No bill upload required.** It asks: name, phone, email, ZIP, which bills, provider, rough monthly amount, best call times.
- Right after, they get an **estimate** (message 4) and a **booking link**.
- The **bill photo is requested later**: with the 24-hour reminder (message 6). By then they've committed to a call time.
- **The agreement + card on file** happen before the call (message 5). No signature, no call. This is what protects us when someone hangs up after the provider agrees: the fee is owed once savings show on the bill, whoever finished the call.

**Booking link (to set up):** a free Cal.com page with 30-minute slots inside Texas calling hours. Bookings land in the staff dashboard by hand for now (set "Who calls" + "Call time"), which texts Jaime or Gio automatically. Next step: connect Cal.com so bookings appear in the dashboard on their own.
