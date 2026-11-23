from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = settings.AUTH_USER_MODEL


class Child(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE"
        ARCHIVED = "ARCHIVED"

    first_name = models.CharField(max_length=50)
    birth_date = models.DateField()
    notes = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="children_created")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name


class ChildAccess(models.Model):
    class Role(models.TextChoices):
        GUARDIAN = "GUARDIAN"
        CAREGIVER = "CAREGIVER"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE"
        REVOKED = "REVOKED"

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="access")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="child_access")
    access_role = models.CharField(max_length=10, choices=Role.choices)
    relationship = models.CharField(max_length=30, blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="access_granted")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["child", "user"], name="uniq_child_user")]


class SafetyZone(models.Model):
    class ZoneType(models.TextChoices):
        HOME = "HOME"
        SCHOOL = "SCHOOL"
        DAYCARE = "DAYCARE"
        RELATIVE = "RELATIVE"
        TUTORING = "TUTORING"
        ACTIVITY = "ACTIVITY"
        OTHER = "OTHER"

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="zones")
    zone_name = models.CharField(max_length=60)
    zone_type = models.CharField(max_length=15, choices=ZoneType.choices)
    address = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6,
                                   validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                    validators=[MinValueValidator(-180), MaxValueValidator(180)])
    radius_m = models.PositiveSmallIntegerField(default=100,
                                                validators=[MinValueValidator(50), MaxValueValidator(1000)])
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="zones_created")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["child", "zone_name"], name="uniq_zone_name_per_child")]

    def __str__(self):
        return f"{self.zone_name} ({self.child})"