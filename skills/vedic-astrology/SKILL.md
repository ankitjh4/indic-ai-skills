---
name: vedic-astrology
description: Complete Vedic astrology chart generation and interpretation. Generate birth charts (D1-D60), calculate Panchanga, Shadbala, Vimshottari Dasha, Ashtakavarga, and provide interpretations using Krishnamurthi Paddhati (KP) system, classical Parashara principles, and traditional texts. Supports both natal and horary (Prasna) charts.
compatibility: Created for Zo Computer
metadata:
  author: buckbuckbot.zo.computer
  category: astrology
  tags: vedic, astrology, jyotish, kp, horoscope, birth-chart, panchanga
---

# Vedic Astrology Skill

Generate and interpret complete Vedic astrology birth charts using multiple systems including Krishnamurthi Paddhati (KP), classical Parashara principles, and traditional Vedic texts.

## Overview

This skill combines three powerful Python libraries for comprehensive Vedic astrology:

1. **flatlib** - Traditional astrology calculations with Swiss Ephemeris
2. **VedicAstro** - Krishnamurthi Paddhati (KP) system specialization  
3. **jyotishganit** - Professional grade Vedic calculations with NASA JPL ephemeris

All three libraries are integrated to provide:
- Complete birth chart generation (D1-D60 divisional charts)
- Panchanga (five limbs of time)
- Vimshottari Dasha periods
- Shadbala (six-fold planetary strength)
- Ashtakavarga point system
- KP system significators and sublords
- Horary (Prasna) chart generation
- Traditional interpretations from classical texts

## Installation

The scripts automatically install required libraries on first run:

```bash
# All dependencies auto-installed:
# - flatlib (from sidereal branch)
# - vedicastro  
# - jyotishganit
# - pyswisseph
# - skyfield
```

## Usage

### Generate Complete Birth Chart

```bash
# Basic natal chart
bun /home/workspace/Skills/vedic-astrology/scripts/generate-chart.ts \
  --date "1990-07-15" \
  --time "14:30:00" \
  --lat 28.6139 \
  --lon 77.2090 \
  --tz 5.5 \
  --name "Sample Person" \
  --place "New Delhi"

# Saves to: Charts/sample-person-chart.json
```

**Output includes:**
- All planetary positions (9 grahas)
- Ascendant and house cusps
- D1-D60 divisional charts
- Panchanga details
- Vimshottari Dasha periods
- Shadbala calculations
- Ashtakavarga points
- KP significators and sublords

### Horary (Prasna) Chart

```bash
# Question-based horary chart
bun /home/workspace/Skills/vedic-astrology/scripts/generate-horary.ts \
  --question "Will I get the job?" \
  --lat 19.0760 \
  --lon 72.8777 \
  --tz 5.5 \
  --place "Mumbai"

# Uses current time or specify:
bun /home/workspace/Skills/vedic-astrology/scripts/generate-horary.ts \
  --question "Should I invest in this business?" \
  --date "2024-03-15" \
  --time "10:45:00" \
  --lat 12.9716 \
  --lon 77.5946 \
  --tz 5.5 \
  --place "Bangalore"
```

### Interpret Chart

```bash
# Get detailed interpretation
bun /home/workspace/Skills/vedic-astrology/scripts/interpret-chart.ts \
  --chart "Charts/sample-person-chart.json" \
  --focus "career" \
  --system "kp"

# Focus areas: career, marriage, health, wealth, education, children
# Systems: kp, parashara, combined
```

### Dasha Predictions

```bash
# Current dasha period analysis
bun /home/workspace/Skills/vedic-astrology/scripts/analyze-dasha.ts \
  --chart "Charts/sample-person-chart.json" \
  --date "2024-03-15"

# Get upcoming events
bun /home/workspace/Skills/vedic-astrology/scripts/analyze-dasha.ts \
  --chart "Charts/sample-person-chart.json" \
  --period "next-year"
```

### Panchanga (Daily Almanac)

```bash
# Today's panchanga
bun /home/workspace/Skills/vedic-astrology/scripts/panchanga.ts \
  --lat 28.6139 \
  --lon 77.2090 \
  --tz 5.5

# Specific date
bun /home/workspace/Skills/vedic-astrology/scripts/panchanga.ts \
  --date "2024-04-15" \
  --lat 13.0827 \
  --lon 80.2707 \
  --tz 5.5 \
  --place "Chennai"
```

