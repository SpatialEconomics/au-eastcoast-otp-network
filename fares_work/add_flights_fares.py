"""Add GTFS Fares V1 (fare_attributes + fare_rules) to gtfs_flights.zip.
Each flight route is a single city pair, so one per-route fare = exact OD fare.
Representative one-way adult economy fares (AUD)."""
import zipfile, csv, io, os

GTFS = r"\gtfs_flights.zip" #update the GTFS file location

FARES = {
    "JST_AVV_SYD": 95,  "JST_MEL_SYD": 110, "VOZ_MEL_SYD": 150, "QFA_MEL_SYD": 170,
    "ABR_MEL_SYD": 150, "XLR_MEL_SYD": 150, "VOZ_CBR_SYD": 130, "JST_CBR_MEL": 120,
    "VOZ_CBR_MEL": 150, "QFA_CBR_MEL": 160, "VOZ_MEL_NTL": 150, "JST_MEL_NTL": 120,
    "JST_BNK_MEL": 160, "VOZ_BNK_SYD": 140, "JST_BNK_SYD": 110, "RXA_ABX_SYD": 300,
    "RXA_GFF_SYD": 290, "RXA_BHQ_SYD": 300, "RXA_MIM_SYD": 250, "RXA_CFS_SYD": 300,
    "RXA_PQQ_SYD": 240, "RXA_MEL_MQL": 230,
}

def read_route_ids(zf):
    data = zf.read("routes.txt").decode("utf-8-sig")
    return [r["route_id"] for r in csv.DictReader(io.StringIO(data))]

def main():
    with zipfile.ZipFile(GTFS, "r") as zf:
        names = set(zf.namelist())
        route_ids = read_route_ids(zf)
    assert "fare_attributes.txt" not in names, "fare files already present!"

    missing = [r for r in route_ids if r not in FARES]
    assert not missing, f"routes without a fare: {missing}"

    attrs = ["fare_id,price,currency_type,payment_method,transfers,transfer_duration"]
    rules = ["fare_id,route_id"]
    for rid in route_ids:
        fid = f"air_{rid}"
        attrs.append(f"{fid},{FARES[rid]:.2f},AUD,1,0,")
        rules.append(f"{fid},{rid}")

    with zipfile.ZipFile(GTFS, "a", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("fare_attributes.txt", "\n".join(attrs) + "\n")
        zf.writestr("fare_rules.txt", "\n".join(rules) + "\n")

    print(f"flights: added {len(route_ids)} fares "
          f"(${min(FARES.values())}-${max(FARES.values())})")

if __name__ == "__main__":
    main()
