#!/usr/bin/env bun

/**
 * Rapido API SDK
 * Complete integration for booking bikes and autos in India
 */

import { readFileSync, writeFileSync, existsSync } from "fs";
import { createHash } from "crypto";

const BASE_URL = "https://m.rapido.bike/pwa/api";
const CONFIG_FILE = `${process.env.HOME}/.rapido-config.json`;

interface Location {
  lat: number;
  lng: number;
  displayName: string;
  address: string;
}

interface Config {
  userId?: string;
  token?: string;
  mobile?: string;
}

class RapidoAPI {
  private config: Config = {};

  constructor() {
    this.loadConfig();
  }

  private loadConfig() {
    if (existsSync(CONFIG_FILE)) {
      this.config = JSON.parse(readFileSync(CONFIG_FILE, "utf-8"));
    }
  }

  private saveConfig() {
    writeFileSync(CONFIG_FILE, JSON.stringify(this.config, null, 2));
  }

  private async request(
    endpoint: string,
    method: string = "GET",
    body?: any,
    authenticated: boolean = false
  ): Promise<any> {
    const url = `${BASE_URL}${endpoint}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "User-Agent": "Mozilla/5.0 (Linux; Android 10) Rapido PWA",
      Origin: "https://m.rapido.bike",
      Referer: "https://m.rapido.bike/",
    };

    if (authenticated && this.config.token) {
      headers["Authorization"] = `Bearer ${this.config.token}`;
      headers["x-consumer-username"] = `${this.config.userId}:`;
    }

    const response = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMsg = `Request failed with status ${response.status}`;
      try {
        const errorJson = JSON.parse(errorText);
        errorMsg = errorJson.message || errorJson.error || errorMsg;
      } catch {
        errorMsg = errorText || errorMsg;
      }
      throw new Error(errorMsg);
    }

    return response.json();
  }

  private generateHash(mobile: string): string {
    const timestamp = Date.now();
    const secret = "rapido_secret_key"; // This may need reverse engineering
    const hashString = `${timestamp}:${mobile}:${secret}`;
    const hash = createHash("sha256").update(hashString).digest("hex");
    return `${timestamp}:${hash}`;
  }

  async generateOtp(mobile: string) {
    console.log(`📱 Generating OTP for ${mobile}...`);

    const body = {
      mobile,
      hash: this.generateHash(mobile),
      recaptchaToken: "", // Optional for testing
    };

    const result = await this.request("/auth/generateOtp", "POST", body, false);
    this.config.mobile = mobile;
    this.saveConfig();

    console.log("✅ OTP sent successfully!");
    return result;
  }

  async verifyOtp(otp: string) {
    if (!this.config.mobile) {
      throw new Error("No mobile number found. Generate OTP first.");
    }

    console.log(`🔐 Verifying OTP...`);

    const body = {
      mobileNumber: this.config.mobile,
      otp,
    };

    const result = await this.request("/auth/verifyOtp", "POST", body, false);

    this.config.token = result.data.token;
    this.config.userId = result.data.userId || this.extractUserIdFromToken(result.data.token);

    this.saveConfig();

    console.log("✅ Authentication successful!");
    console.log(`   User ID: ${this.config.userId}`);
    return result;
  }

  private extractUserIdFromToken(token: string): string {
    try {
      const payload = token.split(".")[1];
      const decoded = JSON.parse(Buffer.from(payload, "base64").toString());
      return decoded._id || decoded.userId;
    } catch {
      throw new Error("Could not extract user ID from token");
    }
  }

  async autocompleteLocation(searchWord: string) {
    const body = { searchWord };
    const result = await this.request(
      "/unup/autocomplete/location",
      "POST",
      body,
      false
    );
    return result.data;
  }

  async geocodePlaceId(placeId: string) {
    const body = { placeId };
    const result = await this.request(
      "/unup/location/geocode/placeId",
      "POST",
      body,
      false
    );
    return result.data;
  }

  async getServices(lat: number, lng: number) {
    const body = { lat, lng };
    const result = await this.request("/location/services", "POST", body);
    return result.data.data;
  }

  async getUnAuthFareEstimate(
    pickupLocation: Location,
    dropLocation: Location
  ) {
    console.log("💰 Getting fare estimate (unauthenticated)...");

    const body = {
      pickupLocation,
      dropLocation,
      deviceId: "seo-route-pages"
    };

    const result = await this.request("/unup/scc/fareEstimate", "POST", body, false);
    
    console.log(`\n📊 Fare Estimates:`);
    if (result.data && result.data.rides) {
      for (const ride of result.data.rides) {
        console.log(`   ${ride.ride_name}: ₹${ride.fare.min_fare} - ₹${ride.fare.max_fare}`);
        console.log(`      Distance: ${ride.distance_text}, ETA: ${ride.eta_text}`);
      }
    }

    return result.data;
  }

  async getFareEstimate(
    pickupLocation: Location,
    dropLocation: Location
  ) {
    console.log("💰 Getting fare estimate...");

    const body = {
      pickupLocation,
      dropLocation,
    };

    const result = await this.request("/pricing/getFareEstimate", "POST", body);
    
    console.log(`\n📊 Fare Estimates:`);
    for (const quote of result.data.quotes) {
      console.log(`   ${quote.serviceName}: ₹${quote.fare} (${quote.distance}km, ${quote.duration}min)`);
    }

    return result.data;
  }

  async bookRide(
    pickupLocation: Location,
    dropLocation: Location,
    serviceDetailId: string,
    paymentMethod: string = "cod"
  ) {
    console.log("🚴 Booking ride...");

    const body = {
      pickupLocation,
      dropLocation,
      serviceDetailId,
      paymentMethod,
      userId: this.config.userId,
    };

    const result = await this.request("/order/book", "POST", body);
    
    console.log(`✅ Ride booked successfully!`);
    console.log(`   Order ID: ${result.data.orderId}`);
    console.log(`   Status: ${result.data.status}`);

    return result.data;
  }

  async getRiderEta(
    orderId: string,
    lat: number,
    lng: number,
    serviceDetailId: string,
    riderId: string
  ) {
    const body = {
      locations: [{ lat, lng }],
      orderId,
      serviceDetailId,
      userId: this.config.userId,
      riderId,
    };

    const result = await this.request("/location/riderEta", "POST", body);
    return result.data;
  }

  async trackRide(orderId: string) {
    // This would need the rider ID and other details from the booking
    // For now, return a placeholder
    console.log(`📍 Tracking order ${orderId}...`);
    console.log("   (Tracking requires rider ID from booking response)");
    return { orderId };
  }

  async cancelRide(orderId: string, reason: string = "Others") {
    console.log(`❌ Cancelling order ${orderId}...`);

    const body = {
      userId: this.config.userId,
      cancelReason: reason,
      locationDetails: {
        lat: 0,
        lng: 0,
        displayName: "0,0",
        address: "0,0",
      },
      orderId,
      otherReason: "User cancellation",
    };

    const result = await this.request("/order/cancel", "POST", body);
    
    console.log("✅ Ride cancelled successfully");
    return result.data;
  }

  async getWalletBalance() {
    console.log("💳 Fetching wallet balance...");

    const body = { channelHost: "browser" };
    const result = await this.request("/wallet/balance", "POST", body);

    console.log(`\n💰 Wallet Balances:`);
    for (const wallet of result.data.wallets) {
      console.log(`   ${wallet.type}: ₹${wallet.balance}`);
    }

    return result.data.wallets;
  }

  async getCaptainRating(captainId: string) {
    const result = await this.request(`/captain/rating/${captainId}`, "GET");
    return result.data;
  }

  async getUserStatus(lat: number, lng: number) {
    const body = {
      lat,
      lng,
      userId: this.config.userId,
    };

    const result = await this.request("/user/customer/status", "POST", body);
    return result.data;
  }

  async getAppConfig() {
    const result = await this.request("/appconfig", "GET");
    return result;
  }
}

// CLI Interface
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  const api = new RapidoAPI();

  try {
    switch (command) {
      case "auth": {
        const mobile = args[args.indexOf("--mobile") + 1];
        if (!mobile) {
          console.error("Usage: rapido.ts auth --mobile <number>");
          process.exit(1);
        }

        await api.generateOtp(mobile);
        console.log("\n📬 Enter OTP:");
        const otp = prompt("OTP: ");
        if (otp) {
          await api.verifyOtp(otp);
        }
        break;
      }

      case "search": {
        const query = args[args.indexOf("--query") + 1];
        if (!query) {
          console.error("Usage: rapido.ts search --query <location>");
          process.exit(1);
        }

        const results = await api.autocompleteLocation(query);
        console.log("\n📍 Search Results:");
        for (const result of results) {
          console.log(`   ${result.name} - ${result.description}`);
          console.log(`   Place ID: ${result.placeId}\n`);
        }
        break;
      }

      case "geocode": {
        const placeId = args[args.indexOf("--place-id") + 1];
        if (!placeId) {
          console.error("Usage: rapido.ts geocode --place-id <id>");
          process.exit(1);
        }

        const location = await api.geocodePlaceId(placeId);
        console.log("\n📍 Location:");
        console.log(`   Lat: ${location.lat}`);
        console.log(`   Lng: ${location.lng}`);
        console.log(`   Address: ${location.address}`);
        break;
      }

      case "fare-estimate": {
        const fromLat = parseFloat(args[args.indexOf("--from-lat") + 1]);
        const fromLng = parseFloat(args[args.indexOf("--from-lng") + 1]);
        const toLat = parseFloat(args[args.indexOf("--to-lat") + 1]);
        const toLng = parseFloat(args[args.indexOf("--to-lng") + 1]);

        if (!fromLat || !fromLng || !toLat || !toLng) {
          console.error(
            "Usage: rapido.ts fare-estimate --from-lat <lat> --from-lng <lng> --to-lat <lat> --to-lng <lng>"
          );
          process.exit(1);
        }

        const pickup: Location = {
          lat: fromLat,
          lng: fromLng,
          displayName: "Pickup",
          address: "Pickup Location",
        };

        const drop: Location = {
          lat: toLat,
          lng: toLng,
          displayName: "Drop",
          address: "Drop Location",
        };

        await api.getUnAuthFareEstimate(pickup, drop);
        break;
      }

      case "wallet": {
        await api.getWalletBalance();
        break;
      }

      case "services": {
        const lat = parseFloat(args[args.indexOf("--lat") + 1]);
        const lng = parseFloat(args[args.indexOf("--lng") + 1]);

        if (!lat || !lng) {
          console.error("Usage: rapido.ts services --lat <lat> --lng <lng>");
          process.exit(1);
        }

        const services = await api.getServices(lat, lng);
        console.log("\n🚗 Available Services:");
        for (const service of services) {
          console.log(`   ${service.displayName || service._id}`);
          console.log(`   ID: ${service._id}\n`);
        }
        break;
      }

      case "cancel": {
        const orderId = args[args.indexOf("--order-id") + 1];
        if (!orderId) {
          console.error("Usage: rapido.ts cancel --order-id <id>");
          process.exit(1);
        }

        await api.cancelRide(orderId);
        break;
      }

      case "config": {
        console.log("\n⚙️  Current Configuration:");
        console.log(JSON.stringify(api["config"], null, 2));
        break;
      }

      default:
        console.log(`
Rapido API CLI

Commands:
  auth --mobile <number>                       Authenticate with mobile
  search --query <location>                    Search for locations
  geocode --place-id <id>                      Get coordinates from place ID
  fare-estimate --from-lat <lat> --from-lng <lng> --to-lat <lat> --to-lng <lng>
  services --lat <lat> --lng <lng>            Get available services
  wallet                                        Check wallet balance
  cancel --order-id <id>                       Cancel a ride
  config                                        Show current configuration

Examples:
  bun rapido.ts auth --mobile "9876543210"
  bun rapido.ts search --query "Horamavu"
  bun rapido.ts fare-estimate --from-lat 13.04 --from-lng 77.66 --to-lat 12.97 --to-lng 77.60
  bun rapido.ts wallet
        `);
    }
  } catch (error: any) {
    console.error(`\n❌ Error: ${error.message}`);
    process.exit(1);
  }
}

main();