### Transit Analysis

```bash
# Current planetary transits
bun /home/workspace/Skills/vedic-astrology/scripts/transit.ts \
  --chart "Charts/sample-person-chart.json"

# Future transit
bun /home/workspace/Skills/vedic-astrology/scripts/transit.ts \
  --chart "Charts/sample-person-chart.json" \
  --date "2024-06-01"
```

### Compatibility (Synastry)

```bash
# Match two charts
bun /home/workspace/Skills/vedic-astrology/scripts/compatibility.ts \
  --chart1 "Charts/person1-chart.json" \
  --chart2 "Charts/person2-chart.json"

# Includes:
# - Kuta/Guna matching
# - Mangal Dosha check
# - Nadi, Bhakuta, Gana compatibility
# - Overall score and recommendations
```

## Key Concepts

### Krishnamurthi Paddhati (KP) System

**What makes KP unique:**
- Uses 249 subdivisions (sublords) instead of just 27 nakshatras
- Planet as significator of houses > Planet posited in house
- More precise timing predictions
- Simplified rules compared to classical systems

**KP Significators (ABCD):**
- **A**: Planets in a house's constellation
- **B**: Planets in a house
- **C**: Planets aspecting a house  
- **D**: Planets in aspect to house lord

### Divisional Charts (Vargas)

| Chart | Name | Significance |
|-------|------|--------------|
| D1 | Rasi | Overall life, personality |
| D2 | Hora | Wealth, financial potential |
| D3 | Drekkana | Siblings, courage |
| D4 | Chaturthamsa | Property, fixed assets |
| D7 | Saptamsa | Children, progeny |
| D9 | Navamsa | Marriage, spouse, dharma |
| D10 | Dasamsa | Career, profession |
| D12 | Dwadasamsa | Parents, ancestry |
| D16 | Shodasamsa | Vehicles, luxuries |
| D24 | Chaturvimsamsa | Education, learning |
| D27 | Bhamsha | Physical strength |
| D30 | Trimsamsa | Misfortunes, suffering |
| D60 | Shashtiamsa | Past life karma |

### Panchanga (Five Limbs)

1. **Tithi** - Lunar day (1-30)
2. **Nakshatra** - Moon's constellation (27 divisions)
3. **Yoga** - Sun-Moon combination (27 types)
4. **Karana** - Half of tithi (11 types)
5. **Vaara** - Weekday (7 days)

### Vimshottari Dasha

**120-year planetary period system:**
- Ketu: 7 years
- Venus: 20 years
- Sun: 6 years
- Moon: 10 years
- Mars: 7 years
- Rahu: 18 years
- Jupiter: 16 years
- Saturn: 19 years
- Mercury: 17 years

Each Mahadasha divided into Antardashas, Pratyantardashas, etc.

### Shadbala (Six-Fold Strength)

1. **Sthanabala** - Positional strength
2. **Kaalabala** - Temporal strength
3. **Digbala** - Directional strength
4. **Cheshtabala** - Motional strength
5. **Naisargikabala** - Natural strength
6. **Drikbala** - Aspectual strength

Minimum required strength (Rupas):
- Sun: 5, Moon: 6, Mars: 5, Mercury: 7
- Jupiter: 6.5, Venus: 5.5, Saturn: 5

### Ashtakavarga

Point-based system showing strength in each sign:
- **Sarvashtakavarga (SAV)**: Combined points from all planets
- **Bhinnashatkavarga (BAV)**: Individual planet contributions
- Used for transit predictions and strength assessment

## Output Format

Charts are saved as JSON with complete astrological data:

```json
{
  "person": {
    "name": "Sample Person",
    "birth_date": "1990-07-15T14:30:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone": 5.5,
    "place": "New Delhi"
  },
  "ayanamsa": 23.87,
  "d1_chart": {
    "ascendant": {"sign": "Libra", "degrees": 12.45},
    "planets": [...],
    "houses": [...]
  },
  "divisional_charts": {
    "d9": {...},
    "d10": {...}
  },
  "panchanga": {
    "tithi": "Krishna Chaturthi",
    "nakshatra": "Pushya",
    "yoga": "Vyaghata",
    "karana": "Bava",
    "vaara": "Sunday"
  },
  "dashas": {
    "current_mahadasha": "Venus",
    "current_antardasha": "Moon",
    "periods": [...]
  },
  "kp_data": {
    "significators": {...},
    "sublords": {...}
  },
  "shadbala": {...},
  "ashtakavarga": {...}
}
```

