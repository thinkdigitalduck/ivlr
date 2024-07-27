import frappe
from hrms.hr.doctype.shift_type.shift_type import process_auto_attendance_for_all_shifts

@frappe.whitelist()
def custom_process_auto_attendance_for_all_shifts():
    return 'VPS'
