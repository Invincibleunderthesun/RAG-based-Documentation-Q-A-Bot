# Payment Service API Documentation

## Overview
The Payment Service handles all payment processing for Helios Platform. It supports multiple payment methods and currencies, integrating with Stripe and PayPal as backend processors.

Base URL: `https://api.helios.io/payments`

---

## Supported Payment Methods
| Method         | Currencies Supported     | Processing Time |
|----------------|--------------------------|-----------------|
| Credit Card    | USD, EUR, GBP, JPY       | Instant         |
| PayPal         | USD, EUR, GBP            | Instant         |
| Bank Transfer  | USD, EUR                 | 2–3 business days |
| Crypto (USDC)  | USD equivalent           | ~10 minutes     |

---

## Endpoints

### POST /charge
Initiates a payment charge.

**Request Body:**
```json
{
  "user_id": "usr_a1b2c3",
  "amount": 4500,
  "currency": "USD",
  "payment_method": "credit_card",
  "card_token": "tok_visa_xxxx",
  "description": "Order #ord_9f8e7d"
}
```

**Response (200 OK):**
```json
{
  "payment_id": "pay_x9y8z7",
  "status": "SUCCESS",
  "amount": 4500,
  "currency": "USD",
  "processor": "stripe",
  "processed_at": "2024-11-01T11:05:00Z"
}
```

**Error Codes:**
- `400` — Invalid payment details
- `402` — Insufficient funds
- `403` — Card declined by issuer
- `422` — Unsupported currency for payment method
- `429` — Rate limit exceeded

---

### GET /{payment_id}
Fetches details of a specific payment.

**Response (200 OK):**
```json
{
  "payment_id": "pay_x9y8z7",
  "user_id": "usr_a1b2c3",
  "status": "SUCCESS",
  "amount": 4500,
  "currency": "USD",
  "payment_method": "credit_card",
  "processor": "stripe",
  "refundable": true,
  "processed_at": "2024-11-01T11:05:00Z"
}
```

**Error Codes:**
- `401` — Unauthorized
- `404` — Payment not found

---

### POST /{payment_id}/refund
Initiates a full or partial refund.

**Request Body:**
```json
{
  "amount": 2000,
  "reason": "Customer request"
}
```

**Response (200 OK):**
```json
{
  "refund_id": "ref_r1s2t3",
  "payment_id": "pay_x9y8z7",
  "status": "REFUND_INITIATED",
  "amount": 2000,
  "eta": "3–5 business days"
}
```

**Error Codes:**
- `400` — Refund amount exceeds original payment
- `403` — Payment not eligible for refund
- `404` — Payment not found
- `409` — Refund already processed

---

### GET /user/{user_id}/history
Returns full payment history for a user.

**Query Parameters:**
- `page` (default: 1)
- `limit` (default: 20, max: 50)
- `status` — Filter by `SUCCESS`, `FAILED`, `REFUNDED`
- `from_date` — ISO8601 date
- `to_date` — ISO8601 date

**Response (200 OK):**
```json
{
  "total": 12,
  "page": 1,
  "payments": [
    { "payment_id": "pay_x9y8z7", "amount": 4500, "status": "SUCCESS" }
  ]
}
```

---

## Rate Limits
| Endpoint              | Limit               |
|-----------------------|---------------------|
| POST /charge          | 10 requests/minute  |
| GET /{payment_id}     | 100 requests/minute |
| POST /refund          | 5 requests/minute   |
| GET /history          | 60 requests/minute  |

---

## Notes
- All amounts are in the smallest currency unit (e.g. cents for USD)
- Crypto payments are non-refundable once confirmed on-chain
- Bank transfer payments cannot be partially refunded
- Failed payments are automatically retried once after 60 seconds
