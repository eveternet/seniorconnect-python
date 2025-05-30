# 📚 SeniorConnect Auth API Documentation

---

## 1. **User Onboarding / Authentication**

**POST** `/user/auth/`

**Description:**  
Onboards a new user or checks if a user already exists.  
If the user does not exist, creates a new user in the database.

**Input JSON:**

```json
{
    "clerk_user_id": "user_xxx",
    "name": "Evelyn Cheong",
    "phone": "+6581234567"
}
```

**Response (user already exists):**

```json
{
    "message": "User already exists"
}
```

**Status:** `200 OK`

**Response (new user created):**

```json
{
    "message": "User successfully onboarded",
    "user_id": "uuid-string",
    "clerk_user_id": "user_xxx"
}
```

**Status:** `201 Created`

**Errors:**

```json
{ "error": "Invalid JSON", "details": "..." }
{ "error": "No data provided" }
{ "error": "Missing required fields" }
{ "error": "Invalid data type" }
{ "message": "An internal server error occurred" }
```

---

## 2. **Check If User Is Admin**

**POST** `/user/auth/isAdmin`

**Description:**  
Checks if the user is an admin.

**Input JSON:**

```json
{
    "clerk_user_id": "user_xxx"
}
```

**Response (user is admin):**

```json
{ "is_admin": true }
```

**Response (user is not admin or does not exist):**

```json
{ "is_admin": false }
```

**Errors:**

```json
{ "error": "Invalid JSON", "details": "..." }
{ "error": "No data provided" }
{ "error": "Missing required fields" }
{ "error": "Invalid data type" }
{ "message": "An internal server error occurred" }
```

---

# **General Error Response**

All endpoints may return:

```json
{ "message": "An internal server error occurred" }
```

on unexpected errors.
