# Sistema de Comunicación Encriptada con Blockchain

MVP de un sistema de mensajería encriptada de extremo a extremo (E2EE) con notarización en blockchain.

## Arquitectura del Proyecto

```
Blockchain/
├── app/
│   ├── api/
│   │   └── endpoints/          # Endpoints de la API REST
│   │       ├── auth.py         # Autenticación (registro, login)
│   │       ├── chat.py         # API de chat (contactos, historial)
│   │       ├── websocket.py    # WebSocket para mensajería en tiempo real
│   │       └── verification.py # Verificación de mensajes en blockchain
│   ├── core/
│   │   ├── config.py          # Configuración de la aplicación
│   │   └── security.py        # JWT, hashing de contraseñas
│   ├── db/
│   │   ├── database.py        # Conexión a la base de datos
│   │   └── models.py          # Modelos SQLAlchemy (User, Message, Contact)
│   ├── schemas/
│   │   ├── auth.py            # Schemas de autenticación
│   │   ├── chat.py            # Schemas de mensajes
│   │   └── user.py            # Schemas de usuario
│   ├── services/
│   │   ├── blockchain.py      # Servicio de integración Web3.py
│   │   └── websocket.py       # Gestor de conexiones WebSocket
│   └── main.py                # Punto de entrada de FastAPI
├── contracts/
│   ├── Notary.sol             # Smart contract para notarización
│   └── scripts/
│       ├── deploy.py          # Script de despliegue
│       └── interact.py        # Script de interacción con el contrato
├── tests/                     # Tests unitarios y de integración
├── alembic/                   # Migraciones de base de datos
├── requirements.txt           # Dependencias de Python
├── .env.example              # Variables de entorno de ejemplo
└── README.md
```

## Tecnologías

**Backend:**
- FastAPI - Framework web moderno y rápido
- SQLAlchemy - ORM para PostgreSQL
- Web3.py - Integración con blockchain Ethereum
- JWT - Autenticación con tokens
- WebSockets - Comunicación en tiempo real

**Blockchain:**
- Solidity - Smart contract para notarización
- Hardhat/Remix - Desarrollo y despliegue
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
- [ ] Semana 4: Frontend React + Despliegue

## Licencia

MIT