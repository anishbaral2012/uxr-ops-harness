# Sample Theme — Fully Worked Example

Use this as a model for shape, tone, and altitude when synthesizing themes. This is what one Insight slide's content should look like before it goes into the deck.

---

## Theme 3 of 6 — Buyers lose trust when order status is invisible

> Headline is an **insight statement**, not a topic label. It names the consequence ("lose trust") and the cause ("order status is invisible").

### Insights under this theme

**Insight 1: Buyers refresh the portal repeatedly because they don't trust async notifications.**

> "I check the portal probably ten times a day. The email updates come hours late, if at all, so I just don't rely on them anymore."
> — P3, Procurement Manager

**Insight 2: When status is unclear, buyers escalate to suppliers directly — bypassing the platform.**

> "If I can't see what's going on, I just call my supplier rep. That's faster than digging through the system."
> — P5, Senior Buyer

**Insight 3: Stale or contradictory statuses erode confidence in the entire workflow, not just the order in question.**

> "Once I saw an order marked 'shipped' that hadn't actually shipped, I stopped trusting any of the statuses."
> — P7, AP Specialist

### Counter-evidence

P2 (Operations Lead) did not support this theme: they relied on a scheduled daily export rather than live status and reported no trust impact. Accounted for as a sub-finding: buyers whose workflow is batch-oriented are less exposed to live-status gaps, so the trust effect is strongest for buyers working order by order.

---

## How this theme feeds the separate Strategic Recommendations section

The theme block above ends at Counter-evidence. It carries no recommendation field. The design implication is consolidated later, in the analysis output's Strategic Recommendations section, where each entry names its source theme. For this theme it would read:

> **Rec 2 (from Theme 3: order status is invisible) — High.** Surface real-time order status as a primary element on the buyer dashboard, with explicit timestamps and an "as of" indicator. When status changes, push an in-app notification rather than relying on email. Investigate the "shipped but not shipped" data discrepancy as a separate workstream, since it is a trust-killer.

This separation is what lets the verifier confirm every recommendation traces to a theme.

---

## Why this works as a model

- **Headline** names a behavior + consequence, not a topic.
- **Insights** are declarative sentences grounded in the cited accounts. Three quotes alone do not establish prevalence or make every sub-claim representative.
- **Quotes** are vivid, 1–2 sentences, and attributed by code + role.
- **Counter-evidence** is present and non-empty, naming who did not support the theme and how it is accounted for.
- **Recommendations live in the separate Strategic Recommendations section**, each naming its source theme, never inside the theme block.
- **Altitude** is consistent: no quotes inside a recommendation, no recommendations buried inside insights.
