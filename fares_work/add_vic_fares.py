"""Add GTFS Fares V1 to the 9 VIC feeds. Adult full fare, NORMAL CAPPED (non-promo).
myki metro/regional bus = $5.70 (2-hour); V/Line train & coach = $11.40 (daily cap, the
representative single intercity fare under the Jan-2025 regional cap; corridor-relevant
V/Line trips e.g. Seymour/Albury/Shepparton are long-distance and reach the cap);
SkyBus City Express = $25.90; The Overland (Journey Beyond) = $145.00.
Fares deduped: one fare_attribute per distinct price, one fare_rule per route."""
import zipfile, csv, io, os

BASE = r" " #update the base folder

# feed filename -> (fare_id prefix, price-in-cents for every route in the feed)
FEEDS = {
    "gtfs_VIC_1_regional_train.zip": ("vline_train", 1140),
    "gtfs_VIC_2_metro_train.zip":    ("metro_train", 570),
    "gtfs_VIC_3_metro_tram.zip":     ("metro_tram", 570),
    "gtfs_VIC_4_bus.zip":            ("metro_bus", 570),
    "gtfs_VIC_5_regional_coach.zip": ("vline_coach", 1140),
    "gtfs_VIC_6_regional_bus.zip":   ("regional_bus", 570),
    "gtfs_VIC_10_interstate.zip":    ("overland", 14500),
    "gtfs_VIC_11_skybus.zip":        ("skybus", 2590),
}

def route_ids(zf):
    d = zf.read("routes.txt").decode("utf-8-sig")
    return [r["route_id"] for r in csv.DictReader(io.StringIO(d))]

def main():
    for fname, (prefix, cents) in FEEDS.items():
        path = os.path.join(BASE, fname)
        with zipfile.ZipFile(path, "r") as zf:
            assert "fare_attributes.txt" not in zf.namelist(), f"{fname}: fares already present"
            rids = route_ids(zf)
        fid = f"{prefix}_{cents}"
        price = f"{cents/100:.2f}"
        attrs = ["fare_id,price,currency_type,payment_method,transfers,transfer_duration",
                 f"{fid},{price},AUD,1,0,"]
        rules = ["fare_id,route_id"] + [f"{fid},{rid}" for rid in rids]
        with zipfile.ZipFile(path, "a", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("fare_attributes.txt", "\n".join(attrs) + "\n")
            zf.writestr("fare_rules.txt", "\n".join(rules) + "\n")
        print(f"{fname}: {len(rids)} routes -> ${price}")

if __name__ == "__main__":
    main()
