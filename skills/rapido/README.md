# Rapido Skill

⚠️ **CURRENT STATUS: NOT WORKING (March 2026)**

This skill is currently **non-functional**. The Rapido API has changed to use a complex encoding scheme (JSON array → ASCII → protobuf binary) for responses, making it impossible to decode fare estimates and booking responses without the proprietary protobuf schema.

**What works:**
- ✅ Location search (autocomplete)
- ✅ Geocoding (place ID to coordinates)

**What doesn't work:**
- ❌ Fare estimates (returns encoded binary)
- ❌ Ride booking (requires authentication)
- ❌ Wallet balance (requires authentication)
- ❌ Live tracking (requires authentication)

---

## Quick Start

### Search Location
```bash
bun scripts/rapido.ts search --query "Horamavu Bangalore"
```

### Get Coordinates
```bash
bun scripts/rapido.ts geocode --place-id "ChIJ99zGooERrjsRzoxiOwCEUhQ"
```

---

## About This Skill

This skill was reverse-engineered from the Rapido PWA but the API has since changed. The code is preserved for educational purposes and in case someone can figure out the new encoding scheme with a fresh authenticated HAR capture.

See `SKILL.md` for full documentation of discovered endpoints.
