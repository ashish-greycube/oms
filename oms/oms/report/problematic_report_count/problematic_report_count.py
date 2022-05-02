# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns=get_columns()
	data=get_data(filters)
	return columns, data


def get_columns():
	columns = [
		{"fieldname": "so_item_name", "label": _("so_item_name"), "fieldtype": "Data", "width": 170},
	]
	return columns		

def get_data(filters):
	warehouse=filters.get('warehouse')
	if warehouse == 1:
		report_conditions = " so_item.warehouse = '' or so_item.warehouse is NULL "
	else:
		report_conditions = " so_item.warehouse is NOT NULL and so_item.warehouse!=''"

	query_output=frappe.db.sql(
		"""
-- Order Created Date, Client, Program, Country(Destination), Brand, Product Name
-- only submit
SELECT so_item.name  as so_item_name from `tabSales Order` as so 
inner join `tabSales Order Item` as so_item 
on so.name =so_item.parent 
where {report_conditions} """.format(report_conditions=report_conditions,as_dict=1,debug=1))	
	return query_output	
