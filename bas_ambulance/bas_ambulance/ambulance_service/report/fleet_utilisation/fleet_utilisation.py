import frappe

def execute(filters=None):
    return get_columns(), get_data(filters)

def get_columns():
    return [
        {"label":"Ambulance","fieldname":"ambulance","fieldtype":"Link",
         "options":"Ambulance Master","width":130},
        {"label":"Type","fieldname":"vehicle_type","fieldtype":"Data","width":100},
        {"label":"Station","fieldname":"home_station","fieldtype":"Link",
         "options":"Ambulance Station","width":130},
        {"label":"Trips","fieldname":"total_trips","fieldtype":"Int","width":70},
        {"label":"Total KM","fieldname":"total_km","fieldtype":"Float","width":90},
        {"label":"Total Hours","fieldname":"total_hours","fieldtype":"Float","width":100},
        {"label":"Downtime (hrs)","fieldname":"downtime_hrs",
         "fieldtype":"Float","width":110},
        {"label":"Maintenance Events","fieldname":"maint_count",
         "fieldtype":"Int","width":140},
        {"label":"Maintenance Cost","fieldname":"maint_cost",
         "fieldtype":"Currency","width":130},
    ]

def get_data(filters):
    from_date = filters.get("from_date", frappe.utils.today())
    to_date   = filters.get("to_date",   frappe.utils.today())

    trips = frappe.db.sql("""
        SELECT
            ts.ambulance,
            am.vehicle_type,
            am.home_station,
            COUNT(ts.name)                 AS total_trips,
            SUM(ts.distance_covered)       AS total_km,
            SUM(ts.total_duration_min)/60  AS total_hours
        FROM `tabAmbulance Trip Sheet` ts
        LEFT JOIN `tabAmbulance Master` am ON am.name = ts.ambulance
        WHERE DATE(ts.departure_time) BETWEEN %(from_date)s AND %(to_date)s
          AND ts.docstatus = 1
        GROUP BY ts.ambulance
    """, {"from_date":from_date,"to_date":to_date}, as_dict=True)

    maint = frappe.db.sql("""
        SELECT ambulance,
               COUNT(name)      AS maint_count,
               SUM(total_cost)  AS maint_cost,
               SUM(downtime)    AS downtime_hrs
        FROM `tabAmbulance Maintenance Record`
        WHERE DATE(completion_date) BETWEEN %(from_date)s AND %(to_date)s
          AND docstatus = 1
        GROUP BY ambulance
    """, {"from_date":from_date,"to_date":to_date}, as_dict=True)

    maint_map = {m.ambulance: m for m in maint}
    for t in trips:
        m = maint_map.get(t.ambulance, {})
        t["maint_count"]  = m.get("maint_count", 0)
        t["maint_cost"]   = m.get("maint_cost", 0)
        t["downtime_hrs"] = m.get("downtime_hrs", 0)
    return trips
