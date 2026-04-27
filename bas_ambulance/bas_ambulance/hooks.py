app_name = "bas_ambulance"
app_title = "BAS Ambulance Service"
app_publisher = "Antigravity"
app_description = "BAS Ambulance Service Management"
app_email = "admin@example.com"
app_license = "MIT"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be evaluated and added to the global scope
# when the user calls `frappe.init`
# before_install = "bas_ambulance.install.before_install"
# after_install = "bas_ambulance.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "bas_ambulance.uninstall.before_uninstall"
# after_uninstall = "bas_ambulance.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "bas_ambulance.utils.before_app_install"
# after_app_install = "bas_ambulance.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "bas_ambulance.utils.before_app_uninstall"
# after_app_uninstall = "bas_ambulance.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "bas_ambulance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"bas_ambulance.tasks.all"
# 	],
# 	"daily": [
# 		"bas_ambulance.tasks.daily"
# 	],
# 	"hourly": [
# 		"bas_ambulance.tasks.hourly"
# 	],
# 	"weekly": [
# 		"bas_ambulance.tasks.weekly"
# 	],
# 	"monthly": [
# 		"bas_ambulance.tasks.monthly"
# 	],
# }
