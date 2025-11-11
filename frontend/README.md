# Encrypted Messaging - Frontend

React frontend for the encrypted messaging system with blockchain notarization.

## Features

- 🔐 **End-to-End Encryption**: Messages encrypted with libsodium (X25519-XSalsa20-Poly1305)
- ⚡ **Real-time Messaging**: WebSocket-based instant messaging
- 🔑 **Key Management**: Automatic keypair generation and secure storage
- ⛓️ **Blockchain Verification**: Verify message integrity on blockchain
- 📱 **Responsive Design**: TailwindCSS-based modern UI
- 🎨 **Beautiful UX**: Clean, intuitive interface

## Tech Stack

- React 18
- Vite
- TailwindCSS
- libsodium-wrappers (E2EE)
- React Router
- Axios
- date-fns

## Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

The app will be available at http://localhost:3000

## Development

```bash
# Run dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Environment Variables

Create a `.env` file:

```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── ContactList.jsx
│   │   ├── MessageWindow.jsx
│   │   ├── UserSettings.jsx
│   │   └── ProtectedRoute.jsx
│   ├── contexts/        # React contexts
│   │   ├── AuthContext.jsx
│   │   └── ChatContext.jsx
│   ├── pages/          # Page components
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   └── Chat.jsx
│   ├── services/       # API & WebSocket services
│   │   ├── api.js
│   │   └── websocket.js
│   ├── utils/          # Utilities
│   │   └── crypto.js   # E2EE functions
│   ├── App.jsx        # Main app component
│   ├── main.jsx       # Entry point
│   └── index.css      # Global styles
├── public/            # Static assets
├── index.html        # HTML template
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## How It Works

### 1. Registration & Key Generation

When a user registers:
1. Account is created on the backend
2. A keypair (public/private) is generated client-side
3. Keys are stored in localStorage
4. No keys are sent to the server

### 2. Encryption Flow

When sending a message:
1. User types plaintext message
2. Message is encrypted with recipient's public key
3. SHA-256 hash is calculated from plaintext
4. Encrypted payload + hash sent via WebSocket
5. Backend stores encrypted message and registers hash on blockchain

### 3. Decryption Flow

When receiving a message:
1. Encrypted payload received via WebSocket
2. Message is decrypted with user's private key
3. Plaintext is displayed to user
4. User can verify message integrity on blockchain

### 4. Blockchain Verification

Click the shield icon on any message to:
1. Query the backend verification endpoint
2. Backend checks if hash is registered on blockchain
3. Returns verification status
4. UI shows verified/unverified status

## Security Features

### End-to-End Encryption

- **Algorithm**: X25519-XSalsa20-Poly1305 (libsodium)
- **Key Length**: 32 bytes (256 bits)
- **Nonce**: Random 24 bytes per message
- **Storage**: Keys stored in browser localStorage (encrypted at rest by browser)

### Key Management

- Keys generated client-side, never sent to server
- Private key never leaves the device
- Public keys shared manually between users
- Keys can be exported for backup

### Message Integrity

- SHA-256 hash calculated from plaintext
- Hash registered on blockchain
- Immutable proof of message content
- Verification available to sender and receiver

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard
# VITE_API_URL=https://your-backend.com
# VITE_WS_URL=wss://your-backend.com/ws
```

### Netlify

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Build
npm run build

# Deploy
netlify deploy --prod --dir=dist
```

### Manual Build

```bash
# Build for production
npm run build

# Output will be in dist/
# Upload dist/ to any static hosting service
```

## Usage

### 1. Register an Account

1. Navigate to `/register`
2. Choose username and password
3. Keys are generated automatically
4. You're redirected to chat

### 2. Add Contacts

1. Click the "+" icon in the sidebar
2. Search for users by username
3. Click "Add" to add them to contacts

### 3. Exchange Public Keys

**Important**: For E2EE to work, you need to exchange public keys:

1. Open Settings (user icon)
2. Copy your public key
3. Share it with your contact (via secure channel)
4. Receive their public key
5. Store it locally (feature to be implemented in UI)

**Current workaround**: Public keys are stored automatically on first message exchange.

### 4. Send Messages

1. Select a contact from the list
2. Type your message
3. Press Enter or click Send
4. Message is encrypted and sent
5. Blockchain notarization happens in background

### 5. Verify Messages

1. Click the shield icon on any message
2. Wait for verification query
3. Green shield = verified on blockchain
4. Red shield = not yet notarized

## Troubleshooting

### Messages won't decrypt

- Ensure you have the sender's public key
- Check if keys were generated properly
- Try regenerating keys in settings

### WebSocket not connecting

- Check if backend is running
- Verify WebSocket URL in .env
- Check browser console for errors
- Ensure JWT token is valid

### Messages not sending

- Verify WebSocket connection (check status)
- Ensure recipient exists
- Check if you have recipient's public key
- Check network tab for errors

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Requires:
- WebSocket support
- localStorage
- WebCrypto API
- ES6+ support

## License

MIT
