// Copyright (c) 2024, vps and contributors
// For license information, please see license.txt

frappe.ui.form.on('IVLR Setting', {
	mark_on_leave: function(frm) {



		frappe.call({
			method: 'ivlr.api.make_absent_on_leave',
			callback: function(r) {
				if (!r.exc) {
					// code snippet
					console.log(r)
				}
			}
		});




		
	}
});
