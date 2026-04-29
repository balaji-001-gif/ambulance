import frappe
from frappe.model.document import Document


class AmbulanceStation(Document):

    def validate(self):
        self.update_statistics()

    def update_statistics(self):
        """Compute ambulance and crew counts."""
        self.total_ambulances = frappe.db.count("Ambulance Master", {"home_station": self.name})
        self.ambulances_available = frappe.db.count("Ambulance Master", {
            "home_station": self.name, "operational_status": "Available"
        })
        self.active_crew_count = frappe.db.count("Crew Member", {
            "home_station": self.name, "on_duty_status": "On Duty"
        })
