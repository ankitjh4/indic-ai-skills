---
name: rapido
description: Complete Rapido ride-booking API integration. Book bikes/autos, get fare estimates, track rides, check wallet balance, and manage orders. Reverse-engineered from Rapido PWA with full authentication flow.
compatibility: Created for Zo Computer
metadata:
  author: buckbuckbot.zo.computer
  category: transport
  tags: rapido, rides, booking, india, bikes, autos

---

⚠️ **CURRENT STATUS: NOT WORKING**

This skill is currently **non-functional** as of March 2026. The Rapido API has changed to use a complex encoding scheme (JSON array → ASCII → protobuf binary) for responses, making it impossible to decode fare estimates and booking responses without the proprietary protobuf schema.

**What works:**
- ✅ Location search (autocomplete)
- ✅ Geocoding (place ID to coordinates)

**What doesn't work:**
- ❌ Fare estimates (returns encoded binary)
- ❌ Ride booking (requires authentication)
- ❌ Wallet balance (requires authentication)
- ❌ Live tracking (requires authentication)

The skill code is preserved for reference and educational purposes, but it cannot successfully book rides at this time. A new authenticated HAR capture would be needed to reverse-engineer the current encoding scheme.

---

# Rapido Ride Booking Skill

Complete API integration for Rapido - India's largest bike taxi service. Book bikes and autos, get fare estimates, track rides in real-time, and manage your wallet.

## Quick Start

```bash
# Install dependencies
cd /home/workspace/Skills/rapido/scripts && bun init -y && bun add axios

# Authenticate
bun /home/workspace/Skills/rapido/scripts/rapido.ts auth --mobile "9876543210"
# Enter OTP when prompted

# Get fare estimate
bun /home/workspace/Skills/rapido/scripts/rapido.ts fare-estimate \
  --from-lat "13.0401" --from-lng "77.6635" \
  --to-lat "12.9756" --to-lng "77.6027"

# Book a ride
bun /home/workspace/Skills/rapido/scripts/rapido.ts book \
  --from-lat "13.0401" --from-lng "77.6635" --from-name "Horamavu" \
  --to-lat "12.9756" --to-lng "77.6027" --to-name "Church Street"

# Track ride
bun /home/workspace/Skills/rapido/scripts/rapido.ts track --order-id "ORDER_ID"

# Check wallet
bun /home/workspace/Skills/rapido/scripts/rapido.ts wallet

# Cancel ride
bun /home/workspace/Skills/rapido/scripts/rapido.ts cancel --order-id "ORDER_ID"
```

## API Endpoints Discovered

### Authentication
- **POST** `/pwa/api/auth/generateOtp` - Generate OTP for mobile number
- **POST** `/pwa/api/auth/verifyOtp` - Verify OTP and get auth token

### Location & Services
- **POST** `/pwa/api/location/services` - Get available services (bike/auto) at location
- **POST** `/pwa/api/unup/location/services` - Unauthenticated service availability
- **POST** `/pwa/api/unup/autocomplete/location` - Autocomplete location search
- **POST** `/pwa/api/unup/location/geocode/placeId` - Geocode place ID to lat/lng

### Pricing & Estimates
- **POST** `/pwa/api/pricing/getFareEstimate` - Get detailed fare estimates for trip
- **POST** `/pwa/api/unup/scc/fareEstimate` - SEO-optimized fare estimate
- **POST** `/pwa/api/location/eta/recursive` - Get ETA and available riders (called repeatedly)

### Booking & Orders
- **POST** `/pwa/api/order/book` - Book a ride
- **POST** `/pwa/api/order/cancel` - Cancel an order
- **POST** `/pwa/api/location/riderEta` - Get rider ETA and live location

### Wallet & Payment
- **POST** `/pwa/api/wallet/balance` - Get wallet balance across all payment methods

### User & Status
- **POST** `/pwa/api/user/customer/status` - Get user status and emergency number
- **GET** `/pwa/api/captain/rating/{captainId}` - Get captain rating
- **GET** `/pwa/api/appconfig` - Get app configuration

### Analytics
- **POST** `/pwa/api/event` - Track authenticated events
- **POST** `/pwa/api/unup/event` - Track unauthenticated events

## Authentication Flow

