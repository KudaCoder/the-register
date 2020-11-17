from django.shortcuts import render
from mailmerge import MailMerge
from datetime import datetime
from main.models import *
import os

class docPrint:
	def __init__(self, querySet, rrnList):
		self.date = datetime.today().strftime('%d %B %Y')

		for rrn in rrnList:
			searchObj = querySet.filter(rrn__rrn__icontains=rrn)

			for entry in searchObj:
				postcode = entry.postcode.postcode
				manager = entry.manager
				if not manager:
					manager = 'Manager'
				expiry = entry.expiry
				expiry = datetime.strftime(expiry, '%d %B %Y')
				rrn = entry.rrn.rrn

				address_parts = entry.site.address.split(',')
				try:
					if address_parts[0].strip().upper() != postcode:
						address_line_1 = address_parts[0].strip()
				except:
					pass
				try:
					if address_parts[1].strip().upper() != postcode:
						address_line_2 = address_parts[1].strip()
				except:
					pass
				try:
					if address_parts[2].strip().upper() != postcode:
						address_line_3 = address_parts[2].strip()
				except:
					pass
				try:
					if address_parts[3].strip().upper() != postcode:
						address_line_4 = address_parts[3].strip()
				except:
					pass

				is_line_4 = 'address_line_4' in locals()
				is_line_3 = 'address_line_3' in locals()

				if is_line_4:
					self.address = f'{address_parts[0].title()},{address_parts[1].title()},{address_parts[2].title()},{address_parts[3].title()}, {postcode}'
					self._print(postcode, manager, rrn, self.date, expiry, self.address, address_line_1, address_line_2, address_line_3, address_line_4)
					del address_line_4
				elif is_line_3 and not is_line_4:
					address_line_3 = postcode
					self.address = f'{address_parts[0].title()},{address_parts[1].title()},{address_parts[2].title()}, {postcode}'
					postcode = ''
					self._print(postcode, manager, rrn, self.date, expiry, self.address, address_line_1, address_line_2, address_line_3)
					del address_line_3
				else:
					address_line_3 = postcode
					self.address = f'{address_parts[0].title()},{address_parts[1].title()}, {postcode}'
					postcode = ''
					self._print(postcode, manager, rrn, self.date, expiry, self.address, address_line_1, address_line_2, address_line_3)
		

	def _print(self, postcode, manager, rrn, date, expiry, address, address_line_1, address_line_2, address_line_3='', address_line_4=''):
		template = 'main/docs/expiry_template.docx'

		document = MailMerge(template)

		document.merge(postcode=postcode, manager=manager, rrn=rrn, date=self.date, expiry=expiry, address=self.address, address_line_1=address_line_1, address_line_2=address_line_2, address_line_3=address_line_3, address_line_4=address_line_4)
		home = os.path.expanduser("~")
		download_location = os.path.join(home,'Downloads/letters')
		if not os.path.exists(download_location):
			os.mkdir(download_location)

		document.write(f'{download_location}/{self.address} - Expiry Letter.docx')
			

	