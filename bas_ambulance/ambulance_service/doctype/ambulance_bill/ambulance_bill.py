import frappe
from frappe.model.document import Document

class AmbulanceBill(Document):

    def validate(self):
        self.compute_amounts()

    def compute_amounts(self):
        gross = sum(row.amount for row in self.service_charges)
        self.gross_amount = gross
        discount = self.discount_amount or (gross * (self.discount_pct or 0) / 100)
        self.discount_amount = round(discount, 2)
        self.net_amount = round(gross - discount, 2)
        self.balance_due = round(self.net_amount - (self.advance_received or 0), 2)

    def on_submit(self):
        """Create ERPNext Sales Invoice on submit."""
        if self.billing_mode not in ("Free", "Waived", "Government Scheme"):
            self.create_sales_invoice()
        frappe.db.set_value("Ambulance Trip Sheet",
            self.trip_sheet, "billing_status", "Billed")

    def create_sales_invoice(self):
        si = frappe.new_doc("Sales Invoice")
        si.customer = self.corporate_client or self.insurance_company or "Cash Customer"
        si.due_date = self.bill_date
        si.append("items", {
            "item_code": "AMB-SERVICE",
            "item_name": "Ambulance Service",
            "qty": 1,
            "rate": self.net_amount,
        })
        si.insert(ignore_permissions=True)
        self.erpnext_sales_invoice = si.name
        self.db_update()
