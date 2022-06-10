# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class CustomerProductShippingFees(Document):
	def validate(self):
		query_output=frappe.db.sql("""select name from `tabCustomer Product Shipping Fees`
				where customer=%s and destination_country=%s and item_code=%s and name!=%s
		""",(self.customer,self.destination_country,self.item_code,self.name),as_dict=1,debug=1)
		if len(query_output)>0:
			frappe.throw(_("This is duplicate of {0}").format( frappe.bold(query_output[0].name)))
		return query_output		
