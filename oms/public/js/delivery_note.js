frappe.ui.form.on("Delivery Note", {
	before_submit: function (frm) {
		return frappe.db.get_value('OMS Settings', 'OMS Settings', ['shipping_charge_account', 'courier_manager'])
			.then(r => {
				let values = r.message;

				return new Promise((resolve) => {
					// coureir manager, he can override
                    console.log( in_list(frappe.user_roles, values.courier_manager),frappe.user_roles,values.courier_manager)
					if (frm.doc.courier_charge_cf && values.shipping_charge_account && values.courier_manager && in_list(frappe.user_roles, values.courier_manager)) {
						let is_valid = true;
                        let tax_amount=0;
						$.each(frm.doc["taxes"] || [], function (i, row) {
							if (row.charge_type == 'Actual' && row.account_head == values.shipping_charge_account && frm.doc.courier_charge_cf > row.tax_amount) {
								is_valid = false;
                                tax_amount=row.tax_amount;
							}
						})
						if (!is_valid) {
							frappe.confirm(
								__("Courier charge of <b>" + frm.doc.courier_charge_cf + "</b>, is greater than customer shipping fee of <b>" + tax_amount + "<br> Do you want to continue?"),
								function () {
									console.log('ok');
									resolve();
								},
								function () {
									console.log('not ok');
									frappe.validated = false;
									resolve();
								}
							);
						} else {
							resolve();
						}

					} else {
						//  non courier manager, he cannot override
						let message_html = []
						$.each(frm.doc["taxes"] || [], function (i, row) {
							if (row.charge_type == 'Actual' && row.account_head == values.shipping_charge_account && frm.doc.courier_charge_cf > row.tax_amount) {
								message_html.push(__("Courier charge of <b>" + frm.doc.courier_charge_cf + "</b>, is greater than customer shipping fee of <b>" + row.tax_amount + "</b><br> Please correct it to proceed."));
							}
						})

						if (message_html.length) {
							frappe.validated = false;
							frappe.throw(message_html.join(","))
						}
						resolve();
					}


				})




			})

	},
})