# Jarv-ish website decisions

Approved by product owner: 2026-07-18

## Architecture
- Build the full multi-page website, not only the existing one-page mockup.

## Primary conversion
- Primary conversion is the paid Jarv-ish Personal plan.
- Checkout must remain a documented placeholder until a hosting/payment platform is selected and configured.

## Product truth
- Current displayed pricing and capability statuses are approved for the next build stage.

## Hosting
- Decision pending between Netlify and Shopify.
- Keep static pages and content host-agnostic until the platform is selected.

## Lead storage
- Form submissions may be saved internally.
- Never write private lead data into the public static site directory or commit it to source control.
- A browser-only static site cannot safely append to a private local file.
- For local/private server operation, the proposed storage format is append-only JSONL or CSV outside the public web root.
- On Netlify, use Netlify Forms or durable external storage because function filesystems are ephemeral.
- On Shopify, use approved customer/contact records or a private app/backend rather than a public file.
