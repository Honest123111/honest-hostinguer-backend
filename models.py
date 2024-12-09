# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    first_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoCeleryBeatClockedschedule(models.Model):
    clocked_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_celery_beat_clockedschedule'


class DjangoCeleryBeatCrontabschedule(models.Model):
    minute = models.CharField(max_length=240)
    hour = models.CharField(max_length=96)
    day_of_week = models.CharField(max_length=64)
    day_of_month = models.CharField(max_length=124)
    month_of_year = models.CharField(max_length=64)
    timezone = models.CharField(max_length=63)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_crontabschedule'


class DjangoCeleryBeatIntervalschedule(models.Model):
    every = models.IntegerField()
    period = models.CharField(max_length=24)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_intervalschedule'


class DjangoCeleryBeatPeriodictask(models.Model):
    name = models.CharField(unique=True, max_length=200)
    task = models.CharField(max_length=200)
    args = models.TextField()
    kwargs = models.TextField()
    queue = models.CharField(max_length=200, blank=True, null=True)
    exchange = models.CharField(max_length=200, blank=True, null=True)
    routing_key = models.CharField(max_length=200, blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    enabled = models.BooleanField()
    last_run_at = models.DateTimeField(blank=True, null=True)
    total_run_count = models.PositiveIntegerField()
    date_changed = models.DateTimeField()
    description = models.TextField()
    crontab = models.ForeignKey(DjangoCeleryBeatCrontabschedule, models.DO_NOTHING, blank=True, null=True)
    interval = models.ForeignKey(DjangoCeleryBeatIntervalschedule, models.DO_NOTHING, blank=True, null=True)
    solar = models.ForeignKey('DjangoCeleryBeatSolarschedule', models.DO_NOTHING, blank=True, null=True)
    one_off = models.BooleanField()
    start_time = models.DateTimeField(blank=True, null=True)
    priority = models.PositiveIntegerField(blank=True, null=True)
    headers = models.TextField()
    clocked = models.ForeignKey(DjangoCeleryBeatClockedschedule, models.DO_NOTHING, blank=True, null=True)
    expire_seconds = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_periodictask'


class DjangoCeleryBeatPeriodictasks(models.Model):
    ident = models.AutoField(primary_key=True)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_celery_beat_periodictasks'


class DjangoCeleryBeatSolarschedule(models.Model):
    event = models.CharField(max_length=24)
    latitude = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    longitude = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float

    class Meta:
        managed = False
        db_table = 'django_celery_beat_solarschedule'
        unique_together = (('event', 'latitude', 'longitude'),)


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class MyappAddressd(models.Model):
    zip_code = models.IntegerField()
    address = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=255)
    customer = models.ForeignKey('MyappCustomer', models.DO_NOTHING, blank=True, null=True)
    state = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'myapp_addressd'


class MyappAddresso(models.Model):
    zip_code = models.IntegerField()
    address = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=255)
    customer = models.ForeignKey('MyappCustomer', models.DO_NOTHING, blank=True, null=True)
    state = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'myapp_addresso'


class MyappCarrieruser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    carrier_type = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(unique=True, max_length=254)
    phone = models.CharField(max_length=15, blank=True, null=True)
    dot_number = models.CharField(db_column='DOT_number', max_length=20, blank=True, null=True)  # Field name made lowercase.
    license_guid = models.CharField(unique=True, max_length=32)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'myapp_carrieruser'


class MyappCarrieruserGroups(models.Model):
    carrieruser = models.ForeignKey(MyappCarrieruser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'myapp_carrieruser_groups'
        unique_together = (('carrieruser', 'group'),)


class MyappCarrieruserUserPermissions(models.Model):
    carrieruser = models.ForeignKey(MyappCarrieruser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'myapp_carrieruser_user_permissions'
        unique_together = (('carrieruser', 'permission'),)


class MyappCustomer(models.Model):
    name = models.CharField(max_length=100)
    corporation = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    dotnumber = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=254)

    class Meta:
        managed = False
        db_table = 'myapp_customer'


class MyappEquipmenttype(models.Model):
    idmmequipment = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'myapp_equipmenttype'


class MyappJobType(models.Model):
    idmmjob = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'myapp_job_type'


class MyappLoad(models.Model):
    equipment_type = models.CharField(max_length=100)
    customer = models.ForeignKey(MyappCustomer, models.DO_NOTHING)
    destiny = models.ForeignKey(MyappAddressd, models.DO_NOTHING)
    origin = models.ForeignKey(MyappAddresso, models.DO_NOTHING)
    classifications_and_certifications = models.CharField(max_length=255)
    commodity = models.CharField(max_length=100)
    loaded_miles = models.IntegerField()
    offer = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    total_weight = models.IntegerField()
    idmmload = models.AutoField(primary_key=True)
    is_offerted = models.BooleanField()
    number_of_offers = models.IntegerField()
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    priority = models.CharField(max_length=10)
    updated_at = models.DateTimeField()
    assigned_user = models.ForeignKey(MyappCarrieruser, models.DO_NOTHING, blank=True, null=True)
    current_location = models.CharField(max_length=255, blank=True, null=True)
    equipment = models.ForeignKey(MyappEquipmenttype, models.DO_NOTHING, blank=True, null=True)
    expiration_date = models.DateTimeField(blank=True, null=True)
    is_reserved = models.BooleanField()
    payment_status = models.CharField(max_length=20)
    tracking_status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'myapp_load'


class MyappLoadWarnings(models.Model):
    load = models.ForeignKey(MyappLoad, models.DO_NOTHING)
    warning = models.ForeignKey('MyappWarning', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'myapp_load_warnings'
        unique_together = (('load', 'warning'),)


class MyappOfferhistory(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    date = models.DateTimeField()
    load = models.ForeignKey(MyappLoad, models.DO_NOTHING)
    proposed_delivery_date = models.DateField(blank=True, null=True)
    proposed_delivery_time = models.TimeField(blank=True, null=True)
    proposed_pickup_date = models.DateField(blank=True, null=True)
    proposed_pickup_time = models.TimeField(blank=True, null=True)
    terms_change = models.BooleanField()
    user = models.ForeignKey(MyappCarrieruser, models.DO_NOTHING, blank=True, null=True)
    status = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'myapp_offerhistory'


class MyappProcessedemail(models.Model):
    message_id = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'myapp_processedemail'


class MyappRole(models.Model):
    name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'myapp_role'


class MyappRolePermissions(models.Model):
    role = models.ForeignKey(MyappRole, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'myapp_role_permissions'
        unique_together = (('role', 'permission'),)


class MyappStop(models.Model):
    location = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    estimated_weight = models.IntegerField()
    quantity = models.IntegerField()
    loaded_on = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=100)
    load = models.ForeignKey(MyappLoad, models.DO_NOTHING)
    action_type = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'myapp_stop'


class MyappWarning(models.Model):
    description = models.CharField(unique=True, max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    load = models.ForeignKey(MyappLoad, models.DO_NOTHING, blank=True, null=True)
    reported_by = models.ForeignKey(MyappCarrieruser, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'myapp_warning'
