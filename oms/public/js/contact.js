frappe.ui.form.on("Contact", {
	after_save: function(frm) {
        if (frm.doc.phone && frm.doc.phone.charAt(0)!='+') {
            frappe.msgprint(__('Phone should start with +'));
        }
        else if(frm.doc.phone && frm.doc.phone.indexOf('-')==-1){
            frappe.msgprint(__("There should be '-' between calling code and phone number. Ex +971-XXXXXXX"))
        }
	}    
})