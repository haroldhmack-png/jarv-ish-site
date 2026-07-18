# Private lead endpoint reference

This directory is documentation/reference code, not browser-facing application code and not a production internet server.

## Local/private operation

Keep the lead file outside the public website directory:

```powershell
$env:JARVISH_LEAD_FILE = 'C:\private\jarv-ish\leads.jsonl'
$env:JARVISH_ALLOWED_ORIGIN = 'http://127.0.0.1:8080'
python private-lead-server.py
```

Then set this in the public site's `content-config.js` for the local environment:

```js
leadEndpoint: 'http://127.0.0.1:8787/api/leads'
```

The server:

- accepts only `POST /api/leads`
- enforces a configured exact browser origin
- rejects bodies over 32 KB
- allowlists fields and strips control characters
- requires name, a basic valid email, and explicit consent
- appends one sanitized JSON record per line
- does not log submitted field values

## Production path

Do not expose this stdlib reference server directly to the internet. A production implementation also needs TLS, authenticated operator access, rate limiting, anti-spam controls, monitoring, backups, retention/deletion procedures, and a reviewed privacy policy.

- **Netlify:** use Netlify Forms or a function writing to durable private storage. Never rely on the function filesystem; it is ephemeral.
- **Shopify:** create approved customer/contact records or use a private app/backend with the minimum required scopes. Never write leads into public theme assets.

Never commit lead files, secrets, API tokens, or endpoint credentials.
