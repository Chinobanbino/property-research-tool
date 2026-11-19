# FeeArmor v2 design review
*Oct 21, 2026*

**Verdict:** The look is a big upgrade: light/dark sections, shield logo, "Put an Armor Around Your Wallet," bilingual-first. Fix the copy below before it goes live.

## Must fix
1. **Don't name competitors with claims we can't prove.** "Billed upfront," "charge hundreds before you've saved," "auto-renegotiate without asking" and "keep charging if your bill goes back up" are false or unproven for Rocket Money and BillShark. That's false-advertising risk. Use unnamed, provable claims instead:
   - "Some charge on up to 24 months; we cap at 12."
   - "Some re-negotiate unless you opt out; we always ask first."
2. **Show the price.** Put "One-time fee: 40% of your first 12 months of savings" next to "No savings, no fee."
3. **Remove "No credit card."** The contract requires a card on file before calls. Use "No charge until you save."
4. **Remove "Walk away free."** Customers approve each change, and the fee is due once savings post. Use "You approve every change. You pay only after savings show on your bill."
5. **Tone down overclaims.** "Experts" and "absolute lowest rates" become "bilingual negotiators" and "lower rates."
6. **Spanish scope.** "Luz" (electricity) negotiation becomes "cargos en su factura de luz" (charges on your electric bill); negotiating electricity plans for pay needs a license. Pick one form of address (usted or tú) and use it throughout.

## Technical
- No signup form; the buttons go nowhere.
- The language toggle sits on one page. Keep a separate `/es` page for Spanish search rankings.
- The logo is a cropped 80px image (a stray "F" shows). Send the original file or use the new vector shield.

## Plan (approved)
Keep the live site's working pieces: the signup, `/es`, `/rescue`, the blog and the compliant copy. Restyle them with v2's colors, logo, headline, trust bar, step cards and a "You decide before you pay" section with no competitor names.
