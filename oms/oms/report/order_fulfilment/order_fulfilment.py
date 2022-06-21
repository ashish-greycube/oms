# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

from ast import If, IfExp
from distutils.log import debug
import frappe
from frappe import _
from frappe.utils import nowdate
from frappe.utils import flt, getdate,get_date_str
import json

def execute(filters=None):
	if not filters:
		filters.setdefault("posting_date", [nowdate(), nowdate()])
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{"fieldname": "so_name", "label": _("Order #"), "fieldtype": "Link","options": "Sales Order", "width": 170},
		{"fieldname": "po_no", "label": _("Order Ref #"), "fieldtype": "Link","options": "Sales Order", "width": 150},
		{"fieldname": "transaction_date", "label": _("Order Date"), "fieldtype": "Date", "width": 150},
		{"fieldname": "creation", "label": _("Order Created Date"), "fieldtype": "Date", "width": 170},
		{"fieldname": "client", "label": _("Client"), "fieldtype": "Link","options": "Customer", "width": 120},
		{"fieldname": "program", "label": _("Program"), "fieldtype": "Link","options": "Project", "width": 120},
		{"fieldname": "status", "label": _("Order Status"), "fieldtype": "Data", "width": 150},
		{"fieldname": "marked_shipped", "label": _("Marked Shipped?"), "fieldtype": "Select","options": "No/nYes", "width": 150},
		{"fieldname": "notes_cf", "label": _("Notes"), "fieldtype": "Small Text", "width": 150},
		{"fieldname": "contact_phone", "label": _("Phone #"), "fieldtype": "Data", "width": 150},
		{"fieldname": "contact_email", "label": _("Email"), "fieldtype": "Data", "width": 150},
		{"fieldname": "city", "label": _("City"), "fieldtype": "Data", "width": 150},
		{"fieldname": "state", "label": _("State"), "fieldtype": "Data", "width": 150},
		{"fieldname": "country", "label": _("Country"), "fieldtype": "Data", "width": 150},
		{"fieldname": "pincode", "label": _("Zip Code"), "fieldtype": "Data", "width": 150},
		{"fieldname": "address_line1", "label": _("Address Line 1"), "fieldtype": "Data", "width": 150},
		{"fieldname": "address_line2", "label": _("Address Line 2"), "fieldtype": "Data", "width": 150},
		{"fieldname": "idx", "label": _("Line Item Sequence #"), "fieldtype": "Int", "width": 170},
		{"fieldname": "cpo_line_no_cf", "label": _("Line Item #"), "fieldtype": "Data", "width": 150},
		{"fieldname": "product_name","label": _("Product Name"),"fieldtype": "Link","options": "Item","width": 120,},	
		{"fieldname": "product_brand","label": _("Product Brand"),"fieldtype": "Link","options": "Brand","width": 120,},
		{"fieldname": "model_no_cf", "label": _("Product Model #"), "fieldtype": "Data", "width": 150},
		{"fieldname": "so_qty", "label": _("Quantity"), "fieldtype": "Float", "width": 150},
		{"fieldname": "serial_no", "label": _("Serial No"), "fieldtype": "Small Text", "width": 150},
		{"fieldname": "so_item_warehouse","label": _("SO Item Warehouse"),"fieldtype": "Link","options": "Warehouse","width": 220,},
		{"fieldname": "stock_uom","label": _("Stock UOM"),"fieldtype": "Link","options": "UOM","width": 100,},		
		{"fieldname": "actual_qty", "label": _("Actual Qty"), "fieldtype": "Float", "width": 100},
		{"fieldname": "applied_fulfilment_rule","label": _("Applied Fulfilment Rule"),"fieldtype": "Link","options": "Fulfilment Center Assignment Rule","width": 220},
		{"fieldname": "fulfilment_rule_result", "label": _("Fulfilment Rule Result"), "fieldtype": "Small Text", "width": 500},
	]
	return columns		

def get_conditions(filters):
	conditions = ""
	conditions += (
		filters.get("order_created_date")
		and " AND SO.transaction_date >= '%s' AND SO.transaction_date <= '%s' "
		% (filters.get("order_created_date")[0], filters.get("order_created_date")[1])
		or ""
	)
	return conditions

def get_data(filters):
	return sales_order_query_with_fulfilment_reuslt(filters)

