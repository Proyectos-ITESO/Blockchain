# Sistema de Comunicación Encriptada con Blockchain

MVP de un sistema de mensajería encriptada de extremo a extremo (E2EE) con notarización en blockchain.

## Arquitectura del Proyecto

```
Blockchain/
├── app/                       # Backend (FastAPI)
│   ├── api/endpoints/         # REST & WebSocket endpoints
│   ├── core/                  # Config & Security
│   ├── db/                    # Models & Database
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   └── main.py               # Entry point
├── frontend/                  # Frontend (React + Vite)
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── contexts/         # React contexts
│   │   ├── pages/           # Page components
│   │   ├── services/        # API & WebSocket
│   │   ├── utils/           # E2EE crypto utilities
│   │   └── App.jsx          # Main component
│   ├── package.json
│   └── vite.config.js
├── contracts/                 # Smart contracts (Solidity)
│   ├── Notary.sol
│   └── scripts/
├── docs/                      # Documentation
├── tests/                     # Tests
└── Docker & Config files
```

## Tecnologías

**Backend:**
- FastAPI - Framework web moderno y rápido
- SQLAlchemy - ORM para PostgreSQL
- Web3.py - Integración con blockchain Ethereum
- JWT - Autenticación con tokens
- WebSockets - Comunicación en tiempo real

**Frontend:**
- React 18 - UI library
- Vite - Build tool
- TailwindCSS - Utility-first CSS
- libsodium - E2EE encryption (X25519-XSalsa20-Poly1305)
- React Router - Client-side routing

**Blockchain:**
- Solidity - Smart contract para notarización
- Hardhat - Development framework
- Testnet Sepolia - Red de pruebas

**Base de Datos:**
- PostgreSQL - Base de datos relacional

## Características Principales

1. **Autenticación Segura**: Sistema de registro/login con JWT
2. **Mensajería en Tiempo Real**: WebSockets para comunicación instantánea
3. **Encriptación E2E**: Los mensajes se encriptan en el cliente
4. **Notarización Blockchain**: Hashes de mensajes registrados en blockchain
5. **Verificación**: Endpoint para verificar integridad de mensajes

## Instalación y Configuración

### Requisitos Previos

- Python 3.9+
- PostgreSQL 14+
- Node.js 18+ (para smart contracts)

### Configuración del Backend

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd Blockchain
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus valores
```

5. **Configurar la base de datos**
```bash
# Crear base de datos PostgreSQL
createdb encrypted_chat

# Ejecutar migraciones
alembic upgrade head
```

6. **Ejecutar el servidor**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: http://localhost:8000

Documentación interactiva: http://localhost:8000/docs

### Configuración del Smart Contract

1. **Instalar Hardhat**
```bash
cd contracts
npm install --save-dev hardhat
npm install --save-dev @nomicfoundation/hardhat-toolbox
```

2. **Compilar el contrato**
```bash
npx hardhat compile
```

3. **Desplegar en Testnet**
```bash
npx hardhat run scripts/deploy.js --network sepolia
```

4. **Actualizar .env con la dirección del contrato**

## Uso de la API

### Autenticación

**Registro:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "securepass123"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user1&password=securepass123"
```

### Chat

**Obtener contactos:**
```bash
curl -X GET http://localhost:8000/api/contacts \
  -H "Authorization: Bearer <token>"
```

**Obtener historial:**
```bash
curl -X GET http://localhost:8000/api/chat/{user_id} \
  -H "Authorization: Bearer <token>"
```

### WebSocket

Conectar al WebSocket en `ws://localhost:8000/ws?token=<jwt_token>`

**Formato de mensaje:**
```json
{
  "to_user_id": 2,
  "payload": "encrypted_message_here",
  "message_hash": "sha256_hash_here"
}
```

### Verificación

**Verificar mensaje:**
```bash
curl -X GET http://localhost:8000/api/verify/{message_id} \
  -H "Authorization: Bearer <token>"
```

## Desarrollo

### Estructura de Datos

**User:**
- id (int)
- username (string, unique)
- hashed_password (string)
- created_at (datetime)

**Message:**
- id (int)
- sender_id (int, FK User)
- receiver_id (int, FK User)
- encrypted_payload (text)
- message_hash (string)
- blockchain_tx_hash (string, nullable)
- timestamp (datetime)

**Contact:**
- id (int)
- user_id (int, FK User)
- contact_id (int, FK User)

### Flujo de Mensajería

1. Cliente A encripta mensaje y calcula hash
2. Cliente A envía via WebSocket: `{payload, hash, to_user_id}`
3. Backend guarda en DB y reenvía a Cliente B (si está conectado)
4. Backend registra hash en blockchain (tarea asíncrona)
5. Backend actualiza `blockchain_tx_hash` cuando se confirma

## Roadmap

- [x] Semana 1: Backend base + Smart Contract
- [x] Semana 2: WebSockets + Integración Web3
- [x] Semana 3: Integración completa + Pruebas E2E
- [x] Semana 4: Frontend React + Deployment config

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.

**TL;DR:**
```bash
# Backend
cp .env.example .env
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python init_db.py
./start.sh

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Licencia

MIT