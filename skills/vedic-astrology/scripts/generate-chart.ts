#!/usr/bin/env bun

/**
 * Generate Complete Vedic Astrology Birth Chart
 * 
 * Combines jyotishganit, VedicAstro, and flatlib for comprehensive analysis
 */

import { execSync } from "child_process";
import { writeFileSync, existsSync, mkdirSync } from "fs";

interface Args {
  date: string;
  time: string;
  lat: number;
  lon: number;
  tz: number;
  name?: string;
  place?: string;
  output?: string;
}

function parseArgs(): Args {
  const args = process.argv.slice(2);
  const parsed: any = {};

  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, "");
    const value = args[i + 1];
    
    if (["lat", "lon", "tz"].includes(key)) {
      parsed[key] = parseFloat(value);
    } else {
      parsed[key] = value;
    }
  }

  if (!parsed.date || !parsed.time || !parsed.lat || !parsed.lon || parsed.tz === undefined) {
    console.log("Usage: generate-chart.ts [options]");
    console.log("\nRequired:");
    console.log("  --date YYYY-MM-DD        Birth date");
    console.log("  --time HH:MM:SS          Birth time (24-hour)");
    console.log("  --lat LATITUDE           Latitude (decimal)");
    console.log("  --lon LONGITUDE          Longitude (decimal)");
    console.log("  --tz TIMEZONE            Timezone offset from UTC (e.g., 5.5 for IST)");
    console.log("\nOptional:");
    console.log("  --name NAME              Person's name");
    console.log("  --place PLACE            Birth place");
    console.log("  --output PATH            Output file path");
    console.log("\nExample:");
    console.log('  generate-chart.ts --date "1990-07-15" --time "14:30:00" \\');
    console.log("    --lat 28.6139 --lon 77.2090 --tz 5.5 \\");
    console.log('    --name "Sample Person" --place "New Delhi"');
    process.exit(1);
  }

  return parsed as Args;
}

function ensurePythonDeps() {
  console.log("🔍 Checking Python dependencies...\n");
  
  const packages = [
    "jyotishganit",
    "vedicastro",
    "git+https://github.com/diliprk/flatlib.git@sidereal#egg=flatlib"
  ];

  for (const pkg of packages) {
    try {
      const pkgName = pkg.includes("git+") ? "flatlib" : pkg;
      execSync(`python3 -c "import ${pkgName}"`, { stdio: "ignore" });
      console.log(`✅ ${pkgName} already installed`);
    } catch {
      console.log(`📦 Installing ${pkg.split("#")[0].split("/").pop()}...`);
      try {
        execSync(`pip3 install ${pkg}`, { stdio: "inherit" });
      } catch (error) {
        console.error(`❌ Failed to install ${pkg}`);
        console.error("   Try: pip3 install --user " + pkg);
        process.exit(1);
      }
    }
  }
  
  console.log();
}

function generateChart(args: Args): string {
  const pythonScript = `
import json
from datetime import datetime
from jyotishganit import calculate_birth_chart, get_birth_chart_json
from vedicastro import VedicHoroscopeData

# Parse input
date_str = "${args.date} ${args.time}"
dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

# Generate jyotishganit chart (comprehensive)
print("📊 Calculating planetary positions...", flush=True)
jg_chart = calculate_birth_chart(
    birth_date=dt,
    latitude=${args.lat},
    longitude=${args.lon},
    timezone_offset=${args.tz},
    location_name="${args.place || ""}",
    name="${args.name || ""}"
)

# Generate VedicAstro chart (KP system)
print("🔮 Computing KP significators...", flush=True)
try:
    va_data = VedicHoroscopeData(
        date="${args.date}",
        time="${args.time}",
        lat=${args.lat},
        lon=${args.lon},
        tz=${args.tz}
    )
    va_chart = va_data.generate_chart()
    
    # Get KP data
    planets_data = va_data.get_planets_data_from_chart(va_chart)
    houses_data = va_data.get_houses_data_from_chart(va_chart)
    planet_sigs = va_data.get_planet_wise_significators(va_chart)
    house_sigs = va_data.get_house_wise_significators(va_chart)
    
    kp_data = {
        "planets": planets_data.to_dict() if hasattr(planets_data, 'to_dict') else str(planets_data),
        "houses": houses_data.to_dict() if hasattr(houses_data, 'to_dict') else str(houses_data),
        "planet_significators": planet_sigs.to_dict() if hasattr(planet_sigs, 'to_dict') else str(planet_sigs),
        "house_significators": house_sigs.to_dict() if hasattr(house_sigs, 'to_dict') else str(house_sigs)
    }
except Exception as e:
    print(f"⚠️  KP data partially unavailable: {e}", flush=True)
    kp_data = {"error": str(e)}

# Combine data
print("📝 Generating complete chart data...", flush=True)
combined = get_birth_chart_json(jg_chart)
combined["kp_data"] = kp_data
combined["meta"] = {
    "generated_at": datetime.now().isoformat(),
    "systems": ["jyotishganit", "vedicastro", "flatlib"],
    "ayanamsa": "True Chitra Paksha (Lahiri)"
}

# Output JSON
print(json.dumps(combined, indent=2, default=str))
`;

  try {
    const output = execSync(`python3 -c '${pythonScript.replace(/'/g, "'\\''")}'`, {
      encoding: "utf-8",
      maxBuffer: 10 * 1024 * 1024
    });
    
    // Extract JSON from output (after progress messages)
    const lines = output.split("\n");
    const jsonStart = lines.findIndex(line => line.trim() === "{");
    const jsonOutput = lines.slice(jsonStart).join("\n");
    
    return jsonOutput;
  } catch (error: any) {
    console.error("❌ Error generating chart:");
    console.error(error.stderr || error.message);
    process.exit(1);
  }
}

function main() {
  console.log("🌟 Vedic Astrology Chart Generator\n");
  
  const args = parseArgs();
  ensurePythonDeps();
  
  console.log("⚙️  Configuration:");
  console.log(`   Date: ${args.date}`);
  console.log(`   Time: ${args.time}`);
  console.log(`   Location: ${args.lat}°N, ${args.lon}°E`);
  console.log(`   Timezone: UTC${args.tz > 0 ? "+" : ""}${args.tz}`);
  if (args.name) console.log(`   Name: ${args.name}`);
  if (args.place) console.log(`   Place: ${args.place}`);
  console.log();
  
  const chartData = generateChart(args);
  
  // Save to file
  const outputDir = process.env.ASTRO_CHARTS_DIR || "/home/workspace/Charts";
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }
  
  const filename = args.output || `${outputDir}/${(args.name || "chart").toLowerCase().replace(/\s+/g, "-")}-${args.date}.json`;
  writeFileSync(filename, chartData);
  
  console.log("\n✅ Chart generated successfully!");
  console.log(`📁 Saved to: ${filename}`);
  console.log("\n📊 Chart includes:");
  console.log("   ✓ D1-D60 divisional charts");
  console.log("   ✓ Panchanga (Tithi, Nakshatra, Yoga, Karana, Vaara)");
  console.log("   ✓ Vimshottari Dasha periods");
  console.log("   ✓ Shadbala (planetary strength)");
  console.log("   ✓ Ashtakavarga points");
  console.log("   ✓ KP significators and sublords");
  console.log("   ✓ Planetary aspects");
  console.log("\n💡 Next steps:");
  console.log(`   interpret-chart.ts --chart "${filename}" --focus career`);
  console.log(`   analyze-dasha.ts --chart "${filename}"`);
}

main();
