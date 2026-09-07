Richard Orido - richie-omondi
Jane Njeri - Jane-Njeri-star
John Nzau - jahntel 
Kennedy Maina - hersaintel


# RelFast – Delivery Readiness for Nigerian Retailers

RelFast replaces WhatsApp and phone-call chaos with a simple system where every delivery is logged, assigned, tracked, and confirmed.

## Problem

Small Nigerian retailers (phone shops, pharmacies, electronics, provision stores) coordinate deliveries over WhatsApp and calls.

This creates:
- No shared record of who was assigned
- No live status visibility
- No proof of delivery

## Who it is for

| Role | What they do |
|------|----------------|
| **Retailer** | Logs a delivery request (customer, phone, address, item) |
| **Dispatcher** | Sees open requests and assigns a rider |
| **Rider** | Sees assigned jobs and updates status (Assigned → Picked Up → Delivered) |
| **Customer** | Can confirm receipt via QR (proof of delivery) |

## Current Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Frontend | Vanilla HTML / CSS / JS | Zero build step, works on any phone browser |
| Real-time | Socket.io | Live updates when a request is created or status changes |
| Backend | Node.js + Express | Simple REST API + WebSockets |
| Database | JSON file store (`reflex-data.json`) | No external DB, zero native modules, easy to demo |
| Auth | JWT | Role-based (retailer / dispatcher / rider) |
| QR | `qrcode` library | Generates proof-of-delivery codes |

### Why this stack?

- One language (JavaScript) so the whole team can contribute
- No Docker, no Postgres setup, no build tools required for the sprint
- Runs with a single `npm run dev`
- Easy to explain and defend in a live panel

## Status Flow
pending → assigned → picked_up → delivered
textOnly legal transitions are allowed. The API rejects invalid jumps.

## Demo Accounts

| Role       | Name                 | Password     |
|------------|----------------------|--------------|
| Retailer   | Chioma Electronics   | retailer123  |
| Dispatcher | Tunde Adebayo        | dispatch123  |
| Rider      | Emeka Obi            | rider123     |

## Quick Start

```bash
npm install
npm run dev
Open: http://localhost:3000

Trade-offs (we own these)
1. No live GPS tracking
What: Status only (Assigned → Picked Up → Delivered). No map or location pings.

Acceptable because: Solves the core visibility problem in one sprint. Real GPS needs a mobile app, permissions, and a map provider.

With more time: Rider PWA + background location + simple map view.
2. Manual assignment only
What: Dispatcher picks a rider from a dropdown. No auto-dispatch.

Acceptable because: Small shops know their riders. Human judgment matters more than optimisation at this scale.

With more time: “Suggest least-loaded / nearest” button, then optional auto-assign rules.
3. JSON file store (single process)
What: All data lives in one reflex-data.json file. No horizontal scaling.

Acceptable because: Zero ops overhead, trivial backup, perfect for a live demo and freeze.

With more time: Move to PostgreSQL (or similar) + Redis adapter for Socket.io.
4. No WhatsApp / SMS notifications yet
What: All updates stay inside the app.

Acceptable because: The core problem (no shared record + no status) is solved first. External messaging is additive.

With more time: Integrate a local SMS / WhatsApp Business API provider for status alerts.
Project Structure
textrelfast/
├── public/
│   └── index.html          # Full SPA (all roles)
├── db.js                   # JSON store + seed data
├── server.js               # Express + Socket.io API
├── seed.js                 # Thin wrapper that calls db.seed()
├── package.json
└── README.md

API Overview
MethodPathRolePurposePOST/api/login—Login, returns JWTGET/api/deliveriesanyList deliveries (scoped by role)POST/api/deliveriesretailerCreate request
POST/api/deliveries/:id/assigndispatcherAssign rider
POST/api/deliveries/:id/statusriderAdvance status
GET/api/deliveries/:id/qranyGenerate QR code
POST/api/deliveries/confirm-scan

Roadmap (next)

Next 2 weeks: SMS/WhatsApp status alerts, “suggest rider” button
Month 1–2: Rider mobile PWA + GPS, live map, photo proof of delivery
Quarter: Multi-store support, PostgreSQL + Redis, auto-dispatch rules