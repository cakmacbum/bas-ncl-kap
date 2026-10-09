# W01 — English landing page (static)

## Goal
Build a premium, engineering-grade English marketing page for the pressure vessel design suite.
Anyone who looks at it should think "this is a serious, high-quality engineering product".
Every call-to-action leads into the real web app. **Only true claims** (fact sheet below).

## Where
Create `pressure-vessel-suite/apps/landing/` only. Touch nothing else.
Files: `index.html`, `styles.css`, `main.js`, `privacy.html`, `terms.html`, `404.html`,
`robots.txt`, `assets/` (favicon.svg, og.svg or og.png 1200x630), `vercel.json`, `README.md`.

## Tech constraints
- Plain static HTML + hand-written CSS + small vanilla JS. No frameworks, no CDN scripts,
  no build step. Google Fonts allowed (e.g. Inter + JetBrains Mono, or an engineering serif for headings).
- CSP-friendly: no inline `<script>` code, no inline event handlers.
- `vercel.json`: `cleanUrls: true`, `trailingSlash: false`, security headers
  (CSP `default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:`,
  X-Content-Type-Options, Referrer-Policy, Permissions-Policy, frame-ancestors none). No catch-all rewrite.
- Light + dark (`prefers-color-scheme`), mobile-first, 16px side gutter, no horizontal scroll at 375px.
- Accessible: semantic landmarks, alt text, visible focus, contrast AA.
- Single config constant in `main.js`: `const APP_URL = "https://app.example.com";` (the chef will set
  the real URL). All CTAs are `<a>` tags with `data-app-link` and an `href` fallback; `main.js` rewrites them
  from APP_URL (Sign in → `APP_URL`, Start free → `APP_URL + "/?signup=1"`).

## Brand
Working name: **Pressure Vessel Suite** (short: PV Suite). Tagline idea:
"Pressure vessel design, calculated in the open." Built by ZeysLabs. Contact: contact@zeyslabs.com (mailto).

## Design direction
Engineering-drawing aesthetic: title block, thin dimension lines, section hatching, monospace callouts
(e.g. `UG-27 · t = PR/(SE−0.6P)`), blueprint grid used sparingly. Neutral greys + one engineering-blue accent.
Hero visual: an **inline SVG** of a horizontal vessel (shell + 2:1 elliptical heads + 2 nozzles + saddles) drawn as a
technical drawing with dimension annotations; subtle CSS line-draw animation (respect `prefers-reduced-motion`).
Calm, generous spacing. No stock photos, no fake logos, no testimonials, no user counts, no ratings.

## Sections
1. Nav: logo · Features · How it works · Validation · FAQ · Sign in · **Start free**
2. Hero: headline, one-sentence subline, CTAs "Start free — sign in with Google" + "See how it works". Note: "Free. No credit card."
3. How it works (3–4 steps): Define project & design conditions → Geometry (or import STEP) → Code calculations → 3D model + report.
4. Features (only true ones, see fact sheet), grouped: Codes · Geometry & CAD · Compliance · Reporting.
5. Validation section (the differentiator): independent verification against published worked examples produced by
   commercial pressure-vessel software; deviations found were fixed and recorded; 900+ automated tests;
   "every assumption is written into the result". Honest tone.
6. Limitations (short, honest list): not a certified/stamped tool; results are a preliminary engineering assessment and must be
   reviewed by a qualified engineer; Appendix 2 flange design not yet in the calculation pipeline; FEA not available;
   nozzle size catalogue values are not yet supplier-verified.
7. "Coming soon" strip: AI assistant — bring your own Claude API key. (Not available yet. Do not imply it works.)
8. FAQ (5–6): Is it free? (yes, Google sign-in) · Which codes? · Is it certified? (no) · Can I import CAD? (STEP, geometry suggestions you confirm; STL view-only) · What data do you store? (account identity via Google sign-in only; calculations are not stored server-side long-term in V1) · Who builds it?
9. Final CTA + footer: Privacy / Terms links, © ZeysLabs, mailto.

## Fact sheet (the ONLY allowed product claims)
- ASME Section VIII Division 1: cylindrical shell UG-27, formed heads UG-32 (2:1 elliptical, torispherical, hemispherical),
  flat covers UG-34, conical sections, external pressure / vacuum UG-28, nozzle reinforcement UG-37/UG-40,
  minimum thickness UG-16(b), hydrostatic UG-99 and pneumatic UG-100 test pressure, MDMT per UCS-66, global MAWP with governing component.
- EN 13445: shell, heads, test pressure (selectable alongside ASME).
- PED 2014/68/EU: category classification (SEP → IV), essential safety requirements checklist, Declaration of Conformity draft, nameplate.
- Supports: saddle (Zick), skirt, legs.
- Parametric 3D model (CadQuery/OpenCascade) with STEP and STL export; in-browser live 3D preview.
- STEP import: recognises shell + heads + radial nozzles and proposes values that the user confirms. STL is view-only.
- HTML calculation report.
- Do NOT claim: certification, ASME stamp, FEA results, flange design, pricing tiers, customers, user numbers, AI features as available.

## Legal pages
Short, plain-English Privacy (Google sign-in via Supabase Auth: email, name, avatar; no selling; contact email) and Terms
(free beta, provided as-is, no warranty, engineering responsibility stays with the user/qualified engineer).

## Done when
- Opens from file/static server with zero console errors; no external JS.
- grep finds none of: `testimonial|aggregateRating|trusted by|customers|users worldwide`.
- Commit inside your worktree with message `W01: English landing page`.
- Report (≤15 lines): files, design notes, anything unclear.
