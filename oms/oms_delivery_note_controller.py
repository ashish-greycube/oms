import json
import frappe
from frappe import _
from frappe.utils import flt, getdate,get_date_str,has_common
import json

def set_courier_as_per_assignment_rule(self,method):
	if self.docstatus==0:
		if self.get("items"):
			courier_based_on_criteria=find_courier_based_on_creiteria(self.items[0].name,self.total_net_weight)
			print('courier_based_on_criteria'*100,courier_based_on_criteria)
			if len(courier_based_on_criteria)>0:
				# self.courier_cf=courier_based_on_criteria[0].courier
				# self.courier_service_type_cf=courier_based_on_criteria[0].courier_service_type
				# self.courier_charge_cf=courier_based_on_criteria[0].rate
				frappe.msgprint(_("Courier <b>{0}</b> of service type <b>{1}</b> with rate {2} is set")
				.format(courier_based_on_criteria[0].courier,courier_based_on_criteria[0].courier_service_type,frappe.bold(courier_based_on_criteria[0].rate)),alert=1,indicator="yellow")  
				frappe.db.set_value('Delivery Note', self.name, 'courier_cf', courier_based_on_criteria[0].courier)
				frappe.db.set_value('Delivery Note', self.name, 'courier_service_type_cf', courier_based_on_criteria[0].courier_service_type)
				frappe.db.set_value('Delivery Note', self.name, 'courier_charge_cf', courier_based_on_criteria[0].rate or 0)
			else:
				frappe.msgprint(_("No matching courier details found for item {0}").format(frappe.bold(self.items[0].item_name)),alert=1,indicator="red")  


def find_courier_based_on_creiteria(dn_item_name,total_net_weight):
	result_data=[]
	find_DN_matching_courier_rule=[]
	report_conditions = " AND DN_item.name = '%s' " % (dn_item_name)
	courier_rules_field=['order_created_date','country','order_warehouse','client','program','brand','product','product_margin','length','width','height','volume','weight']
	doctype_field =	{
					'order_created_date': 'SO.transaction_date',
					'country':'address.country',
					'order_warehouse': 'DN_item.warehouse',
					'client':'DN.customer',
					'program': 'DN.project',
					'brand':'item.brand ',
					'product':'DN_item.item_code',
					'product_margin': 'SO_item.gross_profit',
					'length':'item.length_cf',
					'width':'item.width_cf',
					'height':'item.height_cf',
					'volume':'item.volume_cf',
					'weight':'DN.total_net_weight'
					}
	courier_rules=frappe.db.get_list('Courier Assignment Rule',filters={'disable': '0'},fields=['name'], order_by='creation desc',as_list=False)
	item_weights=" where weight_slab.upto_weight_in_kg >=%s " % (total_net_weight)

	for doc in courier_rules:
		rules_conditions = ""
		rules_filter_values = {}		
		rule=frappe.get_doc('Courier Assignment Rule',doc.name).as_dict()
		for assignment_field in courier_rules_field:
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
		print('rules_conditions',rules_conditions)
		find_DN_matching_courier_rule=delivery_note_query(report_conditions,rules_conditions,rules_filter_values)
		print('find_DN_matching_courier_rule',find_DN_matching_courier_rule)

		if len(find_DN_matching_courier_rule)>0:
			break

	# case A: found courier based on courier assignment rule
	if len(find_DN_matching_courier_rule)>0:
		i=1
		for data in find_DN_matching_courier_rule:
			if i==2:
				break
			frappe.msgprint(_("Courier Assignment Rule {0} is applied.").format(frappe.bold(rule.name)),alert=1,indicator="green")                
			data.update({"courier":rule.supplier})
			data.update({"courier_service_type":rule.courier_service_type})
			rate=get_rate_based_on_courier_detail(item_weights,data.get('source_country'),data.get('destination_country'),rule.supplier,rule.courier_service_type)
			if len(rate)>0:
				data.update({"rate":rate[0].rate})
			result_data.append(data)
			i=i+1
	print('hhhhhhhhhhhhhhhhhhhhhhhhhhhresult_data',result_data)
	# case B: not found A, find courier based on Courier Rate Card
	if len(result_data)==0:
		DN_matching_courier_rate_card=courier_rate_card_query(report_conditions,item_weights)
		if len(DN_matching_courier_rate_card) >0 :
			frappe.msgprint(_("Courier Rate Card {0} is applied.").format(frappe.bold(DN_matching_courier_rate_card[0].courier_rate_card_name)),alert=1,indicator="blue")
			print('DN_matching_courier_rate_card',DN_matching_courier_rate_card)
			# result_data.append({"courier":DN_matching_courier_rate_card[0].courier})
			# result_data.append({"courier_service_type":DN_matching_courier_rate_card[0].service_type})		
			# result_data.append({"rate":DN_matching_courier_rate_card[0].rate})	
			result_data.append(DN_matching_courier_rate_card[0])	
	return result_data	       

