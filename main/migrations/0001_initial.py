# Generated by Django 3.0.6 on 2020-11-08 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assessor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=150)),
                ('scheme_number', models.CharField(db_index=True, max_length=50)),
            ],
            options={
                'db_table': 'assessor',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Complexity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'complexity',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Employer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=150)),
                ('address', models.CharField(db_index=True, max_length=500)),
            ],
            options={
                'db_table': 'employer',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'environment',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Heating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=150)),
            ],
            options={
                'db_table': 'heating',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Postcode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('postcode', models.CharField(db_index=True, max_length=10)),
            ],
            options={
                'db_table': 'postcode',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='RRN',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rrn', models.CharField(db_index=True, max_length=30)),
            ],
            options={
                'db_table': 'rrn',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Scheme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accred_scheme', models.CharField(db_index=True, max_length=255)),
            ],
            options={
                'db_table': 'scheme',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(db_index=True, max_length=500)),
            ],
            options={
                'db_table': 'site',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(db_index=True, max_length=25)),
            ],
            options={
                'db_table': 'type',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('epc_rating', models.IntegerField()),
                ('building_area', models.IntegerField()),
                ('building_emissions', models.DecimalField(decimal_places=2, max_digits=6)),
                ('energy_usage', models.DecimalField(decimal_places=2, max_digits=6)),
                ('refrig_weight', models.IntegerField()),
                ('ac_output', models.IntegerField()),
                ('annual_heating', models.CharField(max_length=50)),
                ('renewable_heating', models.CharField(max_length=50)),
                ('annual_electric', models.CharField(max_length=50)),
                ('typical_heating', models.CharField(max_length=50)),
                ('typical_electric', models.CharField(max_length=50)),
                ('renewable_electric', models.CharField(max_length=50)),
                ('expiry', models.DateField(db_index=True)),
                ('manager', models.CharField(max_length=100)),
                ('assessor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Assessor')),
                ('complexity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Complexity')),
                ('employer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Employer')),
                ('environment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Environment')),
                ('heating', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Heating')),
                ('postcode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Postcode')),
                ('rrn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.RRN')),
                ('scheme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Scheme')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Site')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Type')),
            ],
            options={
                'db_table': 'certificate',
                'managed': True,
            },
        ),
    ]