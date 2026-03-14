# Notification Service API Documentation

## Overview
The Notification Service manages all outbound communications for the Helios Platform — emails, push notifications, and SMS. It supports templated and custom messages with delivery tracking.

Base URL: `https://api.helios.io/notifications`

---

## Notification Channels
| Channel | Delivery Time  | Max Message Size |
|---------|----------------|------------------|
| Email   | 1–2 minutes    | 10 MB            |
| Push    | Instant        | 4 KB             |
| SMS     | 5–30 seconds   | 160 characters   |

---

## Endpoints

### POST /send
Sends a notification to a user via one or more channels.

**Request Body:**
```json
{
  "user_id": "usr_a1b2c3",
  "channels": ["email", "push"],
  "template_id": "order_confirmed",
  "data": {
    "order_id": "ord_9f8e7d",
    "total": "$45.00"
  }
}
```

**Response (202 Accepted):**
```json
{
  "notification_id": "notif_n1m2l3",
  "status": "QUEUED",
  "channels": ["email", "push"],
  "queued_at": "2024-11-01T11:10:00Z"
}
```

**Error Codes:**
- `400` — Missing required fields
- `404` — User not found or template not found
- `422` — Invalid channel specified
- `429` — Rate limit exceeded

---

### GET /{notification_id}
Returns the delivery status of a notification.

**Response (200 OK):**
```json
{
  "notification_id": "notif_n1m2l3",
  "user_id": "usr_a1b2c3",
  "channels": {
    "email": "DELIVERED",
    "push": "FAILED"
  },
  "sent_at": "2024-11-01T11:10:05Z",
  "delivered_at": "2024-11-01T11:11:30Z"
}
```

**Delivery Statuses:** `QUEUED`, `SENT`, `DELIVERED`, `FAILED`, `BOUNCED`

---

### GET /user/{user_id}/history
Returns notification history for a user.

**Query Parameters:**
- `channel` — Filter by `email`, `push`, or `sms`
- `status` — Filter by delivery status
- `limit` (default: 20, max: 100)

---

### POST /templates
Creates a new notification template.

**Request Body:**
```json
{
  "template_id": "welcome_email",
  "channel": "email",
  "subject": "Welcome to Helios, {{name}}!",
  "body": "Hi {{name}}, your account is ready. Start exploring at {{url}}."
}
```

**Response (201 Created):**
```json
{
  "template_id": "welcome_email",
  "channel": "email",
  "created_at": "2024-11-01T09:00:00Z"
}
```

**Error Codes:**
- `409` — Template ID already exists
- `422` — Invalid template syntax

---

### DELETE /templates/{template_id}
Deletes a notification template.

**Response (200 OK):**
```json
{ "message": "Template deleted successfully" }
```

**Error Codes:**
- `403` — Cannot delete system default templates
- `404` — Template not found

---

## Rate Limits
| Endpoint           | Limit                |
|--------------------|----------------------|
| POST /send         | 100 requests/minute  |
| GET /history       | 60 requests/minute   |
| POST /templates    | 20 requests/minute   |

---

## Built-in Templates
| Template ID          | Description                    |
|----------------------|--------------------------------|
| `order_confirmed`    | Sent when order is confirmed   |
| `order_shipped`      | Sent when order is shipped     |
| `password_reset`     | Password reset link            |
| `welcome_email`      | New user welcome message       |
| `payment_failed`     | Payment failure alert          |

---

## Notes
- SMS messages over 160 characters are split into multiple messages and billed separately
- Push notifications require the user to have an active device token registered
- System default templates (e.g. `password_reset`) cannot be deleted or modified
- Failed notifications are retried up to 3 times with exponential backoff
