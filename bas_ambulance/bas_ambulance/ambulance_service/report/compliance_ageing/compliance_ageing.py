import frappe
from frappe.utils import today, date_diff

def execute(filters=None):
    return get_columns(), get_data(filters)

def get_columns():
    return [
        {"label":"Task","fieldname":"name","fieldtype":"Link",
         "options":"Compliance Task","width":140},
        {"label":"Type","fieldname":"compliance_type","fieldtype":"Data","width":160},
        {"label":"Reference","fieldname":"reference_document",
         "fieldtype":"Data","width":130},
        {"label":"Due Date","fieldname":"due_date","fieldtype":"Date","width":100},
        {"label":"Status","fieldname":"status","fieldtype":"Data","width":90},
        {"label":"Days Overdue","fieldname":"days_overdue",
         "fieldtype":"Int","width":100},
        {"label":"Penalty/Day","fieldname":"penalty_per_day",
         "fieldtype":"Currency","width":110},
        {"label":"Est. Penalty","fieldname":"estimated_penalty",
         "fieldtype":"Currency","width":120},
        {"label":"Priority","fieldname":"priority","fieldtype":"Data","width":80},
        {"label":"Assigned To","fieldname":"assigned_to",
         "fieldtype":"Link","options":"Employee","width":130},
    ]

def get_data(filters):
    conditions = {}
    if filters.get("status"):
        conditions["status"] = filters["status"]
    else:
        conditions["status"] = ["in", ["Open","Assigned","In Progress","Overdue"]]
    if filters.get("compliance_type"):
        conditions["compliance_type"] = filters["compliance_type"]

    tasks = frappe.get_all("Compliance Task",
        filters=conditions,
        fields=["name","compliance_type","reference_document","due_date",
                "status","days_overdue","penalty_per_day","estimated_penalty",
                "priority","assigned_to"],
        order_by="days_overdue desc")

    # Colour-code by urgency
    for t in tasks:
        days = date_diff(t.due_date, today())
        if t.days_overdue > 0:
            t["_style"] = "background-color: #FADBD8;"  # red
        elif days <= 7:
            t["_style"] = "background-color: #FEF9E7;"  # amber
        else:
            t["_style"] = ""
    return tasks
