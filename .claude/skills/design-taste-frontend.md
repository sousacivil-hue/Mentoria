# tasteskill: Anti-Slop Frontend Skill

> Landing pages, portfolios, and redesigns. Not dashboards, not data tables, not multi-step product UI.

---

## Core Operating Principles

This skill prevents AI-generated design defaults by enforcing **brief inference first, then deliberate dial-setting, then system selection**. Every layout, color choice, and animation is contextual—nothing fires automatically.

### The Three-Step Entry Point

1. **Read the brief** (Section 0): What page type? Who's the audience? What vibe words are present? What constraints exist?

2. **Declare a one-line design read** before touching code. Example: *"Reading this as: B2B SaaS landing for technical buyers, Linear-style minimalist, leaning Tailwind + Geist + restrained motion."*

3. **Set three dials** based on that read, not templates (Section 1):
   - `DESIGN_VARIANCE` (1=symmetrical, 10=asymmetric chaos)
   - `MOTION_INTENSITY` (1=static, 10=cinematic)
   - `VISUAL_DENSITY` (1=gallery-airy, 10=cockpit-packed)

---

## The Three Dials

| Signal | VARIANCE | MOTION | DENSITY |
|--------|----------|--------|---------|
| Minimalist / Linear-style | 5–6 | 3–4 | 2–3 |
| Premium consumer / Apple-y | 7–8 | 5–7 | 3–4 |
| Playful / Awwwards / agency | 9–10 | 8–10 | 3–4 |
| Landing (SaaS mainstream) | 7 | 6 | 4 |
| Portfolio (Designer) | 8 | 7 | 3 |
| Public-sector / trust-first | 3–4 | 2–3 | 4–5 |

---

## Anti-Default Disciplines

### Typography
- **Default sans-serif, not serif.** Serif is only acceptable when the brand explicitly names it, or when genuinely editorial/luxury/heritage. Banned serif-by-default: Fraunces, Instrument_Serif.
- **Italic descenders must have `leading-[1.1]` minimum** to prevent clipping on words with `y g j p q`.
- **No Inter as automatic choice.** Rotate through Geist, Outfit, Cabinet Grotesk, Satoshi first.
- **EMPHASIS RULE:** Use italic/bold of the *same* font, never inject a serif word into a sans headline for "visual interest."

### Color
- **One accent color per project, locked across all sections.** No warm-grey site suddenly getting a blue CTA in section 7.
- **The Lila Rule (mandatory):** AI-purple/neon-blue glows are discouraged. Use neutral bases (Zinc/Slate/Stone) with high-contrast singular accents.
- **PREMIUM-CONSUMER PALETTE BAN:** The warm beige+brass+oxblood+espresso family is **banned as default** for premium-consumer briefs. Rotate through these instead:
  - Cold Luxury (silver-grey + chrome)
  - Forest (deep green + bone + amber)
  - Black and Tan (sharp contrast, no beige)
  - Cobalt + Cream
  - Terracotta + Slate
  - Pure monochrome + one saturated pop

### Layout & Spacing (Hard Rules)
- **Hero MUST fit the initial viewport.** Headline ≤2 lines, subtext ≤20 words AND ≤4 lines, CTAs visible without scroll.
- **Hero top padding max `pt-24`.** More reads as a layout bug, not intentional breathing room.
- **Hero stack max 4 text elements:** eyebrow (optional), headline, subtext, CTAs. **BANNED in hero:** tiny tagline below CTAs, trust logo strip, pricing teaser, feature bullets.
- **Navigation renders on ONE line** at desktop; max height 80px.
- **ZIGZAG ALTERNATION CAP:** No more than 2 consecutive sections with "left-image + right-text" then "left-text + right-image" pattern. The 3rd is a Pre-Flight Fail.
- **Section-Layout-Repetition:** Max 1 use per layout family. Eight sections need ≥4 different families.
- **EYEBROW RESTRAINT (mandatory):** Max 1 eyebrow per 3 sections. The `uppercase tracking` micro-label above every headline is the #1 LLM default. Counts mechanically in Pre-Flight.
- **Bento has exact cell count:** 3 items → 3 cells, 5 items → 5 cells. No empty cells mid-grid.

### Interactions & States
- **Button contrast:** White text on white button, transparent button on white page, no visible border = banned.
- **CTA labels MUST fit one line** at desktop. "VIEW SELECTED WORK" wrapping = Pre-Flight Fail.
- **No duplicate CTA intent:** One label per intent across the page. "Get in touch" + "Contact us" = same intent → pick one.
- **Form labels above inputs,** helper text optional, error text below. No placeholder-as-label.
- **Tactile feedback:** `-translate-y-[1px]` or `scale-[0.98]` on active state.

