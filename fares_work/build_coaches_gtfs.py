"""Build gtfs_private_coaches.zip — private intercity coach operators on the
Sydney-Canberra-Melbourne + NSW south-coast corridor, valid Wed 20 May 2026.
Operators: Firefly Express, Greyhound, Murrays, Premier Motor Service.
Times taken from real Wednesday timetables (GetAbout/Greyhound/Murrays/Premier),
dated to 20260520. OD fares via origin/destination zones (GTFS Fares V1)."""
import zipfile, csv, io, math, os

OUT = r"\gtfs_private_coaches.zip" #Update the output folder location
SERVICE_DATE = "20260520"          # Wednesday
TZ = "Australia/Sydney"            # Sydney/Melbourne/Canberra share AEST in May

# ---- stops: id -> (name, lat, lon) ----------------------------------------
STOPS = {
    "MEL_SXS":      ("Melbourne Southern Cross Coach Terminal", -37.8170, 144.9520),
    "CAMPBELLFIELD":("Campbellfield (Sydney Rd)",               -37.6790, 144.9490),
    "SEYMOUR":      ("Seymour Interstate Bus Stop",             -37.0276, 145.1360),
    "EUROA":        ("Euroa (Shell Coles Express)",             -36.7480, 145.5710),
    "GLENROWAN":    ("Glenrowan (BP, Hume Fwy)",                -36.4600, 146.2300),
    "ALBURY":       ("Albury Railway Station",                  -36.0833, 146.9180),
    "TARCUTTA":     ("Tarcutta (Sydney St)",                    -35.2760, 147.7330),
    "GUNDAGAI":     ("Gundagai (Tourist Info)",                 -35.0660, 148.1020),
    "YASS":         ("Yass (Yass Valley Way)",                  -34.8400, 148.9100),
    "GOULBURN":     ("Goulburn (Hume St)",                      -34.7540, 149.7180),
    "SUTTON_FOREST":("Sutton Forest (Hume Fwy)",                -34.5650, 150.3200),
    "LIVERPOOL":    ("Liverpool Interchange",                   -33.9200, 150.9230),
    "SYD_CENTRAL":  ("Sydney Central (Pitt St Coach)",          -33.8830, 151.2060),
    "CBR_JOLIMONT": ("Canberra Jolimont Centre",                -35.2780, 149.1300),
    "SYD_DOM_AIR":  ("Sydney Domestic Airport (coach)",         -33.9340, 151.1670),
    "SYD_INT_AIR":  ("Sydney International Airport (coach)",     -33.9320, 151.1660),
    "KOGARAH":      ("Kogarah",                                 -33.9670, 151.1320),
    "WOLLONGONG":   ("Wollongong",                              -34.4250, 150.8930),
    "KIAMA":        ("Kiama (Bombo)",                           -34.6720, 150.8620),
    "NOWRA":        ("Nowra",                                   -34.8810, 150.6000),
    "BOMADERRY":    ("Bomaderry (Rail)",                        -34.8550, 150.6100),
    "ULLADULLA":    ("Ulladulla",                               -35.3550, 150.4720),
    "BATEMANS_BAY": ("Batemans Bay",                            -35.7080, 150.1740),
    "MORUYA":       ("Moruya",                                  -35.9100, 150.0820),
    "NAROOMA":      ("Narooma",                                 -36.2170, 150.1320),
    "BERMAGUI":     ("Bermagui",                                -36.4190, 150.0700),
    "BEGA":         ("Bega",                                    -36.6740, 149.8420),
    "MERIMBULA":    ("Merimbula",                               -36.8980, 149.9100),
    "PAMBULA":      ("Pambula",                                 -36.9420, 149.8770),
    "EDEN":         ("Eden",                                    -37.0640, 149.9020),
}

# ---- agencies: id -> (name, url) ------------------------------------------
AGENCIES = {
    "FLY": ("Firefly Express",      "https://www.fireflyexpress.com.au"),
    "GRY": ("Greyhound Australia",  "https://www.greyhound.com.au"),
    "MUR": ("Murrays Coaches",      "https://www.murrays.com.au"),
    "PRM": ("Premier Motor Service","https://premierms.com.au"),
}

