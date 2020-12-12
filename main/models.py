# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Assessor(models.Model):
    name = models.CharField(blank=True, null=True, max_length=150, db_index=True)
    scheme_number = models.CharField(blank=True, null=True, max_length=50, db_index=True)

    class Meta:
        managed = True
        db_table = 'assessor'


class Complexity(models.Model):
    rating = models.CharField(null=True, max_length=10)

    class Meta:
        managed = True
        db_table = 'complexity'


class Employer(models.Model):
    name = models.CharField(blank=True, null=True, max_length=150, db_index=True)
    address = models.CharField(blank=True, null=True, max_length=500, db_index=True)

    class Meta:
        managed = True
        db_table = 'employer'


class Environment(models.Model):
    type = models.CharField(blank=True, null=True, max_length=255)

    class Meta:
        managed = True
        db_table = 'environment'


class Heating(models.Model):
    type = models.CharField(blank=True, null=True, max_length=150)

    class Meta:
        managed = True
        db_table = 'heating'


class Postcode(models.Model):
    postcode = models.CharField(blank=True, null=True, max_length=10, db_index=True)

    class Meta:
        managed = True
        db_table = 'postcode'


class RRN(models.Model):
    rrn = models.CharField(blank=True, null=True, max_length=30, db_index=True)

    class Meta:
        managed = True
        db_table = 'rrn'


class Scheme(models.Model):
    accred_scheme = models.CharField(blank=True, null=True, max_length=255, db_index=True)

    class Meta:
        managed = True
        db_table = 'scheme'


class Site(models.Model):
    address = models.CharField(blank=True, null=True, max_length=500, db_index=True)

    class Meta:
        managed = True
        db_table = 'site'


class Type(models.Model):
    type = models.CharField(blank=True, null=True, max_length=25, db_index=True)

    class Meta:
        managed = True
        db_table = 'type'


class Certificate(models.Model):
    epc_rating = models.IntegerField(null=True, db_index=False)
    building_area = models.IntegerField(db_index=False)
    building_emissions = models.DecimalField(max_digits=6, decimal_places=2, db_index=False)
    energy_usage = models.DecimalField(max_digits=6, decimal_places=2, db_index=False)
    refrig_weight = models.IntegerField(db_index=False)
    ac_output = models.IntegerField(db_index=False)
    annual_heating = models.CharField(blank=True, null=True, max_length=50, db_index=False)
    renewable_heating = models.CharField(blank=True, null=True, max_length=50, db_index=False)
    annual_electric = models.CharField(blank=True, null=True, max_length=50, db_index=False)
    typical_heating = models.CharField(blank=True, null=True, max_length=50, db_index=False)
    typical_electric = models.CharField(blank=True, null=True, max_length=50, db_index=False)
    renewable_electric = models.CharField(blank=True, null=True, max_length=50, db_index=False)
    expiry = models.DateField(db_index=True)
    manager = models.CharField(blank=True, null=True, max_length=100, db_index=False)
    rrn = models.ForeignKey(RRN, on_delete=models.CASCADE)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    postcode = models.ForeignKey(Postcode, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    heating = models.ForeignKey(Heating, on_delete=models.CASCADE)
    complexity = models.ForeignKey(Complexity, on_delete=models.CASCADE)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE)
    assessor = models.ForeignKey(Assessor, on_delete=models.CASCADE)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'certificate'