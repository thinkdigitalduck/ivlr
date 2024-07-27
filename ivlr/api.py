import frappe


@frappe.whitelist()
def make_absent_on_leave():
    settings = frappe.get_doc('IVLR Setting')
    
    for i in settings.month:
        dd = frappe.db.sql(f"""
            SELECT
                adt.employee,
                adt.attendance_date,
                adt.name,
                adt.status,
                adt.leave_type,
                sh.custom_how_many_day_should_make_as,
                ROW_NUMBER() OVER (PARTITION BY adt.employee ORDER BY adt.attendance_date) AS rn
            FROM
                `tabAttendance` adt
            LEFT JOIN
                `tabShift Type` sh on sh.name = adt.shift
            WHERE
                (adt.status = 'Absent' OR adt.status = 'On Leave')
                AND adt.attendance_date BETWEEN '{i.start_date}' AND '{i.end_date}'
            ORDER BY
                adt.employee,
                adt.attendance_date;
        """, as_dict=1)
        
        employee_absence_count = {}
        
        for record in dd:
            employee = record['employee']
            
            if employee not in employee_absence_count:
                employee_absence_count[employee] = {'on_leave': 0, 'absent': 0}
            
            if record['status'] == 'On Leave' and record['leave_type'] == 'Week off':
                employee_absence_count[employee]['on_leave'] = employee_absence_count[employee]['on_leave'] +  1
                
            elif record['status'] == 'Absent':
                employee_absence_count[employee]['absent'] = employee_absence_count[employee]['absent'] + 1
        
        for record in dd:
            if record['custom_how_many_day_should_make_as']:
                employee = record['employee']
                frappe.log(employee_absence_count[employee])  
                if record['status'] == 'Absent' and employee_absence_count[employee]['on_leave'] < int(record['custom_how_many_day_should_make_as']):
                    frappe.db.set_value('Attendance', record['name'], {'status': 'On Leave', 'leave_type': 'Week off'})
                    frappe.db.commit()
                    employee_absence_count[employee]['on_leave'] = employee_absence_count[employee]['on_leave'] + 1
                    employee_absence_count[employee]['absent'] = employee_absence_count[employee]['absent'] - 1
                    frappe.log(record)

    frappe.msgprint('done')


@frappe.whitelist()
def mark_on_leave_every_shift_end():
    date =  frappe.utils.getdate()
    
    doc = frappe.db.sql(f""" select * from `tabDate table` dt where  dt.end_date = '{date}'    """,as_dict=1)

    for i in doc:
        dd = frappe.db.sql(f"""
                    SELECT
                        adt.employee,
                        adt.attendance_date,
                        adt.name,
                        adt.status,
                        adt.leave_type,
                        sh.custom_how_many_day_should_make_as,
                        ROW_NUMBER() OVER (PARTITION BY adt.employee ORDER BY adt.attendance_date) AS rn
                    FROM
                        `tabAttendance` adt
                    LEFT JOIN
                        `tabShift Type` sh on sh.name = adt.shift
                    WHERE
                        (adt.status = 'Absent' OR adt.status = 'On Leave')
                        AND adt.attendance_date BETWEEN '{i["start_date"]}' AND '{i["end_date"]}'
                    ORDER BY
                        adt.employee,
                        adt.attendance_date;
                """, as_dict=1)
        
        employee_absence_count = {}
        
        for record in dd:
            employee = record['employee']
            
            if employee not in employee_absence_count:
                employee_absence_count[employee] = {'on_leave': 0, 'absent': 0}
            
            if record['status'] == 'On Leave' and record['leave_type'] == 'Week off':
                employee_absence_count[employee]['on_leave'] = employee_absence_count[employee]['on_leave'] +  1
                
            elif record['status'] == 'Absent':
                employee_absence_count[employee]['absent'] = employee_absence_count[employee]['absent'] + 1
        
        for record in dd:
            if record['custom_how_many_day_should_make_as']:
                employee = record['employee']
                frappe.log(employee_absence_count[employee])  
                
                if record['status'] == 'Absent' and employee_absence_count[employee]['on_leave'] < int(record['custom_how_many_day_should_make_as']):
                    frappe.db.set_value('Attendance', record['name'], {'status': 'On Leave', 'leave_type': 'Week off'})
                    frappe.db.commit()
                    employee_absence_count[employee]['on_leave'] = employee_absence_count[employee]['on_leave'] + 1
                    employee_absence_count[employee]['absent'] = employee_absence_count[employee]['absent'] - 1
                    frappe.log(record)
                    
                    
                    
                    
                
                
                
            
            
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    