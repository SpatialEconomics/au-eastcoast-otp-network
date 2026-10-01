"""Validate fare additions across all feeds + full integrity of the coach feed."""
import zipfile, csv, io, os

BASE = r" " #update the base GTFS location folder

def read(zf, name):
    return list(csv.DictReader(io.StringIO(zf.read(name).decode("utf-8-sig"))))

def secs(t):
    h, m, s = map(int, t.split(":"))
    return h*3600 + m*60 + s

def check_fares(fname, with_zones=False):
    errs = []
    with zipfile.ZipFile(os.path.join(BASE, fname)) as zf:
        names = zf.namelist()
        if zf.testzip() is not None:
            errs.append("CRC error in zip")
        for req in ("fare_attributes.txt", "fare_rules.txt"):
            if req not in names:
                errs.append(f"missing {req}");
        if errs: return errs
        attrs = read(zf, "fare_attributes.txt")
        rules = read(zf, "fare_rules.txt")
        routes = {r["route_id"] for r in read(zf, "routes.txt")}
        fare_ids = {a["fare_id"] for a in attrs}
        zones = set()
        if with_zones:
            zones = {s.get("zone_id","") for s in read(zf, "stops.txt")}
        # every attribute well-formed
        for a in attrs:
            if not a["fare_id"] or float(a["price"]) < 0 or a["currency_type"] != "AUD":
                errs.append(f"bad fare_attribute {a}")
        # every rule references valid fare_id + route_id (+zones)
        covered = set()
        for r in rules:
            if r["fare_id"] not in fare_ids:
                errs.append(f"rule fare_id not in attributes: {r['fare_id']}")
            if r["route_id"] and r["route_id"] not in routes:
                errs.append(f"rule route_id not in routes: {r['route_id']}")
            covered.add(r["route_id"])
            if with_zones:
                for z in (r.get("origin_id",""), r.get("destination_id","")):
                    if z and z not in zones:
                        errs.append(f"rule zone not in stops: {z}")
        # all routes priced?
        unpriced = routes - covered
        if unpriced:
            errs.append(f"{len(unpriced)} routes have NO fare rule (e.g. {sorted(unpriced)[:3]})")
        info = f"{len(attrs)} attrs, {len(rules)} rules, {len(routes)} routes"
    return errs or [f"OK: {info}"]

def check_coach_integrity(fname):
    errs = []
    with zipfile.ZipFile(os.path.join(BASE, fname)) as zf:
        stops = {s["stop_id"] for s in read(zf, "stops.txt")}
        routes = {r["route_id"] for r in read(zf, "routes.txt")}
        services = {c["service_id"] for c in read(zf, "calendar.txt")}
        trips = read(zf, "trips.txt")
        trip_ids = {t["trip_id"] for t in trips}
        for t in trips:
            if t["route_id"] not in routes: errs.append(f"trip route missing {t['route_id']}")
            if t["service_id"] not in services: errs.append(f"trip service missing {t['service_id']}")
        # stop_times referential + monotonic
        from collections import defaultdict
        seq = defaultdict(list)
        for st in read(zf, "stop_times.txt"):
            if st["stop_id"] not in stops: errs.append(f"stop_time stop missing {st['stop_id']}")
            if st["trip_id"] not in trip_ids: errs.append(f"stop_time trip missing {st['trip_id']}")
            seq[st["trip_id"]].append((int(st["stop_sequence"]), secs(st["departure_time"])))
        for tid, lst in seq.items():
            lst.sort()
            times = [s for _, s in lst]
            if any(times[i] >= times[i+1] for i in range(len(times)-1)):
                errs.append(f"non-increasing times in trip {tid}")
        # service date present
        cd = read(zf, "calendar_dates.txt")
        if not any(c["date"] == "20260520" for c in cd):
            errs.append("20260520 not in calendar_dates")
    return errs or ["OK: integrity (stops, trips, monotonic times, service date 20260520)"]

if __name__ == "__main__":
    feeds = ["gtfs_flights.zip", "gtfs_VIC_1_regional_train.zip", "gtfs_VIC_2_metro_train.zip",
             "gtfs_VIC_3_metro_tram.zip", "gtfs_VIC_4_bus.zip", "gtfs_VIC_5_regional_coach.zip",
             "gtfs_VIC_6_regional_bus.zip", "gtfs_VIC_10_interstate.zip", "gtfs_VIC_11_skybus.zip",
             "gtfs_NSW_202605130001.zip"]
    for f in feeds:
        print(f"\n## {f}")
        for line in check_fares(f): print("   ", line)
    print(f"\n## gtfs_private_coaches.zip")
    for line in check_fares("gtfs_private_coaches.zip", with_zones=True): print("   ", line)
    for line in check_coach_integrity("gtfs_private_coaches.zip"): print("   ", line)
