# TrustPay

TrustPay is a fintech MVP for connecting **payment confirmation** with **parcel delivery notifications**.

When a customer pays a business for a parcel, the business may see that payment succeeded while the rider does not. That creates delayed deliveries, disputes, and the risk of handing over a parcel without confirmed payment.

TrustPay is the source of truth for payment status. The rider should never rely on a customer claiming they have paid.

```text
Customer pays business
        ↓
TrustPay receives payment confirmation
        ↓
Payment matched to the order
        ↓
Assigned rider notified
        ↓
Rider sees PAYMENT CONFIRMED
        ↓
Delivery can proceed
```

TrustPay is a **payment-to-rider notification bridge**, not a payment processor, wallet, or escrow system.

## Authors

| Name | GitHub |
| --- | --- |
| Yvonnah Shiala | [y-shiala](https://github.com/y-shiala) |
| Samuel Ben | [Houdiniben](https://github.com/Houdiniben) |
| Monica Wanjiku | [WanjikuMonica](https://github.com/WanjikuMonica) |
| Junior Antony Maina | [Juniormaina](https://github.com/Juniormaina) |

---

## Contents

- [Authors](#authors)
- [Stack](#stack)
- [Repository layout](#repository-layout)
- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [Demo accounts](#demo-accounts)
- [Product demo](#product-demo)
- [Frontend](#frontend)
- [Phone numbers](#phone-numbers)
- [Domain model](#domain-model)
- [API](#api)
- [Payment webhook](#payment-webhook)
- [Business rules](#business-rules)
- [Architecture](#architecture)
- [Security](#security)
- [Tests](#tests)
- [Scripts](#scripts)
- [Troubleshooting](#troubleshooting)
- [Out of scope](#out-of-scope)

---

## Stack

| Layer | Tech |
| --- | --- |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, React Router, Lucide icons |
| Backend | Node.js 20+, Express, TypeScript, JWT, bcryptjs, Zod |
| HTTP client | Browser Fetch API (no Axios) |
| Data | In-memory mock store (no database) |
| Payments | Mock webhook via `MockPaymentProvider` |

Package manager: **pnpm**.

Restarting the API clears all users, orders, payments, and notifications, then reseeds the demo accounts.

---

## Repository layout

```text
Trustpay/
├── client/                       React app
│   └── src/
│       ├── auth/                 Auth context + route guards
│       ├── components/           Shared UI (PaymentStatus, etc.)
│       ├── layouts/              Business + rider shells
│       ├── lib/                  API client, formatting, polling
│       └── pages/                Login, business, rider screens
├── server/                       Backend API
│   ├── src/
│   │   ├── auth/                 Register, login, current user
│   │   ├── orders/               Create, list, get, assign rider
│   │   ├── deliveries/           Confirm delivery
│   │   ├── payments/             Webhook + MockPaymentProvider
│   │   ├── notifications/        In-app notifications
│   │   ├── users/                List riders
│   │   ├── store/                In-memory data + demo seed
│   │   ├── middleware/           JWT, roles, validation, errors
│   │   ├── types/                Domain types
│   │   ├── utils/
│   │   ├── app.ts                Express app
│   │   └── server.ts             Process entry
│   ├── tests/                    Payment-to-delivery flow tests
│   └── .env.example
└── README.md
```

Business logic lives in services, not route handlers.

---

## Prerequisites

- Node.js 20 or later
- [pnpm](https://pnpm.io/)

No PostgreSQL, Docker, or Prisma.

---

## Quick start

```bash
pnpm install
cp server/.env.example server/.env
cp client/.env.example client/.env
```

Set `VITE_WEBHOOK_SECRET` in `client/.env` to the **same value** as `WEBHOOK_SECRET` in `server/.env`. The demo payment button sends that secret as `X-Webhook-Secret`.

Start the API:

```bash
pnpm dev
```

- API: [http://localhost:3000](http://localhost:3000)
- Health: `GET /health` → `{ "status": "ok", "service": "trustpay" }`

Start the frontend in another terminal:

```bash
pnpm web
```

- App: [http://localhost:5173](http://localhost:5173)

Production-style builds:

```bash
pnpm build          # compile API to server/dist/
pnpm start          # run compiled API
pnpm web:build      # build client
```

### Environment variables

#### API (`server/.env`)

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `JWT_SECRET` | Yes | — | Signs authentication tokens |
| `JWT_EXPIRES_IN` | No | `7d` | Token lifetime |
| `WEBHOOK_SECRET` | Yes | — | Shared secret for `POST /payments/webhook` |
| `PORT` | No | `3000` | HTTP port |
| `CORS_ORIGIN` | No | `*` | Allowed origin(s), comma-separated |
| `NODE_ENV` | No | `development` | `development`, `test`, or `production` |

#### Frontend (`client/.env`)

| Variable | Purpose |
| --- | --- |
| `VITE_API_URL` | Backend origin (`http://localhost:3000`) |
| `VITE_WEBHOOK_SECRET` | Must match `WEBHOOK_SECRET` for **Demo: Simulate Payment** |

Do not store payment-provider credentials. Passwords are hashed; password hashes are never returned by the API.

---

## Demo accounts

Seeded when the API starts (`server/src/store/seed.ts`):

| Role | Name | Email | Password | Phone |
| --- | --- | --- | --- | --- |
| Business | Kampala Parcels | `business@trustpay.test` | `password123` | `+256700000001` |
| Rider | John Rider | `john@trustpay.test` | `password123` | `+256700000002` |

These credentials also appear on the login screen in development.

You can register additional business or rider accounts from the same screen.

---

## Product demo

This is the flow the MVP is built to prove. Use **two browser tabs** — each tab has its own login session.

1. Log in as the business (`business@trustpay.test`).
2. Create an order: customer name, phone with country code, amount in UGX (for example `50000`).
3. Assign **John Rider** (on create, or later on the order page).
4. Open the order. Payment is **PENDING**. `safeToDeliver` is `false`.
5. In the second tab, log in as the rider (`john@trustpay.test`).
6. Open the delivery. It shows **PAYMENT PENDING**. Confirm delivery is disabled.
7. Back on the business order page, click **Demo: Simulate Payment**. This is mock-only.
8. TrustPay marks the order **PAID**, creates a `PAYMENT_CONFIRMED` notification, and sets `riderNotified`.
9. The rider UI polls every 4 seconds. The bell badge updates, the delivery shows **PAYMENT CONFIRMED**, and confirm delivery is enabled.
10. The rider confirms delivery. The order status becomes **DELIVERED**.

**Demo: Simulate Payment** calls `POST /payments/webhook`. It is not a real payment.

---

## Frontend

### Routes

| Path | Access | Screen |
| --- | --- | --- |
| `/login` | Public | Log in / register |
| `/` | Authenticated | Redirects to `/business` or `/rider` by role |
| `/business` | BUSINESS | Dashboard: totals + orders |
| `/business/orders/new` | BUSINESS | Create order, optional rider |
| `/business/orders/:id` | BUSINESS | Order details, assign rider, simulate payment |
| `/business/notifications` | BUSINESS | Paid / rider-notified activity |
| `/business/profile` | BUSINESS | Profile + logout |
| `/rider` | RIDER | Delivery cards (mobile-first) |
| `/rider/deliveries/:id` | RIDER | Payment banner + confirm delivery |
| `/rider/notifications` | RIDER | In-app notifications |
| `/rider/profile` | RIDER | Profile + logout |

A business cannot open rider routes. A rider cannot open business routes. Unauthenticated users are sent to `/login`.

### Payment UI

`PaymentStatus` is shared by both workspaces:

| State | Rider meaning |
| --- | --- |
| 🔴 Payment pending | Do not complete delivery |
| 🟢 Payment confirmed | Safe to hand over the parcel |
| Payment failed | Do not complete delivery |
| Delivery completed | Order already delivered |

Confirm delivery is enabled only when `paymentStatus === "PAID"` and the order is not already `DELIVERED`.

### Auth and polling

- JWT is stored in `sessionStorage` (`trustpay_token` / `trustpay_user`), so each browser tab can stay logged in as a different account (business in one tab, rider in another).
- Rider notifications and order/delivery screens poll about every 4 seconds so a simulated payment appears without a page refresh.
- All HTTP calls go through `client/src/lib/api.ts` (Fetch API).

---

## Phone numbers

International numbers with **any country code** (E.164-style):

- `+256700000001`
- `+14155552671`

The API requires `+`, then 7–15 digits, first digit 1–9. Uganda is not required.

---

## Domain model

### Roles

| Role | Can |
| --- | --- |
| `BUSINESS` | Register/login, create orders, assign riders, view payment and notification status, trigger demo payment |
| `RIDER` | Register/login, view assigned deliveries, receive payment notifications, confirm delivery after payment |

Customers are fields on the order (`customerName`, `customerPhone`). They do not have accounts.

### Order status

`PENDING` → `ASSIGNED` → `DELIVERED` (also `OUT_FOR_DELIVERY`, `CANCELLED` in the model; the MVP UI uses assigned / delivered)

### Payment status (order)

| Value | Meaning |
| --- | --- |
| `PENDING` | No successful matched payment |
| `PAID` | Successful payment matched the order amount |
| `FAILED` | Webhook processed but status was not successful, or amount did not match |

### Payment record status

`PENDING` · `SUCCESSFUL` · `FAILED`

Stored on the payment object. Provider for the MVP is `MOCK`.

### Notification type

`PAYMENT_CONFIRMED` only.

### Order numbers

Sequential from `TP-1001` (`server/src/utils/orderNumber.ts`).

### Order API shape

```json
{
  "id": "uuid",
  "orderNumber": "TP-1001",
  "businessId": "uuid",
  "riderId": "uuid | null",
  "rider": { "id": "uuid", "name": "John Rider", "phone": "+256700000002" },
  "customerName": "Sarah",
  "customerPhone": "+256700000003",
  "amount": 50000,
  "currency": "UGX",
  "status": "ASSIGNED",
  "paymentStatus": "PENDING",
  "safeToDeliver": false,
  "riderNotified": false,
  "createdAt": "...",
  "updatedAt": "..."
}
```

---

## API

Base URL: `http://localhost:3000`

Protected routes require:

```http
Authorization: Bearer <jwt>
```

Errors look like:

```json
{
  "message": "Invalid email or password.",
  "code": "INVALID_CREDENTIALS"
}
```

### Health

```http
GET /health
```

```json
{ "status": "ok", "service": "trustpay" }
```

### Auth

| Method | Path | Access |
| --- | --- | --- |
| `POST` | `/auth/register` | Public |
| `POST` | `/auth/login` | Public |
| `GET` | `/auth/me` | Authenticated |

#### Register

```http
POST /auth/register
Content-Type: application/json
```

```json
{
  "name": "Kampala Parcels",
  "phone": "+256700000001",
  "email": "business@example.com",
  "password": "password123",
  "role": "BUSINESS"
}
```

| Field | Rules |
| --- | --- |
| `name` | 2–100 characters |
| `phone` | International, `+` and 7–15 digits |
| `email` | Valid email, stored lowercase |
| `password` | 8–128 characters |
| `role` | `BUSINESS` or `RIDER` |

`201` response:

```json
{
  "user": { "id": "...", "name": "...", "phone": "...", "email": "...", "role": "BUSINESS" },
  "token": "<jwt>"
}
```

Duplicate email or phone → `409` `ACCOUNT_EXISTS`.

#### Login

```http
POST /auth/login
```

```json
{
  "email": "business@trustpay.test",
  "password": "password123"
}
```

Invalid credentials → `401` `INVALID_CREDENTIALS`.

#### Me

```http
GET /auth/me
Authorization: Bearer <token>
```

```json
{ "user": { "id": "...", "name": "...", "role": "BUSINESS" } }
```

### Orders

| Method | Path | Access |
| --- | --- | --- |
| `POST` | `/orders` | BUSINESS |
| `GET` | `/orders` | BUSINESS (own) / RIDER (assigned) |
| `GET` | `/orders/:orderId` | Owner or assigned rider |
| `POST` | `/orders/:orderId/assign-rider` | BUSINESS |
| `POST` | `/orders/:orderId/deliver` | Assigned RIDER |

#### Create

```http
POST /orders
Authorization: Bearer <business-token>
```

```json
{
  "customerName": "Sarah",
  "customerPhone": "+256700000003",
  "amount": 50000
}
```

`201` → `{ "order": { ... } }` with `paymentStatus: "PENDING"`.

#### Assign rider

```http
POST /orders/:orderId/assign-rider
```

```json
{ "riderId": "<uuid>" }
```

Sets `status` to `ASSIGNED`. If the order is already `PAID`, TrustPay notifies the newly assigned rider.

Cannot assign on `DELIVERED` or `CANCELLED` orders (`409`). Unknown rider → `404` `RIDER_NOT_FOUND`.

#### Confirm delivery

```http
POST /orders/:orderId/deliver
Authorization: Bearer <rider-token>
```

Payment not confirmed (`409` `PAYMENT_NOT_CONFIRMED`):

```json
{
  "message": "Payment has not been confirmed. Delivery cannot be completed.",
  "code": "PAYMENT_NOT_CONFIRMED"
}
```

Success (`200`):

```json
{
  "message": "Delivery confirmed successfully.",
  "order": { "status": "DELIVERED", "paymentStatus": "PAID", "safeToDeliver": true }
}
```

Already delivered → `409` `ALREADY_DELIVERED`. Rider not assigned to the order → `403`.

### Riders

| Method | Path | Access |
| --- | --- | --- |
| `GET` | `/riders` | BUSINESS |

```json
{
  "riders": [
    { "id": "...", "name": "John Rider", "phone": "+256700000002", "email": "john@trustpay.test" }
  ]
}
```

### Notifications

| Method | Path | Access |
| --- | --- | --- |
| `GET` | `/notifications` | RIDER |
| `PATCH` | `/notifications/:id/read` | RIDER (own) |

`GET /notifications?unread=true` returns unread only.

Example item:

```json
{
  "id": "...",
  "riderId": "...",
  "orderId": "...",
  "type": "PAYMENT_CONFIRMED",
  "title": "Payment Confirmed",
  "message": "Order TP-1001 has been paid successfully.\nAmount: UGX 50,000.\nYou can proceed with the delivery.",
  "read": false,
  "createdAt": "..."
}
```

---

## Payment webhook

| Method | Path | Access |
| --- | --- | --- |
| `POST` | `/payments/webhook` | `X-Webhook-Secret` must equal `WEBHOOK_SECRET` |

No JWT. Wrong or missing secret → `401` `INVALID_WEBHOOK`.

```http
POST /payments/webhook
X-Webhook-Secret: <WEBHOOK_SECRET>
Content-Type: application/json
```

```json
{
  "transactionReference": "TXN123456",
  "orderNumber": "TP-1001",
  "amount": 50000,
  "status": "SUCCESSFUL"
}
```

| Field | Rules |
| --- | --- |
| `transactionReference` | 3–100 characters, unique per payment |
| `orderNumber` | Existing order, e.g. `TP-1001` |
| `amount` | Must match the order amount for success |
| `status` | `PENDING`, `SUCCESSFUL`, or `FAILED` |

### Processing

1. Validate secret and payload (`MockPaymentProvider.verifyPayment`).
2. If `transactionReference` already exists, return `duplicate: true` and do not create another payment or notification.
3. Find the order by `orderNumber`. Missing → `404` `ORDER_NOT_FOUND`.
4. If the order is already `PAID`, return duplicate / already paid.
5. If status is not `SUCCESSFUL` or the amount does not match: store a `FAILED` payment, set order `paymentStatus` to `FAILED`, **do not notify**.
6. On success: store `SUCCESSFUL` payment, set order to `PAID`, notify the assigned rider (InApp).

Success body:

```json
{
  "received": true,
  "duplicate": false,
  "matched": true,
  "orderNumber": "TP-1001",
  "paymentStatus": "PAID",
  "notificationCreated": true
}
```

Amount mismatch:

```json
{
  "received": true,
  "matched": false,
  "reason": "AMOUNT_MISMATCH",
  "notificationCreated": false,
  "message": "Payment amount does not match the order amount."
}
```

The frontend demo button generates a unique `transactionReference` (`DEMO-<orderNumber>-<timestamp>`).

---

## Business rules

1. TrustPay is the only source of truth for whether a parcel is paid.
2. Notify the rider only when **all** of these hold: payment `SUCCESSFUL`, amount matches, rider assigned.
3. Do not notify on failed payment, amount mismatch, or unknown order.
4. Delivery is blocked until `paymentStatus = PAID`.
5. The webhook is idempotent on `transactionReference`.
6. Duplicate `PAYMENT_CONFIRMED` notifications for the same order + rider are not created.
7. Payment before assignment still marks the order `PAID`. Assigning a rider afterwards sends the notification.

---

## Architecture

```text
POST /payments/webhook
        ↓
MockPaymentProvider.verifyPayment()
        ↓
PaymentService (match order, amount, idempotency)
        ↓
NotificationService.notifyPaymentConfirmed()
        ↓
NotificationChannel
        ├── InApp          implemented
        ├── SMS            future
        ├── WhatsApp       future
        └── Push           future
```

To point at a real provider later (for example MTN Mobile Money), implement `PaymentProvider` in `server/src/payments/providers/` and swap it in `server/src/payments/providers/index.ts`. Order and notification code should not need a rewrite.

```typescript
interface PaymentProvider {
  verifyPayment(payload: unknown): Promise<VerifiedPayment>;
  getTransactionStatus(transactionReference: string): Promise<VerifiedPayment | null>;
}
```

Data is held in `server/src/store/memory.ts` (`users`, `orders`, `payments`, `notifications`). It is not written to disk.

---

## Security

| Control | How |
| --- | --- |
| Passwords | bcryptjs hashes; hashes never returned |
| Auth | JWT Bearer tokens; role checks on business/rider routes |
| Validation | Zod on request bodies |
| Webhook | Shared secret header; payload schema |
| Helmet | HTTP security headers |
| CORS | Configurable origin; webhook header allowed |
| Secrets | Environment variables only |
| Demo payment | Clearly labelled; not presented as a live payment |

---

## Tests

```bash
pnpm test
```

Uses the in-memory store (no database). `server/tests/setup.ts` sets `NODE_ENV=test` so demo seed is skipped; each run registers its own users.

Covered path:

1. Business creates an order  
2. Business assigns a rider  
3. Rider cannot confirm delivery before payment  
4. Payment webhook is received  
5. Payment is matched to the order  
6. Order becomes `PAID`  
7. Rider receives `PAYMENT_CONFIRMED`  
8. Rider can list and mark the notification read  
9. Rider can confirm delivery after payment  
10. Duplicate webhook does not create a second payment or notification  
11. Invalid webhook secret is rejected  
12. Amount mismatch does not notify the rider  

Watch mode: `pnpm test:watch`.

---

## Scripts

| Script | Where | Description |
| --- | --- | --- |
| `pnpm dev` | root → `server` | API with reload (`tsx watch`) |
| `pnpm web` | root → `client` | Vite frontend on port 5173 |
| `pnpm web:build` | root → `client` | Production frontend build |
| `pnpm build` | root → `server` | Compile API to `server/dist/` |
| `pnpm start` | root → `server` | Run compiled API |
| `pnpm test` | root → `server` | Vitest payment-flow suite |
| `pnpm test:watch` | root → `server` | Vitest watch mode |

---

## Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| Demo accounts missing | Restart the API; seed runs on startup |
| Data disappeared | In-memory store resets on restart |
| Simulate payment → invalid webhook | `VITE_WEBHOOK_SECRET` ≠ `WEBHOOK_SECRET` |
| Cannot reach API from the UI | API not running, or `VITE_API_URL` is wrong |
| Logged out after refresh | Sign in again (`trustpay_token` is per tab in sessionStorage) |
| Delivery button disabled | Order is not `PAID`, or you are not the assigned rider |
| Phone validation error | Send `+` and country code, e.g. `+256700000001` |
| Register `ACCOUNT_EXISTS` | Email or phone already in the in-memory store |

---

## Out of scope

This MVP does not include:

- Real payment processing, wallets, or escrow
- Multiple live payment providers
- Customer accounts or a customer portal
- GPS, maps, or logistics optimization
- SMS, WhatsApp, or push infrastructure
- WebSockets (polling is used instead)
- Analytics dashboards
- Persistent database storage
