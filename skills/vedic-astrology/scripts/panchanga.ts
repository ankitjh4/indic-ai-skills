#!/usr/bin/env bun

/**
 * Generate Panchanga (Vedic Almanac)
 * 
 * Five limbs: Tithi, Nakshatra, Yoga, Karana, Vaara
 */

import { execSync } from "child_process";

interface Args {
  date?: string;
  lat: number;
  lon: number;
  tz: number;
  place?: string;
  startDate?: string;
  endDate?: string;
  format?: "json" | "table";
}

function parseArgs(): Args {
  const args = process.argv.slice(2);
  const parsed: any = { format: "table" };

  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, "").replace(/-([a-z])/g, (_, c) => c.toUpperCase());
    const value = args[i + 1];
    
    if (["lat", "lon", "tz"].includes(key)) {
      parsed[key] = parseFloat(value);
    } else {
      parsed[key] = value;
    }
  }

  if (!parsed.lat || !parsed.lon || parsed.tz === undefined) {
    console.log("Usage: panchanga.ts [options]");
    console.log("\nRequired:");
    console.log("  --lat LATITUDE           Latitude (decimal)");
    console.log("  --lon LONGITUDE          Longitude (decimal)");
    console.log("  --tz TIMEZONE            Timezone offset from UTC");
    console.log("\nOptional:");
    console.log("  --date YYYY-MM-DD        Specific date (default: today)");
    console.log("  --place PLACE            Location name");
    console.log("  --start-date YYYY-MM-DD  Start date for range");
    console.log("  --end-date YYYY-MM-DD    End date for range");
    console.log("  --format json|table      Output format (default: table)");
    console.log("\nExample:");
    console.log("  panchanga.ts --lat 28.6139 --lon 77.2090 --tz 5.5 --place Delhi");
    console.log("  panchanga.ts --start-date 2024-04-01 --end-date 2024-04-30 \\");
    console.log("    --lat 12.9716 --lon 77.5946 --tz 5.5");
    process.exit(1);
  }

  return parsed as Args;
}

function getPanchanga(args: Args) {
  const pythonScript = `
import json
from datetime import datetime, timedelta
from jyotishganit import calculate_birth_chart

def get_panchanga_for_date(date_str, lat, lon, tz, place=""):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    # Use noon for panchanga calculation
    dt = dt.replace(hour=12, minute=0, second=0)
    
    chart = calculate_birth_chart(
        birth_date=dt,
        latitude=lat,
        longitude=lon,
        timezone_offset=tz,
        location_name=place
    )
    
    p = chart.panchanga
    return {
        "date": date_str,
        "vaara": p.vaara,
        "tithi": p.tithi,
        "nakshatra": p.nakshatra,
        "yoga": p.yoga,
        "karana": p.karana,
        "sunrise": getattr(p, "sunrise", "N/A"),
        "sunset": getattr(p, "sunset", "N/A"),
        "moonrise": getattr(p, "moonrise", "N/A"),
        "moonset": getattr(p, "moonset", "N/A")
    }

${args.startDate && args.endDate ? `
# Range mode
start = datetime.strptime("${args.startDate}", "%Y-%m-%d")
end = datetime.strptime("${args.endDate}", "%Y-%m-%d")
results = []

current = start
while current <= end:
    date_str = current.strftime("%Y-%m-%d")
    results.append(get_panchanga_for_date(date_str, ${args.lat}, ${args.lon}, ${args.tz}, "${args.place || ""}"))
    current += timedelta(days=1)

print(json.dumps(results, indent=2))
` : `
# Single date mode
date_str = "${args.date || datetime.now().strftime("%Y-%m-%d")}"
result = get_panchanga_for_date(date_str, ${args.lat}, ${args.lon}, ${args.tz}, "${args.place || ""}")
print(json.dumps(result, indent=2))
`}
`;

  try {
    const output = execSync(`python3 -c '${pythonScript.replace(/'/g, "'\\''")}'`, {
      encoding: "utf-8"
    });
    
    const data = JSON.parse(output);
    
    if (args.format === "json") {
      console.log(JSON.stringify(data, null, 2));
    } else {
      displayTable(Array.isArray(data) ? data : [data]);
    }
  } catch (error: any) {
    console.error("❌ Error generating Panchanga:");
    console.error(error.stderr || error.message);
    process.exit(1);
  }
}

function displayTable(panchangas: any[]) {
  console.log("\n📅 Panchanga (Vedic Almanac)\n");
  console.log("═".repeat(100));
  console.log(
    "Date       ".padEnd(12) +
    "Vaara     ".padEnd(11) +
    "Tithi           ".padEnd(17) +
    "Nakshatra      ".padEnd(16) +
    "Yoga           ".padEnd(16) +
    "Karana"
  );
  console.log("─".repeat(100));
  
  for (const p of panchangas) {
    console.log(
      p.date.padEnd(12) +
      p.vaara.padEnd(11) +
      p.tithi.padEnd(17) +
      p.nakshatra.padEnd(16) +
      p.yoga.padEnd(16) +
      p.karana
    );
  }
  
  console.log("═".repeat(100));
  
  if (panchangas.length === 1) {
    const p = panchangas[0];
    console.log("\n🌅 Sun & Moon Timings:");
    console.log(`   Sunrise:  ${p.sunrise}`);
    console.log(`   Sunset:   ${p.sunset}`);
    console.log(`   Moonrise: ${p.moonrise}`);
    console.log(`   Moonset:  ${p.moonset}`);
  }
  
  console.log("\n📖 Panchanga Components:");
  console.log("   Vaara:     Weekday (7 days)");
  console.log("   Tithi:     Lunar day (30 tithis)");
  console.log("   Nakshatra: Moon's constellation (27 nakshatras)");
  console.log("   Yoga:      Sun-Moon combination (27 yogas)");
  console.log("   Karana:    Half of Tithi (11 karanas)");
  console.log();
}

function main() {
  console.log("🌙 Vedic Panchanga Calculator\n");
  
  const args = parseArgs();
  
  console.log("⚙️  Location:");
  console.log(`   Coordinates: ${args.lat}°N, ${args.lon}°E`);
  console.log(`   Timezone: UTC${args.tz > 0 ? "+" : ""}${args.tz}`);
  if (args.place) console.log(`   Place: ${args.place}`);
  
  if (args.startDate && args.endDate) {
    console.log(`\n📆 Date Range: ${args.startDate} to ${args.endDate}`);
  } else {
    console.log(`\n📆 Date: ${args.date || "Today"}`);
  }
  
  getPanchanga(args);
}

main();
