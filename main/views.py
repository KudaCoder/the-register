from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.template.loader import render_to_string
from django.template import RequestContext
from django.db.models import Count, Q
from django.contrib import messages

from dateutil.relativedelta import *
from datetime import datetime, timedelta
import time

from main.utils.docPrint import docPrint
from main.utils.search import search
from .forms import CreateUserForm
from main.models import *



def main(request):
	main_start = time.time()
	currentDate = datetime.now().date()
	currentYear = currentDate.strftime('%Y')
	currentMonth = currentDate.strftime('%m')

	certObj = Certificate.objects.all()
	epcCount = certObj.filter(type__type='EPC').count()
	tm44Count = certObj.filter(type__type='TM44').count()
	decCount = certObj.filter(type__type='DEC').count()

	epcExpiryData = []
	tm44ExpiryData = []
	decExpiryData = []

	prev_half_year = currentDate - relativedelta(months=6)
	next_half_year = currentDate + relativedelta(months=6)

	expiryObj = certObj.filter(expiry__range=[prev_half_year, next_half_year])
	# raw("""SELECT c.id, count(c.id) as Quantity, to_char(expiry, 'YYYY.mm') as Expiry from certificate as c
	# 	join type as t on t.id = c.type_id
	# 	where expiry >= (now() - interval '6' month)
	# 	and expiry <= (now() + interval '6' month)
	# 	group by expiry, t.type, c.id
	# 	order by expiry asc""")
	
	for entry in expiryObj:
		if entry.type.type == 'EPC':
			epcExpiryData.append(entry.Quantity)
		elif entry.type.type == 'TM44':
			tm44ExpiryData.append(entry.Quantity)
		elif entry.type.type == 'DEC':
			decExpiryData.append(entry.Quantity)

	if 'current_month' in request.POST:
		titles = []
		INdata = []
		linkType = []

		searchObj = Certificate.objects.raw("""SELECT * from certificate 
			where YEAR(expiry) = YEAR(CURRENT_DATE()) and MONTH(expiry) = MONTH(CURRENT_DATE()) """)

		titles.extend(['', 'RRN', 'Site Address', 'Certificate Type', 'Assessor Name', 'Expiry Date'])

		for entry in searchObj:
			expiry = search.extract_date(object, entry.expiry)
			temp_dict = {}
			temp_dict = {'entry1': entry.rrn.rrn, 'entry2': entry.site.address, 'entry3': entry.type.type, 'entry4': entry.assessor.name, 'entry5': expiry}
			INdata.append(temp_dict)

		postData = []
		plus_one_month = datetime.now().date() + relativedelta(months=+1)
		temp_dict = {'query': '', 'queryType1': 'postcode', 'query2': datetime.now().date(), 'queryType2': 'expiry_before', 'query3': plus_one_month,'queryType3': 'expiry_after'}
		postData.append(temp_dict)

		linkType = 'rrn'

		context = {
			'INdata': INdata,
			'linkType': linkType,
			'titles': titles,
			'postData': postData,
		}

		return render(request, 'main/database.html', context)

	else:
		context = {
		'epcCount': epcCount,
		'tm44Count': tm44Count,
		'decCount': decCount,
		'epcExpiryData': epcExpiryData,
		'tm44ExpiryData': tm44ExpiryData,
		'decExpiryData': decExpiryData,
		}

	main_end_time = time.time() - main_start
	print(main_end_time)
	return render(request, 'main/main.html', context)

