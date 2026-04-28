import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class HelplineCallRecord(Document):

    def validate(self):
        self.validate_ambulance_availability()

    def validate_ambulance_availability(self):
        if self.assigned_ambulance:
            status = frappe.db.get_value(
                "Ambulance Master", self.assigned_ambulance, "operational_status"
            )
            if status not in ("Available",):
                frappe.throw(f"Ambulance {self.assigned_ambulance} is {status}. Cannot assign.")

    def on_submit(self):
        """On submit: update ambulance status + create dispatch record."""
        if self.assigned_ambulance:
            frappe.db.set_value(
                "Ambulance Master",
                self.assigned_ambulance,
                "operational_status", "On Trip"
            )
            self.create_dispatch_record()

    def create_dispatch_record(self):
        dispatch = frappe.new_doc("Ambulance Dispatch")
        dispatch.helpline_call = self.name
        dispatch.dispatch_datetime = now_datetime()
        dispatch.assigned_ambulance = self.assigned_ambulance
        dispatch.dispatch_station = frappe.db.get_value(
            "Ambulance Master", self.assigned_ambulance, "home_station"
        )
        dispatch.dispatch_mode = "Manual"
        dispatch.dispatch_status = "Assigned"
        dispatch.insert(ignore_permissions=True)
        frappe.db.commit()

    def on_cancel(self):
        if self.assigned_ambulance:
            frappe.db.set_value(
                "Ambulance Master",
                self.assigned_ambulance,
                "operational_status", "Available"
            )