def sales_order_query_with_fulfilment_reuslt(filters):
	report_conditions = get_conditions(filters)

	show_insufficient_items=filters.get('show_insufficient_items')
	if show_insufficient_items==1:
		report_conditions += " AND SO_item.qty > SO_item.actual_qty AND SO_item.delivered_qty=0"
	else:
		report_conditions += " AND SO_item.actual_qty> SO_item.qty"
			
	warehouse=filters.get('warehouse')
	if warehouse:
		report_conditions += " AND SO_item.warehouse = '%s' " % (warehouse)



	query_output=frappe.db.sql(
		"""
-- Order Created Date, Client, Program, Country(Destination), Brand, Product Name
-- only submit
SELECT 
SO.name as so_name,
SO.po_no as po_no,
SO.transaction_date as transaction_date,
SO.creation as creation,
SO.customer as client,
SO.project as program,
SO.status as status,
IF(SO.per_delivered=100,'Yes','No') as marked_shipped,
SO.notes_cf as notes_cf,
SO.contact_phone as contact_phone,
SO.contact_email as contact_email,
address.city as city,
address.state as state,
address.country as country,
address.pincode as pincode,
address.address_line1 as address_line1,
address.address_line2 as address_line2,
SO_item.idx as idx,
SO_item.cpo_line_no_cf as cpo_line_no_cf,
SO_item.brand as product_brand,
SO_item.model_no_cf as model_no_cf,
SO_item.qty as so_qty,
delivery_note_item.serial_no,
SO_item.item_name as product_name,
SO_item.warehouse as so_item_warehouse,
SO_item.stock_uom as stock_uom,
SO_item.actual_qty as actual_qty ,
SO_item.delivered_qty as delivered_qty,
SO_item.fulfilment_center_assignment_rule_cf as applied_fulfilment_rule,
SO_item.fulfilment_rule_result_cf as fulfilment_rule_result,
SO_item.idx
FROM `tabSales Order` SO 
left outer join `tabAddress` address
on address.name =SO.shipping_address_name 
inner join `tabSales Order Item` SO_item 
on SO.name =SO_item.parent 
inner join  `tabItem` item 
on SO_item.item_code =item.item_code 
inner join `tabItem Default` item_default 
on item.item_code =item_default.parent  
left outer join `tabDelivery Note Item` delivery_note_item
on delivery_note_item.so_detail =SO_item.name
where SO.docstatus=1 {report_conditions} 
order by SO.name desc, SO_item.idx asc
""".format(report_conditions=report_conditions),as_dict=1)
	return query_output		

#  for SO logic	
def sales_order_query(report_conditions,rules_filter_values,rules_conditions):
	query_output=frappe.db.sql(
		"""
-- Order Created Date, Client, Program, Country(Destination), Brand, Product Name
-- only submit
SELECT 
SO.name as so_name,
SO.transaction_date as order_created_date,
SO.customer as client,
SO.project  as program,
address.country as country,
item.brand as brand,
SO_item.name as si_item_hex_name,
SO_item.item_code as product,
SO_item.item_name as product_name,
'' as warehouse,
SO_item.warehouse as so_item_warehouse,
SO_item.base_net_rate as selling_price,
SO_item.valuation_rate  as cost,
item.length_cf as length,
item.width_cf as width,
item.height_cf as height,
item.volume_cf as volume,
item.weight_per_unit as weight,
item_default.default_supplier as supplier,
SO_item.stock_uom as stock_uom,
SO_item.qty as so_qty,
SO_item.actual_qty as actual_qty ,
'' as applied_fulfilment_rule,
SO_item.fulfilment_rule_result_cf as fulfilment_rule_result
FROM `tabSales Order` SO 
left outer join `tabAddress` address
on address.name =SO.shipping_address_name 
inner join `tabSales Order Item` SO_item 
on SO.name =SO_item.parent 
inner join  `tabItem` item 
on SO_item.item_code =item.item_code 
inner join `tabItem Default` item_default 
on item.item_code =item_default.parent  
where SO.docstatus=0 {report_conditions} {rules_conditions} """.format(report_conditions=report_conditions,rules_conditions=rules_conditions),rules_filter_values,as_dict=1)
	return query_output	


