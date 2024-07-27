import frappe
from datetime import datetime, time, timedelta

def attendance():
    shift = frappe.get_doc("Shift Type", "General")
    today_date = datetime.today().date()
    emp_list = frappe.get_list("Employee", fields=["name"])

    start_time = (datetime.combine(today_date, time()) + shift.start_time).time()
    end_time = (datetime.combine(today_date, time()) + shift.end_time).time()

    for emp in emp_list:
        employee_name = emp.name

        # Query Employee Checkin records for the specified time range
        checkins = frappe.get_list(
            "Employee Checkin",
            filters={
                "employee": employee_name,
                "time": ["between", [datetime.combine(today_date, start_time), datetime.combine(today_date, end_time)]]
            },
            fields=["name", "time"],
            order_by="time"
        )

        for checkin in checkins:
            checkin_time = checkin.time
            status = ""
            if checkin_time < datetime.combine(today_date, start_time) and  checkin_time > datetime.combine(today_date, end_time):
                status = "Marked"
            else:
                status = "High Risk"

            chk = frappe.get_doc("Employee Checkin" , checkin.name )
            chk.custom_status = status
            chk.save()
            chk.reload()

    frappe.log_error("Attendance Processing Completed", "Attendance")
    return "Attendance processing completed."


import frappe
from datetime import datetime, timedelta

def attendance():
    today_date = datetime.today().date()
    emp_list = frappe.db.get_list("Employee", fields=["name", "default_shift"])
   
    for emp in emp_list:
        employee_name = emp.name
        default_shift = emp.default_shift

        if not default_shift:
            frappe.log_error(f"Employee {employee_name} has no shift enabled", "Shift Error")
        else:
            try:
                shift = frappe.get_doc("Shift Type", default_shift)
                start_datetime = datetime.combine(today_date, (datetime.min + shift.start_time).time())
                end_datetime = datetime.combine(today_date, (datetime.min + shift.end_time).time())
            except frappe.DoesNotExistError:
                frappe.log_error(f"Shift Type '{default_shift}' not found for Employee {employee_name}", "Shift Error")
                continue

            checkins = frappe.get_list(
                "Employee Checkin",
                filters={
                    "employee": employee_name,
                    "time": ["between", [start_datetime, end_datetime]]
                },
                fields=["name", "time"],
                order_by="time"
            )

            if checkins:
                first_checkin = checkins[0]
                last_checkin = checkins[-1]
                        
                first_checkin_time = first_checkin.time
                last_checkin_time = last_checkin.time
                
                # Determine the status based on the conditions
                if first_checkin_time < start_datetime and last_checkin_time > end_datetime:
                    status = "Marked"
                elif first_checkin_time < start_datetime and last_checkin_time < end_datetime:
                    status = "High Risk"
                else:
                    status = "Unmarked"

                for checkin in checkins:
                    chk = frappe.get_doc("Employee Checkin", checkin.name)
                    chk.custom_status = status
                    chk.save()
                    chk.reload()
            else:
                frappe.log_error(f"Employee {employee_name} has no check-ins today", "Check-in Error")

    return "Attendance processing completed."

