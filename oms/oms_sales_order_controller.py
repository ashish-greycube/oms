

from erpnext.selling.doctype.sales_order.sales_order import SalesOrder
import frappe
from frappe import _
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html
from oms.oms.report.order_fulfilment.order_fulfilment import find_warehouse_based_on_creiteria

class WarehouseRequired(frappe.ValidationError):
    pass

class CustomSalesOrder(SalesOrder):
    def validate_warehouse(self):
        if self.docstatus==0:
            super(SalesOrder, self).validate_warehouse()

            for d in self.get("items"):
                if (
                    (
                        self.has_product_bundle(d.item_code) and self.product_bundle_has_stock_item(d.item_code)
                    )
                    and not d.warehouse
                    and not cint(d.delivered_by_supplier)
                ):
                    frappe.throw(
                        _("Delivery warehouse required for stock item {0}").format(d.item_code), WarehouseRequired)
        else:
            super(CustomSalesOrder, self).validate_warehouse()


def set_warehouse_as_per_fullfilment_rule(self,method):
    print('-'*100)
    output=''
    modified=False
    for d in self.get("items"):
        print('d.name',d.name)
        if  (
                frappe.get_cached_value("Item", d.item_code, "is_stock_item") == 1
                or (self.has_product_bundle(d.item_code) and self.product_bundle_has_stock_item(d.item_code))
            ):
            # case 4: Manual WH set, hence no FR check
            if d.warehouse and (not d.fulfilment_center_assignment_rule_cf):
                fulfilment_rule_result_cf='Manual'
                # frappe.db.set_value('Sales Order Item', d.name, 'fulfilment_rule_result_cf', fulfilment_rule_result_cf)
                d.fulfilment_rule_result_cf=fulfilment_rule_result_cf
                frappe.msgprint(_("Row # {0} : Item {1} , Warehouse is already set. <br> Hence fulfilment result is {2}").format(d.idx,d.item_name,frappe.bold(fulfilment_rule_result_cf)),alert=1,indicator="orange")                
                modified=True
            elif not d.warehouse:
                output=find_warehouse_based_on_creiteria(filters=None,so_item_name=d.name)
                #case 3 : No FR Applicable
                if len(output)==0:
                    fulfilment_rule_result_cf="No FR Applicable"
                    # frappe.db.set_value('Sales Order Item', d.name, 'fulfilment_rule_result_cf', fulfilment_rule_result_cf)
                    d.fulfilment_rule_result_cf=fulfilment_rule_result_cf
                    frappe.msgprint(_("Row # {0} : Item {1} , No matching fulfilment rule found. <br> Hence fulfilment result is {2}").format(d.idx,d.item_name,frappe.bold(fulfilment_rule_result_cf)),alert=1,indicator="red") 
                    modified=True
                #case 1 : Single FR Applied
                elif len(output)==1:
                    warehouse=output[0].warehouse
                    fulfilment_center_assignment_rule_cf=output[0].applied_fulfilment_rule
                    fulfilment_rule_result_cf="Success"
                    d.fulfilment_rule_result_cf=fulfilment_rule_result_cf
                    d.fulfilment_center_assignment_rule_cf=fulfilment_center_assignment_rule_cf
                    d.warehouse=warehouse
                    # frappe.db.set_value('Sales Order Item', d.name, 
                    # {'fulfilment_rule_result_cf':fulfilment_rule_result_cf,
                    # 'fulfilment_center_assignment_rule_cf':fulfilment_center_assignment_rule_cf,
                    # 'warehouse':warehouse
                    # })
                    frappe.msgprint(_("Row # {0} : Item {1} , Fulfilment rule {2} found. <br> Hence warehouse set to {3} and fulfilment result is {4}")
                    .format(d.idx,d.item_name,get_link_to_form('Fulfilment Center Assignment Rule',fulfilment_center_assignment_rule_cf),warehouse,frappe.bold(fulfilment_rule_result_cf)),alert=1,indicator="green")
                    modified=True
                #case 2: Multiple FR Applied
                elif len(output)>1:
                    fulfilment_rule_result_cf=' ,'.join(i.applied_fulfilment_rule+":"+i.warehouse for i in output)
                    fulfilment_rule_result_cf= 'Multiple FR -' + fulfilment_rule_result_cf
                    d.fulfilment_rule_result_cf=fulfilment_rule_result_cf
                    # frappe.db.set_value('Sales Order Item', d.name, 'fulfilment_rule_result_cf',  fulfilment_rule_result_cf)
                    frappe.msgprint(_("Row # {0} : Item {1} , Multiple matching fulfilment rule found. <br> Hence fulfilment result is {2}").format(d.idx,d.item_name,frappe.bold(fulfilment_rule_result_cf)),alert=1,indicator="red") 
                    modified=True                    
    # self.save()    
    # if modified==True:
        # self.reload()
    print(d.name,'output',output)
        
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
""",company,as_dict=1,debug=1)	

	next_query_output=frappe.db.sql(
		"""
