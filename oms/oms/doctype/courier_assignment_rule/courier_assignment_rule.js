// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Courier Assignment Rule', {
	onload: function (frm) {
		frm.set_query('courier_service_type', 'courier_assignment_detail', function (doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			if (row.courier) {
			  return {
				query: "oms.oms.doctype.courier_assignment_rule.courier_assignment_rule.get_service_type",
				filters: {
					courier: row.courier
				}
			  }
			}
		  });
	},
	refresh: function (frm) {
		hide_show_all_to_fields(frm)
	},
	order_created_date_condition: function (frm) {
		from_to_fields_setup(frm, 'order_created_date_condition', 'order_created_date_value_1', 'order_created_date_value_2', 'Order Date')
	},
	product_margin_condition: function (frm) {
		from_to_fields_setup(frm, 'product_margin_condition', 'product_margin_value_1', 'product_margin_value_2', 'Product Margin')
	},
	length_condition: function (frm) {
		from_to_fields_setup(frm, 'length_condition', 'length_value_1', 'length_value_2', 'Length')
	},
	width_condition: function (frm) {
		from_to_fields_setup(frm, 'width_condition', 'width_value_1', 'width_value_2', 'Width')
	},
	height_condition: function (frm) {
		from_to_fields_setup(frm, 'height_condition', 'height_value_1', 'height_value_2', 'Height')
	},
	volume_condition: function (frm) {
		from_to_fields_setup(frm, 'volume_condition', 'volume_value_1', 'volume_value_2', 'Volume')
	},
	weight_condition: function (frm) {
		from_to_fields_setup(frm, 'weight_condition', 'weight_value_1', 'weight_value_2', 'Weight')
	},
});

function hide_show_all_to_fields(frm) {
	$('[data-fieldname=product_blank_value_2]').css("visibility", "hidden");
	from_to_fields_setup(frm, 'order_created_date_condition', 'order_created_date_value_1', 'order_created_date_value_2', 'Order Date')
	from_to_fields_setup(frm, 'product_margin_condition', 'product_margin_value_1', 'product_margin_value_2', 'Product Margin')
	from_to_fields_setup(frm, 'length_condition', 'length_value_1', 'length_value_2', 'Length')
	from_to_fields_setup(frm, 'width_condition', 'width_value_1', 'width_value_2', 'Width')
	from_to_fields_setup(frm, 'height_condition', 'height_value_1', 'height_value_2', 'Height')
	from_to_fields_setup(frm, 'volume_condition', 'volume_value_1', 'volume_value_2', 'Volume')
	from_to_fields_setup(frm, 'weight_condition', 'weight_value_1', 'weight_value_2', 'Weight')
}

function hide_all_to_fields(frm) {
	let to_hide_fields = ["product_blank_value_2", "order_created_date_value_2", "selling_price_value_2", "product_margin_value_2",
		"length_value_2", "width_value_2", "height_value_2", "volume_value_2", "weight_value_2"
	]
	to_hide_fields.forEach(element => {
		$('[data-fieldname=' + element + ']').css("visibility", "hidden");
	});
}

function from_to_fields_setup(frm, field_cond, field_from, field_to, field_label) {
	if (frm.doc[field_cond] == 'between') {
		$('[data-fieldname=' + field_to + ']').css("visibility", "visible");
		frappe.meta.get_docfield(frm.doc.doctype, field_from, frm.doc.name).label = field_label + ' From';
		frappe.meta.get_docfield(frm.doc.doctype, field_to, frm.doc.name).label = field_label + ' To';
	} else if (frm.doc[field_cond] == '>' || frm.doc[field_cond] == '<') {
		$('[data-fieldname=' + field_to + ']').css("visibility", "hidden");
		frappe.meta.get_docfield(frm.doc.doctype, field_from, frm.doc.name).label = field_label + ' Value';
		frappe.meta.get_docfield(frm.doc.doctype, field_to, frm.doc.name).label = '';
	} else {
		$('[data-fieldname=' + field_to + ']').css("visibility", "hidden");
		frappe.meta.get_docfield(frm.doc.doctype, field_from, frm.doc.name).label = field_label + ' Value';
		frappe.meta.get_docfield(frm.doc.doctype, field_to, frm.doc.name).label = '';
	}
	frm.refresh_fields([field_from, field_to])
}