1. **Generate OTP**:
```json
POST /pwa/api/auth/generateOtp
{
  "mobile": "8917385221",
  "hash": "1773048641486:af0bceda95d07d787df9f6a4d35c5c6842018e51d963b19d343644107882937f",
  "recaptchaToken": "..."
}
```

2. **Verify OTP**:
```json
POST /pwa/api/auth/verifyOtp
{
  "mobileNumber": "8917385221",
  "otp": "766928"
}

Response:
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userId": "5b4c589184f0907d4cc4d6cf"
  }
}
```

3. **Use Token**: Add `x-consumer-username: {userId}:` header to all authenticated requests

## Key Request/Response Structures

### Fare Estimate Request
```json
{
  "pickupLocation": {
    "lat": 13.0401171,
    "lng": 77.66346709999999,
    "displayName": "Anutham Eastside Apartment...",
    "address": "Anutham Eastside Apartment, 3rd Cross..."
  },
  "dropLocation": {
    "lat": 12.9756453,
    "lng": 77.60267999999999,
    "displayName": "Church Street Social...",
    "address": "46/1, Church St..."
  }
}
```

### Fare Estimate Response
```json
{
  "data": {
    "requestId": "69ae935042318f43f16b0c18",
    "timeInMts": "44.42",
    "quotes": [
      {
        "serviceId": "57370b61a6855d70057417d1",
        "serviceName": "Rapido Bike",
        "fare": 115,
        "distance": "9.5",
        "duration": "25"
      }
    ]
  }
}
```

### Book Ride Request
```json
{
  "pickupLocation": { ... },
  "dropLocation": { ... },
  "serviceDetailId": "5c53562fceb6fc9241980547",
  "paymentMethod": "cod",
  "userId": "5b4c589184f0907d4cc4d6cf"
}
```

### Book Ride Response
```json
{
  "data": {
    "orderId": "69ae93667c2f2824d10ba700",
    "nudgeConfig": [...],
    "status": "dispatch"
  }
}
```

### Rider ETA Request
```json
{
  "locations": [
    { "lat": 13.0401171, "lng": 77.66346709999999 }
  ],
  "orderId": "69ae93667c2f2824d10ba700",
  "serviceDetailId": "5c53562fceb6fc9241980547",
  "userId": "5b4c589184f0907d4cc4d6cf",
  "riderId": "632fda99e143e10b20817a23"
}
```

### Rider ETA Response
```json
{
  "data": {
    "etaInMinutes": 4,
    "polyline": "irqnA}e_yM]qE\\cEmHa@",
    "captain": {
      "status": "6",
      "location": {
        "lat": 13.038666686154096,
        "lng": 77.66126990318298
      }
    }
  }
}
```

## Service IDs

### Vehicle Types
- **Bike**: `57370b61a6855d70057417d1`
- **Auto**: (check `/location/services` response)
- **Cab**: (check `/location/services` response)

### Payment Methods
- **Cash**: `cod`
- **Wallet**: `rapido_wallet`
- **UPI**: `upi`
- **Card**: `card`

## Headers Required

### Authenticated Requests
```
x-consumer-username: {userId}:
Content-Type: application/json
```

### Unauthenticated Requests
```
Content-Type: application/json
```

## Rate Limiting

The `/location/eta/recursive` endpoint is called **138 times** during a typical session, suggesting:
- Polling every 2-3 seconds during ride dispatch
- No apparent rate limiting
- Use WebSocket alternative if available

## Error Handling

### Common Errors
```json
{
  "info": {
    "status": "error",
    "message": "No riders available"
  }
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad request (invalid parameters)
- `401` - Unauthorized (invalid/expired token)
- `404` - Not found (invalid order ID)
- `500` - Server error

## Location Search

### Autocomplete
```bash
POST /pwa/api/unup/autocomplete/location
{
  "searchWord": "Horamavu"
}

Response:
{
  "data": [
    {
      "placeId": "ChIJ99zGooERrjsRzoxiOwCEUhQ",
      "description": "Horamavu, Bengaluru...",
      "name": "Horamavu"
    }
  ]
}
```

### Geocode Place ID
```bash
POST /pwa/api/unup/location/geocode/placeId
{
  "placeId": "ChIJ99zGooERrjsRzoxiOwCEUhQ"
}

