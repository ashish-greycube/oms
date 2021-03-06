# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import get_url_to_form

class CustomerProductShippingFees(Document):
	def validate(self):
		query_output=frappe.db.sql("""select name from `tabCustomer Product Shipping Fees`
				where customer=%s and destination_country=%s and item_code=%s and name!=%s
		""",(self.customer,self.destination_country,self.item_code,self.name),as_dict=1)
		if len(query_output)>0:
			frappe.throw(_("Shipping fees already exist for fields {0}, {1}, {2} : <a href={3}><b>link</b></a> ")
			.format(self.customer,self.destination_country,self.item_code,get_url_to_form('Customer Product Shipping Fees',query_output[0].name)))
		return query_output		