### Visual Assets (Mandatory)
- **Image-gen tool first** if available. Generate section-specific photography at the right aspect ratio.
- **Real web images second:** Picsum with descriptive seed (`picsum.photos/seed/marrow-cookware-kitchen/1600/1200`).
- **Last resort:** Explicit placeholder slots. **NEVER** fill with hand-rolled SVG illustrations or div-based fake screenshots.
- **"Trusted by" logo walls:** Real SVG logos (Simple Icons, devicon), NOT plain text wordmarks. Logos only, no industry labels underneath.
- **No pills/labels overlaid on images** (`Plate · Brand`). No photo-credit captions as decoration.

---

## Forbidden Tells (Section 9)

### The Em-Dash Ban (Absolute, Non-Negotiable)
**Em-dash (`—`) is completely banned everywhere:**
- Headlines, eyebrows, pills, buttons, captions, nav items, body copy, quotes, attribution, alt text.
- Use periods, commas, parentheses, colons, or line breaks instead.
- If your output contains a single `—` or `–` anywhere visible, the output fails Pre-Flight and must be rewritten.

### Other Critical Tells
- **No generic fake names.** "John Doe", "Sarah Chan" → creative, realistic names.
- **No generic avatars.** Plain SVG "egg" icons → believable placeholders or specific styling.
- **No fake-precise numbers.** `99.99%`, `1234567` unless real data. Avoid engineering precision the brand doesn't claim.
- **No startup-slop names.** "Acme", "Nexus", "CloudLy" → contextual, premium names.
- **No filler verbs.** "Elevate", "Seamless", "Unleash" → concrete language.
- **No hand-rolled SVG icons.** Phosphor / HugeIcons / Radix / Tabler only. Lucide by request only.
- **No div-based fake product UIs** rendered as screenshots.
- **No version labels in hero** (`V0.6`, `BETA`) unless the brief is a product launch.
- **No section-numbering eyebrows** (`001 · Capabilities`, `06 · how it works`).
- **No "Quietly in use at"** social-proof headers. Use "Trusted by" or skip the heading.
- **No decorative dots** by default. Allowed only for real semantic state (live server status, availability flags).
- **No decoration text strip at hero bottom** (`BRAND. MOTION. SPATIAL.`).
- **No floating top-right sub-text** in section headings.
- **No scoring/progress bars with filled background tracks** as comparison visuals.
- **No locale/city-name/time/weather strips** unless brief explicitly describes a distributed studio.
- **No scroll cues.** Users know what scroll is.

---

## Stack & Architecture Defaults

### Framework & Styling
- **Next.js / React** with Server Components by default.
- **Tailwind v4** (use `@tailwindcss/postcss`; not the `tailwindcss` plugin in PostCSS config).
- **Motion** (import from `motion/react`; legacy `framer-motion` alias still works but prefer `motion/react`).
- **Fonts:** `next/font` or self-hosted `@font-face` with `font-display: swap`. Never `<link>` to Google Fonts in production.

### Icons
- Priority: **Phosphor**, HugeIcons, Radix, Tabler.
- Avoid Lucide by default; accept only on explicit request.
- One family per project. Never mix libraries in the same tree.

### State Management
- Local `useState` / `useReducer` for isolated UI.
- **NEVER** use `useState` for continuous values (mouse position, scroll progress, pointer physics). Use Motion's `useMotionValue` / `useTransform` / `useScroll`. `useState` re-renders on every frame and collapses on mobile.

### Dark Mode (Mandatory)
- Design for **both modes from the start.** Use Tailwind `dark:` variant OR CSS variables.
- Respect `prefers-color-scheme: dark`. Default to system preference.
- Test in both modes before shipping.

### Accessibility & Performance
- **Reduced motion (mandatory for `MOTION_INTENSITY > 3`):** Wrap with `useReducedMotion()` and degrade to static.
- **Core Web Vitals:** LCP < 2.5s, INP < 200ms, CLS < 0.1. Hero image must be `next/image priority` or preloaded.
- **Z-index discipline:** Never spam `z-50`. Use systemic layer contexts only (sticky nav, modals, grain overlays).
- **Grain/noise filters only on fixed `pointer-events-none` pseudo-elements.** NEVER on scrolling containers—destroys mobile FPS.

---

## Motion & Animation Protocols

### When Motion Fires
- **`MOTION_INTENSITY 1–3`:** Static only. CSS `:hover` / `:active` states. `prefers-reduced-motion` is the default mode.
- **`MOTION_INTENSITY 4–7`:** CSS transitions on `transform` / `opacity`. `animation-delay` cascades for load-ins.
- **`MOTION_INTENSITY 8–10`:** Scroll-triggered reveals, parallax, GSAP ScrollTrigger. **NEVER `window.addEventListener('scroll')`** – it's a hard ban. Use Motion `useScroll()`, ScrollTrigger, IntersectionObserver, or CSS `animation-timeline: view()`.