# ---- per-operator OD fare model: cents = base + rate*road_km ---------------
# road_km approximated as great-circle * 1.2
FARE_MODEL = {  # agency -> (base_cents, cents_per_km)
    "FLY": (2000, 7.0),
    "GRY": (2500, 8.5),
    "MUR": (2500, 8.0),
    "PRM": (1000, 13.5),   # higher /km: far-south-coast road is very indirect vs great-circle
}

# ---- routes & trips --------------------------------------------------------
# route: (route_id, agency, short, long). trip: (trip_id, route_id, headsign,
#         direction, [(stop, "HH:MM:SS"), ...]); times may exceed 24h (next day).
ROUTES = [
    ("FLY_HUME", "FLY", "FLY", "Firefly Express Melbourne - Sydney"),
    ("GRY_HUME", "GRY", "GX",  "Greyhound Sydney - Canberra - Melbourne"),
    ("MUR_CBR",  "MUR", "MUR", "Murrays Sydney - Canberra Express"),
    ("PRM_SC",   "PRM", "PRM", "Premier Sydney - South Coast - Eden"),
]

def T(h, m):  # "HH:MM:00"
    return f"{h:02d}:{m:02d}:00"

TRIPS = []

# Firefly Melbourne -> Sydney (FLY0031, dep 19:00, real timetable)
TRIPS.append(("FLY_MS", "FLY_HUME", "Sydney Central", 0, [
    ("MEL_SXS","19:00:00"),("CAMPBELLFIELD","19:25:00"),("SEYMOUR","20:25:00"),
    ("EUROA","20:55:00"),("GLENROWAN","21:35:00"),("ALBURY","22:35:00"),
    ("TARCUTTA","24:30:00"),("GUNDAGAI","25:05:00"),("YASS","26:35:00"),
    ("GOULBURN","27:25:00"),("SUTTON_FOREST","28:00:00"),("LIVERPOOL","29:15:00"),
    ("SYD_CENTRAL","30:10:00")]))
# Firefly Sydney -> Melbourne (FLY0021, dep 19:00, real timetable)
TRIPS.append(("FLY_SM", "FLY_HUME", "Melbourne Southern Cross", 1, [
    ("SYD_CENTRAL","19:00:00"),("LIVERPOOL","19:50:00"),("SUTTON_FOREST","21:05:00"),
    ("GOULBURN","21:40:00"),("YASS","23:05:00"),("GUNDAGAI","23:59:00"),
    ("TARCUTTA","24:35:00"),("ALBURY","26:25:00"),("GLENROWAN","27:35:00"),
    ("EUROA","28:15:00"),("SEYMOUR","28:45:00"),("CAMPBELLFIELD","29:45:00"),
    ("MEL_SXS","30:15:00")]))
# Greyhound Sydney -> Melbourne (GX233, dep 17:30, real timetable)
TRIPS.append(("GRY_SM", "GRY_HUME", "Melbourne Southern Cross", 1, [
    ("SYD_CENTRAL","17:30:00"),("SYD_DOM_AIR","17:50:00"),("SYD_INT_AIR","18:00:00"),
    ("CBR_JOLIMONT","21:30:00"),("ALBURY","25:05:00"),("MEL_SXS","29:30:00")]))
# Greyhound Melbourne -> Sydney (GX322, dep 22:00, real timetable)
TRIPS.append(("GRY_MS", "GRY_HUME", "Sydney Central", 0, [
    ("MEL_SXS","22:00:00"),("ALBURY","26:20:00"),("CBR_JOLIMONT","30:30:00"),
    ("SYD_INT_AIR","33:30:00"),("SYD_DOM_AIR","33:40:00"),("SYD_CENTRAL","34:00:00")]))
