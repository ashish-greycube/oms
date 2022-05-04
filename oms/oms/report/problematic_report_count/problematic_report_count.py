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

@frappe.whitelist()
def get_so_count(warehouse):
	print('warehouse'*10,warehouse,warehouse == 1)
	if warehouse == '1':
		report_conditions = " so_item.warehouse = '' or so_item.warehouse is NULL "
	else:
		report_conditions = " so_item.warehouse is NOT NULL and so_item.warehouse!=''"

	query_output=frappe.db.sql(
		"""
-- Order Created Date, Client, Program, Country(Destination), Brand, Product Name
-- only submit
SELECT count(so_item.name) from `tabSales Order` as so 
inner join `tabSales Order Item` as so_item 
on so.name =so_item.parent 
where {report_conditions} """.format(report_conditions=report_conditions,as_dict=1,debug=1))
	print(query_output)	
	return query_output		

@frappe.whitelist()
def get_all_so_count():	
	company = frappe.db.get_single_value("Global Defaults", "default_company")

	print('--'*10)
	query_output=frappe.db.sql(
		"""
-- Order Created Date, Client, Program, Country(Destination), Brand, Product Name
-- only submit
SELECT count(so_item.name) as count from `tabSales Order` as so 
inner join `tabSales Order Item` as so_item 
on so.name =so_item.parent 
where  so.status='Draft' and (so_item.warehouse = '' or so_item.warehouse is NULL)
and so.company=%s
""",company,as_dict=1)	

	next_query_output=frappe.db.sql(
		"""
-- Order Created Date, Client, Program, Country(Destination), Brand, Product Name
-- only submit
SELECT count(so_item.name) as count from `tabSales Order` as so 
inner join `tabSales Order Item` as so_item 
on so.name =so_item.parent 
where  so.status='Draft' and (so_item.warehouse is NOT NULL and so_item.warehouse!='')
and so.company=%s
""",company,as_dict=1)
	print('query_output',query_output)
	print('next_query_output',next_query_output)
	query_output.append(next_query_output[0])
	print(query_output)
	return query_output