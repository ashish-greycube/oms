// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fulfilment Center Assignment Rule', {
	refresh: function (frm) {
		hide_show_all_to_fields(frm)
	},
	order_created_date_condition: function (frm) {
		from_to_fields_setup(frm, 'order_created_date_condition', 'order_created_from_date', 'order_created_to_date', 'Order Date')
	},
	selling_price_condtion: function (frm) {
		from_to_fields_setup(frm, 'selling_price_condtion', 'selling_price_from_value', 'selling_price_to_value', 'Selling Price')
	},
	cost_condition: function (frm) {
		from_to_fields_setup(frm, 'cost_condition', 'cost_from_value', 'cost_to_value', 'Cost')
	},
	length_condition: function (frm) {
		from_to_fields_setup(frm, 'length_condition', 'length_from_value', 'length_to_value', 'Length')
	},
	width_condition: function (frm) {
		from_to_fields_setup(frm, 'width_condition', 'width_from_value', 'width_to_value', 'Width')
	},
	height_condition: function (frm) {
		from_to_fields_setup(frm, 'height_condition', 'height_from_value', 'height_to_value', 'Height')
	},
	volume_condition: function (frm) {
		from_to_fields_setup(frm, 'volume_condition', 'volume_from_value', 'volume_to_value', 'Volume')
	},
	weight_condition: function (frm) {
		from_to_fields_setup(frm, 'weight_condition', 'weight_from_value', 'weight_to_value', 'Weight')
	},
});

function hide_show_all_to_fields(frm) {
	from_to_fields_setup(frm, 'order_created_date_condition', 'order_created_from_date', 'order_created_to_date', 'Order Date')
	from_to_fields_setup(frm, 'selling_price_condtion', 'selling_price_from_value', 'selling_price_to_value', 'Selling Price')
	from_to_fields_setup(frm, 'cost_condition', 'cost_from_value', 'cost_to_value', 'Cost')
	from_to_fields_setup(frm, 'length_condition', 'length_from_value', 'length_to_value', 'Length')
	from_to_fields_setup(frm, 'width_condition', 'width_from_value', 'width_to_value', 'Width')
	from_to_fields_setup(frm, 'height_condition', 'height_from_value', 'height_to_value', 'Height')
	from_to_fields_setup(frm, 'volume_condition', 'volume_from_value', 'volume_to_value', 'Volume')
	from_to_fields_setup(frm, 'weight_condition', 'weight_from_value', 'weight_to_value', 'Weight')
}

function hide_all_to_fields(frm) {
	let to_hide_fields = ["product_blank_value_2", "order_created_to_date", "selling_price_to_value", "cost_to_value",
		"length_to_value", "width_to_value", "height_to_value", "volume_to_value", "weight_to_value"
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