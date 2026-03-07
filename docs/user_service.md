# User Service API Documentation

## Overview
The User Service manages all user accounts, authentication, and profile data for NexaCommerce. It is a RESTful microservice running on port 8081.

Base URL: `https://api.nexacommerce.io/users`

---

## Authentication
All endpoints require a Bearer token in the Authorization header.

```
Authorization: Bearer <your_token>
```

Tokens are issued by the Auth Service and expire after 24 hours.

---

## Endpoints

### POST /register
Registers a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "strongpassword123",
  "full_name": "Jane Doe",
  "role": "customer"
}
```

**Response (201 Created):**
```json
{
  "user_id": "usr_a1b2c3",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "role": "customer",
  "created_at": "2024-11-01T10:00:00Z"
}
```

**Error Codes:**
- `400` — Missing required fields
- `409` — Email already registered
- `422` — Invalid email format or weak password

---

### POST /login
Authenticates a user and returns a token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "strongpassword123"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "expires_at": "2024-11-02T10:00:00Z",
  "user_id": "usr_a1b2c3"
}
```

**Error Codes:**
- `401` — Invalid credentials
- `403` — Account suspended
- `429` — Too many login attempts, rate limited for 15 minutes

---

### GET /profile/{user_id}
Returns the profile of a specific user.

**Path Parameter:**
- `user_id` — The unique user identifier (e.g. `usr_a1b2c3`)

**Response (200 OK):**
```json
{
  "user_id": "usr_a1b2c3",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "role": "customer",
  "address": "123 Main St, Tokyo, Japan",
  "loyalty_points": 840,
  "created_at": "2024-11-01T10:00:00Z"
}
```

**Error Codes:**
- `401` — Unauthorized
- `404` — User not found

---

### PATCH /profile/{user_id}
Updates user profile fields. Only the fields provided will be updated.

**Request Body (partial update):**
```json
{
  "full_name": "Jane Smith",
  "address": "456 New St, Osaka, Japan"
}
```

**Response (200 OK):**
```json
{
  "user_id": "usr_a1b2c3",
  "updated_fields": ["full_name", "address"],
  "updated_at": "2024-11-05T12:00:00Z"
}
```

**Error Codes:**
- `400` — Invalid field values
- `401` — Unauthorized
- `404` — User not found

---

### DELETE /profile/{user_id}
Soft-deletes a user account. Data is retained for 30 days before permanent deletion.

**Response (200 OK):**
```json
{
  "message": "User account scheduled for deletion",
  "deletion_date": "2024-12-05T12:00:00Z"
}
```

**Error Codes:**
- `401` — Unauthorized
- `403` — Cannot delete admin accounts via API
- `404` — User not found

---

## Rate Limits
| Endpoint       | Limit            |
|----------------|------------------|
| POST /login    | 5 requests/minute |
| POST /register | 10 requests/minute |
| GET /profile   | 100 requests/minute |
| PATCH /profile | 30 requests/minute |

---

## Notes
- Passwords must be at least 8 characters, include one uppercase letter and one number.
- The `role` field can be `customer`, `vendor`, or `admin`. Only internal services can assign the `admin` role.
- Loyalty points are read-only and managed by the Rewards Service.
