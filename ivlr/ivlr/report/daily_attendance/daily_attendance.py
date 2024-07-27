import frappe
from datetime import datetime, timedelta
from frappe import _

# Define status mapping
status_mapping = {
    "Present": "P",
    "Absent": "A",
    "Half Day": "HD",
    "Work From Home": "WFH",
    "On Leave": "L",
    "Holiday": "H",
    "Weekly Off": "WO"
}

def get_date_range(from_date, to_date):
    start_date = datetime.strptime(from_date, "%Y-%m-%d")
    end_date = datetime.strptime(to_date, "%Y-%m-%d")
    date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
    return [(date.strftime("%Y-%m-%d"), date.strftime("%d-%b")) for date in date_range]

def get_shifts(company, employee=None):
    filters = {"company": company}
    if employee:
        filters["employee"] = employee  # Correct filter field for employee name
    return frappe.get_all("Employee", filters=filters, fields=['name',"employee_name", "default_shift"])

def get_default_holiday_list(company):
    return frappe.get_cached_value("Company", company, "default_holiday_list")

def get_holiday_map(filters):
    company = filters["company"]
    from_date = filters["from_date"]
    to_date = filters["to_date"]
    
    holiday_lists = frappe.db.get_all("Holiday List", pluck="name")
    default_holiday_list = get_default_holiday_list(company)
    if default_holiday_list:
        holiday_lists.append(default_holiday_list)

    holiday_map = frappe._dict()

    for d in holiday_lists:
        if not d:
            continue

        holidays = frappe.get_all("Holiday",
                                   filters={"parent": d,
                                            "holiday_date": [">=", from_date],
                                            "holiday_date": ["<=", to_date]},
                                   fields=["holiday_date", "weekly_off"])
        for holiday in holidays:
            holiday_date = holiday["holiday_date"].strftime("%Y-%m-%d")
            holiday_map[holiday_date] = holiday.get("weekly_off", False)

    return holiday_map

def get_columns_for_days(filters, holiday_map):
    total_days = (datetime.strptime(filters["to_date"], "%Y-%m-%d") - datetime.strptime(filters["from_date"], "%Y-%m-%d")).days + 1
    days = []

    for day in range(total_days):
        date_obj = datetime.strptime(filters["from_date"], "%Y-%m-%d") + timedelta(days=day)
        date = date_obj.strftime("%Y-%m-%d")
        day_of_week = date_obj.strftime("%a")  # Get the abbreviated day of the week
        label = f"{date_obj.strftime('%d')} {day_of_week}"
        is_holiday = date in holiday_map
        days.append({"label": label, "fieldname": date, "fieldtype": "Data", "width": 75, "is_holiday": is_holiday})

    return days

def get_employee_attendance(employee_name, from_date, to_date):
    attendance_records = frappe.db.get_all("Attendance",
                                           filters={"employee_name": employee_name,
                                                    "attendance_date": [">=", from_date],
                                                    "attendance_date": ["<=", to_date]},
                                           fields=["attendance_date", "status"])
    
    attendance_data = {}
    for record in attendance_records:
        attendance_date = record.get("attendance_date").strftime("%Y-%m-%d")
        attendance_status = record.get("status")
        attendance_data[attendance_date] = status_mapping.get(attendance_status, "A")  # Use status mapping, default to "A"
    
    return attendance_data

def execute(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    company = filters.get("company")
    employee = filters.get("employee")  

    columns = [
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Shift", "fieldname": "default_shift", "fieldtype": "Data", "width": 150},
    ]

    if filters.group_by:
        options_mapping = {
            "Branch": "Branch",
            "Grade": "Employee Grade",
            "Department": "Department",
            "Designation": "Designation",
        }
        options = options_mapping.get(filters.group_by)
        columns.append(
            {
                "label": _(filters.group_by),
                "fieldname": frappe.scrub(filters.group_by),
                "fieldtype": "Link",
                "options": options,
                "width": 120,
            }
        )

    holiday_map = get_holiday_map(filters)
    columns += get_columns_for_days(filters, holiday_map)

    date_range = get_date_range(from_date, to_date)

    data = []
    shifts = get_shifts(company, employee)
    for shift in shifts:
        employee_data = {
            "employee_name": shift.employee_name,
            "default_shift": shift.default_shift,
        }
        if filters.group_by:
            employee_data.update({
                frappe.scrub(filters.group_by):frappe.get_value('Employee',shift.name,frappe.scrub(filters.group_by))
            })
        attendance_data = get_employee_attendance(shift.employee_name, from_date, to_date)
        for date, month_abbr in date_range:
            is_holiday = date in holiday_map
            if is_holiday:
                employee_data[date] = status_mapping["Holiday"]
            else:
                employee_data[date] = attendance_data.get(date, status_mapping["Absent"])  # Default to "A" if no record
        data.append(employee_data)

    return columns, data

# Example usage
filters = {
    "from_date": "2024-05-01",
    "to_date": "2024-05-31",
    "company": "Your Company Name",
    "employee": "John Doe"  # Specify an employee name if you want to filter by a specific employee
}
