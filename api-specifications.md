---

# 🎟️ Support Ticket API – Specification

## 🔧 Global Configuration

```yaml
MAX_QUEUES: integer (configured at app startup)
MAX_TICKETS_PER_QUEUE: integer (optional enhancement)
STANDARD_EFFORT_BLOCKS: [1, 2, 5, 10, 20, 50, 100]
METRIC: "POINTS"
```

---

# 📦 Data Models

## Queue

```json
{
  "id": "bigint (default)",
  "name": "string (e.g. Billing, IT-Support)",
  "capacity": 10,
  "current_ticket_count": 5,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## Ticket

```json
{
  "id": "bigint (default)",
  "title": "Login Error",
  "complexity": 40,
  "queue_id": "bigint",
  "quantity": 5,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

# 1️⃣ Add Queue

### POST `/queues`

Creates a new queue.

### Request

```json
{
  "name": "Billing",
  "capacity": 10
}
```

### Validation Rules

* Cannot exceed `MAX_QUEUES`
* `name` must be unique
* capacity > 0

### Response (201)

```json
{
  "id": "uuid",
  "name": "Billing",
  "capacity": 10,
  "current_ticket_count": 0
}
```

### Errors

* `400` → Queue limit reached
* `409` → Queue name already exists

---

# 2️⃣ View All Queues

### GET `/queues`

### Response

```json
[
  {
    "id": "uuid",
    "name": "Billing",
    "capacity": 10,
    "current_ticket_count": 5
  }
]
```

---

# 3️⃣ Remove Queue

### DELETE `/queues/{queue_id}`

### Rules

* Cannot delete if queue contains tickets (optional strict rule)

### Response

```json
{
  "message": "Queue removed successfully"
}
```

---

# 4️⃣ Add Ticket to Queue

### POST `/queues/{queue_id}/tickets`

Adds a new ticket type into the queue.

### Request

```json
{
  "title": "Login Error",
  "complexity": 40,
  "quantity": 5
}
```

### Rules

* Queue must exist
* quantity > 0
* total tickets must not exceed queue capacity
* complexity >= 0

### Response

```json
{
  "id": "uuid",
  "title": "Login Error",
  "complexity": 40,
  "quantity": 5
}
```

---

# 5️⃣ Bulk Add Tickets to Queue

### POST `/queues/{queue_id}/tickets/bulk`

### Request

```json
{
  "tickets": [
    {
      "title": "Password Reset",
      "complexity": 35,
      "quantity": 5
    },
    {
      "title": "Server Outage",
      "complexity": 100,
      "quantity": 1
    }
  ]
}
```

### Rules

* Total new quantity must not exceed queue capacity

### Response

```json
{
  "message": "Tickets added successfully",
  "added_count": 2
}
```

---

# 6️⃣ View Tickets of a Queue

### GET `/queues/{queue_id}/tickets`

### Response

```json
[
  {
    "id": "uuid",
    "title": "Login Error",
    "complexity": 40,
    "quantity": 5
  }
]
```

---

# 7️⃣ Create Standalone Ticket

### POST `/tickets`

Creates a ticket without needing a queue. You can optionally assign it to a queue.

### Request

```json
{
  "title": "Database Timeout",
  "complexity": 80,
  "quantity": 1,
  "queue_id": "uuid (optional)"
}
```

### Rules

* `quantity` > 0
* `complexity` >= 0
* If `queue_id` provided, queue must exist and capacity must not be exceeded.

### Response

```json
{
  "id": "uuid",
  "title": "Database Timeout",
  "complexity": 80,
  "quantity": 1
}
```

---

# 8️⃣ View Single Ticket

### GET `/tickets/{ticket_id}`

### Response

```json
{
  "id": "uuid",
  "title": "Login Error",
  "complexity": 40,
  "quantity": 5,
  "queue_id": "uuid"
}
```

---

# 9️⃣ Update Complexity for a Ticket

### PATCH `/tickets/{ticket_id}/complexity`

### Request

```json
{
  "complexity": 45
}
```

### Rules

* complexity >= 0

### Response

```json
{
  "message": "Complexity updated successfully"
}
```

---

# 1️⃣0️⃣ Remove Tickets from Queue (Partial Removal)

### DELETE `/queues/{queue_id}/tickets/{ticket_id}`

Removes quantity or entire ticket batch.

### Query Param (Optional)

```
?quantity=2
```

### Behavior

* If quantity provided → subtract
* If no quantity → delete ticket entirely

### Response

```json
{
  "message": "Ticket(s) removed successfully"
}
```

---

# 1️⃣1️⃣ Bulk Remove Tickets / Empty Queue

### DELETE `/queues/{queue_id}/tickets`

### Optional Body

```json
{
  "ticket_ids": ["uuid1", "uuid2"]
}
```

### Behavior

* If body provided → remove specific tickets
* If no body → empty queue completely

### Response

```json
{
  "message": "Queue cleared successfully"
}
```

---

# 1️⃣2️⃣ Full View (Queues + Tickets)

### GET `/queues/full-view`

### Response

```json
[
  {
    "id": "uuid",
    "name": "Billing",
    "capacity": 10,
    "tickets": [
      {
        "id": "uuid",
        "title": "Login Error",
        "complexity": 40,
        "quantity": 5
      }
    ]
  }
]
```

---

# 1️⃣3️⃣ Resolve Ticket

This is where the fun logic lives.

### POST `/resolve`

### Request

```json
{
  "ticket_id": "uuid",
  "effort_logged": 50
}
```

---

## Business Rules

* Ticket must exist
* quantity > 0
* effort_logged >= complexity
* Overtime = effort_logged - complexity
* Decrement quantity by 1
* Transaction must be atomic

---

## Response

```json
{
  "ticket": "Login Error",
  "complexity": 40,
  "effort_logged": 50,
  "overtime_returned": 10,
  "remaining_quantity": 4,
  "message": "Ticket resolved successfully"
}
```

---

## Error Cases

### 400 – Insufficient Effort Logged

```json
{
  "error": "Insufficient effort logged",
  "required": 40,
  "logged": 30
}
```

---

### 400 – Ticket batch already resolved

```json
{
  "error": "Ticket batch already resolved"
}
```

---

---

# Bonus 

Add:

### 🎯 GET `/resolve/overtime-breakdown`

Return standard block-wise breakdown for the overtime:

```json
{
  "overtime": 70,
  "blocks": {
    "50": 1,
    "20": 1
  }
}
```

Implement greedy algorithm for block breakdown.