Response:
{
  "data": {
    "lat": 13.0401171,
    "lng": 77.66346709999999,
    "address": "Horamavu, Bengaluru..."
  }
}
```

## Wallet Balance

```bash
POST /pwa/api/wallet/balance
{
  "channelHost": "browser"
}

Response:
{
  "data": {
    "wallets": [
      {
        "type": "rapido",
        "userId": "5b4c589184f0907d4cc4d6cf",
        "phoneNumber": "8917385221",
        "balance": 77.61,
        "rapidoWalletBalance": 77.61
      }
    ]
  }
}
```

## Captain Rating

```bash
GET /pwa/api/captain/rating/632fda99e143e10b20817a23

Response:
{
  "data": 4.7
}
```

## User Status

```bash
POST /pwa/api/user/customer/status
{
  "lat": 13.0401171,
  "lng": 77.66346709999999,
  "userId": "5b4c589184f0907d4cc4d6cf"
}

Response:
{
  "data": {
    "emergency_number": "07760520424"
  }
}
```

## App Configuration

```bash
GET /pwa/api/appconfig

Response:
{
  "homeScreenServices": {
    "data": [
      {
        "displayName": "Bike",
        "imageUrl": "https://..."
      },
      {
        "displayName": "Auto",
        "imageUrl": "https://..."
      }
    ]
  },
  "sosNumber": {
    "data": "01171768112"
  }
}
```

## Base URL

```
https://m.rapido.bike/pwa/api
```

## SDK Integration

See `scripts/rapido.ts` for a complete TypeScript SDK with:
- Authentication flow
- Fare estimation
- Ride booking
- Real-time tracking
- Order cancellation
- Wallet management

## Use Cases

### 1. Automated Ride Booking
```typescript
// Book a ride from current location to office
const fare = await rapido.getFareEstimate(currentLat, currentLng, officeLat, officeLng);
if (fare.quotes[0].fare < 150) {
  const order = await rapido.bookRide(pickup, drop, 'bike', 'cod');
  console.log(`Ride booked! Order ID: ${order.orderId}`);
}
```

### 2. Fare Comparison
```typescript
// Compare fares across different times
const morningFare = await rapido.getFareEstimate(...);
const eveningFare = await rapido.getFareEstimate(...);
console.log(`Save ₹${eveningFare - morningFare} by traveling in evening`);
```

### 3. Wallet Monitoring
```typescript
// Track wallet balance
const balance = await rapido.getWalletBalance();
if (balance < 100) {
  console.log('Wallet balance low, please recharge');
}
```

### 4. Ride History Analytics
```typescript
// Track all rides and analyze spending
const rides = await rapido.getRideHistory();
const totalSpent = rides.reduce((sum, ride) => sum + ride.fare, 0);
console.log(`Total spent on Rapido: ₹${totalSpent}`);
```

## Security Notes

1. **Token Storage**: Store auth token securely in environment variables
2. **User ID Format**: `{userId}:` (note the colon at the end)
3. **reCAPTCHA**: Required for OTP generation (can be bypassed in automation)
4. **Hash Generation**: See `generateHash()` function in SDK

## Limitations

1. **No Public API**: This is reverse-engineered from PWA
2. **Token Expiry**: Tokens expire after ~30 days
3. **Device ID**: Optional but recommended for tracking
4. **Location Accuracy**: Uses Google Maps geocoding

## References

- **PWA URL**: https://m.rapido.bike
- **API Base**: https://m.rapido.bike/pwa/api
- **Support**: 01171768112
- **Emergency**: 07760520424

## Ethical Use

This skill is for:
- Personal automation
- Research and learning
- Building complementary services

Do NOT use for:
- Spam or abuse
- Violating Rapido's terms of service
- Commercial scraping without permission

## Contributing

Found more endpoints? Improved the SDK? Submit improvements:
1. Update `scripts/rapido.ts`
2. Document new endpoints in this file
3. Add usage examples
4. Test thoroughly

## Support

For issues with this skill:
1. Check your auth token is valid
2. Verify mobile number is registered with Rapido
3. Ensure location coordinates are accurate
4. Check network connectivity

---

**Reverse-engineered from Rapido PWA on 2026-03-09**  
*Jai Hind! 🇮🇳*
