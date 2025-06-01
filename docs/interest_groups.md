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
**Note:** This endpoint is now superseded by the expanded `PATCH /interest_groups/edit/<group_id>` endpoint, which handles ownership transfer along with other editing capabilities.

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
Allows an admin or the group creator to edit group details, remove members, or transfer ownership. This is a versatile endpoint for administrative management of interest groups.

**Input JSON:**  
The request body must include `clerk_user_id` for authorization. Other fields are optional and can be combined.

```json
{
    "clerk_user_id": "user_xxx", // Required: Clerk ID of the acting user (admin or creator)
    "name": "New Group Name", // Optional: New name for the group
    "description": "New description", // Optional: New description for the group
    "image_url": "https://example.com/new_image.jpg", // Optional: New image URL for the group
    "remove_member_id": "uuid-of-member-to-remove", // Optional: UUID of the user to remove from the group
    "new_owner_id": "uuid-of-new-owner" // Optional: UUID of the user to transfer ownership to
}
```

**Response:**

```json
{ "message": "Group updated successfully" }
```

**Errors:**

```json
{ "error": "User does not exist" }                             // Acting user does not exist
{ "error": "No user id provided / Invalid user id type" }     // Missing/invalid clerk_user_id
{ "error": "Group does not exist" }                           // Group not found
{ "error": "Not authorized to edit this group" }              // Acting user is neither admin nor creator
{ "error": "No valid fields or actions to update" }           // No recognized parameters in the request body
{ "error": "Invalid remove_member_id format" }                // remove_member_id is not a valid UUID string
{ "error": "Cannot remove the group creator from the group" } // Attempt to remove the group creator
{ "error": "User is not a member of this group" }             // Attempt to remove a non-member
{ "error": "Invalid new_owner_id format" }                    // new_owner_id is not a valid UUID string
{ "error": "New owner user does not exist" }                  // new_owner_id does not correspond to an existing user
{ "error": "Only the current group creator or a site admin can transfer ownership" } // Unauthorized ownership transfer
{ "error": "Cannot transfer ownership to the current owner" } // Attempt to transfer ownership to self
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

## 10. **List All Interest Group Applications (Pending/New)**

**GET** `/interest_groups/applications`

**Description:**  
Returns a list of interest group applications that are still awaiting action (e.g., `pending`, `new` status). This endpoint is primarily for admins.

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