-- Order Created Date, Client, Program, Country(Destination), Brand, Product Name
-- only submit
SELECT count(so_item.name) as count from `tabSales Order` as so 
inner join `tabSales Order Item` as so_item 
on so.name =so_item.parent 
where  so.status='Draft' and (so_item.warehouse is NOT NULL and so_item.warehouse!='')
and so.company=%s
""",company,as_dict=1,debug=1)
	print('query_output',query_output)
	print('next_query_output',next_query_output)
	query_output.append(next_query_output[0])
	print(query_output)
	return query_output

def check_order_info_is_sufficient(self,method):
    print('--self.is_order_info_sufficient_cf',self.is_order_info_sufficient_cf)
    if self.is_order_info_sufficient_cf=='No':
        frappe.throw(title='Insufficient Order', msg=_('Sales Order has not all the required information. You cannot submit it.',))   

def check_order_information(self,method):
    insufficient_messages=[]
    country=None
    if self.shipping_address_name==None or self.shipping_address_name=='':
        insufficient_messages.append(_('Shipping address is missing'))
    elif self.shipping_address_name:
        address_line1,city,country=frappe.db.get_value('Address', self.shipping_address_name, ['address_line1','city','country'])
        if address_line1==None or address_line1=='':
            insufficient_messages.append(_('Address Line 1 is missing in shipping address {0}.'.format(self.shipping_address_name))) 
        elif len(cstr(address_line1))<30:
            insufficient_messages.append(_('Address Line 1 length is {0}. It should be greater than 30 characters.').format(len(cstr(address_line1))))
        if city==None or city=='':
            insufficient_messages.append(_('City is missing in shipping address {0}.'.format(self.shipping_address_name)))        
        if country==None or country=='':
            insufficient_messages.append(_('Country is missing in shipping address {0}.'.format(self.shipping_address_name))) 

    if self.contact_phone==None or self.contact_phone=='':
        insufficient_messages.append(_('Contact phone is missing'))
    elif self.contact_phone and country:   
        country_calling_codes_cf = frappe.db.get_value('Country', country, 'country_calling_codes_cf') 
        if country_calling_codes_cf==None or country_calling_codes_cf=='':
            insufficient_messages.append(_('Country calling code is missing in {0}.'.format(country)))   
        else:
            country_code_start=self.contact_phone.find("+")
            country_code_end=self.contact_phone.find("-")   
            if country_code_start==-1:
                insufficient_messages.append(_('Country code in phone number doesnot start with "+" {0}.'.format(self.contact_phone))) 
            elif country_code_end==-1:
                insufficient_messages.append(_('There should be "-" between calling code and phone number. {0}.'.format(self.contact_phone)))
            else:
                country_code_in_phone=self.contact_phone[country_code_start:country_code_end]  
                if country_code_in_phone!= country_calling_codes_cf:
                    insufficient_messages.append(_('Country code in phone number is {0}. It doesnot match code {1} mentioned in country.'
                    .format(country_code_in_phone,country_calling_codes_cf))) 
    print('country',country)
    if country:
        # shipping charges
        shipping_fees=frappe.db.get_list('Customer Product Shipping Fees', filters={'customer': ['=', self.customer], 
                        'destination_country': ['=', country], 'item_code': ['=', self.items[0].item_code]},fields=['shipping_fees'])
        account_head=frappe.db.get_single_value('OMS Settings', 'shipping_charge_account')
        print('shipping_fees',shipping_fees)
        if len(shipping_fees)>0:
            query_output=frappe.db.sql("""select name from `tabSales Taxes and Charges` 
                        where parent=%s and charge_type ='Actual'and account_head =%s""",(self.name,account_head),as_dict=1,debug=1)  
            print('query_output',query_output)    
            if len(query_output)==0:      
                self.append('taxes',{'charge_type':'Actual','account_head':account_head,'tax_amount':shipping_fees[0].shipping_fees,'description':account_head})
        else:
            insufficient_messages.append(_('Shipping fees not found for customer: {0}, destination:{1} and item:{2}.'
            .format(self.customer,country, self.items[0].item_name)))             
                


    if len(insufficient_messages)>0:
        self.is_order_info_sufficient_cf='No'
        self.order_info_insufficient_reason_cf='\n'.join(insufficient_messages) 
    else:
        print('else'*100)
        self.is_order_info_sufficient_cf='Yes'
        self.order_info_insufficient_reason_cf=None
    print('-'*10)
    # self.save()
    print(insufficient_messages,len(insufficient_messages),self.is_order_info_sufficient_cf,self.order_info_insufficient_reason_cf)

