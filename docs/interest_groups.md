# 📚 SeniorConnect Interest Groups API Documentation

---

## 1. **Get All Interest Groups**

**GET** `/interest_groups/info/all`

**Description:**  
Returns a list of all interest groups with their id, name, description, and creator’s display name.

**Response:**

```json
{
    "groups": [
        {
            "id": "uuid-string",
            "name": "Group Name",
            "description": "Group description",
            "creator_name": "Alice Tan"
        }
        // ...
    ]
}
```

---

## 2. **Get One Interest Group Info**

**GET** `/interest_groups/info/<group_id>`

**Description:**  
Returns info for a single interest group.

**Response:**

```json
{
    "id": "uuid-string",
    "name": "Group Name",
    "description": "Group description",
    "creator_name": "Alice Tan"
}
```

**Error:**

```json
{ "error": "Group does not exist" }
```

---

## 3. **Join an Interest Group**

**POST** `/interest_groups/join/<group_id>`

**Description:**  
Adds the user as a member of the group.

**Input JSON:**

```json
{
    "clerk_user_id": "user_xxx"
}
```

**Response:**

```json
{ "message": "User successfully joined the group" }
```

**Errors:**

```json
{ "error": "User does not exist" }
{ "error": "Group does not exist" }
{ "error": "User already a member of this group" }
```

---

## 4. **Leave an Interest Group**

**POST** `/interest_groups/leave/<group_id>`

**Description:**  
Removes the user from the group.

**Input JSON:**

```json
{
    "clerk_user_id": "user_xxx"
}
```

**Response:**

```json
{ "message": "User successfully left the group" }
```

**Errors:**

```json
{ "error": "User does not exist" }
{ "error": "Group does not exist" }
{ "error": "User is not a member of this group" }
```

---

## 5. **Get All Members of a Group**

**GET** `/interest_groups/members/<group_id>`

**Description:**  
Returns a list of all members in the group.

**Response:**

```json
{
    "members": [
        {
            "clerk_user_id": "user_xxx",
            "display_name": "Alice Tan",
            "user_id": "uuid-string"
        }
        // ...
    ]
}
```

---

## 6. **Get Group Creator’s Clerk User ID**

**GET** `/interest_groups/creator/<group_id>`

**Description:**  
Returns the Clerk user ID of the group creator.

**Response:**

```json
{ "creator_clerk_user_id": "user_xxx" }
```

**Error:**

```json
{ "error": "Group does not exist" }
```

---

## 7. **Transfer Group Ownership**

**POST** `/interest_groups/transfer_owner/<group_id>`

**Description:**  
Transfers group ownership to another member.

**Input JSON:**

```json
{
    "clerk_user_id": "current_creator_clerk_id",
    "transfer_user_uuid": "uuid-of-new-creator"
}
```

**Response:**

```json
{ "message": "Ownership successfully transferred" }
```

**Errors:**

```json
{ "error": "User does not exist" }
{ "error": "Group does not exist" }
{ "error": "User is not the creator of this group" }
{ "error": "Transfer user is not a member of this group" }
```

---

## 8. **Edit Interest Group (Admin/Creator Only)**

**PATCH** `/interest_groups/edit/<group_id>`

**Description:**  
Allows an admin or the group creator to edit group details.

**Input JSON:**

```json
{
    "clerk_user_id": "user_xxx",
    "name": "New Group Name", // optional
    "description": "New description", // optional
    "image_url": "https://..." // optional
}
```

**Response:**

```json
{ "message": "Group updated successfully" }
```

**Errors:**

```json
{ "error": "User does not exist" }
{ "error": "Group does not exist" }
{ "error": "Not authorized" }
{ "error": "No valid fields to update" }
```

---

## 9. **Apply to Create an Interest Group**

**POST** `/interest_groups/apply`

**Description:**  
User submits an application to create a new interest group.

**Input JSON:**

```json
{
    "clerk_user_id": "user_xxx",
    "name": "Proposed Group Name",
    "description": "Proposed group description",
    "image_url": "https://..." // optional
}
```

**Response:**

```json
{
    "message": "Application submitted",
    "application_id": "uuid-string"
}
```

**Errors:**

```json
{ "error": "User does not exist" }
{ "error": "Missing required fields" }
```

---

## 10. **List All Interest Group Applications**

**GET** `/interest_groups/applications`

**Description:**  
Returns all interest group applications (for admins).

**Response:**

```json
{
    "applications": [
        {
            "id": "uuid-string",
            "applicant_name": "Alice Tan",
            "name": "Proposed Group Name",
            "description": "Proposed group description",
            "status": "pending",
            "created_at": "2024-06-01T12:00:00Z"
        }
        // ...
    ]
}
```

---

## 11. **Get One Interest Group Application**

**GET** `/interest_groups/application/<application_id>`

**Description:**  
Returns details of a single application.

**Response:**

```json
{
    "id": "uuid-string",
    "applicant_name": "Alice Tan",
    "name": "Proposed Group Name",
    "description": "Proposed group description",
    "status": "pending",
    "created_at": "2024-06-01T12:00:00Z",
    "image_url": "https://..."
}
```

**Error:**

```json
{ "error": "Application not found" }
```

---

## 12. **Approve an Interest Group Application**

**POST** `/interest_groups/application/<application_id>/approve`

**Description:**  
Admin approves an application, creating the group.

**Input JSON:**

```json
{
    "clerk_user_id": "admin_user_xxx"
}
```

**Response:**

```json
{
    "message": "Application approved and group created",
    "group_id": "uuid-string"
}
```

**Errors:**

```json
{ "error": "Admin user does not exist" }
{ "error": "Not authorized" }
{ "error": "Application not found" }
{ "error": "Application already processed" }
```

---

# **General Error Response**

All endpoints may return:

```json
{ "message": "An internal server error occurred" }
```

on unexpected errors.
