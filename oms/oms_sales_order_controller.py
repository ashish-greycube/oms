

from erpnext.selling.doctype.sales_order.sales_order import SalesOrder
import frappe
from frappe import _
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html

class WarehouseRequired(frappe.ValidationError):
    pass

class CustomSalesOrder(SalesOrder):
    def validate_warehouse(self):
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