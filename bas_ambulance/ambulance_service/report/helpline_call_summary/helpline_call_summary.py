import frappe

def execute(filters=None):
    return get_columns(), get_data(filters)

def get_columns():
    return [
        {"label":"Helpline","fieldname":"helpline_number",
         "fieldtype":"Data","width":80},
        {"label":"Received","fieldname":"received","fieldtype":"Int","width":90},
        {"label":"Dispatched","fieldname":"dispatched","fieldtype":"Int","width":100},
        {"label":"Completed","fieldname":"completed","fieldtype":"Int","width":100},
        {"label":"Cancelled","fieldname":"cancelled","fieldtype":"Int","width":100},
        {"label":"Missed","fieldname":"missed","fieldtype":"Int","width":80},
        {"label":"Dispatch Rate %","fieldname":"dispatch_rate",
         "fieldtype":"Float","width":110},
        {"label":"Avg Response (min)","fieldname":"avg_response",
         "fieldtype":"Float","width":130},
    ]

def get_data(filters):
    from_date = filters.get("from_date", frappe.utils.today())
    to_date   = filters.get("to_date",   frappe.utils.today())

    rows = frappe.db.sql("""
        SELECT
            cr.helpline_number,
            COUNT(*) AS received,
            SUM(cr.call_status IN ('Dispatched','En Route','On Scene',
                                   'Transporting','Completed')) AS dispatched,
            SUM(cr.call_status = 'Completed') AS completed,
            SUM(cr.call_status = 'Cancelled') AS cancelled,
            SUM(cr.call_status = 'Missed')    AS missed,
            ROUND(AVG(ts.response_time_min), 2) AS avg_response
        FROM `tabHelpline Call Record` cr
        LEFT JOIN `tabAmbulance Trip Sheet` ts ON ts.helpline_call = cr.name
        WHERE DATE(cr.call_datetime) BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY cr.helpline_number
        ORDER BY received DESC
    """, {"from_date": from_date, "to_date": to_date}, as_dict=True)

    for r in rows:
        r["dispatch_rate"] = round(
            (r.dispatched / r.received * 100) if r.received else 0, 1)
    return rows
