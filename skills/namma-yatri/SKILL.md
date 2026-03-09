---
name: namma-yatri
description: Build, contribute to, and deploy Namma Yatri — India's open-source, zero-commission ride-hailing platform. Covers Haskell backend, PureScript frontend, Rust services, Beckn/ONDC mobility protocol, Nix-based dev setup, and API integration. Use when working with Namma Yatri, ride-hailing, Beckn protocol, or open mobility.
metadata:
  author: ankitjh4
  category: transport
  tags: namma-yatri, ride-hailing, open-source, beckn, ondc, mobility, haskell, purescript, rust, juspay
---

# Namma Yatri

Open-source, zero-commission, driver-centric ride-hailing platform built by [JusPay](https://juspay.in). Powers 71M+ rides across Bengaluru, Chennai, Kolkata, Delhi, Hyderabad, Kochi, and Mysuru.

- **Zero commission** — drivers keep the full fare
- **No surge pricing** — transparent, stable fares
- **Open source** — AGPL-3.0 licensed
- **Beckn/ONDC native** — built on India's open mobility protocol

**Repository**: https://github.com/nammayatri/nammayatri
**Open Data Dashboard**: https://nammayatri.in/open/
**Community**: https://github.com/orgs/nammayatri/discussions

## Architecture

Namma Yatri follows the [Beckn Protocol](https://developers.becknprotocol.io/) for open, interoperable mobility:

```
┌─────────────┐    Beckn     ┌──────────────┐    Beckn     ┌─────────────┐
│  Rider App  │◄────────────►│    Beckn     │◄────────────►│ Driver App  │
│    (BAP)    │   search/    │   Gateway    │   on_search/ │    (BPP)    │
│             │   confirm    │              │   on_confirm │             │
└─────────────┘              └──────────────┘              └─────────────┘
       │                                                          │
       ▼                                                          ▼
┌─────────────┐                                          ┌──────────────┐
│   Rider     │                                          │   Provider   │
│  Dashboard  │                                          │  Dashboard   │
└─────────────┘                                          └──────────────┘
```

**Key Beckn concepts:**
- **BAP** (Beckn Application Platform) — consumer/rider side
- **BPP** (Beckn Provider Platform) — driver/provider side
- **Beckn Gateway** — routes requests between BAP and BPP
- **Registry** — service discovery and trust layer

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | **Haskell** | Core business logic, APIs, ride matching |
| Frontend | **PureScript** | Rider and driver mobile apps |
| Location tracking | **Rust** | Real-time GPS tracking service |
| Notifications | **Rust** | Push notifications via gRPC + Redis Streams |
| GTFS server | **Rust** | Public transit data |
| Build system | **Nix** | Reproducible builds and dev environments |
| Haskell build | **Cabal** | Package management and compilation |
| Configuration | **Dhall** | Type-safe config files |
| Database | **PostgreSQL** | Primary data store |
| Cache | **Redis** | Session/location caching |
| Messaging | **Kafka** | Event streaming between services |
| Routing | **OSRM** | Open-source route calculations |

## Project Structure (Monorepo)

```
nammayatri/
├── Backend/                         # Haskell backend (main codebase)
│   ├── rider-platform/
│   │   ├── rider-app/               # Rider-facing APIs (port 8013)
│   │   └── public-transport/        # Public transit integration
│   ├── provider-platform/
│   │   └── dynamic-offer-driver-app/
│   │       ├── Main/                # Driver-facing APIs (port 8016)
│   │       └── Allocator/           # Ride matching engine (port 9996)
│   ├── dashboard/
│   │   ├── rider-dashboard/         # Rider ops dashboard
│   │   └── provider-dashboard/      # Provider ops dashboard
│   ├── kafka-consumers/             # Async event processors
│   ├── mocks/                       # Mock third-party services
│   ├── dhall-configs/               # Dhall configuration files
│   └── load-test/                   # Load testing suite
├── Frontend/                        # PureScript frontend
│   ├── ui-customer/                 # Rider mobile app
│   └── ui-driver/                   # Driver mobile app
└── docs/                            # Documentation
```

### Related Repositories

| Repository | Language | Purpose |
|-----------|----------|---------|
| `nammayatri/shared-kernel` | Haskell | Shared types, utilities, and business logic |
| `nammayatri/location-tracking-service` | Rust | Real-time driver location tracking |
| `nammayatri/notification-service` | Rust | Push notification delivery |
| `nammayatri/beckn-gateway` | Haskell | Beckn protocol routing |
| `nammayatri/common` | Nix | Shared Nix configuration |

## Development Setup

### Prerequisites

- **Nix** package manager (with flakes enabled)
- **direnv** for automatic shell activation
- ~16GB RAM recommended

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/nammayatri/nammayatri.git
cd nammayatri

# Activate backend dev environment
ln -sf .envrc.backend .envrc
direnv allow

# Build all backend packages
cd Backend
cabal build all

# Run the full mobility stack (starts all services + DB/Redis/Kafka/OSRM)
, run-mobility-stack-dev
```

The `, ` prefix is a Nix-provided command runner. Run `, ` alone to see all available commands.

### Frontend Setup

```bash
# Enter frontend dev shell
nix develop .#frontend

# Rider app
cd Frontend/ui-customer
npm install && npm start

# Driver app
cd Frontend/ui-driver
npm install && npm start
```

Android builds require Android Studio, `google-services.json`, and `MAPS_API_KEY`.

### Useful Dev Commands

| Command | Purpose |
|---------|---------|
| `, run-mobility-stack-dev` | Start full stack via cabal (recommended) |
| `, run-mobility-stack-nix` | Start full stack via Nix build |
| `, ghcid lib/location-updates` | Fast compile feedback loop |
| `, run-pgadmin` | Start pgAdmin for DB inspection |
| `, run-monitoring` | Start Prometheus + Grafana |
| `, kill-svc-ports` | Kill all running services |
| `cabal test all` | Run test suite |

### Services & Ports

| Service | Port |
|---------|------|
| rider-app | 8013 |
| beckn-gateway | 8015 |
| dynamic-offer-driver-app | 8016 |
| mock-registry | 8020 |
| transporter-scheduler | 8053 |
| allocation-service | 9996 |

Swagger docs available at `http://localhost:<port>/swagger`.

## API Overview

### Rider APIs (BAP — port 8013)

Core rider-side flows following Beckn lifecycle:

| Endpoint Pattern | Purpose |
|-----------------|---------|
| `/search` | Search for available rides |
| `/select` | Select a ride option |
| `/init` | Initialize booking (address, payment) |
| `/confirm` | Confirm and place the booking |
| `/status` | Check ride status |
| `/track` | Track driver location |
| `/cancel` | Cancel a ride |
| `/rating` | Rate the driver |

### Driver APIs (BPP — port 8016)

Driver-side operations:

| Endpoint Pattern | Purpose |
|-----------------|---------|
| `/on_search` | Receive ride requests |
| `/on_select` | Respond to ride selection |
| `/on_init` | Confirm driver availability |
| `/on_confirm` | Accept ride booking |
| `/on_status` | Send ride status updates |
| `/on_track` | Send location updates |
| `/on_cancel` | Handle cancellation |

### Allocator (port 9996)

The ride matching engine that connects riders with nearby drivers. Handles:
- Proximity-based driver search
- Dynamic offer management (drivers quote their price)
- Ride assignment optimization

### Dashboard APIs

Ops dashboards for fleet management, analytics, and administration:
- **Rider dashboard** — user management, ride history, support
- **Provider dashboard** — driver management, earnings, compliance

## Contributing

### Commit Convention

```
<sub-project>/<type>: #<issue-number> <short summary>
```

**Sub-projects**: `backend`, `frontend`

**Types**: `feat`, `fix`, `chore`, `ci`, `docs`, `perf`, `refactor`, `test`

**Examples**:
```
backend/feat: #341 Driver onboarding flow
frontend/fix: #322 Font size in ride request popup
backend/refactor: #400 Extract payment module
```

### Branch Naming

```
<sub-project>/<type>/<issue-number><short-description>
```

**Examples**:
```
backend/feat/GH-341/driver-onboarding
frontend/fix/GH-322/font-size
```

### Contribution Flow

1. Find or create an issue on [GitHub Issues](https://github.com/nammayatri/nammayatri/issues)
2. Fork and create a branch following naming conventions
3. Make changes with atomic commits
4. Ensure `cabal build all` and `cabal test all` pass
5. Submit a PR with clear description
6. PRs are typically squash-merged

### Code Style

- Haskell: follow existing patterns in the codebase; HLS (Haskell Language Server) configured via Nix
- PureScript: standard PS conventions
- Use `direnv` + VSCode with recommended extensions for best IDE experience

## Key Concepts

### Dynamic Offer Model

Unlike fixed-price platforms, Namma Yatri uses a **dynamic offer** model:
1. Rider searches for a ride
2. Nearby drivers receive the request
3. Each driver quotes their own price
4. Rider selects from available offers

### services-flake

External services (PostgreSQL, Redis, Kafka, OSRM) are managed via [services-flake](https://github.com/juspay/services-flake), a Nix-based alternative to docker-compose. Services start automatically with `, run-mobility-stack-dev`.

### Shared Kernel

Common types, utilities, and business logic live in the [shared-kernel](https://github.com/nammayatri/shared-kernel) repo. To develop against a local checkout:

```nix
# In flake.nix, change:
inputs.shared-kernel.url = "path:/path/to/local/shared-kernel";
```

Then run `nix flake lock --update-input shared-kernel`.

## Troubleshooting

| Issue | Solution |
|-------|---------|
| Segfault during linking | `ulimit -s 9999` (stack size limit) |
| Services won't stop after Ctrl-C | `, kill-svc-ports` |
| VSCode direnv error | `unset NIX_STORE && direnv reload` |
| Slow nix build | Check Nix binary cache is configured |
| Slow cabal build | Increase `jobs` in `cabal.project` or uncomment dev flags |
| Find Nix dependency source | `nix run github:nix-community/nix-melt` |

## References

- **Website**: https://nammayatri.in
- **GitHub Org**: https://github.com/nammayatri
- **Open Data**: https://nammayatri.in/open/
- **Beckn Protocol**: https://developers.becknprotocol.io/
- **ONDC**: https://ondc.org
- **Founder's Vision (video)**: https://youtube.com/watch?v=NnyoxiiZLZg
- **JusPay**: https://juspay.in
- **services-flake**: https://github.com/juspay/services-flake
- **Contributing Guide**: https://github.com/nammayatri/nammayatri/blob/main/docs/CONTRIBUTING.md

---

**Jai Hind! 🇮🇳**
