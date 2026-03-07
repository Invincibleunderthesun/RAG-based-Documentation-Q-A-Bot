# Recommendations Service API Documentation

## Overview
The Recommendations Service powers personalised product suggestions across NexaCommerce using real-time ML models trained on user behaviour, purchase history, and product metadata. It exposes a low-latency gRPC API internally and a REST API externally.

Base URL: `https://api.nexacommerce.io/recommendations`

---

## Authentication
All endpoints require a Bearer token in the Authorization header.

```
Authorization: Bearer <your_token>
```

---

## Recommendation Types
| Type              | Description                                              |
|-------------------|----------------------------------------------------------|
| `PERSONALISED`    | Based on user's full purchase and browsing history       |
| `SIMILAR_ITEMS`   | Products similar to a given product                      |
| `TRENDING`        | Most popular products in the last 24 hours               |
| `FREQUENTLY_BOUGHT` | Items commonly bought together with a given product    |

---

## Endpoints

### GET /for-user/{user_id}
Returns personalised product recommendations for a user.

**Query Parameters:**
- `limit` — Number of recommendations (default: 10, max: 50)
- `category` — Filter by product category (optional)
- `exclude_purchased` — Boolean, exclude previously purchased items (default: true)

**Response (200 OK):**
```json
{
  "user_id": "usr_a1b2c3",
  "type": "PERSONALISED",
  "recommendations": [
    {
      "product_id": "prod_r9s8",
      "name": "Noise Cancelling Earbuds",
      "score": 0.97,
      "reason": "Based on your recent purchase of Wireless Headphones"
    },
    {
      "product_id": "prod_t7u6",
      "name": "Phone Stand",
      "score": 0.85,
      "reason": "Trending in Electronics"
    }
  ],
  "generated_at": "2024-11-01T12:00:00Z"
}
```

**Error Codes:**
- `404` — User not found or no history available, falls back to TRENDING
- `429` — Rate limit exceeded

---

### GET /similar/{product_id}
Returns products similar to the given product.

**Query Parameters:**
- `limit` — Number of results (default: 10, max: 30)

**Response (200 OK):**
```json
{
  "product_id": "prod_x1y2",
  "type": "SIMILAR_ITEMS",
  "recommendations": [
    { "product_id": "prod_r9s8", "name": "Noise Cancelling Earbuds", "score": 0.94 },
    { "product_id": "prod_v5w4", "name": "Bluetooth Speaker", "score": 0.88 }
  ]
}
```

**Error Codes:**
- `404` — Product not found

---

### GET /trending
Returns the top trending products across the platform.

**Query Parameters:**
- `limit` — Number of results (default: 20, max: 100)
- `category` — Filter by category (optional)
- `window` — Time window: `1h`, `6h`, `24h` (default: `24h`)

**Response (200 OK):**
```json
{
  "type": "TRENDING",
  "window": "24h",
  "recommendations": [
    { "product_id": "prod_m3n2", "name": "Smart Watch", "trend_score": 9.8, "orders_count": 1240 },
    { "product_id": "prod_k1l0", "name": "Laptop Stand", "trend_score": 9.1, "orders_count": 980 }
  ],
  "generated_at": "2024-11-01T12:00:00Z"
}
```

---

### POST /feedback
Submit user feedback on a recommendation to improve the model.

**Request Body:**
```json
{
  "user_id": "usr_a1b2c3",
  "product_id": "prod_r9s8",
  "action": "clicked",
  "context": "homepage_recommendations"
}
```

**Accepted `action` values:** `clicked`, `purchased`, `dismissed`, `saved`

**Response (202 Accepted):**
```json
{
  "message": "Feedback recorded",
  "model_update": "scheduled"
}
```

---

## Rate Limits
| Endpoint                    | Limit               |
|-----------------------------|---------------------|
| GET /for-user/{user_id}     | 60 requests/minute  |
| GET /similar/{product_id}   | 120 requests/minute |
| GET /trending               | 200 requests/minute |
| POST /feedback              | 300 requests/minute |

---

## Model Details
- Models are retrained every 6 hours using data from BigQuery
- New users with fewer than 3 purchases automatically fall back to TRENDING recommendations
- The `score` field represents confidence (0.0 to 1.0) — above 0.8 is considered high confidence
- Recommendations are cached for 5 minutes per user to reduce latency

---

## Notes
- For high-throughput internal use, prefer the gRPC endpoint at `grpc.nexacommerce.io:50051`
- The REST API adds ~15ms overhead compared to gRPC due to JSON serialisation
- Feedback data is used only for model training, never shared externally
