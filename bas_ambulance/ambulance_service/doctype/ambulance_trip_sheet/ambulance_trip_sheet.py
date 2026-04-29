import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_seconds


class AmbulanceTripSheet(Document):

    def validate(self):
        self.compute_response_time()
        self.compute_distance()

    def compute_response_time(self):
        if self.departure_time and self.scene_arrival_time:
            diff = time_diff_in_seconds(self.scene_arrival_time, self.departure_time)
            self.response_time_min = round(diff / 60, 2)
        if self.departure_time and self.return_to_base_time:
            diff = time_diff_in_seconds(self.return_to_base_time, self.departure_time)
            self.total_duration_min = round(diff / 60, 2)

    def compute_distance(self):
        if self.odometer_start and self.odometer_end:
            self.distance_covered = round(self.odometer_end - self.odometer_start, 2)

    def on_submit(self):
        """On approval: release ambulance back to available."""
        if self.trip_status == "Approved":
            frappe.db.set_value(
                "Ambulance Master",
                self.ambulance,
                "operational_status", "Available"
            )
        if self.incident_flagged:
            self.create_incident_report()

    def create_incident_report(self):
        if frappe.db.exists("Incident Report", {"trip_sheet": self.name}):
            return
        inc = frappe.new_doc("Incident Report")
        inc.trip_sheet = self.name
        inc.incident_datetime = self.hospital_arrival_time or frappe.utils.now_datetime()
        inc.status = "Reported"
        inc.insert(ignore_permissions=True)
        frappe.msgprint(f"Incident Report {inc.name} created automatically.")

    def on_update_after_submit(self):
        """Update helpline call billing status."""
        if self.billing_status == "Billed" and self.helpline_call:
            frappe.db.set_value(
                "Helpline Call Record",
                self.helpline_call,
                "call_status", "Completed"
            )
