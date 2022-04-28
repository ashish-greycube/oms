// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Order Fulfilment"] = {
	"filters": [
		{
			'fieldname': 'order_created_date',
			'label': __("Date"),
			'fieldtype': 'DateRange',
			'default': [frappe.datetime.nowdate(), frappe.datetime.nowdate()]
		},
		{
			'label': __('Warehouse'),
			'fieldtype': 'Link',
			'fieldname': 'warehouse',
			'options': 'Warehouse',
			get_query: () => {
				return {
					filters: {
						'is_group': 0
					}
				}
			}			
		},		
	]
};
