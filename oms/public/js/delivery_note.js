frappe.ui.form.on("Delivery Note", {
	validate: function(frm) {
        frappe.db.get_value('OMS Settings', 'OMS Settings', ['shipping_charge_account', 'courier_manager'])
        .then(r => {
            let values = r.message;
            // coureir manager, he can override
            if (frm.doc.courier_charge_cf && values.shipping_charge_account && values.courier_manager && in_list(frappe.user_roles, values.courier_manager)) {
                $.each(frm.doc["taxes"] || [], function(i, row) {
                    if (row.charge_type=='Actual' && row.account_head==values.shipping_charge_account && frm.doc.courier_charge_cf > row.tax_amount) {
                        if (frm.ignore_warning) {
                            return;
                        }                        
                        frappe.validated = false;
                        const warning_html =
                        `<p class="bold">
                            ${__('Are you sure you want to save this document?')}
                        </p>
                        <p>
                            ${__("Courier charge is <b>"+ frm.doc.courier_charge_cf +"</b>, which is greater than customer shipping fee <b>"+ row.tax_amount+"</b>")}
                        </p>`;
                    const message_html = warning_html;
                    let proceed_action = () => {
                        frm.ignore_warning = true;
                        frm.save();
                    };
            
                    frappe.warn(
                        __("Mismatch between courier and shipping charges."),
                        message_html,
                        proceed_action,
                        __("Save Anyway")
                    );                        
                        
                    }
                })
            }
            //  non courier manager, he cannot override
            else{
                $.each(frm.doc["taxes"] || [], function(i, row) {
                    if (row.charge_type=='Actual' && row.account_head==values.shipping_charge_account && frm.doc.courier_charge_cf > row.tax_amount) {
                    const message_html = __("Courier charge is <b>"+ frm.doc.courier_charge_cf +"</b>, which is greater than customer shipping fee <b>"+ row.tax_amount+"</b>");
                    frappe.throw(message_html)
                    }
                })                
            }            
        })

	},
})