### Canonical Patterns (When Needed)

**Sticky-Stack on Scroll:**
```
• start: "top top" (pin at viewport top, not center)
• pin: true on every card except the last
• scale/opacity transforms driven by NEXT card's scroll trigger
• cleanup in useEffect return
```

**Horizontal-Pan Hijack:**
```
• start: "top top", pin: true on wrapper
• end: "+=${distance}" (scroll length = track width − viewport)
• scrub: 1 for smooth scrub
• invalidateOnRefresh: true
```

**Scroll-Reveal Stagger (lighter):**
Prefer Motion's `whileInView` over GSAP for simple "items appear as they enter viewport" – no pinning, lighter bundle.

### Motion Discipline
- **MOTION MUST BE MOTIVATED.** Every animation answers: "what does this communicate?" Valid: hierarchy, storytelling, feedback, state transition. Invalid: "it looked cool."
- **MARQUEE MAX ONE PER PAGE.** Horizontal text scroll allowed once; two or more reads as filler.
- **Motion claimed = motion shown.** If `MOTION_INTENSITY > 4`, the page must actually animate. Never half-build broken motion.

---

## Design System Selection (Section 2)

Reach for official packages when the brief matches:

| Brief reads as… | Use |
|---|---|
| Microsoft / enterprise SaaS / dashboards | `@fluentui/react-components` |
| Google-ish / Material-flavored | `@material/web` |
| IBM B2B / enterprise analytics | `@carbon/react` |
| Shopify app | `polaris.js` web components / Polaris React |
| Atlassian / Jira-style | `@atlaskit/*` |
| GitHub / devtool / community | `@primer/react-brand` |
| UK public-sector | `govuk-frontend` |
| US public-sector / trust-first | `uswds` |
| Fast MVP (boring, works) | Bootstrap 5.3 |
| Modern accessible React | `@radix-ui/themes` |
| Modern SaaS (own components) | `shadcn/ui` |
| Indie / AI marketing SaaS | Tailwind v4 utilities + `dark:` |

**One system per project.** Do not mix Fluent React with Carbon in the same tree.

---

## Redesign Protocol (Section 11)

### Detect the Mode
- **Greenfield:** No existing site, or full overhaul approved. Use baseline dials.
- **Preserve:** Modernise without breaking brand. Audit first, extract tokens, evolve gradually.
- **Overhaul:** New visual language on existing content. Treat visuals as greenfield; preserve content & IA.

### Audit Before Touching
Document current state:
- Brand tokens (colors, type, logo, radii)
- Information architecture (page tree, primary nav, conversion paths)
- Content blocks (what exists, what's working, what's filler)
- Signature patterns (recognisable interactions to keep)
- Dials to retire (AI-slop tells, broken layouts, dead links)
- **SEO baseline (current ranking pages, meta, structured data, OG cards)—SEO migration is the #1 redesign risk.**

### Preservation Rules
- Do not change information architecture unless asked.
- Extract brand colors before applying color rules (override LILA RULE if brand is already purple).
- Preserve copy voice unless asked for a rewrite.
- Honor existing accessibility wins; do not regress.
- Respect analytics event names (do not rename buttons, form fields, section IDs).

### Modernisation Levers (Priority Order)
1. Typography refresh (highest visual lift, lowest risk).
2. Spacing & rhythm (increase section padding, fix vertical rhythm).
3. Color recalibration (desaturate, unify neutrals, keep brand accent).
4. Motion layer (add MOTION_INTENSITY-appropriate interactions).
5. Hero & key-section recomposition.
6. Full block replacement (only when unsalvageable).

---

## Pre-Flight Checklist (Mandatory Before Ship)

**Run every box. If any fails, the page is not done.**

