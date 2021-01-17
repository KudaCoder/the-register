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
import sys

from main.utils.docPrint import docPrint
from main.utils.search import search
from .forms import CreateUserForm
from main.models import *



def main(request):
	main_start = time.time()

	# Setting global date objects for later use
	currentDate = datetime.now().date()
	currentYear = currentDate.strftime('%Y')
	currentMonth = currentDate.strftime('%m')
	prev_half_year = currentDate - relativedelta(months=6)
	next_half_year = currentDate + relativedelta(months=6)
	plus_one_month = currentDate + relativedelta(months=1)

	# Main queryset
	certObj = Certificate.objects.all()

	epcCount = certObj.filter(type__id=1).count()
	tm44Count = certObj.filter(type__id=4).count()
	decCount = certObj.filter(Q(type__id=2) | Q(type__id=3)).count()

	epcExpiryData = []
	tm44ExpiryData = []
	decExpiryData = []

	# Querset to return all rows with an expiry date +/- 6 months from current month then separate into 3 lists of EPC, TM44 & DEC
	expiryObj = certObj.filter(expiry__range=[prev_half_year, next_half_year]).values_list('expiry__year', 'expiry__month', 'type__type').annotate(Count('type__id')).order_by('expiry__year') # expiryObj returns 3 element tuple
	prev_half_year = currentDate - relativedelta(months=6)
	next_half_year = currentDate + relativedelta(months=6)

	expiryObj = certObj.filter(expiry__range=[prev_half_year, next_half_year]).values_list('expiry__year', 'expiry__month', 'type__type').annotate(Count('type__id')).order_by('expiry__year')

	for entry in expiryObj:
		if 'EPC' in entry:
			epcExpiryData.append(entry[3])
		elif 'TM44' in entry:
			tm44ExpiryData.append(entry[3])
		elif 'DEC' in entry:
			decExpiryData.append(entry[3])

	# If show current month button pressed on main page
	if 'current_month' in request.POST:
		titles = []
		INdata = []
		linkType = []

		# Queryset to return all rows with an expiry date in the current month & year
		searchObj = certObj.filter(Q(expiry__month=currentMonth) & Q(expiry__year=currentYear)).exclude(type_id=3).order_by('-expiry')[:1000]

		# Set titles & display data for datatables on database page
		searchObj = Certificate.objects.filter(Q(expiry__month=currentMonth) & Q(expiry__year=currentYear)).exclude(type_id=3).order_by('-expiry')[:1000]

		# ("""SELECT * from certificate 
		# 	where YEAR(expiry) = YEAR(CURRENT_DATE()) and MONTH(expiry) = MONTH(CURRENT_DATE()) """)

		titles.extend(['', 'RRN', 'Site Address', 'Certificate Type', 'Assessor Name', 'Expiry Date'])

		for entry in searchObj:
			expiry = search.extract_date(object, entry.expiry)
			temp_dict = {'entry1': entry.rrn.rrn, 'entry2': entry.site.address, 'entry3': entry.type.type, 'entry4': entry.assessor.name, 'entry5': expiry}
			INdata.append(temp_dict)

		# Set a postData list which contains data to populate the search fields at the top of the database page
		postData = []
		temp_dict = {'query': '', 'queryType1': 'postcode', 'query2': currentDate, 'queryType2': 'expiry_before', 'query3': plus_one_month,'queryType3': 'expiry_after'}
		postData.append(temp_dict)

		# Set the correct linktype so the datatable show the correct titles
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

	# This generates the reminder letter if the 'generate letter' button presses on database page
	if request.method == 'POST' and 'print_doc' in request.POST:
		rrnList = request.POST.getlist("radio_check")
		outDoc = docPrint(base_qs, rrnList)
		
		return render(request, 'main/database.html', {})

	# Set a postData list which contains data to populate the search fields at the top of the database page
	# Data is gained from the search field user input on the database page
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

		# Set the query restrictions global - If set True all searches are limited to 1000 rows
		if request.POST.get('restrict'):
			restrict = False
		else:
			restrict = True

		OUTdata = search(base_qs, query, query2, query3, queryType1, queryType2, queryType3, restrict)

		# Set utils.search output to variables for html context and datatable population
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

	def format_address(site):
		if not site:
			address_line_1 = 'No Address Provided'
			address_line_2 = ''
			address_line_3 = ''
			address_line_4 = ''
		elif site.split(',') == []:
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

		return address_line_1, address_line_2, address_line_3, address_line_4


	rrnData = []
	temp_dict = {}

	rrnObj = Certificate.objects.get(rrn__rrn=rrn)

	# Check if address is more than 1 line and, if so, separate out into individual lines for better display
	site = rrnObj.site.address

	address_line_1, address_line_2, address_line_3, address_line_4 = format_address(site)

	# Populate dictionary with data shared by all certificate entries for display on rrn page
	temp_dict = {'rrn': rrn, 'postcode': rrnObj.postcode.postcode, 'site': site, 'complexity': rrnObj.complexity.rating, 'employer': rrnObj.employer.name, 'employerAddress': rrnObj.employer.address, 
	'assessor': rrnObj.assessor.name, 'number': rrnObj.assessor.scheme_number, 'scheme': rrnObj.scheme.accred_scheme, 'expiry': rrnObj.expiry, 'area': rrnObj.building_area, 'address_line_1': address_line_1, 'address_line_2': address_line_2, 'address_line_3': address_line_3, 'address_line_4': address_line_4}

	# Set additional fields specific to EPCs
	if rrnObj.type.type == 'EPC':
		certType = 'EPC'
		epc_dict = {'certType': certType, 'heating': rrnObj.heating.type, 'environment': rrnObj.environment.type, 'rating': rrnObj.epc_rating, 'emissions': rrnObj.building_emissions, 'energy': rrnObj.energy_usage}
		temp_dict.update(epc_dict)
		
	# Set additional fields specific to TM44s
	elif rrnObj.type.type == 'TM44':
		certType = 'TM44'
		tm44_dict = {'certType': certType, 'ac': rrnObj.ac_output, 'refrig': rrnObj.refrig_weight, 'manager': rrnObj.manager}
		temp_dict.update(tm44_dict)

	# Set additional fields specific to TM44s
	elif rrnObj.type.type == 'DEC':
		certType = 'DEC'
		dec_dict = {'certType': certType, 'annual_electric': rrnObj.annual_electric, 'typical_electric': rrnObj.typical_electric, 'renewable_electric': rrnObj.renewable_electric, 'annual_heating': rrnObj.annual_heating, 'typical_heating': rrnObj.typical_heating, 'renewable_heating': rrnObj.renewable_heating}
		temp_dict.update(dec_dict)
		
	rrnData.append(temp_dict)

	# Collecting data within each foreign key table to populate drop down menus on edit page
	# Only need to gather columns from tables with specific rows such as 'environment' or 'type' as these have only a specific number of possibles for all entries in database
	if request.method == 'POST' and 'edit' in request.POST:
		typeData = []
		typeObj = Type.objects.all()
		for entry in typeObj:
			type_dict = {'type': entry.type}
			typeData.append(type_dict)

		schemeData = []
		schemeObj = Scheme.objects.all()
		for entry in schemeObj:
			scheme_dict = {'scheme': entry.accred_scheme}
			schemeData.append(scheme_dict)

		compData = []
		compObj = Complexity.objects.all()
		for entry in compObj:
			rating_dict = {'comp': entry.rating}
			compData.append(rating_dict)

		envData = []
		envObj = Environment.objects.all()
		for entry in envObj:
			environ_dict = {'environment': entry.type}
			envData.append(environ_dict)

		heatData = []
		heatObj = Heating.objects.all()
		for entry in heatObj:
			heat_dict = {'heating': entry.type}
			heatData.append(heat_dict)

		context = {
			'data': rrnData, # Used to populate the placeholders with current data of entry
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

		# Use new type from user input to retrieve appropriate type ID
		if request.POST.get("type_check"):
			new_type = request.POST.get('type')
			rrnData[0]['certType'] = new_type
			
			# Only specific types so check for ID of new type and update certificate typeID appropriately
			typeObj = Type.objects.get(type=new_type)
			newTypeID = typeObj.id

			t = Certificate.objects.get(rrn_id=rrnID)
			t.type_id = newTypeID
			t.save()

		# Add check for duplicates
		if request.POST.get("site_check"):
			new_site = request.POST.get('site_address')
			address_line_1, address_line_2, address_line_3, address_line_4 = format_address(new_site)
			rrnData[0]['site'] = new_site
			rrnData[0]['address_line_1'] = address_line_1
			rrnData[0]['address_line_2'] = address_line_2
			rrnData[0]['address_line_3'] = address_line_3
			rrnData[0]['address_line_4'] = address_line_4
			
			current_siteID = certObj.site_id

			s = Site.objects.get(id=current_siteID)
			s.address = new_site
			s.save()

		# Want to add a check on assessor and number to see if the previous name/number combination is still being used anywhere in the DB
		# if the Certificate.assessor_id was changed instead of the Assessor table values
		if request.POST.get("assessor_check"):
			new_assessor = request.POST.get('assessor')
			current_number = rrnData[0]['number']
			rrnData[0]['assessor'] = new_assessor

			# Checks if the new assessor name is in the database with an existing number and sets the certificate assessorID appropriately
			if Assessor.objects.filter(Q(name=new_assessor) & Q(scheme_number=current_number)):
				assessorObj = Certificate.objects.get(Q(assessor__name=new_assessor) & Q(assessor__scheme_number=current_number))
				newAssessorID = assessorObj.assessor_id

				a = Certificate.objects.get(rrn_id=rrnID)
				a.assessor_id = newAssessorID
				a.save()
				
			# This will update the current assessorID with new assessor name provided by user input
			# Want this to only change the name for this certificate so may need to create new assessor with new name and existing number
			# Currently changes the assessor name for all entries in database with the existing assessor name
			else:
				current_assessorID = certObj.assessor_id
				a = Assessor.objects.get(id=current_assessorID)
				a.name = new_assessor
				a.save()

		if request.POST.get("number_check"):
			new_number = request.POST.get('number')
			current_assessor = rrnData[0]['assessor']
			rrnData[0]['number'] = new_number

			# Checks if the new number is in the database with an existing assessor name and sets the certificate assessorID appropriately
			if Assessor.objects.filter(Q(scheme_number=new_number) & Q(name=current_assessor)):
				numberObj = Certificate.objects.get(Q(assessor__scheme_number=new_number) & Q(assessor__name=current_assessor))
				newNumberID = numberObj.assessor_id

				n = Certificate.objects.get(rrn_id=rrnID)
				n.assessor_id = newAssessorID
				n.save()

			# If new assessor number does not exist in the database then this changes the existing assessor table entry with data provided by user input
			else:
				current_assessorID = certObj.assessor_id
				n = Assessor.objects.get(id=current_assessorID)
				n.scheme_number = new_number
				n.save()

		# Use new scheme from user input to retrieve schemeID and update certificate schemeID appropriately - much like type above 
		if request.POST.get("scheme_check"):
			new_scheme = request.POST.get('scheme')
			rrnData[0]['scheme'] = new_scheme

			new_scheme = request.POST.get('scheme')
			schemeObj = Scheme.objects.get(accred_scheme=new_scheme)
			newSchemeID = schemeObj.id

			sch = Certificate.objects.get(rrn_id=rrnID)
			sch.scheme_id = newSchemeID
			sch.save()

		# Takes user input date and formats before updating certificate expiry
		# Need to add exception clause for incorrect format
		if request.POST.get("expiry_check"):
			new_expiry = request.POST.get('expiry')
			try:
				dateObj = dt.datetime.strptime(new_expiry, '%m/%d/%Y').date()
				exp = Certificate.objects.get(rrn_id=rrnID)
				exp.expiry = dateObj
				exp.save()

				rrnData[0]['expiry'] = dateObj
			except:
				# Add section to return to edit page with warning that date format is incorrect
				pass

		# Same function as the type and scheme sections above
		if request.POST.get("comp_check"):
			new_comp = request.POST.get('complexity')
			rrnData[0]['complexity'] = new_comp

			compObj = Complexity.objects.get(rating=new_comp)
			newCompID = compObj.id

			c = Certificate.objects.get(rrn_id=rrnID)
			c.complexity_id = newCompID
			c.save()

		# Updates certificate area with user input
		# Maybe add check to ensure integer value at later date, not important yet.
		if request.POST.get("area_check"):
			new_area = request.POST.get('area')
			rrnData[0]['area'] = new_area

			areaObj = Certificate.objects.get(rrn_id=rrnID)
			areaObj.building_area = new_area
			areaObj.save()

		if request.POST.get("emp_check"):
			new_emp = request.POST.get('employer')
			current_employerAddress = rrnData[0]['employerAddress']
			rrnData[0]['employer'] = new_emp

			# Checks if an employer entry exists with new employer details provided by user, retrieves employerID and sets certificate employerID appropriately
			if Employer.objects.filter(Q(name=new_emp) & Q(address=current_employerAddress)):
				employerObj = Certificate.objects.get(Q(employer__name=new_emp) & Q(employer__address=current_employerAddress))
				newEmployerID = employerObj.employer_id

				e = Certificate.objects.get(rrn_id=rrnID)
				e.employer_id = newEmployerID
				e.save()
			# If new employer does not exist in the database then this changes the existing employer table entry with data provided by user input
			else:
				current_employerID = certObj.employer_id
				e = Employer.objects.get(id=current_employerID)
				e.name = new_emp
				e.save()

		if request.POST.get("empAdd_check"):
			new_empAdd = request.POST.get('empAdd')
			current_employer = rrnData[0]['employer']
			rrnData[0]['employerAddress'] = new_empAdd

			# Checks if an employer entry exists with new employer address details provided by user, retrieves employerID and sets certificate employerID appropriately
			if Employer.objects.filter(Q(name=current_employer) & Q(address=new_empAdd)):
				employerObj = Certificate.objects.get(Q(employer__name=current_employer) & Q(employer__address=new_empAdd))
				newEmployerID = employerObj.employer_id

				emp = Certificate.objects.get(rrn_id=rrnID)
				emp.employer_id = newEmployerID
				emp.save()
			# If new employer address does not exist in the database then this changes the existing employer table entry with data provided by user input
			else:
				current_employerID = certObj.employer_id
				emp = Employer.objects.get(id=current_employerID)
				emp.address = new_empAdd
				emp.save()

		# Updates certificate epc_rating with user input
		# Maybe add check to ensure integer value at later date, not important yet.
		if request.POST.get("rating_check"):
			new_rating = request.POST.get('rating')
			rrnData[0]['rating'] = new_rating

			ratingObj = Certificate.objects.get(rrn_id=rrnID)
			ratingObj.epc_rating = new_rating
			ratingObj.save()

		# Gets new environment_typeID from environment table depending on user input and updates certificate environment_id appropriately
		if request.POST.get("env_check"):
			new_env = request.POST.get('environment')
			rrnData[0]['environment'] = new_env

			envObj = Environment.objects.get(environment__type=new_env)
			newEnvID = envObj.id

			env = Certificate.objects.get(rrn_id=rrnID)
			env.environment_id = newEnvID
			env.save()

		# Add regex to ensure RRN is entered in correct format
		if request.POST.get("rrn_check"):
			check_list.append('rrn_check')
			new_rrn = request.POST.get('rrn')

			instance = RRN.objects.get(id=rrnID)
			instance.rrn = new_rrn
			instance.save()
			
			rrnData[0]['rrn'] = new_rrn

		context = {
			'rrnData': rrnData,
		}

		return render(request, 'main/rrn.html', context)

	elif request.method == 'POST' and 'return' in request.POST:
		context = {
			'INdata': rrnData,
		}

		return render(request, 'main/database.html', context)

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

