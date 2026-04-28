import frappe
from frappe.utils import getdate

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label":"Trip ID","fieldname":"name","fieldtype":"Link",
         "options":"Ambulance Trip Sheet","width":140},
        {"label":"Helpline","fieldname":"helpline_number","fieldtype":"Data","width":70},
        {"label":"Station","fieldname":"station","fieldtype":"Link",
         "options":"Ambulance Station","width":130},
        {"label":"Ambulance","fieldname":"ambulance","fieldtype":"Link",
         "options":"Ambulance Master","width":110},
        {"label":"Trip Type","fieldname":"trip_type","fieldtype":"Data","width":110},
        {"label":"Response Time (min)","fieldname":"response_time_min",
         "fieldtype":"Float","width":120},
        {"label":"SLA (min)","fieldname":"sla","fieldtype":"Int","width":80},
        {"label":"SLA Status","fieldname":"sla_status","fieldtype":"Data","width":100},
        {"label":"Distance (km)","fieldname":"distance_covered",
         "fieldtype":"Float","width":100},
        {"label":"Departure","fieldname":"departure_time",
         "fieldtype":"Datetime","width":150},
    ]

def get_data(filters):
    conditions = []
    values = {}
    if filters.get("from_date"):
        conditions.append("ts.departure_time >= %(from_date)s")
        values["from_date"] = filters["from_date"] + " 00:00:00"
    if filters.get("to_date"):
        conditions.append("ts.departure_time <= %(to_date)s")
        values["to_date"] = filters["to_date"] + " 23:59:59"
    if filters.get("station"):
        conditions.append("am.home_station = %(station)s")
        values["station"] = filters["station"]
    if filters.get("helpline"):
        conditions.append("cr.helpline_number = %(helpline)s")
        values["helpline"] = filters["helpline"]

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    rows = frappe.db.sql(f"""
        SELECT
            ts.name,
            cr.helpline_number,
            am.home_station AS station,
            ts.ambulance,
            ts.trip_type,
            ts.response_time_min,
            ts.distance_covered,
            ts.departure_time
        FROM `tabAmbulance Trip Sheet` ts
        LEFT JOIN `tabHelpline Call Record` cr ON cr.name = ts.helpline_call
        LEFT JOIN `tabAmbulance Master` am ON am.name = ts.ambulance
        {where}
        ORDER BY ts.departure_time DESC
    """, values=values, as_dict=True)

    sla_map = {"108": 15, "102": 20, "104": None, "112": 15, "1033": 20}
    for r in rows:
        sla = sla_map.get(r.get("helpline_number") or "", 15)
        r["sla"] = sla
        if sla and r.response_time_min:
            r["sla_status"] = "Within SLA" if r.response_time_min <= sla else "Breached"
        else:
            r["sla_status"] = "N/A"
    return rows

def get_filters():
    return [
        {"fieldname":"from_date","label":"From Date","fieldtype":"Date",
         "default":"Today"},
        {"fieldname":"to_date","label":"To Date","fieldtype":"Date",
         "default":"Today"},
        {"fieldname":"station","label":"Station","fieldtype":"Link",
         "options":"Ambulance Station"},
        {"fieldname":"helpline","label":"Helpline","fieldtype":"Select",
         "options":"\n108\n102\n104\n112\n1033\n100\n181"},
    ]
