# Fare assumptions — east-coast AU OTP network

**Basis:** Adult full fare, peak (NSW Opal). GTFS Fares V1 (`fare_attributes.txt` + `fare_rules.txt`). AUD.
**Reference day:** Wed 20 May 2026.
**Modeling choices (confirmed with user):** flat representative fare per urban mode; origin–destination fares for intercity (flights, coaches, long-distance rail). VIC government feeds priced at **normal capped fares** (NOT the temporary free/half-price promotion that actually applies on 20 May 2026).

## NSW — Opal (normal fares, effective 14 July 2025; adult peak)
Representative single fare per mode (flat). Source: Transport NSW / IPART.
- Sydney Trains (urban, route_type 2 "Sydney Trains Network"): **$5.40** (10–20 km band representative)
- Sydney Metro (route_type 401): **$5.40** (same Opal train scale)
- Intercity trains (route_type 2 "Intercity Trains Network"): **$10.66** (65 km+ band; long trips e.g. Newcastle/Blue Mtns/South Coast)
- Bus (route_type 700/712/714 etc.): **$4.47** (3–8 km band)
- Light rail (route_type 900): **$4.49** (3–8 km band)
- Ferry (route_type 4, Sydney): **$7.35** (inner-harbour 0–9 km)
- Newcastle ferry: **$3.30** (short crossing)
- Anchor check (IPART): 5 km trip = $4.20 train / $4.36 bus & light rail / $7.13 ferry (adult peak 2024-25).
- Daily cap $19.30 (Mon–Thu) / $9.65 (Fri–Sun), weekly cap $50 — NOT representable in Fares V1 (per-leg only); noted as a limitation.
- NSW TrainLink regional trains (route_type 106): per-route end-to-end economy fare, scoped by route_id (Fares V1 can't vary by boarding distance within a combined Opal+regional feed sharing Central; documented limitation). Anchors:
  - Sydney–Melbourne (XPT): **$110**
  - Sydney–Canberra / Southern (Xplorer): **$50**
  - Sydney–Griffith: **$80**; Sydney–Dubbo: **$80**
  - Sydney–Grafton/Casino (North Coast XPT): **$110**
  - Sydney–Armidale/Moree (NW Xplorer): **$96**
  - Sydney–Broken Hill (Outback Xplorer): **$120**
  - Sydney–Bathurst/Orange (Central West): **$45**
  - default regional train if unmatched: **$90**
- NSW TrainLink regional coaches (route_type 204/205, incl. "Temporary coaches" rail-replacement): flat **$45** representative.
- Regional URBAN buses (Newcastle/Hunter/Central Coast/Illawarra/North Coast networks, route_type 700): Opal bus **$4.47** (same as Sydney bus).

## VIC — normal capped fares (adult full; the permanent Jan-2025 regional cap, NOT the free/half-price promo)
- Metro train (VIC_2): **$5.70** (myki 2-hour Zone 1+2 full fare, 2026)
- Metro tram (VIC_3): **$5.70**
- Metro bus (VIC_4): **$5.70**
- Regional town bus (VIC_6): **$5.70** (regional 2-hour, capped to metro)
- V/Line regional train (VIC_1): short/commuter lines (Geelong, Ballarat, Bendigo, Seymour, Traralgon, <2 h) **$5.70**; long-distance (Albury, Shepparton, Warrnambool, Bairnsdale, Swan Hill, Echuca) **$11.40** (daily cap)
- V/Line regional coach (VIC_5): **$11.40** default (long feeders), short feeders **$5.70**
- SkyBus Melbourne City Express (VIC_11): **$25.90** one-way (commercial; not part of free/half-price PT)
- The Overland Melbourne–Adelaide (VIC_10, route_type 102, Journey Beyond): **$145.00** (Red Standard, commercial)
- NOTE: myki daily cap $11.40 — not representable in Fares V1.

## Flights (gtfs_flights.zip) — per-route OD fares (each route = one city pair, so route_id fare is exact)
Representative one-way adult economy (AUD, indicative — airfares vary widely). Sources: Expedia/Trip.com/momondo/Rex.
| route_id | pair | fare |
|---|---|---|
| JST_AVV_SYD | Avalon–Sydney (Jetstar) | 95 |
| JST_MEL_SYD | Melbourne–Sydney (Jetstar) | 110 |
| VOZ_MEL_SYD | Melbourne–Sydney (Virgin) | 150 |
| QFA_MEL_SYD | Melbourne–Sydney (Qantas) | 170 |
| ABR_MEL_SYD | Melbourne–Sydney (ASL) | 150 |
| XLR_MEL_SYD | Melbourne–Sydney (Texel) | 150 |
| VOZ_CBR_SYD | Canberra–Sydney (Link) | 130 |
| JST_CBR_MEL | Canberra–Melbourne (Jetstar) | 120 |
| VOZ_CBR_MEL | Canberra–Melbourne (Link) | 150 |
| QFA_CBR_MEL | Canberra–Melbourne (Qantas) | 160 |
| VOZ_MEL_NTL | Melbourne–Newcastle (Virgin) | 150 |
| JST_MEL_NTL | Melbourne–Newcastle (Jetstar) | 120 |
| JST_BNK_MEL | Ballina–Melbourne (Jetstar) | 160 |
| VOZ_BNK_SYD | Ballina–Sydney (Virgin) | 140 |
| JST_BNK_SYD | Ballina–Sydney (Jetstar) | 110 |
| RXA_ABX_SYD | Albury–Sydney (Rex) | 300 |
| RXA_GFF_SYD | Griffith–Sydney (Rex) | 290 |
| RXA_BHQ_SYD | Broken Hill–Sydney (Rex) | 300 |
| RXA_MIM_SYD | Merimbula–Sydney (Rex) | 250 |
| RXA_CFS_SYD | Coffs Harbour–Sydney (Rex) | 300 |
| RXA_PQQ_SYD | Port Macquarie–Sydney (Rex) | 240 |
| RXA_MEL_MQL | Melbourne–Mildura (Rex) | 230 |

## Private intercity coaches (new feed `gtfs_private_coaches.zip`) — OD fares
Service date Wed 20 May 2026 (`calendar` Wed-only + `calendar_dates`). 4 operators found:
- **Firefly Express (FLY)** — SYD↔MEL overnight via Hume. MEL dep 19:00→SYD 06:10; SYD dep 19:00→MEL 06:15. Stops: Melbourne SXS, Campbellfield, Seymour, Euroa, Glenrowan, Albury(x2), Tarcutta, Gundagai, Yass, Goulburn, Sutton Forest, Liverpool, Sydney Central. Fare from $47–65 (SYD–MEL).
- **Greyhound (GRY)** — SYD↔CBR↔Albury↔MEL. SYD dep 17:30→CBR 21:00→Albury 01:05→MEL 05:30 (GX233); MEL dep 22:00→Albury 02:20→CBR 06:00→SYD 10:00 (GX322). Stops: Sydney Central, Sydney Domestic Apt, Sydney Intl Apt, Canberra Jolimont, Albury, Melbourne SXS. Fare SYD–MEL ~$108, SYD–CBR ~$45, CBR–MEL ~$78.
- **Murrays (MUR)** — SYD↔CBR express, ~hourly (16–17/day each way), ~3–3.5 h, via Sydney Domestic Apt. Stops: Sydney Central (486 Pitt St), Sydney Domestic Apt, Canberra Jolimont. Fare ~$48.
- **Premier Motor Service (PRM)** — SYD↔Eden far south coast (Princes Hwy). Eden dep 06:05→Sydney 16:15 (real PM1); reverse SYD→Eden modelled dep 13:35 (PM2 forward times not machine-readable). Major stops: Sydney Central, Sydney Domestic Apt, Sydney Intl Apt, Wollongong, Kiama, Nowra, Bomaderry, Ulladulla, Batemans Bay, Moruya, Narooma, Bermagui, Bega, Merimbula, Pambula, Eden. Fare distance-based, SYD–Eden ~$70.

**Coach OD fare model:** each coach stop gets a unique `zone_id`; fare_rules per (route_id, origin_id, destination_id). Fare = round(base + rate·road_km) per operator (road_km ≈ haversine·1.2), capped at end-to-end anchor:
- FLY: base $20 + $0.07/km (SYD–MEL≈$80, ALB–SYD≈$60, MEL–ALB≈$45)
- GRY: base $25 + $0.085/km (SYD–CBR≈$45, CBR–MEL≈$78, SYD–MEL≈$108)
- MUR: flat $48 SYD–CBR ($45 to Sydney Airport)
- PRM: base $10 + $0.115/km (SYD–Wollongong≈$20, SYD–Batemans≈$45, SYD–Eden≈$70)
