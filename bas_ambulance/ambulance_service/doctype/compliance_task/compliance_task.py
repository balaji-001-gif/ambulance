import frappe
from frappe.model.document import Document
from frappe.utils import today, date_diff

class ComplianceTask(Document):

    def before_save(self):
        self.compute_penalty()

    def compute_penalty(self):
        if self.due_date and self.status not in ("Completed", "Waived"):
            days = date_diff(today(), self.due_date)
            self.days_overdue = max(0, days)
            if self.penalty_per_day:
                self.estimated_penalty = self.days_overdue * self.penalty_per_day
        else:
            self.days_overdue = 0
            self.estimated_penalty = 0


def auto_mark_overdue():
    """Scheduled daily: move past-due tasks to Overdue status."""
    overdue_tasks = frappe.get_all("Compliance Task",
        filters={
            "status": ["in", ["Open","Assigned","In Progress"]],
            "due_date": ["<", today()],
        },
        fields=["name","penalty_per_day","due_date"])

    for t in overdue_tasks:
        days = date_diff(today(), t.due_date)
        penalty = days * (t.penalty_per_day or 0)
        frappe.db.set_value("Compliance Task", t.name, {
            "status": "Overdue",
            "days_overdue": days,
            "estimated_penalty": penalty,
        })
    frappe.db.commit()
