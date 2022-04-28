

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
                frappe.db.set_value('Sales Order Item', d.name, 'fulfilment_rule_result_cf', fulfilment_rule_result_cf)
                frappe.msgprint(_("Row # {0} : Item {1} , Warehouse is already set. <br> Hence fulfilment result is {2}").format(d.idx,d.item_name,frappe.bold(fulfilment_rule_result_cf)),alert=1,indicator="orange")                
                modified=True
            elif not d.warehouse:
                output=find_warehouse_based_on_creiteria(filters=None,so_item_name=d.name)
                #case 3 : No FR Applicable
                if len(output)==0:
                    fulfilment_rule_result_cf="No FR Applicable"
                    frappe.db.set_value('Sales Order Item', d.name, 'fulfilment_rule_result_cf', fulfilment_rule_result_cf)
                    frappe.msgprint(_("Row # {0} : Item {1} , No matching fulfilment rule found. <br> Hence fulfilment result is {2}").format(d.idx,d.item_name,frappe.bold(fulfilment_rule_result_cf)),alert=1,indicator="red") 
                    modified=True
                #case 1 : Single FR Applied
                elif len(output)==1:
                    warehouse=output[0].warehouse
                    fulfilment_center_assignment_rule_cf=output[0].applied_fulfilment_rule
                    fulfilment_rule_result_cf="Success"
                    frappe.db.set_value('Sales Order Item', d.name, 
                    {'fulfilment_rule_result_cf':fulfilment_rule_result_cf,
                    'fulfilment_center_assignment_rule_cf':fulfilment_center_assignment_rule_cf,
                    'warehouse':warehouse
                    })
                    frappe.msgprint(_("Row # {0} : Item {1} , Fulfilment rule {2} found. <br> Hence warehouse set to {3} and fulfilment result is {4}")
                    .format(d.idx,d.item_name,get_link_to_form('Fulfilment Center Assignment Rule',fulfilment_center_assignment_rule_cf),warehouse,frappe.bold(fulfilment_rule_result_cf)),alert=1,indicator="green")
                    modified=True
                #case 2: Multiple FR Applied
                elif len(output)>1:
                    fulfilment_rule_result_cf=' ,'.join(i.applied_fulfilment_rule+":"+i.warehouse for i in output)
                    frappe.db.set_value('Sales Order Item', d.name, 'fulfilment_rule_result_cf',  fulfilment_rule_result_cf)
                    frappe.msgprint(_("Row # {0} : Item {1} , Multiple matching fulfilment rule found. <br> Hence fulfilment result is {2}").format(d.idx,d.item_name,frappe.bold(fulfilment_rule_result_cf)),alert=1,indicator="red") 
                    modified=True                    
    # self.save()    
    if modified==True:
        self.reload()
    print(d.name,'output',output)
        