- [ ] Brief inference declared (one-liner)?
- [ ] Dial values explicit and reasoned?
- [ ] Design system chosen from Section 2 or aesthetic labeled honestly?
- [ ] Redesign mode detected and audited (if applicable)?
- [ ] **ZERO em-dashes (`—`) anywhere** (non-negotiable)?
- [ ] Page Theme Lock: ONE theme for whole page, no mid-scroll inversions?
- [ ] Color Consistency Lock: one accent color used identically across sections?
- [ ] Shape Consistency Lock: one corner-radius system applied consistently?
- [ ] Button Contrast Check: all CTA text readable (WCAG AA 4.5:1)?
- [ ] CTA Button Wrap: no label wraps to 2+ lines at desktop?
- [ ] Form Contrast Check: inputs, placeholders, labels pass WCAG AA?
- [ ] Serif discipline: no Fraunces/Instrument_Serif without explicit brand justification?
- [ ] Premium-consumer palette: NOT AI-default beige+brass+oxblood+espresso?
- [ ] Italic descender clearance: `leading-[1.1]` + `pb-1` reserve on descender words?
- [ ] Hero fits viewport: ≤2-line headline, ≤20-word subtext, ≤4 lines, CTA visible without scroll?
- [ ] Hero top padding: max `pt-24` at desktop?
- [ ] Hero stack: max 4 text elements, no tiny tagline below CTAs?
- [ ] **EYEBROW COUNT (mechanical):** count instances of `uppercase tracking`. Count ≤ ceil(sectionCount / 3)?
- [ ] Split-Header Ban: no "left big + right explainer" pattern?
- [ ] Zigzag Alternation: no 3+ consecutive image+text-split sections?
- [ ] No Duplicate CTA Intent: no two CTAs with same intent?
- [ ] Logo wall = logos only, NO category labels underneath?
- [ ] Bento Background Diversity: ≥2–3 cells with real visual variation?
- [ ] "Used by" logo wall UNDER hero, uses REAL SVG logos, not plain text?
- [ ] Copy Self-Audit: no grammatically-broken or AI-hallucinated strings?
- [ ] Motion motivated: every animation justified in one sentence?
- [ ] Marquee max-one-per-page?
- [ ] Navigation ONE line at desktop, height ≤80px?
- [ ] Section-Layout-Repetition: ≥4 different layout families across 8 sections?
- [ ] Bento exact cell count (N items → N cells, no empty cells)?
- [ ] Long lists use right UI component (not default `<ul>` for >5 items)?
- [ ] Real images used (gen-tool first, Picsum-seed, explicit placeholders) – NO fake screenshots or decorative SVGs?
- [ ] No pills/labels on images?
- [ ] No photo-credit captions as decoration?
- [ ] No version footers?
- [ ] No micro-meta-sentences under eyebrows?
- [ ] No decoration text strip at hero bottom?
- [ ] No floating top-right sub-text in section headings?
- [ ] No scoring/progress bars with filled tracks?
- [ ] No locale/city/time/weather strips?
- [ ] No scroll cues?
- [ ] No version labels in hero?
- [ ] No section-numbering eyebrows?
- [ ] No decorative dots?
- [ ] No `border-t` + `border-b` on every list row?
- [ ] Content density sane: no 20-row data tables, ≤25-word sub-paragraphs?
- [ ] Quotes ≤3 lines, clean attribution (no em-dash)?
- [ ] Motion claimed = motion shown (if `MOTION_INTENSITY > 4`, page animates)?
- [ ] GSAP sticky-stack / horizontal-pan per canonical skeletons (Section 5)?
- [ ] No `window.addEventListener('scroll')`?
- [ ] Reduced motion wrapped (all `MOTION_INTENSITY > 3`)?
- [ ] Dark mode tokens defined and tested in both modes?
- [ ] Mobile collapse explicit for high-variance layouts?
- [ ] Viewport stability: `min-h-[100dvh]`, never `h-screen`?
- [ ] `useEffect` animations have strict cleanup functions?
- [ ] Empty / loading / error states provided?
- [ ] Cards omitted where spacing suffices?
- [ ] Icons from allowed library only (Phosphor / HugeIcons / Radix / Tabler)?
- [ ] Motion isolated in client-leaf components with `'use client'` at top?
- [ ] No AI Tells (inter-as-default, purple-neon, three-equal-cards, Jane Doe, Acme, "Quietly in use at")?
- [ ] Core Web Vitals plausibly hit (LCP < 2.5s, INP < 200ms, CLS < 0.1)?
- [ ] One design system per project?

---

## Key References

### Install Commands
```bash
npm install @material/web
npm install @fluentui/react-components
npm install @carbon/react @carbon/styles
npm install @radix-ui/themes
npx shadcn@latest init && npx shadcn@latest add button
npm install @primer/react-brand
npm install govuk-frontend
npm install uswds
npm install bootstrap
```

### Canonical Documentation Links
- **Material Web:** https://material-web.dev
- **Fluent UI:** https://fluent2.microsoft.design/get-started/develop
- **Carbon:** https://carbondesignsystem.com/developing/react-tutorial/overview/
- **Shopify Polaris:** https://shopify.dev/docs/api/app-home/web-components
- **Atlassian:** https://atlassian.design/get-started/develop
- **Primer:** https://primer.style/
- **GOV.UK:** https://design-system.service.gov.uk/
- **USWDS:** https://designsystem.digital.gov/documentation/developers/
- **Radix Themes:** https://www.radix-ui.com/themes/docs/components/theme
- **shadcn/ui:** https://ui.shadcn.com/docs

---

**End of tasteskill documentation.** This skill is for **landing pages, portfolios, and redesigns only.** Not dashboards, data tables, or multi-step product UIs. Read the brief first. Declare your design read. Set the dials. Then ship.