# Premier Eden -> Sydney (PM1, real anchor times, major stops)
TRIPS.append(("PRM_ES", "PRM_SC", "Sydney Central", 0, [
    ("EDEN","06:05:00"),("PAMBULA","06:20:00"),("MERIMBULA","06:35:00"),
    ("BEGA","07:05:00"),("BERMAGUI","07:50:00"),("NAROOMA","08:30:00"),
    ("MORUYA","09:10:00"),("BATEMANS_BAY","09:50:00"),("ULLADULLA","11:05:00"),
    ("NOWRA","12:30:00"),("BOMADERRY","12:40:00"),("KIAMA","13:45:00"),
    ("WOLLONGONG","14:20:00"),("KOGARAH","15:20:00"),("SYD_INT_AIR","15:45:00"),
    ("SYD_DOM_AIR","15:55:00"),("SYD_CENTRAL","16:15:00")]))
# Premier Sydney -> Eden (PM2, afternoon, modelled reverse)
TRIPS.append(("PRM_SE", "PRM_SC", "Eden", 1, [
    ("SYD_CENTRAL","13:35:00"),("SYD_DOM_AIR","13:50:00"),("SYD_INT_AIR","14:00:00"),
    ("KOGARAH","14:20:00"),("WOLLONGONG","15:15:00"),("KIAMA","15:50:00"),
    ("BOMADERRY","16:55:00"),("NOWRA","17:05:00"),("ULLADULLA","18:15:00"),
    ("BATEMANS_BAY","19:30:00"),("MORUYA","20:10:00"),("NAROOMA","20:50:00"),
    ("BERMAGUI","21:30:00"),("BEGA","22:10:00"),("MERIMBULA","22:40:00"),
    ("PAMBULA","22:55:00"),("EDEN","23:10:00")]))

# Murrays Sydney <-> Canberra express (frequent; representative departures)
def add_minutes(hhmmss, mins):
    h, m, s = map(int, hhmmss.split(":"))
    tot = h*60 + m + mins
    return f"{tot//60:02d}:{tot%60:02d}:00"
for i, dep in enumerate(["07:00","09:00","11:00","13:00","15:00","17:00","19:00","22:00"]):
    d = dep + ":00"
    TRIPS.append((f"MUR_SC_{i}", "MUR_CBR", "Canberra Jolimont", 1, [
        ("SYD_CENTRAL", d), ("SYD_DOM_AIR", add_minutes(d,20)),
        ("CBR_JOLIMONT", add_minutes(d,180))]))
for i, dep in enumerate(["06:00","08:00","10:00","12:00","14:00","16:00","18:00"]):
    d = dep + ":00"
    TRIPS.append((f"MUR_CS_{i}", "MUR_CBR", "Sydney Central", 0, [
        ("CBR_JOLIMONT", d), ("SYD_DOM_AIR", add_minutes(d,195)),
        ("SYD_CENTRAL", add_minutes(d,210))]))

# ---------------------------------------------------------------------------
def haversine_km(a, b):
    (la1, lo1), (la2, lo2) = a, b
    R = 6371.0
    p1, p2 = math.radians(la1), math.radians(la2)
    dp, dl = math.radians(la2-la1), math.radians(lo2-lo1)
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))

def fare_cents(agency, o, d):
    base, rate = FARE_MODEL[agency]
    km = haversine_km(STOPS[o][1:], STOPS[d][1:]) * 1.2
    cents = base + rate*km
    dollars = max(5, round(cents/100))      # nearest dollar, min $5
    return dollars*100

def route_agency(rid):
    return next(a for (r, a, *_ ) in ROUTES if r == rid)