@login_required(login_url='login')
def database(request):
	db_start = time.time()

	base_qs = Certificate.objects.all().exclude(type__id=3)

	if request.method == 'POST' and 'print_doc' in request.POST:
		rrnList = request.POST.getlist("radio_check")
		outDoc = docPrint(base_qs, rrnList)
		
		return render(request, 'main/database.html', {})

	# # THIS SECTION APPLIES USER QUERIES TO VARIABLES AND RETURNS THEM AS 'POSTDATA' TO PRE-FILL SEARCH QUERY FORM
	elif request.method == "POST":
		query = request.POST.get("search_query")
		query2 = request.POST.get("search_query2")
		query3 = request.POST.get("search_query3")
		queryType1 = request.POST.get('Category1')
		queryType2 = request.POST.get('Category2')
		queryType3 = request.POST.get('Category3')

		postData = []
		temp_dict = {'query': query, 'query2': query2, 'query3': query3, 'queryType1': queryType1, 'queryType2': queryType2, 'queryType3': queryType3}
		postData.append(temp_dict)

		if request.POST.get('restrict'):
			restrict = False
		else:
			restrict = True

		OUTdata = search(base_qs, query, query2, query3, queryType1, queryType2, queryType3, restrict)

		# # CREATE CLASS OBJECT IN UTILS/SEARCH.PY/'SEARCH' TO COMPILE SEARCH OUTPUT AS ONE DICTIONARY AND DYNAMICALLY CREATE THE HTML TO SUIT OUTPUT 
		INdata = OUTdata.combinedData
		titles = OUTdata.titles
		linkType = OUTdata.linkType

		context = {
			'INdata': INdata,
			'titles': titles,
			'linkType': linkType,
			'postData': postData,
		}

		db_end_time = time.time() - db_start
		print(db_end_time)
		return render(request, 'main/database.html', context)
	else:
		return render(request, 'main/database.html', {})