## Chart Interpretation Principles

### House Significations (Parashara System)

1. **1st House (Lagna)**: Self, body, personality, general fortune
2. **2nd House**: Wealth, family, speech, food, early education
3. **3rd House**: Siblings, courage, communication, short journeys
4. **4th House**: Mother, home, property, vehicles, happiness
5. **5th House**: Children, education, intelligence, romance, speculation
6. **6th House**: Enemies, diseases, debts, service, obstacles
7. **7th House**: Spouse, marriage, partnerships, business
8. **8th House**: Longevity, inheritance, occult, sudden events
9. **9th House**: Father, dharma, fortune, higher education, long journeys
10. **10th House**: Career, profession, status, authority, fame
11. **11th House**: Gains, income, friends, ambitions, elder siblings
12. **12th House**: Losses, expenses, foreign lands, spirituality, isolation

### Planetary Natures

**Natural Benefics:**
- Jupiter (guru) - Great benefic
- Venus (shukra) - Lesser benefic
- Moon (chandra) - Benefic when waxing
- Mercury (budha) - Benefic when alone or with benefics

**Natural Malefics:**
- Saturn (shani) - Great malefic
- Mars (mangal) - Lesser malefic
- Sun (surya) - Mild malefic
- Rahu/Ketu - Shadow planets (malefic)

**Functional Benefics/Malefics:**
Depends on ascendant and lordship of houses.

### Yogas (Planetary Combinations)

**Powerful Yogas:**
- **Raj Yoga**: Combinations giving power, status
- **Dhana Yoga**: Wealth-giving combinations
- **Neecha Bhanga Raj Yoga**: Debilitation cancellation
- **Gajakesari Yoga**: Jupiter-Moon combination
- **Mahapurusha Yogas**: Pancha Mahapurusha combinations

**Challenging Yogas:**
- **Kemadruma Yoga**: Moon isolated (no planets in adjacent houses)
- **Daridra Yoga**: Poverty-giving combinations
- **Kala Sarpa Yoga**: All planets between Rahu-Ketu axis

### Dasha Interpretation Rules

1. **Mahadasha Lord**:
   - Natural significations of the planet
   - Houses owned by the planet
   - Houses occupied and aspected

2. **Antardasha Lord**:
   - Relationship with Mahadasha lord
   - Its own significations and house lordship

3. **Transit Influence**:
   - Current position of dasha lords
   - Aspects to natal positions
   - Ashtakavarga strength in transit sign

### KP Judgment Rules

**For any event to manifest:**

1. **Significators must be present**:
   - Check house significations (ABCD method)
   - Primary significators > Secondary > Tertiary

2. **Dasha must be supportive**:
   - Current Mahadasha-Antardasha lords
   - Must be significators of relevant houses

3. **Sublord must promise**:
   - Cusp sublord more important than house lord
   - Sublord shows final fructification

**Example (Marriage timing):**
- Houses: 2, 7, 11 (positive), avoid 1, 6, 10 (negative)
- Check significators of 2-7-11
- Dasha must run of these significators
- 7th cusp sublord should not be in 1-6-10 star lord

## Traditional Texts Referenced

The interpretation incorporates wisdom from:

1. **Brihat Parashara Hora Shastra** - Foundation of Vedic astrology
2. **Brihat Jataka** (Varahamihira) - Classical text on natal astrology
3. **Saravali** (Kalyana Varma) - Comprehensive horoscopy
4. **Phaladeepika** (Mantreswara) - Results of planetary positions
5. **Jataka Parijata** (Vaidyanatha) - Natal astrology compendium
6. **KP Readers** (K.S. Krishnamurti) - KP system foundation

## Environment Variables

Set these in [Settings > Advanced](/?t=settings&s=advanced) if needed:

```bash
# Optional: Swiss Ephemeris path
SWISSEPH_PATH="/custom/path/to/ephe"

# Optional: Output directory
ASTRO_CHARTS_DIR="/home/workspace/Charts"
```

## Technical Details

**Ayanamsa Used:**
- True Chitra Paksha (Lahiri) - Default
- Based on Spica star position
- ~23.87° for year 2024

**Ephemeris Source:**
- NASA JPL DE421 (jyotishganit)
- Swiss Ephemeris (flatlib, VedicAstro)
- Accuracy to arc-seconds

