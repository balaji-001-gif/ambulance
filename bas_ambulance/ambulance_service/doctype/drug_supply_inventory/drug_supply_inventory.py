import frappe
from frappe.model.document import Document
from frappe.utils import today, date_diff

class DrugSupplyInventory(Document):
    pass

def check_expiry_and_stock():
    """Daily job: flag expired drugs and low-stock items."""
    items = frappe.get_all("Drug Supply Inventory",
        fields=["name","item_name","expiry_date","quantity_in_stock",
                "minimum_stock_level","stock_status"])

    for item in items:
        new_status = item.stock_status
        if item.expiry_date and date_diff(today(), item.expiry_date) >= 0:
            new_status = "Expired"
        elif item.quantity_in_stock == 0:
            new_status = "Out of Stock"
        elif item.quantity_in_stock <= item.minimum_stock_level:
            new_status = "Low Stock"
        else:
            new_status = "Adequate"

        if new_status != item.stock_status:
            frappe.db.set_value("Drug Supply Inventory",
                item.name, "stock_status", new_status)
            if new_status in ("Low Stock", "Out of Stock", "Expired"):
                frappe.sendmail(
                    recipients=frappe.get_all("User",
                        filters={"role_profile_name": "Fleet Manager"},
                        pluck="email"),
                    subject=f"Drug Alert: {item.item_name} — {new_status}",
                    message=f"Item {item.item_name} is now <b>{new_status}</b>. Please replenish immediately.",
                )
    frappe.db.commit()

def update_stock_status(doc, method=None):
    """before_save hook."""
    if doc.expiry_date and date_diff(today(), doc.expiry_date) >= 0:
        doc.stock_status = "Expired"
    elif doc.quantity_in_stock == 0:
        doc.stock_status = "Out of Stock"
    elif doc.quantity_in_stock <= doc.minimum_stock_level:
        doc.stock_status = "Low Stock"
    else:
        doc.stock_status = "Adequate"
