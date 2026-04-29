import frappe
from frappe.utils import today, add_days, date_diff


@frappe.whitelist()
def generate_compliance_calendar():
    """
    Monthly scheduler: auto-create Compliance Tasks for all vehicles,
    stations, and crew members based on seeded templates.
    """
    templates = [
        {"compliance_type": "Vehicle Fitness", "applies_to": "Ambulance Master",
         "trigger_days_before": 45, "penalty_per_day": 500},
        {"compliance_type": "Insurance Renewal", "applies_to": "Ambulance Master",
         "trigger_days_before": 30, "penalty_per_day": 200},
        {"compliance_type": "Vehicle Permit", "applies_to": "Ambulance Master",
         "trigger_days_before": 30, "penalty_per_day": 300},
        {"compliance_type": "PUC Certificate", "applies_to": "Ambulance Master",
         "trigger_days_before": 15, "penalty_per_day": 100},
        {"compliance_type": "Drug License", "applies_to": "Ambulance Station",
         "trigger_days_before": 60, "penalty_per_day": 1000},
        {"compliance_type": "BLS Certification", "applies_to": "Crew Member",
         "trigger_days_before": 60, "penalty_per_day": 0},
        {"compliance_type": "ACLS Certification", "applies_to": "Crew Member",
         "trigger_days_before": 60, "penalty_per_day": 0},
        {"compliance_type": "PALS Certification", "applies_to": "Crew Member",
         "trigger_days_before": 60, "penalty_per_day": 0},
        {"compliance_type": "Driving License", "applies_to": "Crew Member",
         "trigger_days_before": 90, "penalty_per_day": 0},
        {"compliance_type": "Annual Medical Fitness", "applies_to": "Crew Member",
         "trigger_days_before": 30, "penalty_per_day": 0},
        {"compliance_type": "GPS Data Plan", "applies_to": "GPS Device Master",
         "trigger_days_before": 15, "penalty_per_day": 0},
        {"compliance_type": "Govt Contract Renewal", "applies_to": "Government Contract",
         "trigger_days_before": 90, "penalty_per_day": 0},
        {"compliance_type": "SLA Monthly Reporting", "applies_to": "Government Contract",
         "trigger_days_before": 5, "penalty_per_day": 2000},
    ]

    doctype_map = {
        "Ambulance Master": "Ambulance Master",
        "Ambulance Station": "Ambulance Station",
        "Crew Member": "Crew Member",
        "GPS Device Master": "GPS Device Master",
        "Government Contract": "Government Contract",
    }

    for tmpl in templates:
        applies_to = tmpl["applies_to"]
        if applies_to in doctype_map:
            records = frappe.get_all(doctype_map[applies_to], fields=["name"])
        else:
            continue

        for rec in records:
            existing = frappe.db.exists("Compliance Task", {
                "compliance_type": tmpl["compliance_type"],
                "reference_document": rec["name"],
                "status": ["in", ["Open", "Assigned", "In Progress"]],
            })
            if not existing:
                due = add_days(today(), tmpl["trigger_days_before"])
                ct = frappe.new_doc("Compliance Task")
                ct.compliance_type = tmpl["compliance_type"]
                ct.reference_doctype = applies_to
                ct.reference_document = rec["name"]
                ct.due_date = due
                ct.priority = "High"
                ct.penalty_per_day = tmpl["penalty_per_day"]
                ct.status = "Open"
                ct.insert(ignore_permissions=True)
    frappe.db.commit()


@frappe.whitelist()
def get_available_ambulances(station=None, vehicle_type=None):
    """Return list of available ambulances, optionally filtered."""
    filters = {"operational_status": "Available"}
    if station:
        filters["home_station"] = station
    if vehicle_type:
        filters["vehicle_type"] = vehicle_type
    return frappe.get_all(
        "Ambulance Master",
        filters=filters,
        fields=["name", "vehicle_type", "home_station", "registration_number", "current_gps_status"]
    )


@frappe.whitelist()
def get_on_duty_crew(station=None, role=None):
    """Return crew members currently on duty."""
    filters = {"on_duty_status": "On Duty"}
    if station:
        filters["home_station"] = station
    if role:
        filters["role"] = role
    return frappe.get_all(
        "Crew Member",
        filters=filters,
        fields=["name", "crew_member_name", "role", "home_station"]
    )


@frappe.whitelist()
def get_dashboard_stats():
    """Command & Control Room live stats."""
    return {
        "calls_today": frappe.db.count("Helpline Call Record", {
            "call_datetime": ["between", [today() + " 00:00:00", today() + " 23:59:59"]]
        }),
        "active_trips": frappe.db.count("Helpline Call Record", {
            "call_status": ["in", ["Dispatched", "En Route", "On Scene", "Transporting"]]
        }),
        "available_ambulances": frappe.db.count("Ambulance Master", {
            "operational_status": "Available"
        }),
        "overdue_compliance": frappe.db.count("Compliance Task", {
            "status": "Overdue"
        }),
        "missed_calls_today": frappe.db.count("Helpline Call Record", {
            "call_status": "Missed",
            "call_datetime": ["between", [today() + " 00:00:00", today() + " 23:59:59"]]
        }),
    }


def get_call_permission_query(user):
    """Row-level permission: Dispatch Officers see all, Paramedics see assigned only."""
    if "Dispatch Officer" in frappe.get_roles(user):
        return ""
    emp = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if emp:
        return f"`tabHelpline Call Record`.operator_name = '{emp}'"
    return "1=0"
