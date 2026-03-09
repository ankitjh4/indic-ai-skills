# Namma Yatri

Open-source, zero-commission ride-hailing platform by [JusPay](https://juspay.in).

## Quick Start

```bash
# Clone
git clone https://github.com/nammayatri/nammayatri.git
cd nammayatri

# Backend dev environment (requires Nix + direnv)
ln -sf .envrc.backend .envrc && direnv allow

# Build and run
cd Backend
cabal build all
, run-mobility-stack-dev
```

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Haskell |
| Frontend | PureScript |
| Location / Notifications | Rust |
| Build | Nix + Cabal |
| Database | PostgreSQL |
| Cache | Redis |
| Messaging | Kafka |

## Key Ports

| Service | Port |
|---------|------|
| rider-app | 8013 |
| beckn-gateway | 8015 |
| dynamic-offer-driver-app | 8016 |
| allocation-service | 9996 |

## Links

- **Repo**: https://github.com/nammayatri/nammayatri
- **Website**: https://nammayatri.in
- **Open Data**: https://nammayatri.in/open/
- **Discussions**: https://github.com/orgs/nammayatri/discussions
