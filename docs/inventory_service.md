# Inventory Service API Documentation

## Overview
The Inventory Service manages product stock levels, warehouse locations, and availability across all Helios Platform fulfilment centres. It provides real-time stock checks and reservation capabilities.

Base URL: `https://api.helios.io/inventory`

---

## Key Concepts
- **Stock Level** — Total units available across all warehouses
- **Reserved Stock** — Units held for pending orders, not available for new purchases
- **Available Stock** — Stock Level minus Reserved Stock
- **Low Stock Threshold** — Configurable per product; triggers alerts when breached

---

## Endpoints

### GET /product/{product_id}
Returns current stock information for a product.

**Response (200 OK):**
```json
{
  "product_id": "prod_x1y2",
  "name": "Wireless Headphones",
  "stock_level": 240,
  "reserved_stock": 35,
  "available_stock": 205,
  "low_stock_threshold": 50,
  "warehouses": [
    { "warehouse_id": "wh_tokyo", "stock": 140 },
    { "warehouse_id": "wh_osaka", "stock": 100 }
  ],
  "last_updated": "2024-11-01T10:00:00Z"
}
```

**Error Codes:**
- `404` — Product not found

---

### POST /reserve
Temporarily reserves stock for an order. Reservation expires after 15 minutes if not confirmed.

**Request Body:**
```json
{
  "order_id": "ord_9f8e7d",
  "items": [
    { "product_id": "prod_x1y2", "quantity": 2 }
  ]
}
```

**Response (200 OK):**
```json
{
  "reservation_id": "res_r9s8t7",
  "status": "RESERVED",
  "expires_at": "2024-11-01T11:25:00Z",
  "items": [
    { "product_id": "prod_x1y2", "quantity": 2, "warehouse_id": "wh_tokyo" }
  ]
}
```

**Error Codes:**
- `409` — Insufficient stock available
- `422` — Quantity must be greater than zero

---

### POST /confirm/{reservation_id}
Confirms a reservation, permanently deducting stock.

**Response (200 OK):**
```json
{
  "reservation_id": "res_r9s8t7",
  "status": "CONFIRMED",
  "confirmed_at": "2024-11-01T11:15:00Z"
}
```

**Error Codes:**
- `404` — Reservation not found
- `410` — Reservation has expired

---

### POST /release/{reservation_id}
Releases a reservation, returning stock to available pool.

**Response (200 OK):**
```json
{
  "reservation_id": "res_r9s8t7",
  "status": "RELEASED",
  "stock_returned": 2
}
```

---

### PATCH /product/{product_id}/stock
Manually updates stock level (warehouse operations only).

**Request Body:**
```json
{
  "adjustment": 100,
  "reason": "New shipment received",
  "warehouse_id": "wh_tokyo"
}
```

**Response (200 OK):**
```json
{
  "product_id": "prod_x1y2",
  "previous_stock": 140,
  "new_stock": 240,
  "warehouse_id": "wh_tokyo"
}
```

**Error Codes:**
- `400` — Adjustment would result in negative stock
- `403` — Insufficient permissions

---

## Rate Limits
| Endpoint                    | Limit               |
|-----------------------------|---------------------|
| GET /product/{product_id}   | 200 requests/minute |
| POST /reserve               | 50 requests/minute  |
| POST /confirm               | 50 requests/minute  |
| POST /release               | 50 requests/minute  |
| PATCH /stock                | 20 requests/minute  |

---

## Notes
- Reservations automatically expire after 15 minutes if not confirmed
- Available stock can never go below zero — reservation requests exceeding available stock return a 409
- Stock adjustments require the `warehouse_operator` role
- Low stock alerts are sent via the Notification Service when available stock drops below the threshold
