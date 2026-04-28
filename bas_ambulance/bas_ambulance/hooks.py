app_name = "bas_ambulance"
app_title = "BAS Ambulance Service"
app_publisher = "BAS Technologies"
app_description = "Ambulance Service Management Module for ERPNext v15+"
app_email = "admin@bas.in"
app_license = "MIT"

# Document Events
doc_events = {
    "Helpline Call Record": {
        "on_submit": "bas_ambulance.ambulance_service.doctype.helpline_call_record.helpline_call_record.on_submit",
    },
    "Ambulance Trip Sheet": {
        "on_submit": "bas_ambulance.ambulance_service.doctype.ambulance_trip_sheet.ambulance_trip_sheet.on_submit",
        "on_update_after_submit": "bas_ambulance.ambulance_service.doctype.ambulance_trip_sheet.ambulance_trip_sheet.on_update_after_submit",
    },
    "Ambulance Maintenance Record": {
        "on_submit": "bas_ambulance.ambulance_service.doctype.ambulance_maintenance_record.ambulance_maintenance_record.update_ambulance_status",
        "on_cancel": "bas_ambulance.ambulance_service.doctype.ambulance_maintenance_record.ambulance_maintenance_record.reset_ambulance_status",
    },
    "Compliance Task": {
        "before_save": "bas_ambulance.ambulance_service.doctype.compliance_task.compliance_task.compute_penalty",
    },
    "Drug Supply Inventory": {
        "before_save": "bas_ambulance.ambulance_service.doctype.drug_supply_inventory.drug_supply_inventory.update_stock_status",
    },
}

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "bas_ambulance.ambulance_service.doctype.compliance_task.compliance_task.auto_mark_overdue",
        "bas_ambulance.ambulance_service.doctype.drug_supply_inventory.drug_supply_inventory.check_expiry_and_stock",
        "bas_ambulance.ambulance_service.doctype.gps_device_master.gps_device_master.check_offline_devices",
    ],
    "monthly": [
        "bas_ambulance.api.generate_compliance_calendar",
    ],
}

# Fixtures — exported on bench export-fixtures
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "BAS Ambulance Service"]]},
    {
        "dt": "Role",
        "filters": [
            ["name", "in", [
                "Dispatch Officer", "Paramedic", "Fleet Manager",
                "Compliance Officer", "CAD Operator", "Billing Executive",
                "Call Centre Agent", "MMU Coordinator", "Training Officer"
            ]]
        ]
    },
]

# Permissions
permission_query_conditions = {
    "Helpline Call Record": "bas_ambulance.api.get_call_permission_query",
}

override_whitelisted_methods = {}
