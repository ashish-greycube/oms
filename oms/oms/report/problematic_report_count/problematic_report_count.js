// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Problematic Report Count"] = {
	"filters": [
		{
			'label': __('Warehouse'),
			'fieldtype': 'Check',
			'fieldname': 'warehouse',
			'default':0			
		},
	]
};
