# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints

### Authentication

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "string",
  "created_at": "2024-01-01T00:00:00"
}
```

#### POST /auth/token
Login and obtain JWT token.

**Request Body (Form Data):**
```
username=string
password=string
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### GET /auth/me
Get current user information (requires authentication).

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "string",
  "created_at": "2024-01-01T00:00:00"
}
```

---

### Chat

#### GET /api/contacts
Get list of user's contacts (requires authentication).

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "username": "contact1",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

#### POST /api/contacts/{user_id}
Add a user to contacts (requires authentication).

**Response (201 Created):**
```json
{
  "message": "Contact added successfully"
}
```

#### GET /api/chat/{user_id}
Get chat history with a specific user (requires authentication).

**Query Parameters:**
- `limit` (optional): Number of messages to retrieve (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "sender_id": 1,
    "receiver_id": 2,
    "encrypted_payload": "encrypted_message_here",
    "message_hash": "0xabc...",
    "blockchain_tx_hash": "0x123...",
    "timestamp": "2024-01-01T00:00:00"
  }
]
```

#### GET /api/messages/recent
Get recent messages for current user (requires authentication).

**Query Parameters:**
- `limit` (optional): Number of messages (default: 20)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "sender_id": 1,
    "receiver_id": 2,
    "encrypted_payload": "encrypted_message_here",
    "message_hash": "0xabc...",
    "blockchain_tx_hash": "0x123...",
    "timestamp": "2024-01-01T00:00:00"
  }
]
```

#### GET /api/users/search
Search for users by username (requires authentication).

**Query Parameters:**
- `query`: Search term (minimum 2 characters)
- `limit` (optional): Number of results (default: 10)

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "username": "user1"
  }
]
```

---

### WebSocket

#### WS /ws?token={jwt_token}
Real-time messaging WebSocket connection.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_JWT_TOKEN');
```

**Send Message:**
```json
{
  "to_user_id": 2,
  "payload": "encrypted_message_here",
  "message_hash": "0xabc..."
}
```

**Receive Message:**
```json
{
  "type": "message",
  "message_id": 1,
  "from_user_id": 1,
  "from_username": "sender",
  "payload": "encrypted_message_here",
  "message_hash": "0xabc...",
  "timestamp": "2024-01-01T00:00:00"
}
```

**Message Types:**
- `connected`: Connection established
- `message`: New message received
- `sent`: Message sent confirmation
- `error`: Error occurred

#### GET /ws/online
Get list of currently online users.

**Response (200 OK):**
```json
{
  "online_users": [1, 2, 3],
  "count": 3
}
```

---

### Verification

#### GET /api/verify/{message_id}
Verify a message on the blockchain (requires authentication).

**Response (200 OK):**
```json
{
  "message_id": 1,
  "message_hash": "0xabc...",
  "verified": true,
  "blockchain_tx_hash": "0x123..."
}
```

#### POST /api/notarize/{message_id}
Manually trigger notarization of a message (requires authentication).

**Response (200 OK):**
```json
{
  "message": "Notarization started",
  "message_id": 1
}
```

#### GET /api/hash-info/{message_id}
Get detailed blockchain information about a message (requires authentication).

**Response (200 OK):**
```json
{
  "message_id": 1,
  "message_hash": "0xabc...",
  "registered": true,
  "timestamp": 1640995200,
  "registrar": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "blockchain_tx_hash": "0x123..."
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Message Flow

1. **Client A encrypts message** with Client B's public key
2. **Client A calculates SHA-256 hash** of the plaintext message
3. **Client A sends via WebSocket:**
   ```json
   {
     "to_user_id": 2,
     "payload": "encrypted_payload",
     "message_hash": "0xabc..."
   }
   ```
4. **Backend saves message** to database
5. **Backend forwards message** to Client B (if online)
6. **Backend registers hash** on blockchain (asynchronous)
7. **Client B receives message** and decrypts with private key
8. **Client B can verify** message integrity via `/api/verify/{message_id}`

---

## Security Notes

- All passwords are hashed using bcrypt
- JWT tokens expire after 30 minutes (configurable)
- Message payloads are encrypted end-to-end (client-side)
- Only message hashes (not content) are stored on blockchain
- WebSocket connections require valid JWT authentication
- Users can only access their own messages

---

## Rate Limiting

Currently no rate limiting is implemented. In production, consider:
- Login attempts: 5 per minute
- API requests: 100 per minute per user
- WebSocket messages: 10 per second per user