#  case A : to find rate for courier assignment rule
def get_rate_based_on_courier_detail(item_weights,source_country,destination_country,courier,courier_service_type):
	order_by_result=frappe.db.sql("""select 
										case courier_criteria  
										when 'Least Price' THEN 'weight_slab.rate'
										when 'Least Duration' THEN 'courier_service_type.maximum_days'
										when 'Tracking Available' THEN 'courier_service_type.is_tracking_available'
										END as courier_criteria
										from `tabAuto Courier Assignment Priority`
										order by idx ASC""",as_dict=1)
	print('order_by_result',order_by_result)
	order_by_list = [d.courier_criteria for d in order_by_result]
	print('order_by_list',order_by_list)
	order_by_condition="order by " +", ".join(order_by_list)

	query_output=frappe.db.sql("""select weight_slab.upto_weight_in_kg ,weight_slab.rate ,courier_service_type.is_tracking_available , courier_service_type.maximum_days ,
									courier_rate_card.courier,courier_rate_card.service_type,
									courier_rate_card.source_country, courier_rate_card.destination_country, courier_rate_card.maximum_weight_allowed_in_kg, 
									courier_rate_card.maximum_height_allowed_in_mm, courier_rate_card.maximum_width_allowed_in_mm, courier_rate_card.maximum_length_allowed_in_mm 
									from `tabCourier Rate Card` courier_rate_card
									inner join `tabCourier Service Type` courier_service_type
									on courier_rate_card.service_type =courier_service_type.name 
									inner join `tabCourier Rate Weight Slab` weight_slab 
									on weight_slab.parent=courier_rate_card.name
									{item_weights} 
									and courier_rate_card.source_country =%s
									and courier_rate_card.destination_country =%s
									and courier_rate_card.courier=%s
									and courier_rate_card.service_type=%s
									{order_by_condition}
									limit 1"""
									.format(item_weights=item_weights,order_by_condition=order_by_condition),(source_country,destination_country,courier,courier_service_type),as_dict=1,debug=1)
	return query_output		

# case B : find matching courier rate card
def courier_rate_card_query(report_conditions,item_weights):
	order_by_result=frappe.db.sql("""select 
										case courier_criteria  
										when 'Least Price' THEN 'courier_detail.rate'
										when 'Least Duration' THEN 'courier_detail.maximum_days'
										when 'Tracking Available' THEN 'courier_detail.is_tracking_available'
										END as courier_criteria
										from `tabAuto Courier Assignment Priority`
										order by idx ASC""",as_dict=1)
	print('order_by_result',order_by_result)
	order_by_list = [d.courier_criteria for d in order_by_result]
	print('order_by_list',order_by_list)
	order_by_condition="order by " +", ".join(order_by_list)
	# order_by_condition="order by " + ", ".join(["%s"] * len(order_by_list))
	print('xxx----------order_by_condition',order_by_condition)
	query_output=frappe.db.sql("""with 
									courier_detail as (select weight_slab.upto_weight_in_kg ,weight_slab.rate ,courier_service_type.is_tracking_available , courier_service_type.maximum_days ,
									courier_rate_card.name,courier_rate_card.courier,courier_rate_card.service_type,
									courier_rate_card.source_country, courier_rate_card.destination_country, courier_rate_card.maximum_weight_allowed_in_kg, 
									courier_rate_card.maximum_height_allowed_in_mm, courier_rate_card.maximum_width_allowed_in_mm, courier_rate_card.maximum_length_allowed_in_mm 
									from `tabCourier Rate Card` courier_rate_card
									inner join `tabCourier Service Type` courier_service_type
									on courier_rate_card.service_type =courier_service_type.name 
									inner join `tabCourier Rate Weight Slab` weight_slab 
									on weight_slab.parent=courier_rate_card.name 
									{item_weights}
									),
									dn_detail as (SELECT 
									DN.name as dn_name,
									address.country as destination_country,
									item.length_cf as length_cf,
									item.width_cf as width,
									item.height_cf as height,
									DN.total_net_weight as weight,
									warehouse.country_cf as source_country
									FROM `tabDelivery Note`  DN 
									left outer join `tabAddress` address
									on address.name =DN.shipping_address_name 
									inner join `tabDelivery Note Item` DN_item 
									on DN.name =DN_item.parent
									inner join `tabWarehouse` warehouse 
									on warehouse.name = DN_item.warehouse
									inner join  `tabItem` item 
									on DN_item.item_code =item.item_code 
									where DN.docstatus=0   {report_conditions}
									)
									select courier_detail.name as courier_rate_card_name, courier_detail.courier as courier,courier_detail.service_type  as courier_service_type, dn_detail.weight , courier_detail.maximum_weight_allowed_in_kg,
									courier_detail.is_tracking_available,courier_detail.maximum_days,courier_detail.upto_weight_in_kg, courier_detail.rate as rate
									from courier_detail join dn_detail
									where 
									courier_detail.source_country =dn_detail.source_country 
									and courier_detail.destination_country =dn_detail.destination_country 
									and IF(courier_detail.maximum_weight_allowed_in_kg, dn_detail.weight <= courier_detail.maximum_weight_allowed_in_kg,1=1)
									and IF(courier_detail.maximum_height_allowed_in_mm,dn_detail.height <= courier_detail.maximum_height_allowed_in_mm ,1=1)
									and IF(courier_detail.maximum_length_allowed_in_mm,dn_detail.length_cf <= courier_detail.maximum_length_allowed_in_mm ,1=1)
									and IF(courier_detail.maximum_width_allowed_in_mm, dn_detail.width <= courier_detail.maximum_width_allowed_in_mm ,1=1)
									{order_by_condition}
									limit 1"""
									.format(report_conditions=report_conditions,item_weights=item_weights,order_by_condition=order_by_condition),as_dict=1,debug=1)
	return query_output	

