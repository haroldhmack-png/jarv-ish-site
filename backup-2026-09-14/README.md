# Jarv-ish static multi-page website

A polished, host-agnostic static website based on the July 2026 Jarv-ish brand guide and approved product decisions in `PROJECT-DECISIONS.md`.

## Run locally

No build, framework, package installation, or environment variables are required for the public site.

```powershell
cd C:\Users\bbadmin\.openclaw\workspace\jarv-ish-site
python -m http.server 8080
```

Open `http://127.0.0.1:8080/`. Relative links also work when HTML files are opened directly.

## Public page inventory

- `index.html` — Home
- `personal.html` — Jarv-ish Personal
- `office.html` — Jarv-ish Office
- `capabilities.html` — filterable status inventory
- `integrations.html` — agent/framework/tool compatibility
- `pricing.html` — Personal and Office pricing
- `roadmap.html` — phased product roadmap
- `about.html` — mission, name, personality, eClawmerce relationship
- `contact.html` — early access, Personal, Office, integration, and partner inquiries
- `privacy.html` — pre-launch privacy notice
- `terms.html` — pre-launch terms
- `checkout.html` — paid Personal plan-selection handoff; no payment collection

## Shared system

- `styles.css` — design tokens, shared responsive components, page layouts, focus and reduced-motion behavior
- `script.js` — navigation, filters, analytics events, pricing switch, paid-plan handoff, and configurable lead adapter
- `content-config.js` — central prices, plan summaries, capability statuses, base URL, and lead endpoint
- `assets/logo-mark.svg` — current concept vector mark / favicon placeholder
- `assets/brand-concept.png` — supplied raster concept extracted from the DOCX; brand reference only
- `sitemap.xml` and `robots.txt` — production placeholders using `https://jarv-ish.com`

### Final logo replacement path

Final vector assets are intentionally non-blocking for preview. Keep the current placeholders until approved artwork arrives, then replace/add:

- `assets/logo-mark.svg` — final icon-only mark; replacing this file updates the header icon, footer icon, favicon, and in-page product diagrams without markup changes.
- `assets/logo-core.svg` — final icon + Jarv-ish horizontal wordmark for production navigation/signage if the team chooses to replace the current HTML wordmark.
- `assets/logo-brand.svg` — icon + wordmark + approved slogan.
- `assets/logo-corporate.svg` — icon + wordmark + slogan + eClawmerce subsidiary line.
- `assets/favicon.ico`, `favicon-32.png`, `apple-touch-icon.png`, and final app-icon exports.

Do not treat `assets/brand-concept.png` as a production logo master.
- `.gitignore` — excludes leads, secrets, private data, and QA output

## Primary paid conversion

The primary journey is a paid Jarv-ish Personal plan:

- **Jarv-ish Connect — $49/month:** one seat, bring your own compatible agent.
- **Jarv-ish Complete — $99/month:** one seat, managed Jarv-ish agent included.

`checkout.html` provides a polished plan-selection handoff. It explicitly does **not** collect card, bank, or payment credentials and does not claim to activate a subscription. Secure checkout will be connected only after Netlify versus Shopify is decided.

Office remains a secondary inquiry journey.

## Lead adapter

Set the private endpoint in `content-config.js`:

```js
leadEndpoint: 'https://approved-private-endpoint.example/api/leads'
```

When blank (the default), forms validate locally and explicitly report that nothing was transmitted or persisted. When configured, `script.js` sends a JSON POST and displays success/error states. Do not put API secrets in this browser file; authentication and anti-abuse controls belong on the server.

Analytics hooks use `window.dataLayer` and `jarvish:analytics` DOM events without loading a vendor. Events include CTA clicks, plan selection, checkout placeholder use, filters, successful lead intent, and submission failures.

## Private/local lead reference

`docs/server-reference/private-lead-server.py` is a stdlib-only reference for local/private operation. It appends sanitized JSONL to a path supplied by `JARVISH_LEAD_FILE`, which must remain outside the public web root. It is not a production internet server.

See `docs/server-reference/README.md` for usage and security constraints.

Never commit actual lead data. `.gitignore` excludes common lead and secret paths.

## Hosting paths

### Netlify

- Deploy the static public files as-is.
- Use Netlify Forms, or a function/API writing to a durable private store.
- Never rely on Netlify function filesystem writes; function filesystems are ephemeral.
- Connect an approved hosted checkout/payment provider after the decision is made.
- Configure redirects/clean URLs only after confirming they preserve the relative-link behavior.

### Shopify

- Port shared HTML/CSS/JS into theme sections/templates while retaining content/status truth.
- Use approved customer/contact records or a private app/backend for lead intake.
- Use Shopify's approved checkout/product architecture for paid plans after product/legal setup.
- Never store private leads, tokens, or credentials in theme assets/metafields exposed to the storefront.

## Editing

- Prices, plan summaries, statuses, base URL, and endpoint: `content-config.js`
- Shared appearance/layout: `styles.css`
- Shared behavior/form adapter: `script.js`
- Page-specific copy: each `.html` file
- Update `sitemap.xml` and canonical/OG URLs after the final domain and URL policy are confirmed.

## Launch gaps

- [ ] Choose Netlify or Shopify and implement approved secure checkout. No payment is active now.
- [ ] Select the production private lead path, add anti-spam/rate limiting, monitoring, retention/deletion, and operator access controls.
- [ ] Legal review of name, slogan, JARVIS references, pricing terms, Privacy, Terms, recording consent, and data practices.
- [ ] Replace concept mark with approved production vector lockups, favicon set, app icons, and social image.
- [ ] Confirm exact production compatibility for every named framework and integration.
- [ ] Add final product screenshots/prototypes.
- [ ] Define included usage, overage behavior, billing/cancellation, taxes, support, and managed-agent infrastructure.
- [ ] Select analytics/consent behavior and connect approved tracking.
- [ ] Self-host licensed fonts or approve the Google Fonts dependency.
- [ ] Add final domain canonical URLs and validate the sitemap/robots policy.
- [ ] Run formal accessibility, security, privacy, payment, and cross-browser QA after host integrations.

## Accessibility

The static implementation includes semantic landmarks, a skip link, keyboard focus, labeled forms, native validation, live status messages, keyboard-operable controls, mobile navigation, responsive layouts, contrast-conscious tokens, and reduced-motion support. A production audit remains required after payment and form integrations.
