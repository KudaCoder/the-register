from django.shortcuts import render
from datetime import datetime, time
from django.db.models import Q
from main.models import *


class search:
    # # INIT FUNCTION WILL DECIDE WHAT TYPE OF QUERY AND SEND TO THE CORRECT FUNCTION OR PARSE INTO SEPARATE QUERIES
    # # DECIDE WHETHER TO PRE-LOAD ALL ENTRIES INTO OBJECTS WITHIN THE INIT OR WITHIN THE INDIVIDUAL METHODS
    def __init__(self, querySet, query, query2, query3, queryType1, queryType2, queryType3, restrict):
        self.combinedData = []
        self.query = query
        self.query2 = query2
        self.query3 = query3
        self.queryType1 = queryType1
        self.queryType2 = queryType2
        self.queryType3 = queryType3
        self.restrict = restrict

        self.base_qs = querySet

        if self.queryType1 == 'assessor':
            self.assessor()
        elif self.queryType1 == 'site':
            self.site()
        elif self.queryType1 == 'type':
            self.type()
        elif self.queryType1 == 'scheme':
            self.scheme()
        elif self.queryType1 == 'postcode':
            self.postcode()
        elif self.queryType1 == 'rrn':
            self.rrn()

        self.output()


    def extract_date(self, date):
        date_formats = [
            '%b %d %Y',
            '%d/%m/%Y',
            '%d %m %Y',
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%b. %d, %Y',
            '%b %d, %Y',
            ]

        date_string = str(date)

        for formattedDate in date_formats:
            try:
                expiry = datetime.strptime(date_string, formattedDate).date()
            except Exception as e:
                # NO NEED TO WORK WITH EXCEPTION AS ONLY TRYING TO FIND THE DATE FORMAT INPUT BY USER
                pass
        
        return expiry

    def build_search_object(self, linkType, searchObj):
        # CHECK HOW BIG QUERYSET SHOULD BE BY USER 'RESTRICTION' SETTING
        if self.restrict != False and len(searchObj) > 1000:
            searchObj = searchObj[:1000]

        if linkType == 'rrn':
            for entry in searchObj:
                expiry = self.extract_date(entry.expiry)
                temp_dict = {'entry1': entry.rrn.rrn, 'entry2': entry.site.address, 'entry3': entry.type.type, 'entry4': entry.assessor.name, 'entry5': expiry}
                self.combinedData.append(temp_dict)
        elif linkType == 'assessor':
            # USE SCHEME POOL TO PREVENT MULTIPLES OF SAME ASSESSOR - WILL RETURN DATA FOR EVERY ENTRY IN DATABASE WHICH IS NOT NEEDED
            scheme_pool = []
            for entry in searchObj:
                expiry = self.extract_date(entry.expiry)
                temp_dict = {'entry1': entry.assessor.name, 'entry2': entry.assessor.scheme_number, 'entry3': entry.employer.name, 'entry4': entry.employer.address}
                if entry.assessor.scheme_number not in scheme_pool:
                    scheme_pool.append(entry.assessor.scheme_number)
                    self.combinedData.append(temp_dict)
                else:
                    pass

        return searchObj

    def set_titles(self, linkType):
        if linkType == 'rrn':
            titles = ['', 'RRN', 'Site Address', 'Certificate Type', 'Assessor Name', 'Expiry Date']
        elif linkType == 'assessor':
            titles = ['Assessor Name', 'Assessor Number', 'Employer', 'Employer Address']
        elif linkType == 'scheme':
            titles = ['Accreditation Scheme', 'EPCs', 'TM44s', 'DECs']

        return titles

    def second_query(self, queryType, searchObj):
        if queryType == 'assessor':
            returnObj = searchObj.filter(assessor__name__icontains=self.query2)
        elif queryType == 'postcode':
            returnObj = searchObj.filter(postcode__postcode__icontains=self.query2)
        elif queryType == 'type':
            returnObj = searchObj.filter(type__type__icontains=self.query2)
        elif queryType == 'scheme':
            returnObj = searchObj.filter(scheme__accred_scheme__icontains=self.query2)
        elif queryType == 'expiry_before':
            expiry = self.extract_date(self.query2)
            returnObj = searchObj.filter(expiry__lte=expiry)

        return returnObj

    def third_query(self, queryType, searchObj):
        if queryType == 'assessor':
            returnObj = searchObj.filter(assessor__name__icontains=self.query3)
        elif queryType == 'type':
            returnObj = searchObj.filter(type__type__icontains=self.query3)
        elif queryType == 'postcode':
            returnObj = searchObj.filter(postcode__postcode__icontains=self.query3)
        elif queryType == 'expiry_after':
            expiry = self.extract_date(self.query3)
            returnObj = searchObj.filter(expiry__gte=expiry)

        return returnObj


    # START OF INDIVIDUAL SEARCH METHODS
    def assessor(self):
        # 1ST QUERY
        searchObj = self.base_qs.filter(assessor__name__icontains=self.query).order_by('expiry')
        self.linkType = 'assessor'

        # DOESN'T RETURN THE CORRECT NUMBER OF ENTRIES WHEN SEARCHING 3 ASSESSORS??!!
        # NEED TO COME UP WITH A BETTER WAY OF DOING THIS SO USER CAN SEARCH FOR 2 ASSESSORS WITH A 
        # 3RD SEPARATE QUERY I.E. 'TYPE = TM44'
        if self.queryType2 == self.queryType3 == '--':
            self.titles = self.set_titles(self.linkType)
        elif self.queryType2 == 'assessor' and self.queryType3 == '--':
            self.titles = self.set_titles(self.linkType)
            searchObj = self.base_qs.filter(Q(assessor__name__icontains=self.query) | Q(assessor__name__icontains=self.query2))
        elif self.queryType2 == self.queryType3 == 'assessor':
            self.titles = self.set_titles(self.linkType)
            searchObj = self.base_qs.filter(Q(assessor__name__icontains=self.query) | Q(assessor__name__icontains=self.query2) | Q(assessor__name__icontains=self.query3))
        else:
            self.linkType = 'rrn'
            self.titles = self.set_titles(self.linkType)

            # 2ND QUERY
            if self.queryType2 != '--':
                searchObj = self.second_query(self.queryType2, searchObj)

            # 3RD QUERY
            if self.queryType3 != '--':
                searchObj = self.third_query(self.queryType3, searchObj)

        self.build_search_object(self.linkType, searchObj)

    def employer(self):
        self.employerData = []
        self.employers = []
        self.addresses = []
        certID_list = []

        for entry in self.ID_list:
            employer_certObj = Certificate.objects.raw(" SELECT id, employer_id FROM certificate WHERE id = %s", [entry])

            for entry in employer_certObj:
                certID_list.append(entry.employer_id)

        for certID in certID_list:
            employerObj = Employer.objects.raw("SELECT id, name, address FROM employer WHERE id = %s", [certID])

            for emp in employerObj:
                self.employers.append(emp.name)
                self.addresses.append(emp.address)

        # AS NO LINK IS REQUIRED AT PRESENT SET TO 'BLANK' AS DEFAULT NOT USED
        self.linkType = 'blank'

    def site(self):
        self.linkType = 'rrn'
        self.titles = self.set_titles(self.linkType)

        # 1ST QUERY - ORDERING BY 'SITE ADDRESS' AS 'EXPIRY' ADDS NEARLY 2 MINUTES TO SEARCH TIME??!!
        searchObj = self.base_qs.filter(site__address__icontains=self.query).order_by('site__address')

        # 2ND QUERY
        if self.queryType2 != '--':
            searchObj = self.second_query(self.queryType2, searchObj)

        # 3RD QUERY
        if self.queryType3 != '--':
            searchObj = self.third_query(self.queryType3, searchObj)

        self.build_search_object(self.linkType, searchObj)

    def type(self):
        self.linkType = 'rrn'
        self.titles = self.set_titles(self.linkType)
        
        # 1ST QUERY
        searchObj = self.base_qs.filter(type__type__icontains=self.query).order_by('expiry')

        # 2ND QUERY
        if self.queryType2 != '--':
            searchObj = self.second_query(self.queryType2, searchObj)

        # 3RD QUERY
        if self.queryType3 != '--':
            searchObj = self.third_query(self.queryType3, searchObj)

        self.build_search_object(self.linkType, searchObj)

    def scheme(self):
        self.linkType = 'scheme'

        if self.queryType2 == '--' and self.queryType3 == '--':
            self.titles = self.set_titles(self.linkType)
            schemeObj = Scheme.objects.all()

            if self.query == '':
                schemeIDs = schemeObj.filter(accred_scheme__icontains='').values_list('id', flat=True).count()
                for x in range(schemeIDs + 1):
                    schemeNames = schemeObj.filter(id=x).values('accred_scheme')
                    for entry in schemeNames:
                        scheme = entry.get('accred_scheme')
                        epcCount = self.base_qs.filter(Q(scheme_id=x) & Q(type_id=1)).count()
                        tm44Count = self.base_qs.filter(Q(scheme_id=x) & Q(type_id=4)).count()
                        decCount = self.base_qs.filter(Q(scheme_id=x) & Q(type_id=2)).count()

                        temp_dict = {}
                        temp_dict = {'entry1': scheme, 'entry2': epcCount, 'entry3': tm44Count, 'entry4': decCount}
                        self.combinedData.append(temp_dict)
            else:
                schemes = schemeObj.filter(accred_scheme__icontains=self.query)

                # CHANGE THIS TO USE MESSAGES INSTEAD OF WITHIN THE DATATABLE
                if not schemes:
                    temp_dict = {}
                    temp_dict = {'entry1': 'Scheme Does Not Exist', 'entry2': '', 'entry3': '', 'entry4': ''}
                    self.combinedData.append(temp_dict)
                for entry in schemes:
                    scheme = entry.accred_scheme

                    epcCount = self.base_qs.filter(Q(scheme__accred_scheme=scheme) & Q(type_id=1)).count()
                    tm44Count = self.base_qs.filter(Q(scheme__accred_scheme=scheme) & Q(type_id=4)).count()
                    decCount = self.base_qs.filter(Q(scheme__accred_scheme=scheme) & Q(type_id=2)).count()                
        else:
            self.linkType = 'rrn'
            self.titles = self.set_titles(self.linkType)
            
            # 1ST QUERY
            searchObj = self.base_qs.filter(scheme__accred_scheme__icontains=self.query).order_by('expiry')

            # 2ND QUERY
            if self.queryType2 != '--':
                searchObj = self.second_query(self.queryType2, searchObj)

            # 3RD QUERY
            if self.queryType3 != '--':
                searchObj = self.third_query(self.queryType3, searchObj)

            self.build_search_object(self.linkType, searchObj)

    def postcode(self):
        self.linkType = 'rrn'
        self.titles = self.set_titles(self.linkType)

        # IF 2ND QUERY IS ALSO POSTCODE SORT FIRST AS WILL NEED Q SEARCH
        if self.queryType2 == 'postcode':
            searchObj = self.base_qs.filter(Q(postcode__postcode__icontains=self.query) | Q(postcode__postcode__icontains=self.query2)).order_by('expiry')
        else:
            # OTHERWISE....1ST QUERY
            searchObj = self.base_qs.filter(postcode__postcode__icontains=self.query).order_by('expiry')
        # 2ND QUERY
        if self.queryType2 != '--':
            searchObj = self.second_query(self.queryType2, searchObj)

        # 3RD QUERY
        if self.queryType3 != '--':
            searchObj = self.third_query(self.queryType3, searchObj)

        # CHECK HOW BIG QUERYSET SHOULD BE BY USER 'RESTRICTION' SETTING
        self.build_search_object(self.linkType, searchObj)

    def rrn(self):
        self.linkType = 'rrn'
        self.titles = self.set_titles(self.linkType)

        # 1ST & ONLY QUERY IF SEARCHING FOR RRN AS WILL ONLY RETURN 1 SPECIFIC ENTRY
        searchObj = self.base_qs.filter(rrn__rrn__icontains=self.query)

        self.build_search_object(self.linkType, searchObj)



    def output(self):
        return self.combinedData, self.titles, self.linkType