# case A : check if DN matched the defined courier assignment rules
def delivery_note_query(report_conditions,rules_conditions,rules_filter_values):
	print("report_conditions,rules_filter_values,rules_conditions")
	print(report_conditions,rules_filter_values,rules_conditions)
	query_output=frappe.db.sql("""SELECT 
									DN.name as dn_name,
									SO.transaction_date as order_created_date,
									address.country as destination_country,
									warehouse.country_cf as source_country,
									DN_item.warehouse as dn_item_warehouse,
									DN.customer as client,
									DN.project  as program,
									item.brand as brand,
									DN_item.name as dn_item_hex_name,
									DN_item.item_code as product,
									DN_item.item_name as product_name,
									SO_item.gross_profit as product_margin,
									item.length_cf as length,
									item.width_cf as width,
									item.height_cf as height,
									item.volume_cf as volume,
									DN.total_net_weight as weight
									FROM `tabDelivery Note`  DN 
									left outer join `tabAddress` address
									on address.name =DN.shipping_address_name 
									inner join `tabDelivery Note Item` DN_item 
									on DN.name =DN_item.parent
									inner join `tabSales Order` SO 
									on SO.name=DN_item.against_sales_order 
									inner join `tabSales Order Item` SO_item 
									on SO_item.name = DN_item.so_detail 
									inner join `tabWarehouse` warehouse 
									on warehouse.name = DN_item.warehouse
									inner join  `tabItem` item 
									on DN_item.item_code =item.item_code 
									where DN.docstatus=0 
									{report_conditions} {rules_conditions} limit 1"""
									.format(report_conditions=report_conditions,rules_conditions=rules_conditions),rules_filter_values,as_dict=1,debug=1)
	return query_output	    

def compare_shipping_charges_against_courier_charges(self,method):
	# print(frappe.form.dict["cmd"])
	courier_manager=frappe.db.get_single_value('OMS Settings', 'courier_manager')
	account_head=frappe.db.get_single_value('OMS Settings', 'shipping_charge_account')
	print('-'*10,self.items[0].against_sales_order)
	query_output=frappe.db.sql("""select tax_amount from `tabSales Taxes and Charges` 
				where parent=%s and charge_type ='Actual'and account_head =%s""",(self.name,account_head),as_dict=1,debug=1) 		
	print('query_output'*10,query_output,query_output[0].tax_amount,self.courier_charge_cf)
	if len(query_output)>0:
		customer_shipping_fee=query_output[0].tax_amount
		if self.courier_charge_cf>customer_shipping_fee:
			if not courier_manager or courier_manager not in frappe.get_roles(): 
				frappe.throw(_("Courier charge is {0}, which is greater than customer shipping fee {1}")
				.format(frappe.bold(self.courier_charge_cf),frappe.bold(customer_shipping_fee)))
			else:
				if not frappe.flags.compare_shipping_charges_against_courier_charges:
					frappe.msgprint(
						msg=frappe._(
							"Courier charge is <b> {} </b>, which is greater than customer shipping fee <b> {} </b>.<br> Do you want to proceed with this change?"
						).format(self.courier_charge_cf, customer_shipping_fee),
						title="Mismatch between courier and shipping charges.",
						primary_action={
							"label": frappe._("Yes, Proceed"),
							"server_action": "oms.oms_delivery_note_controller.override_charge_mismatch",
							"args":{
								"delivery_note": self.name,
							}						
						},
						raise_exception=frappe.ValidationError,
					)					

@frappe.whitelist()
def override_charge_mismatch(args):
	args = json.loads(args)
	frappe.flags.compare_shipping_charges_against_courier_charges=True
	print('pass')
	doc = frappe.get_doc('Delivery Note', args.get("delivery_note"))
	doc.submit()

	# raise frappe.ValidationError
