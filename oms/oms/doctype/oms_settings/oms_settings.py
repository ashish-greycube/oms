# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class OMSSettings(Document):
	def validate(self):
		unqiue_values=[]
		for item in self.auto_courier_assignment_priority:
			if item.courier_criteria not in unqiue_values:
				unqiue_values.append(item.courier_criteria)
			else:
				frappe.throw(_("Courier Criteria {0} is already used. You cannot duplicate it.").format( frappe.bold(item.courier_criteria)))
