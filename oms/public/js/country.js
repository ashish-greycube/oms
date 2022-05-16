frappe.ui.form.on('Country', {
	validate: function(frm) {
        if (frm.doc.country_calling_codes_cf && frm.doc.country_calling_codes_cf.charAt(0)!='+') {
            frappe.throw(__('Country Calling Codes (ISD) should start with +'))
        }

	}
});