def find_warehouse_based_on_creiteria(filters,so_item_name):
	unique_so_name_data=[]
	result_data=[]

	if so_item_name==None:
		report_conditions = get_conditions(filters)
	else:
		report_conditions = " AND SO_item.name = '%s' " % (so_item_name)

	assignment_rules_field=['order_created_date','client','program','country','brand','product','selling_price','cost','length','width','height','volume','weight','supplier']
	doctype_field =	{
					'order_created_date': 'SO.transaction_date',
					'client':'SO.customer',
					'program': 'SO.project',
					'country':'address.country',
					'brand':'item.brand ',
					'product':'SO_item.item_code',
					'selling_price':'SO_item.base_net_rate',
					'cost':'SO_item.valuation_rate ',
					'length':'item.length_cf',
					'width':'item.width_cf',
					'height':'item.height_cf',
					'volume':'item.volume_cf',
					'weight':'item.weight_per_unit',
					'supplier' :'item_default.default_supplier'
					}
	assignment_rules=frappe.db.get_list('Fulfilment Center Assignment Rule',filters={'disable': '0'},fields=['name'], order_by='priority desc',as_list=False)

	for doc in assignment_rules:
		rules_conditions = ""
		rules_filter_values = {}		
		rule=frappe.get_doc('Fulfilment Center Assignment Rule',doc.name).as_dict()
		for assignment_field in assignment_rules_field:
			if rule[assignment_field+'_logic'] != 'NOT USED':
				if rule[assignment_field+'_condition'] == '>' or rule[assignment_field+'_condition'] == '<':
					if assignment_field == 'order_created_date':
						rules_conditions += ' ' + rule[assignment_field+'_logic'] + ' ' + doctype_field[assignment_field] + ' ' + rule[assignment_field+'_condition'] +' %('+ assignment_field+'_value_1)s' 
						rules_filter_values[assignment_field+'_value_1']=get_date_str(rule[assignment_field+'_value_1'])
					else:
						rules_conditions += ' ' + rule[assignment_field+'_logic'] + ' ' + doctype_field[assignment_field] + ' ' + rule[assignment_field+'_condition'] +' %('+ assignment_field+'_value_1)s' 
						rules_filter_values[assignment_field+'_value_1']=flt(rule[assignment_field+'_value_1'])
				elif rule[assignment_field+'_condition'] == 'between':
					if assignment_field == 'order_created_date':
						rules_conditions += ' ' + rule[assignment_field+'_logic'] + ' ' + doctype_field[assignment_field] + ' ' + rule[assignment_field+'_condition'] + ' %('+ assignment_field+'_value_1)s' + ' and ' + '%('+ assignment_field+'_value_2)s' 
						rules_filter_values[assignment_field+'_value_1']=get_date_str(rule[assignment_field+'_value_1'])
						rules_filter_values[assignment_field+'_value_2']=get_date_str(rule[assignment_field+'_value_2'])
					else:
						rules_conditions += ' ' + rule[assignment_field+'_logic'] + ' ' + doctype_field[assignment_field] + ' ' + rule[assignment_field+'_condition'] + ' %('+ assignment_field+'_value_1)s' + ' and ' + '%('+ assignment_field+'_value_2)s' 
						rules_filter_values[assignment_field+'_value_1']=flt(rule[assignment_field+'_value_1'])
						rules_filter_values[assignment_field+'_value_2']=flt(rule[assignment_field+'_value_2'])					
				elif rule[assignment_field+'_condition'] == 'IN' or rule[assignment_field+'_condition'] == 'NOT IN':
					in_values=[]
					for value in rule[assignment_field+'_value_1']:
						in_values.append(value[assignment_field])
					rules_conditions += ' ' + rule[assignment_field+'_logic'] + ' ' + doctype_field[assignment_field] + ' ' + rule[assignment_field+'_condition'] +' ({})' \
						.format(' ,'.join(frappe.db.escape(i) for i in in_values)) 
		find_SO_matching_assignment_rule=sales_order_query(report_conditions,rules_filter_values,rules_conditions,)

		if so_item_name==None:
			for data in find_SO_matching_assignment_rule:
				if filters.get("warehouse"):
					report_filter_warehouse=filters.get("warehouse")
					if rule.for_warehouse == report_filter_warehouse:
						data.update({"warehouse":rule.for_warehouse})
						data.update({"applied_fulfilment_rule":rule.name})
						if data.si_item_hex_name not in unique_so_name_data:
							result_data.append(data)
							unique_so_name_data.append(data.si_item_hex_name)
				else:
					data.update({"warehouse":rule.for_warehouse})
					data.update({"applied_fulfilment_rule":rule.name})
					if data.si_item_hex_name not in unique_so_name_data:
						result_data.append(data)
						unique_so_name_data.append(data.si_item_hex_name)
		else:
			for data in find_SO_matching_assignment_rule:
				data.update({"warehouse":rule.for_warehouse})
				data.update({"applied_fulfilment_rule":rule.name})
				result_data.append(data)


	if so_item_name==None:
		#  SO non covered via fullfilment rule
		find_all_SO_irrespective_of_assignment_rule=sales_order_query(report_conditions,rules_filter_values,rules_conditions="and 1=1",)

		for other_data in find_all_SO_irrespective_of_assignment_rule:
			if other_data.si_item_hex_name not in unique_so_name_data:
				other_data.update({"warehouse":""})
				other_data.update({"applied_fulfilment_rule":"Manual"})				
				result_data.append(other_data)
				unique_so_name_data.append(other_data.si_item_hex_name)

	return result_data	

		