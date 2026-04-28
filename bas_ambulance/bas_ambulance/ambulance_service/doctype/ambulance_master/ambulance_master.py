import frappe
from frappe.model.document import Document
from frappe.utils import today, date_diff


class AmbulanceMaster(Document):

    def validate(self):
        self.check_document_expiry()
        self.validate_gps_device()

    def check_document_expiry(self):
        """Warn if critical documents are expiring within 30 days."""
        fields_to_check = [
            ("fitness_expiry", "Fitness Certificate"),
            ("insurance_expiry", "Insurance Policy"),
            ("permit_expiry", "Vehicle Permit"),
            ("puc_expiry", "PUC Certificate"),
        ]
        for field, label in fields_to_check:
            expiry = self.get(field)
            if expiry:
                days = date_diff(expiry, today())
                if days < 0:
                    frappe.throw(f"{label} has EXPIRED on {expiry}. Please renew before activating.")
                elif days <= 30:
                    frappe.msgprint(
                        f"Warning: {label} expires in {days} day(s) on {expiry}.",
                        indicator="orange"
                    )

    def validate_gps_device(self):
        if self.gps_device:
            existing = frappe.db.get_value("GPS Device Master", self.gps_device, "assigned_ambulance")
            if existing and existing != self.name:
                frappe.throw(f"GPS Device {self.gps_device} is already assigned to {existing}.")

    def on_update(self):
        """Sync GPS Device assignment."""
        if self.gps_device:
            frappe.db.set_value("GPS Device Master", self.gps_device, "assigned_ambulance", self.name)

    @frappe.whitelist()
    def set_available(self):
        self.operational_status = "Available"
        self.save()
        return "Status updated to Available"

    @frappe.whitelist()
    def set_on_trip(self):
        self.operational_status = "On Trip"
        self.save()
        return "Status updated to On Trip"
