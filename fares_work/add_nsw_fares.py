"""Add GTFS Fares V1 to the NSW (Transport for NSW) feed. Adult, Opal peak (14 Jul 2025).
Urban: flat representative fare per mode. Regional NSW TrainLink trains: per-route
end-to-end economy fare (mapped from trip headsigns), scoped by route_id.
Appends to the ~291 MB zip in place (no recompression of existing entries)."""
import zipfile, csv, io, os

GTFS = r"\gtfs_NSW_202605130001.zip" #update the GTFS file location

# Regional train (route_type 106) end-to-end economy fares in cents, by route_id
# (destinations identified from trip_headsign).
REG_TRAIN = {
    "76-223-sj2-1": 9600,  "76-224-sj2-1": 9600,   # Armidale (New England)
    "76-243-sj2-1": 9600,  "76-244-sj2-1": 7000,   # Moree / Werris Creek
    "76-31-sj2-1": 11000,  "76-32-sj2-1": 11000,   # North Coast XPT (Casino/Brisbane)
    "76-33-sj2-1": 11000,  "76-34-sj2-1": 11000,   # Casino
    "76-35-sj2-1": 10000,  "76-36-sj2-1": 10000,   # Grafton
    "76-427-sj2-1": 8000,  "76-428-sj2-1": 8000,   # Dubbo
    "76-445-sj2-1": 12000, "76-446-sj2-1": 12000,  # Broken Hill (Outback)
    "76-621-sj2-1": 11000, "76-622-sj2-1": 11000,  # Melbourne/Albury XPT (south)
    "76-623-sj2-1": 11000, "76-624-sj2-1": 11000,
    "76-631-sj2-1": 5000,  "76-632-sj2-1": 5000,   # Canberra (Xplorer)
    "76-633-sj2-1": 5000,  "76-634-sj2-1": 5000,
    "76-635-sj2-1": 5000,  "76-636-sj2-1": 5000,
    "76-641-sj2-1": 8000,  "76-643-sj2-1": 8000,   # Griffith
    "76-644-sj2-1": 4500,                          # Goulburn
}

def fare_cents(r):
    t, desc, rid = r["route_type"], r["route_desc"], r["route_id"]
    if t == "2":
        return 1066 if desc == "Intercity Trains Network" else 540  # Opal intercity vs Sydney Trains
    if t == "401":
        return 540          # Sydney Metro (Opal train scale)
    if t == "900":
        return 449          # light rail
    if t == "4":
        return 330 if desc == "Newcastle Ferries" else 735  # Newcastle vs Sydney/private ferry
    if t in ("700", "712", "714"):
        return 447          # bus / school bus / temporary bus (Opal bus)
    if t in ("204", "205"):
        return 4500         # NSW TrainLink regional & temporary coaches
    if t == "106":
        return REG_TRAIN[rid]
    raise ValueError(f"unclassified route {rid} type={t} desc={desc}")

def main():
    with zipfile.ZipFile(GTFS, "r") as zf:
        assert "fare_attributes.txt" not in zf.namelist(), "fares already present"
        rows = list(csv.DictReader(io.StringIO(zf.read("routes.txt").decode("utf-8-sig"))))

    rule_lines = ["fare_id,route_id"]
    used = {}  # cents -> fare_id
    from collections import Counter
    tally = Counter()
    for r in rows:
        cents = fare_cents(r)
        fid = f"nsw_{cents}"
        used[cents] = fid
        rule_lines.append(f"{fid},{r['route_id']}")
        tally[cents] += 1

    attr_lines = ["fare_id,price,currency_type,payment_method,transfers,transfer_duration"]
    for cents in sorted(used):
        attr_lines.append(f"{used[cents]},{cents/100:.2f},AUD,1,0,")

    with zipfile.ZipFile(GTFS, "a", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("fare_attributes.txt", "\n".join(attr_lines) + "\n")
        zf.writestr("fare_rules.txt", "\n".join(rule_lines) + "\n")

    print(f"NSW: {len(rows)} routes -> {len(used)} distinct fares")
    for cents in sorted(used):
        print(f"  ${cents/100:>7.2f}  x{tally[cents]}")

if __name__ == "__main__":
    main()
