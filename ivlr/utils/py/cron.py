import frappe
import datetime
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from frappe.utils import add_days, today

def earned_leave_allocation():
    el_settings = frappe.get_doc("EL Settings", "EL Settings")
    today = datetime.date.today()
    first_day_of_current_month = today.replace(day=1)
    first_day_of_previous_month = first_day_of_current_month - relativedelta(months=1)
    last_day_of_previous_month = first_day_of_previous_month.replace(day=monthrange(first_day_of_previous_month.year, first_day_of_previous_month.month)[1])
    previous_month = first_day_of_previous_month.month
    previous_year = first_day_of_previous_month.year
    if el_settings and el_settings.leave_type and el_settings.el_slab_type_table:
        branch_value = frappe.db.get_all("EL Slab Table", fields=["branch"], group_by="branch")
        if branch_value:
            for i in branch_value:
                branch_doc = frappe.get_doc("Branch", i.branch)
                if branch_doc and branch_doc.custom_payroll_start_date and branch_doc.custom_payroll_end_date:
                    custom_start_date = branch_doc.custom_payroll_start_date
                    custom_end_date = branch_doc.custom_payroll_end_date
                    # Set the start date to the previous month
                    start_date = datetime.date(previous_year, previous_month, custom_start_date)
                    # Determine the end date based on the conditions
                    if custom_end_date < custom_start_date:
                        end_date = datetime.date(today.year, today.month, custom_end_date)
                    else:
                        end_date = datetime.date(previous_year, previous_month, custom_end_date)
                    today_date = add_days(today(), - 1)
                    if end_date == today_date:
                        emp_list = frappe.db.get_all("Employee", filters={"status": "Active", "branch": i.branch}, fields=["name"])
                        if emp_list:
                            for emp in emp_list:
                                el_leave = 0
                                for el in el_settings.el_slab_type_table:
                                    from_date = add_days(start_date, el.from_present - 1)                                    
                                    to_date = add_days(start_date, el.to_present - 1)                                    
                                    att_list = frappe.db.get_all(
                                        "Attendance",
                                        filters={
                                            "employee": emp.name,
                                            "attendance_date": ["between", [from_date, to_date]],
                                            "status": ["!=", "Present"]
                                        },
                                        fields=["name", "attendance_date"]
                                    )
                                    if att_list and len(att_list):
                                        break
                                    else:
                                        el_leave = el.earned_leave
                                if el_leave > 0:
                                    absent_list = frappe.db.get_all(
                                        "Attendance",
                                        filters={
                                            "employee": emp.name,
                                            "attendance_date": ["between", [start_date, end_date]],
                                            "status": "Absent"
                                        },
                                        fields=["name"]
                                    )
                                    if absent_list:
                                        for absent in absent_list:
                                            if not el_leave:
                                                break
                                            att_doc = frappe.get_doc("Attendance", absent.name)
                                            if att_doc:
                                                frappe.db.set_value("Attendance", absent.name, "status", "On Leave")
                                                frappe.db.set_value("Attendance", absent.name, "leave_type", el_settings.leave_type)
                                                el_leave -= 1