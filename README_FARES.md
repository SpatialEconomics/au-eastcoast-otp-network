# Fares added to the east-coast AU OTP network

Fares were added to **every** GTFS feed and a **new private-coach feed** was created, so that
OpenTripPlanner can return a monetary cost for each itinerary in the strategic demand model.

- **Standard:** GTFS **Fares V1** (`fare_attributes.txt` + `fare_rules.txt`) — what OTP 2.6 computes from reliably.
- **Basis:** Adult full fare, NSW Opal **peak**. Currency **AUD**.
- **Reference day:** Wednesday **20 May 2026**.
- **Modelling choice:** flat representative fare per **urban** mode; **origin–destination** fares for
  intercity (flights, coaches, long-distance rail).

Full assumptions, numbers and web sources are in [`fares_work/FARE_DECISIONS.md`](fares_work/FARE_DECISIONS.md).

## What changed (in `graphs/default/`)

| Feed | Fare approach | Example fare |
|------|---------------|--------------|
| `gtfs_flights.zip` | per-route (city pair) | MEL–SYD $110 (JST) … Rex regional $240–300 |
| `gtfs_VIC_2/3/4_metro_*`, `gtfs_VIC_6_regional_bus` | flat myki 2-hour | $5.70 |
| `gtfs_VIC_1_regional_train`, `gtfs_VIC_5_regional_coach` | V/Line capped | $11.40 |
| `gtfs_VIC_11_skybus` | flat | $25.90 |
| `gtfs_VIC_10_interstate` (The Overland) | flat | $145.00 |
| `gtfs_NSW_*` urban (train/metro/bus/ferry/light rail) | flat per mode | train $5.40, bus $4.47, ferry $7.35, LR $4.49, intercity train $10.66 |
| `gtfs_NSW_*` regional TrainLink trains | per-route end-to-end | Sydney–Melbourne XPT $110, Sydney–Canberra $50, Broken Hill $120 … |
| `gtfs_NSW_*` regional/temporary coaches | flat | $45 |
| **`gtfs_private_coaches.zip`** (NEW) | OD by distance | Firefly/Greyhound/Murrays/Premier — see below |

### New private-coach feed `gtfs_private_coaches.zip`
4 operators, valid **Wed 20 May 2026** (`calendar` Wed-only + `calendar_dates` 20260520), real Wednesday timetables:
- **Firefly Express** — Sydney⇄Melbourne overnight (Hume), 1 service each way.
- **Greyhound** — Sydney⇄Canberra⇄Melbourne, 1 service each way.
- **Murrays** — Sydney⇄Canberra express, ~8 services each way.
- **Premier Motor Service** — Sydney⇄Eden (far south coast / Princes Hwy), 1 each way.

OD fares via origin/destination zones, e.g. Firefly MEL–SYD **$80**, Greyhound SYD–CBR **$50**,
Murrays SYD–CBR **$49**, Premier SYD–Eden **$70**, SYD–Wollongong **$21**.

## IMPORTANT — to make fares take effect

1. **Rebuild the OTP graph.** Fares are read at *build* time; the existing `graph.obj` predates them.
   ```
   java -Xmx<RAM> -jar otp-2.6.0-shaded.jar --build --save graphs/default
   ```
2. No `build-config.json` change is needed — OTP 2.6 computes GTFS Fares V1 automatically when present.
3. In the GraphQL API, read fares from each **leg's `fareProducts`** (in OTP 2.x the itinerary-level
   `fare` field is deprecated/often empty).

## Known simplifications (deliberate, for a strategic model)
- Opal/myki **daily & weekly caps**, peak/off-peak and free-transfer discounts are **not** modelled
  (GTFS Fares V1 is per-leg only). Each boarding is charged its mode fare.
- **Victoria is genuinely *free* on 20 May 2026** (state-wide promotion to 31 May 2026, then half-price
  to 1 Jan 2027). By request, the VIC feeds use **normal capped fares** instead, to represent long-run
  conditions. Halve them for the Jun–Dec 2026 window, or zero them for the literal free period.
- NSW regional trains are priced **per route end-to-end**; an intermediate boarding is charged the
  full-route fare (Fares V1 can't vary by distance within a feed that shares Central with Opal services).
- Flight & coach fares are **representative** one-way adult economy values (airfares vary widely).

## Reproducibility (`fares_work/`)
- `add_flights_fares.py`, `add_vic_fares.py`, `add_nsw_fares.py` — append fare files to existing feeds.
- `build_coaches_gtfs.py` — build the private-coach feed from scratch.
- `validate_all.py` — referential-integrity + monotonic-time checks (all feeds pass).
- `FARE_DECISIONS.md` — every fare value with its source.
- Original feeds backed up to `%LOCALAPPDATA%\Temp\gtfs_backups\` before modification.
