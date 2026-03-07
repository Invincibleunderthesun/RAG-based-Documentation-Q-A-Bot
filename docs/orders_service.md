# Orders Service API Documentation

## Overview
The Orders Service handles the full order lifecycle for NexaCommerce — from cart checkout to delivery confirmation. It communicates internally with the Inventory Service, Payment Service, and Notification Service.

Base URL: `https://api.nexacommerce.io/orders`

---

## Authentication
All endpoints require a Bearer token in the Authorization header.

```
Authorization: Bearer <your_token>
```

---

## Order Lifecycle
Orders move through the following states:

```
PENDING → CONFIRMED → PROCESSING → SHIPPED → DELIVERED
                                          ↘ CANCELLED
```

- **PENDING** — Order created, awaiting payment confirmation
- **CONFIRMED** — Payment successful, order confirmed
- **PROCESSING** — Warehouse is preparing the order
- **SHIPPED** — Order handed to delivery partner
- **DELIVERED** — Customer confirmed delivery
- **CANCELLED** — Order cancelled (only possible before SHIPPED)

---

## Endpoints

### POST /create
Creates a new order from the user's cart.

**Request Body:**
```json
{
  "user_id": "usr_a1b2c3",
  "items": [
    { "product_id": "prod_x1y2", "quantity": 2 },
    { "product_id": "prod_z3w4", "quantity": 1 }
  ],
  "shipping_address": "123 Main St, Tokyo, Japan",
  "payment_method": "credit_card"
}
```

**Response (201 Created):**
```json
{
  "order_id": "ord_9f8e7d",
  "status": "PENDING",
  "total_amount": 4500,
  "currency": "JPY",
  "estimated_delivery": "2024-11-08T00:00:00Z",
  "created_at": "2024-11-01T11:00:00Z"
}
```

**Error Codes:**
- `400` — Missing required fields or empty items list
- `404` — One or more product IDs not found
- `409` — Insufficient stock for one or more items
- `422` — Invalid shipping address format

---

### GET /{order_id}
Fetches full details of a specific order.

**Response (200 OK):**
```json
{
  "order_id": "ord_9f8e7d",
  "user_id": "usr_a1b2c3",
  "status": "SHIPPED",
  "items": [
    { "product_id": "prod_x1y2", "name": "Wireless Headphones", "quantity": 2, "unit_price": 1800 },
    { "product_id": "prod_z3w4", "name": "USB-C Cable", "quantity": 1, "unit_price": 900 }
  ],
  "total_amount": 4500,
  "currency": "JPY",
  "tracking_number": "TRK123456JP",
  "estimated_delivery": "2024-11-08T00:00:00Z"
}
```

**Error Codes:**
- `401` — Unauthorized
- `403` — Order belongs to a different user
- `404` — Order not found

---

### GET /user/{user_id}
Returns all orders for a specific user, paginated.

**Query Parameters:**
- `page` (default: 1)
- `limit` (default: 20, max: 100)
- `status` — Filter by order status (e.g. `SHIPPED`)

**Response (200 OK):**
```json
{
  "total": 45,
  "page": 1,
  "limit": 20,
  "orders": [ { "order_id": "ord_9f8e7d", "status": "SHIPPED", "total_amount": 4500 } ]
}
```

---

### POST /{order_id}/cancel
Cancels an order. Only possible when status is PENDING or CONFIRMED.

**Response (200 OK):**
```json
{
  "order_id": "ord_9f8e7d",
  "status": "CANCELLED",
  "refund_initiated": true,
  "refund_eta": "3-5 business days"
}
```

**Error Codes:**
- `400` — Order cannot be cancelled at current status
- `404` — Order not found

---

## Rate Limits
| Endpoint              | Limit              |
|-----------------------|--------------------|
| POST /create          | 20 requests/minute |
| GET /{order_id}       | 100 requests/minute |
| GET /user/{user_id}   | 60 requests/minute |
| POST /cancel          | 10 requests/minute |

---

## Notes
- Orders in PROCESSING, SHIPPED, or DELIVERED status cannot be cancelled via API. Contact support.
- Refunds are processed automatically when an order is cancelled.
- The `total_amount` is calculated server-side. Client-provided totals are ignored.
- Currency is always stored in JPY internally and converted at display time.
