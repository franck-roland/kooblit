# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
import usr_management.utils


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=20, verbose_name='Type', choices=[(b'HOME', 'Home'), (b'WORK', 'Work'), (b'OTHER', 'Other')])),
                ('departement', models.CharField(max_length=50, verbose_name='Departement', blank=True)),
                ('corporation', models.CharField(max_length=100, verbose_name='Corporation', blank=True)),
                ('building', models.CharField(max_length=20, verbose_name='Building', blank=True)),
                ('floor', models.CharField(max_length=20, verbose_name='Floor', blank=True)),
                ('door', models.CharField(max_length=20, verbose_name='Door', blank=True)),
                ('number', models.CharField(max_length=30, verbose_name='Number', blank=True)),
                ('street_line1', models.CharField(max_length=100, verbose_name='Address 1', blank=True)),
                ('street_line2', models.CharField(max_length=100, verbose_name='Address 2', blank=True)),
                ('zipcode', models.CharField(max_length=5, verbose_name='ZIP code', blank=True)),
                ('city', models.CharField(max_length=100, verbose_name='City', blank=True)),
                ('state', models.CharField(max_length=100, verbose_name='State', blank=True)),
                ('cedex', models.CharField(max_length=100, verbose_name='CEDEX', blank=True)),
                ('postal_box', models.CharField(max_length=20, verbose_name='Postal box', blank=True)),
                ('country', models.CharField(blank=True, max_length=100, verbose_name='Country', choices=[(b'WF', 'Wallis and Futuna'), (b'JP', 'Japan'), (b'JM', 'Jamaica'), (b'JO', 'Jordan'), (b'WS', 'Samoa'), (b'JE', 'Jersey'), (b'GW', 'Guinea-Bissau'), (b'GU', 'Guam'), (b'GT', 'Guatemala'), (b'GS', 'South Georgia and the South Sandwich Islands'), (b'GR', 'Greece'), (b'GQ', 'Equatorial Guinea'), (b'GP', 'Guadeloupe'), (b'GY', 'Guyana'), (b'GG', 'Guernsey'), (b'GF', 'French Guiana'), (b'GE', 'Georgia'), (b'GD', 'Grenada'), (b'GB', 'United Kingdom'), (b'GA', 'Gabon'), (b'GN', 'Guinea'), (b'GM', 'Gambia (The)'), (b'GL', 'Greenland'), (b'GI', 'Gibraltar'), (b'GH', 'Ghana'), (b'PR', 'Puerto Rico'), (b'PS', 'Palestine, State of'), (b'PW', 'Palau'), (b'PT', 'Portugal'), (b'PY', 'Paraguay'), (b'PA', 'Panama'), (b'PF', 'French Polynesia'), (b'PG', 'Papua New Guinea'), (b'PE', 'Peru'), (b'PK', 'Pakistan'), (b'PH', 'Philippines'), (b'PN', 'Pitcairn'), (b'PL', 'Poland'), (b'PM', 'Saint Pierre and Miquelon'), (b'ZM', 'Zambia'), (b'ZA', 'South Africa'), (b'ZW', 'Zimbabwe'), (b'ME', 'Montenegro'), (b'MD', 'Moldova (the Republic of)'), (b'MG', 'Madagascar'), (b'MF', 'Saint Martin (French part)'), (b'MA', 'Morocco'), (b'MC', 'Monaco'), (b'MM', 'Myanmar'), (b'ML', 'Mali'), (b'MO', 'Macao'), (b'MN', 'Mongolia'), (b'MH', 'Marshall Islands'), (b'MK', 'Macedonia (the former Yugoslav Republic of)'), (b'MU', 'Mauritius'), (b'MT', 'Malta'), (b'MW', 'Malawi'), (b'MV', 'Maldives'), (b'MQ', 'Martinique'), (b'MP', 'Northern Mariana Islands'), (b'MS', 'Montserrat'), (b'MR', 'Mauritania'), (b'MY', 'Malaysia'), (b'MX', 'Mexico'), (b'MZ', 'Mozambique'), (b'FR', 'France'), (b'FI', 'Finland'), (b'FJ', 'Fiji'), (b'FK', 'Falkland Islands  [Malvinas]'), (b'FM', 'Micronesia (the Federated States of)'), (b'FO', 'Faroe Islands'), (b'CK', 'Cook Islands'), (b'CI', "C\xf4te d'Ivoire"), (b'CH', 'Switzerland'), (b'CO', 'Colombia'), (b'CN', 'China'), (b'CM', 'Cameroon'), (b'CL', 'Chile'), (b'CC', 'Cocos (Keeling) Islands'), (b'CA', 'Canada'), (b'CG', 'Congo'), (b'CF', 'Central African Republic'), (b'CD', 'Congo (the Democratic Republic of the)'), (b'CZ', 'Czech Republic'), (b'CY', 'Cyprus'), (b'CX', 'Christmas Island'), (b'CR', 'Costa Rica'), (b'CW', 'Cura\xe7ao'), (b'CV', 'Cabo Verde'), (b'CU', 'Cuba'), (b'SZ', 'Swaziland'), (b'SY', 'Syrian Arab Republic'), (b'SX', 'Sint Maarten (Dutch part)'), (b'SS', 'South Sudan'), (b'SR', 'Suriname'), (b'SV', 'El Salvador'), (b'ST', 'Sao Tome and Principe'), (b'SK', 'Slovakia'), (b'SJ', 'Svalbard and Jan Mayen'), (b'SI', 'Slovenia'), (b'SH', 'Saint Helena, Ascension and Tristan da Cunha'), (b'SO', 'Somalia'), (b'SN', 'Senegal'), (b'SM', 'San Marino'), (b'SL', 'Sierra Leone'), (b'SC', 'Seychelles'), (b'SB', 'Solomon Islands'), (b'SA', 'Saudi Arabia'), (b'SG', 'Singapore'), (b'SE', 'Sweden'), (b'SD', 'Sudan'), (b'YE', 'Yemen'), (b'YT', 'Mayotte'), (b'LB', 'Lebanon'), (b'LC', 'Saint Lucia'), (b'LA', "Lao People's Democratic Republic"), (b'LK', 'Sri Lanka'), (b'LI', 'Liechtenstein'), (b'LV', 'Latvia'), (b'LT', 'Lithuania'), (b'LU', 'Luxembourg'), (b'LR', 'Liberia'), (b'LS', 'Lesotho'), (b'LY', 'Libya'), (b'VA', 'Holy See  [Vatican City State]'), (b'VC', 'Saint Vincent and the Grenadines'), (b'VE', 'Venezuela, Bolivarian Republic of'), (b'VG', 'Virgin Islands (British)'), (b'IQ', 'Iraq'), (b'VI', 'Virgin Islands (U.S.)'), (b'IS', 'Iceland'), (b'IR', 'Iran (the Islamic Republic of)'), (b'IT', 'Italy'), (b'VN', 'Viet Nam'), (b'IM', 'Isle of Man'), (b'IL', 'Israel'), (b'IO', 'British Indian Ocean Territory'), (b'IN', 'India'), (b'IE', 'Ireland'), (b'ID', 'Indonesia'), (b'BD', 'Bangladesh'), (b'BE', 'Belgium'), (b'BF', 'Burkina Faso'), (b'BG', 'Bulgaria'), (b'BA', 'Bosnia and Herzegovina'), (b'BB', 'Barbados'), (b'BL', 'Saint Barth\xe9lemy'), (b'BM', 'Bermuda'), (b'BN', 'Brunei Darussalam'), (b'BO', 'Bolivia, Plurinational State of'), (b'BH', 'Bahrain'), (b'BI', 'Burundi'), (b'BJ', 'Benin'), (b'BT', 'Bhutan'), (b'BV', 'Bouvet Island'), (b'BW', 'Botswana'), (b'BQ', 'Bonaire, Sint Eustatius and Saba'), (b'BR', 'Brazil'), (b'BS', 'Bahamas'), (b'BY', 'Belarus'), (b'BZ', 'Belize'), (b'RU', 'Russian Federation'), (b'RW', 'Rwanda'), (b'RS', 'Serbia'), (b'RE', 'R\xe9union'), (b'RO', 'Romania'), (b'OM', 'Oman'), (b'HR', 'Croatia'), (b'HT', 'Haiti'), (b'HU', 'Hungary'), (b'HK', 'Hong Kong'), (b'HN', 'Honduras'), (b'HM', 'Heard Island and McDonald Islands'), (b'EH', 'Western Sahara'), (b'EE', 'Estonia'), (b'EG', 'Egypt'), (b'EC', 'Ecuador'), (b'ET', 'Ethiopia'), (b'ES', 'Spain'), (b'ER', 'Eritrea'), (b'UY', 'Uruguay'), (b'UZ', 'Uzbekistan'), (b'US', 'United States'), (b'UM', 'United States Minor Outlying Islands'), (b'UG', 'Uganda'), (b'UA', 'Ukraine'), (b'VU', 'Vanuatu'), (b'NI', 'Nicaragua'), (b'NL', 'Netherlands'), (b'NO', 'Norway'), (b'NA', 'Namibia'), (b'NC', 'New Caledonia'), (b'NE', 'Niger'), (b'NF', 'Norfolk Island'), (b'NG', 'Nigeria'), (b'NZ', 'New Zealand'), (b'NP', 'Nepal'), (b'NR', 'Nauru'), (b'NU', 'Niue'), (b'KG', 'Kyrgyzstan'), (b'KE', 'Kenya'), (b'KI', 'Kiribati'), (b'KH', 'Cambodia'), (b'KN', 'Saint Kitts and Nevis'), (b'KM', 'Comoros'), (b'KR', 'Korea (the Republic of)'), (b'KP', "Korea (the Democratic People's Republic of)"), (b'KW', 'Kuwait'), (b'KZ', 'Kazakhstan'), (b'KY', 'Cayman Islands'), (b'DO', 'Dominican Republic'), (b'DM', 'Dominica'), (b'DJ', 'Djibouti'), (b'DK', 'Denmark'), (b'DE', 'Germany'), (b'DZ', 'Algeria'), (b'TZ', 'Tanzania, United Republic of'), (b'TV', 'Tuvalu'), (b'TW', 'Taiwan (Province of China)'), (b'TT', 'Trinidad and Tobago'), (b'TR', 'Turkey'), (b'TN', 'Tunisia'), (b'TO', 'Tonga'), (b'TL', 'Timor-Leste'), (b'TM', 'Turkmenistan'), (b'TJ', 'Tajikistan'), (b'TK', 'Tokelau'), (b'TH', 'Thailand'), (b'TF', 'French Southern Territories'), (b'TG', 'Togo'), (b'TD', 'Chad'), (b'TC', 'Turks and Caicos Islands'), (b'AE', 'United Arab Emirates'), (b'AD', 'Andorra'), (b'AG', 'Antigua and Barbuda'), (b'AF', 'Afghanistan'), (b'AI', 'Anguilla'), (b'AM', 'Armenia'), (b'AL', 'Albania'), (b'AO', 'Angola'), (b'AQ', 'Antarctica'), (b'AS', 'American Samoa'), (b'AR', 'Argentina'), (b'AU', 'Australia'), (b'AT', 'Austria'), (b'AW', 'Aruba'), (b'AX', '\xc5land Islands'), (b'AZ', 'Azerbaijan'), (b'QA', 'Qatar')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(default=False, max_length=2048)),
                ('date', models.DateField(default=datetime.datetime.now, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Demande',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('book', models.CharField(default=False, max_length=240)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Entree',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('montant', models.DecimalField(default=False, max_digits=6, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valeur', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reinitialisation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rnd', models.CharField(unique=True, max_length=42)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Syntheses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.IntegerField(default=0)),
                ('_file_html', models.FileField(storage=usr_management.utils.MyFileStorage(), upload_to=b'syntheses')),
                ('file_pdf', models.FileField(storage=usr_management.utils.MyFileStorage(), upload_to=b'syntheses')),
                ('livre_id', models.CharField(max_length=240)),
                ('book_title', models.CharField(default=b'', max_length=1024)),
                ('nb_achat', models.BigIntegerField(default=0)),
                ('note_moyenne', models.FloatField(default=0)),
                ('nbre_notes', models.BigIntegerField(default=0)),
                ('date', models.DateField(default=datetime.datetime.now, null=True)),
                ('prix', models.FloatField(default=0)),
                ('gain', models.FloatField(default=0)),
                ('has_been_published', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('remote_id', models.CharField(default=False, max_length=64)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserKooblit',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('civility', models.CharField(max_length=20, verbose_name='Status', blank=True)),
                ('birthday', models.DateField(null=True)),
                ('cagnotte', models.FloatField(default=0)),
                ('cagnotte_HT', models.FloatField(default=0)),
                ('syntheses', models.ManyToManyField(related_name='syntheses_bought+', null=True, to='usr_management.Syntheses', blank=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='Verification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('verification_id', models.CharField(default=False, unique=True, max_length=240)),
                ('user', models.ForeignKey(to='usr_management.UserKooblit')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Version_Synthese',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.IntegerField()),
                ('prix', models.FloatField()),
                ('publication_date', models.DateField(default=datetime.datetime.now, null=True)),
                ('gain', models.FloatField(default=0)),
                ('nb_achat', models.BigIntegerField(default=0)),
                ('_file', models.FileField(storage=usr_management.utils.MyFileStorage(), upload_to=b'syntheses')),
                ('synthese', models.ForeignKey(to='usr_management.Syntheses')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='version_synthese',
            unique_together=set([('version', 'synthese')]),
        ),
        migrations.AddField(
            model_name='userkooblit',
            name='syntheses_achetees',
            field=models.ManyToManyField(to='usr_management.Version_Synthese', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='user_from',
            field=models.ForeignKey(default=False, to='usr_management.UserKooblit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='syntheses',
            name='user',
            field=models.ForeignKey(related_name='+', to='usr_management.UserKooblit'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='syntheses',
            unique_together=set([('user', 'livre_id')]),
        ),
        migrations.AddField(
            model_name='reinitialisation',
            name='user',
            field=models.ForeignKey(to='usr_management.UserKooblit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='note',
            name='synthese',
            field=models.ForeignKey(to='usr_management.Syntheses'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='note',
            name='user',
            field=models.ForeignKey(to='usr_management.UserKooblit'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='note',
            unique_together=set([('user', 'synthese')]),
        ),
        migrations.AddField(
            model_name='entree',
            name='transaction',
            field=models.ForeignKey(default=False, to='usr_management.Transaction'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entree',
            name='user_dest',
            field=models.ForeignKey(default=False, to='usr_management.UserKooblit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='demande',
            name='user',
            field=models.ForeignKey(to='usr_management.UserKooblit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comments',
            name='synthese',
            field=models.ForeignKey(to='usr_management.Syntheses'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comments',
            name='user',
            field=models.ForeignKey(to='usr_management.UserKooblit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='user',
            field=models.ForeignKey(to='usr_management.UserKooblit'),
            preserve_default=True,
        ),
    ]