def rrn(request, rrn):
	rrnData = []

	searchObj = Certificate.objects.all().filter(rrn__rrn=rrn)

	for entry in searchObj:
		postcode = entry.postcode.postcode
		complexity = entry.complexity.rating
		employer = entry.employer.name
		employerAddress = entry.employer.address
		assessor = entry.assessor.name
		accred_number = entry.assessor.scheme_number
		scheme = entry.scheme.accred_scheme
		area = entry.building_area
		site = entry.site.address

		if site.split(',') == []:
			address_line_1 = site
			address_line_2 = ''
			address_line_3 = ''
			address_line_4 = ''
		else:
			address_parts = site.split(',')
			address_line_1 = address_parts[0].strip()

			try:
				address_line_2 = address_parts[1].strip()
			except:
				address_line_2 = ''
			try:
				address_line_3 = address_parts[2].strip()
			except:
				address_line_3 = ''
			try:
				address_line_4 = address_parts[3].strip()
			except:
				address_line_4 = ''

		# SET THE FIELDS WHICH ARE SHARED BY ALL CERTIFICATES
		temp_dict = {'rrn': rrn, 'postcode': postcode, 'site': site, 'complexity': complexity, 'employer': employer, 'employerAddress': employerAddress, 
		'assessor': assessor, 'number': accred_number, 'scheme': scheme, 'expiry': entry.expiry, 'area': area, 'address_line_1': address_line_1, 'address_line_2': address_line_2, 
		'address_line_3': address_line_3, 'address_line_4': address_line_4}

		# SET THE ADDITIONAL FIELDS SPECIFIC TO EPCs
		if entry.type.type == 'EPC':
			certType = 'EPC'
			heating = entry.heating.type
			environ = entry.environment.type
			rating = entry.epc_rating
			emissions = entry.building_emissions
			energy = entry.energy_usage

			epc_dict = {'certType': certType, 'heating': heating, 'environment': environ, 'rating': rating, 'emissions': emissions, 'energy': energy}
			temp_dict.update(epc_dict)
			
		# SET THE ADDITIONAL FIELDS SPECIFIC TO TM44s
		elif entry.type.type == 'TM44':
			certType = 'TM44'
			manager = entry.manager
			refrig = entry.refrig_weight
			ac = entry.ac_output

			tm44_dict = {'certType': certType, 'ac': ac, 'refrig': refrig, 'manager': manager}
			temp_dict.update(tm44_dict)
			
		rrnData.append(temp_dict)

	if request.method == 'POST' and 'edit' in request.POST:
		typeData = []
		typeObj = Type.objects.all()
		for entry in typeObj:
			temp_dict = {}
			temp_dict = {'type': entry.type}
			typeData.append(temp_dict)

		schemeData = []
		schemeObj = Scheme.objects.all()
		for entry in schemeObj:
			temp_dict = {}
			temp_dict = {'scheme': entry.accred_scheme}
			schemeData.append(temp_dict)

		compData = []
		compObj = Complexity.objects.all()
		for entry in compObj:
			temp_dict = {}
			temp_dict = {'comp': entry.rating}
			compData.append(temp_dict)

		envData = []
		envObj = Environment.objects.all()
		for entry in envObj:
			temp_dict = {}
			temp_dict = {'environment': entry.type}
			envData.append(temp_dict)

		heatData = []
		heatObj = Heating.objects.all()
		for entry in heatObj:
			temp_dict = {}
			temp_dict = {'heating': entry.type}
			heatData.append(temp_dict)

		context = {
			'data': rrnData,
			'typeData': typeData,
			'schemeData': schemeData,
			'compData': compData,
			'envData': envData,
			'heatData': heatData,
		}

		return render(request, 'main/edit.html', context)

	# Need to add exceptions and redirects if no data or incorrect data has been input
	# This section checks if the radio buttons have been checked and then updates DB by input value
	elif request.method == 'POST' and 'change' in request.POST:
		certObj = Certificate.objects.get(rrn__rrn=rrn)
		rrnID = certObj.rrn_id

		check_list = []

		# Add regex to ensure RRN is entered in correct format
		if request.POST.get("rrn_check"):
			check_list.append('rrn_check')
			new_rrn = request.POST.get('rrn')

			r = Certificate.objects.get(rrn_id=rrnID)
			r.rrn.rrn = new_rrn
			r.save()

			r2 = {'rrn': new_rrn}
			for entry in rrnData:
				entry.update(r2)

		if request.POST.get("type_check"):
			new_type = request.POST.get('type')
			typeObj = Type.objects.get(type=new_type)
			newTypeID = typeObj.id

			t = Certificate.objects.get(rrn_id=rrnID)
			t.type_id = newTypeID
			t.save()

			t2 = {'certType': new_type}
			for entry in rrnData:
				entry.update(t2)

		# Add check for duplicates
		if request.POST.get("site_check"):
			new_site = request.POST.get('site')

			s = Certificate.objects.get(rrn_id=rrnID)
			s.site.address = new_site
			s.save()

			s2 = {'site': new_site}
			for entry in rrnData:
				entry.update(s2)

		# Want to add a check on assessor and number to see if the previous name/number combination is still being used anywhere in the DB
		# if the Certificate.assessor_id was changed instead of the Assessor table values
		if request.POST.get("assessor_check"):
			new_assessor = request.POST.get('assessor')

			for entry in rrnData:
				number = entry['number']

			if Assessor.objects.filter(Q(name=new_assessor) & Q(scheme_number=number)):
				assessorObj = Certificate.objects.get(Q(assessor__name=new_assessor) & Q(assessor__scheme_number=number))
				newAssessorID = assessorObj.assessor_id

				a = Certificate.objects.get(rrn_id=rrnID)
				a.assessor_id = newAssessorID
				a.save()

				a2 = {'assessor': new_assessor}
				for entry in rrnData:
					entry.update(a2)

			# Want this to only change the name for this certificate so may need to create new assessor with new name and existing number
			# Currently changes all certificates with the existing assessor name
			else:
				a = Certificate.objects.get(rrn_id=rrnID)
				a.assessor.name = new_assessor
				a.save()

				a2 = {'assessor': new_assessor}
				for entry in rrnData:
					entry.update(a2)

		if request.POST.get("number_check"):
			new_number = request.POST.get('number')

			for entry in rrnData:
				assessor = entry['assessor']

			if Assessor.objects.filter(Q(scheme_number=new_number) & Q(name=assessor)):
				numberObj = Certificate.objects.get(Q(assessor__scheme_number=new_number) & Q(assessor__name=assessor))
				newNumberID = numberObj.assessor_id

				n = Certificate.objects.get(rrn_id=rrnID)
				n.assessor_id = newAssessorID
				n.save()

				n2 = {'number': new_number}
				for entry in rrnData:
					entry.update(n2)

			else:
				n = Certificate.objects.get(rrn_id=rrnID)
				n.assessor.scheme_number = new_number
				n.save()

				n2 = {'number': new_number}
				for entry in rrnData:
					entry.update(n2)

		if request.POST.get("scheme_check"):
			new_scheme = request.POST.get('scheme')
			schemeObj = Scheme.objects.get(accred_scheme=new_scheme)
			newSchemeID = schemeObj.id

			sch = Certificate.objects.get(rrn_id=rrnID)
			sch.scheme_id = newSchemeID
			sch.save()

			sch2 = {'scheme': new_scheme}
			for entry in rrnData:
				entry.update(sch2)

		if request.POST.get("expiry_check"):
			new_expiry = request.POST.get('expiry')
			try:
				dateObj = dt.datetime.strptime(new_expiry, '%m/%d/%Y').date()
				exp = Certificate.objects.get(rrn_id=rrnID)
				exp.expiry = dateObj
				exp.save()

				exp2 = {'expiry': dateObj}
				for entry in rrnData:
					entry.update(exp2)
			except:
				# Add section to return to edit page with warning that date format is incorrect
				pass

		if request.POST.get("comp_check"):
			new_comp = request.POST.get('complexity')
			compObj = Complexity.objects.get(rating=new_comp)
			newCompID = compObj.id

			c = Certificate.objects.get(rrn_id=rrnID)
			c.complexity_id = newCompID
			c.save()

			c2 = {'complexity': new_comp}
			for entry in rrnData:
				entry.update(c2)

		if request.POST.get("area_check"):
			new_area = request.POST.get('area')

			areaObj = Certificate.objects.get(rrn_id=rrnID)
			areaObj.building_area = new_area
			areaObj.save()

			area2 = {'area': new_area}
			for entry in rrnData:
				entry.update(area2)

		if request.POST.get("emp_check"):
			new_emp = request.POST.get('employer')

			for entry in rrnData:
				employerAddress = entry['employerAddress']

			if Employer.objects.filter(Q(name=new_emp) & Q(address=employerAddress)):
				employerObj = Certificate.objects.get(Q(employer__name=new_emp) & Q(employer__address=employerAddress))
				newEmployerID = employerObj.employer_id

				e = Certificate.objects.get(rrn_id=rrnID)
				e.employer_id = newEmployerID
				e.save()

				e2 = {'employer': new_emp}
				for entry in rrnData:
					entry.update(e2)

			else:
				e = Certificate.objects.get(rrn_id=rrnID)
				e.employer.name = new_emp
				e.save()

				e2 = {'employer': new_emp}
				for entry in rrnData:
					entry.update(e2)

		if request.POST.get("empAdd_check"):
			new_empAdd = request.POST.get('empAdd')

			for entry in rrnData:
				employer = entry['employer']

			if Employer.objects.filter(Q(name=employer) & Q(address=new_empAdd)):
				employerObj = Certificate.objects.get(Q(employer__name=employer) & Q(employer__address=new_empAdd))
				newEmployerID = employerObj.employer_id

				emp = Certificate.objects.get(rrn_id=rrnID)
				emp.employer_id = newEmployerID
				emp.save()

				emp2 = {'employerAddress': new_empAdd}
				for entry in rrnData:
					entry.update(emp2)

			else:
				emp = Certificate.objects.get(rrn_id=rrnID)
				emp.employer.address = new_empAdd
				emp.save()

				emp2 = {'employerAddress': new_empAdd}
				for entry in rrnData:
					entry.update(emp2)

		if request.POST.get("rating_check"):
			new_rating = request.POST.get('rating')

			ratingObj = Certificate.objects.get(rrn_id=rrnID)
			ratingObj.epc_rating = new_rating
			ratingObj.save()

		if request.POST.get("env_check"):
			new_env = request.POST.get('environment')
			envObj = Environment.objects.get(environment__type=new_env)
			newEnvID = envObj.id

			env = Certificate.objects.get(rrn_id=rrnID)
			env.environment_id = newEnvID
			env.save()

			env2 = {'environment': new_env}
			for entry in rrnData:
				entry.update(env2)

		context = {
			'rrnData': rrnData,
		}

		return render(request, 'main/rrn.html', context)

	elif request.method == 'POST' and 'return' in request.POST:
		context = {
			'rrnData': rrnData,
		}

		return render(request, 'main/rrn.html', context)

	else:
		context = {
			'rrnData': rrnData,
		}

		return render(request, 'main/rrn.html', context) # Is this way to complex with too many DB calls??

def assessor(request, assessor):
	return render(request, 'main/assessor.html', {})

def loginPage(request):
	if request.POST:
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			request.session.set_expiry(0)
			try:
				return redirect(request.POST.get('next'))
			except:
				return redirect('main')
		else:
			messages.info(request, 'Username OR Password is Incorrect!')

	return render(request, 'main/login.html', {})

def logoutUser(request):
	logout(request)
	return redirect('login')

def register(request):
	form = CreateUserForm()
	
	if request.method == 'POST':
		form = CreateUserForm(request.POST)

		if form.is_valid():
			form.save()
			return redirect('login')


	return render(request, 'main/register.html', {'form': form})

