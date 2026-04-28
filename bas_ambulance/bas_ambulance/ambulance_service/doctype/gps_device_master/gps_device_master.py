import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_seconds, now_datetime

class GPSDeviceMaster(Document):
    pass

def check_offline_devices():
    """Scheduled job to mark devices inactive if they haven't pinged in 24h."""
    devices = frappe.get_all("GPS Device Master", 
                             filters={"device_status": "Active"}, 
                             fields=["name", "last_ping_time"])
    
    for dev in devices:
        if dev.last_ping_time:
            diff = time_diff_in_seconds(now_datetime(), dev.last_ping_time)
            if diff > 86400: # 24 hours
                frappe.db.set_value("GPS Device Master", dev.name, "device_status", "Inactive")
    frappe.db.commit()
