# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class CourierAssignmentRule(Document):
	def validate(self):
		self.validate_duplicate_courier_assignment()

	def validate_duplicate_courier_assignment(self):
		courier_assignment_list = []
		for d in self.courier_assignment_detail:
			value_to_check=[d.courier,d.courier_service_type]
			if value_to_check not in courier_assignment_list:
				courier_assignment_list.append(value_to_check)
			else:
				frappe.throw(
					_("Row {0}: Courier {1} : Service Type {2} added multiple times").format(
						d.idx, frappe.bold(d.courier),frappe.bold(d.courier_service_type)
					)
				)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_service_type(doctype, txt, searchfield, start, page_len, filters):
	if filters and filters.get('courier'):
		cond = "'%s'" % filters.get('courier')
		return frappe.db.sql("""select service_type from `tabCourier Rate Card`
				where courier = {cond}
				order by name limit %(start)s, %(page_len)s"""
				.format(cond=cond), {
					'start': start, 'page_len': page_len
				})