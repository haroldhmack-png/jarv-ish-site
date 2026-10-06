"""
Shopify webhook handler for Jarvish subscription payments.
Deploy to app.jarv-ish.com (187.77.192.151) behind a reverse proxy (nginx/caddy) with TLS.

Environment:
  SHOPIFY_API_SECRET — shared secret from Shopify Partner dashboard (for HMAC verification)
  SHOPIFY_WEBHOOK_PORT — port to listen on (default 8788)
  JARVISH_PAYMENT_LOG — file to log payment events (default /var/log/jarvish/payments.jsonl)

Endpoints:
  POST /api/webhooks/shopify/order-paid       — order paid
  POST /api/webhooks/shopify/order-created    — order created (backup)

Shopify webhook signature verification:
  Each request includes X-Shopify-Hmac-SHA256 header.
  Compute HMAC-SHA256 of the raw request body using the shared secret; compare.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from datetime import datetime, timezone
import json, os, hmac, hashlib, re

HOST = os.getenv('SHOPIFY_WEBHOOK_HOST', '127.0.0.1')
PORT = int(os.getenv('SHOPIFY_WEBHOOK_PORT', '8788'))
PAYMENT_LOG = os.getenv('JARVISH_PAYMENT_LOG', '/var/log/jarvish/payments.jsonl')
API_SECRET = os.getenv('SHOPIFY_API_SECRET', '')

# — Subscription plan mapping —
PLAN_PRICES = {
    49.00: {"plan": "basic", "name": "Jarvish Basic Plan", "monthly": 49},
    99.00: {"plan": "premium", "name": "Jarvish Premium Plan", "monthly": 99},
}

def verify_hmac(body: bytes, hmac_header: str) -> bool:
    """Verify Shopify HMAC signature on the raw request body."""
    if not API_SECRET:
        print("[WARN] SHOPIFY_API_SECRET not set — skipping HMAC verification")
        return True
    computed = hmac.new(
        API_SECRET.encode(), body, hashlib.sha256
    ).digest()
    expected = computed.hex()
    return hmac.compare_digest(expected, hmac_header)

def extract_payment_payload(shopify_body: dict) -> dict | None:
    """Extract the fields Jarvish cares about from an orders/paid or orders/create payload."""
    try:
        order = shopify_body
        line_items = order.get('line_items', [])
        customer = order.get('customer', {})
        shipping = order.get('shipping_address', {}) or {}

        items = []
        for li in line_items:
            items.append({
                'product_id': li.get('product_id'),
                'variant_id': li.get('variant_id'),
                'title': li.get('title'),
                'price': float(li.get('price', 0)),
                'quantity': li.get('quantity', 1),
                'selling_plan_id': li.get('selling_plan_id'),
            })

        total = float(order.get('total_price', 0))
        plan_info = None
        for price, info in PLAN_PRICES.items():
            if abs(total - price) < 0.01:
                plan_info = info
                break

        return {
            'order_id': order.get('id'),
            'order_number': order.get('order_number'),
            'email': customer.get('email', ''),
            'customer_id': customer.get('id'),
            'first_name': customer.get('first_name', ''),
            'last_name': customer.get('last_name', ''),
            'total_price': total,
            'currency': order.get('currency', 'USD'),
            'financial_status': order.get('financial_status', ''),
            'plan': plan_info,
            'items': items,
            'created_at': order.get('created_at', ''),
            'processed_at': order.get('processed_at', ''),
        }
    except Exception as exc:
        print(f"[ERROR] Failed to extract payment payload: {exc}")
        return None

def log_payment(record: dict):
    """Append one JSONL record to the payment log."""
    target = Path(PAYMENT_LOG).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    record['jarvish_received_at'] = datetime.now(timezone.utc).isoformat()
    with target.open('a', encoding='utf-8', newline='\n') as fh:
        fh.write(json.dumps(record, ensure_ascii=False, separators=(',', ':')) + '\n')

class WebhookHandler(BaseHTTPRequestHandler):
    def _ok(self, body: dict | None = None):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body or {"status": "ok"}).encode())

    def _fail(self, code: int, msg: str):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "error", "message": msg}).encode())

    def do_POST(self):
        path = self.path.rstrip('/')

        if path not in (
            '/api/webhooks/shopify/order-paid',
            '/api/webhooks/shopify/order-created',
        ):
            self._fail(404, 'not found')
            return

        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length <= 0 or length > 1_048_576:  # 1MB max
                self._fail(400, 'invalid body size')
                return

            raw_body = self.rfile.read(length)

            # HMAC verification
            hmac_header = self.headers.get('X-Shopify-Hmac-SHA256', '')
            if not verify_hmac(raw_body, hmac_header):
                self._fail(401, 'invalid signature')
                return

            shopify_body = json.loads(raw_body)
            webhook_topic = self.headers.get('X-Shopify-Topic', 'unknown')
            shopify_domain = self.headers.get('X-Shopify-Shop-Domain', 'unknown')

            print(f"[WEBHOOK] {webhook_topic} from {shopify_domain}")

            if webhook_topic in ('orders/paid', 'orders/create'):
                payload = extract_payment_payload(shopify_body)
                if payload:
                    payload['webhook_topic'] = webhook_topic
                    payload['shopify_domain'] = shopify_domain
                    log_payment(payload)

                    plan_name = payload['plan']['name'] if payload['plan'] else 'unknown plan'
                    print(f"[PAYMENT] Order #{payload['order_number']} — {plan_name} — ${payload['total_price']} — {payload['email']}")

                    self._ok({
                        "status": "ok",
                        "order_number": payload['order_number'],
                        "plan": payload['plan']['plan'] if payload['plan'] else None,
                    })
                else:
                    self._ok({"status": "ok", "note": "payload extraction returned None"})
            else:
                self._ok({"status": "ok", "note": f"unhandled topic: {webhook_topic}"})

        except json.JSONDecodeError:
            self._fail(400, 'invalid json body')
        except Exception as exc:
            print(f"[ERROR] Webhook processing failed: {exc}")
            self._fail(500, 'internal error')

    def do_GET(self):
        """Health check endpoint."""
        if self.path.rstrip('/') == '/api/webhooks/shopify/health':
            self._ok({"status": "healthy", "service": "jarvish-shopify-webhook"})
            return
        self._fail(404, 'not found')

    def log_message(self, format, *args):
        print(f'{self.address_string()} - {format % args}')

if __name__ == '__main__':
    if not API_SECRET:
        print("WARNING: SHOPIFY_API_SECRET is not set. HMAC verification is DISABLED.")
        print("         Set it to the shared secret from Shopify Partner Dashboard > Webhooks.")
    print(f'Jarvish Shopify Webhook Handler: http://{HOST}:{PORT}')
    print(f'Payment log: {Path(PAYMENT_LOG).expanduser().resolve()}')
    print(f'Endpoints:')
    print(f'  POST /api/webhooks/shopify/order-paid')
    print(f'  POST /api/webhooks/shopify/order-created')
    print(f'  GET  /api/webhooks/shopify/health')
    ThreadingHTTPServer((HOST, PORT), WebhookHandler).serve_forever()