**Coordinate System:**
- Geocentric sidereal zodiac
- Whole sign house system (traditional)
- Equal house divisions

## Common Use Cases

### Career Guidance
```bash
# Generate chart and get career insights
bun generate-chart.ts --date "1990-05-20" --time "08:15:00" \
  --lat 18.5204 --lon 73.8567 --tz 5.5 --name "Client" --place "Pune"
  
bun interpret-chart.ts --chart "Charts/client-chart.json" --focus "career" --system "combined"
```

### Marriage Timing
```bash
# Check marriage prospects
bun interpret-chart.ts --chart "Charts/client-chart.json" --focus "marriage"

# Check compatibility with partner
bun compatibility.ts --chart1 "Charts/person1.json" --chart2 "Charts/person2.json"
```

### Health Analysis
```bash
# Health indicators
bun interpret-chart.ts --chart "Charts/client-chart.json" --focus "health"

# Check current dasha for health matters
bun analyze-dasha.ts --chart "Charts/client-chart.json"
```

### Business Partnership
```bash
# Horary question
bun generate-horary.ts --question "Should I partner with this person?" \
  --lat 22.5726 --lon 88.3639 --tz 5.5 --place "Kolkata"

# Interpret horary chart using KP rules
bun interpret-chart.ts --chart "Charts/horary-*.json" --system "kp"
```

### Muhurta (Auspicious Timing)
```bash
# Find auspicious time for event
bun panchanga.ts --date "2024-04-15" --lat 28.6139 --lon 77.2090 --tz 5.5

# Check multiple dates
bun panchanga.ts --start-date "2024-04-01" --end-date "2024-04-30" \
  --lat 12.9716 --lon 77.5946 --tz 5.5 --format "table"
```

## Ethical Guidelines

When using this skill for chart interpretation:

1. **Emphasize Free Will**: Charts show potentials, not certainties
2. **Be Compassionate**: Avoid fatalistic language
3. **Provide Remedies**: Suggest mantras, gemstones, charity
4. **Respect Privacy**: Handle birth data confidentially
5. **Continuous Learning**: Cross-reference with classical texts
6. **Seek Expertise**: For complex charts, consult experienced astrologers

## Troubleshooting

**Missing ephemeris data:**
```bash
# Libraries auto-download on first run
# If issues, check internet connection and:
pip install --upgrade pyswisseph skyfield
```

**Wrong positions:**
```bash
# Verify timezone is correct (IST = 5.5)
# Check latitude/longitude format (decimal degrees)
# Ensure date format: YYYY-MM-DD
# Ensure time format: HH:MM:SS (24-hour)
```

**Interpretation accuracy:**
```bash
# Always verify birth time accuracy (±5 minutes changes ascendant)
# Birth time rectification may be needed
# Use divisional charts (D9, D10) to confirm D1 readings
```

## Further Learning

**Books:**
- "Light on Life" by Hart de Fouw and Robert Svoboda
- "Brihat Parashara Hora Shastra" translated by R. Santhanam
- "KP Reader" series by K.S. Krishnamurti
- "Fundamentals of Hindu Astrology" by S. Kannan

**Online Resources:**
- Saptarishis Astrology (saptarishisastrology.com)
- Vedic Astrology Research Portal (vedic-astrology.net)
- KP Astrology Forum (kpastroforum.com)

## API Integration

For programmatic access, you can import the Python modules directly:

```python
from vedicastro import VedicHoroscopeData
from jyotishganit import calculate_birth_chart
from flatlib import const
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart

# Use in your own scripts
# See references/api-examples.py for detailed usage
```

## Contributing

To enhance this skill:
1. Add more interpretation rules from classical texts
2. Implement additional yoga calculations
3. Add regional variations (Tamil, Kerala systems)
4. Enhance remedy suggestions
5. Add PDF report generation

## References

See `references/` directory for:
- Complete house significations
- Planetary dignity tables
- Yoga definitions
- Nakshatra characteristics
- Dasha interpretation rules
- Classical text excerpts

## When to Use This Skill

Use this skill when you need to:
- Generate complete Vedic birth charts
- Calculate Panchanga for any date/location
- Analyze planetary periods (Dashas)
- Time events using KP or classical systems
- Check compatibility between charts
- Answer specific questions (horary)
- Provide astrological consultations
- Research astrological patterns
- Teach Vedic astrology concepts