def main():
    # agency.txt
    agency = ["agency_id,agency_name,agency_url,agency_timezone,agency_lang"]
    for aid,(name,url) in AGENCIES.items():
        agency.append(f"{aid},{name},{url},{TZ},en")

    # stops.txt (zone_id = stop_id for OD fares)
    stops = ["stop_id,stop_name,stop_lat,stop_lon,zone_id"]
    for sid,(name,lat,lon) in STOPS.items():
        stops.append(f'{sid},"{name}",{lat:.5f},{lon:.5f},{sid}')   # quote name (may contain commas)

    # routes.txt (route_type 3 = bus/coach)
    routes = ["route_id,agency_id,route_short_name,route_long_name,route_type,route_color,route_text_color"]
    for rid,aid,short,long in ROUTES:
        routes.append(f'{rid},{aid},{short},"{long}",3,1F4E79,FFFFFF')

    # calendar.txt / calendar_dates.txt — only Wed 20 May 2026
    calendar = ["service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date",
                f"WED,0,0,1,0,0,0,0,20260518,20260524"]
    calendar_dates = ["service_id,date,exception_type", f"WED,{SERVICE_DATE},1"]

    # trips.txt + stop_times.txt
    trips = ["route_id,service_id,trip_id,trip_headsign,direction_id"]
    stop_times = ["trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type"]
    route_stops = {}  # route_id -> set of stops served
    for tid, rid, head, dirn, seq in TRIPS:
        trips.append(f"{rid},WED,{tid},{head},{dirn}")
        for i,(sid,t) in enumerate(seq, 1):
            stop_times.append(f"{tid},{t},{t},{sid},{i},0,0")
        route_stops.setdefault(rid, set()).update(s for s,_ in seq)

    # fares: OD per route, fare_id deduped by (agency, cents)
    fare_attr = ["fare_id,price,currency_type,payment_method,transfers,transfer_duration"]
    fare_rules = ["fare_id,route_id,origin_id,destination_id"]
    seen_fare = {}   # (agency,cents) -> fare_id
    for rid, sset in route_stops.items():
        aid = route_agency(rid)
        slist = sorted(sset)
        for o in slist:
            for d in slist:
                if o == d: continue
                cents = fare_cents(aid, o, d)
                key = (aid, cents)
                if key not in seen_fare:
                    fid = f"{aid}_{cents}"
                    seen_fare[key] = fid
                    fare_attr.append(f"{fid},{cents/100:.2f},AUD,1,0,")
                fare_rules.append(f"{seen_fare[key]},{rid},{o},{d}")

    feed_info = ["feed_publisher_name,feed_publisher_url,feed_lang,feed_start_date,feed_end_date,feed_version",
                 f"Private Intercity Coaches (compiled for OTP),https://example.org,en,{SERVICE_DATE},{SERVICE_DATE},1.0"]

    files = {
        "agency.txt": agency, "stops.txt": stops, "routes.txt": routes,
        "calendar.txt": calendar, "calendar_dates.txt": calendar_dates,
        "trips.txt": trips, "stop_times.txt": stop_times,
        "fare_attributes.txt": fare_attr, "fare_rules.txt": fare_rules,
        "feed_info.txt": feed_info,
    }
    if os.path.exists(OUT): os.remove(OUT)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, lines in files.items():
            zf.writestr(name, "\n".join(lines) + "\n")

    print(f"built {os.path.basename(OUT)}: {len(STOPS)} stops, {len(ROUTES)} routes, "
          f"{len(TRIPS)} trips, {len(stop_times)-1} stop_times, "
          f"{len(fare_attr)-1} fare_attributes, {len(fare_rules)-1} fare_rules")
    # sample fares
    for o,d in [("FLY","y")]:
        pass
    for (rid,o,d) in [("FLY_HUME","MEL_SXS","SYD_CENTRAL"),("GRY_HUME","SYD_CENTRAL","MEL_SXS"),
                      ("GRY_HUME","SYD_CENTRAL","CBR_JOLIMONT"),("MUR_CBR","SYD_CENTRAL","CBR_JOLIMONT"),
                      ("PRM_SC","SYD_CENTRAL","EDEN"),("PRM_SC","SYD_CENTRAL","WOLLONGONG")]:
        print(f"  {rid} {o}->{d}: ${fare_cents(route_agency(rid),o,d)/100:.2f}")

if __name__ == "__main__":
    main()
