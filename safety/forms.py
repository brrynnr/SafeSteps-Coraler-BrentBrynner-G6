from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from .models import Child, SafetyZone, CheckinRecord

MAX_CHILDREN = 5   # BR-08
MAX_ZONES = 10     # BR-12


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ("first_name", "birth_date", "notes")
        widgets = {"birth_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, guardian=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.guardian = guardian

    def clean_birth_date(self):
        b = self.cleaned_data["birth_date"]
        today = date.today()
        age = today.year - b.year - ((today.month, today.day) < (b.month, b.day))
        if b > today:
            raise forms.ValidationError("Birth date cannot be in the future.")
        if age >= 18:
            raise forms.ValidationError("A child must be younger than 18 years.")  # BR-09
        return b

    def clean(self):
        data = super().clean()
        if not self.instance.pk and self.guardian:
            count = Child.objects.filter(
                access__user=self.guardian, access__access_role="GUARDIAN",
                access__status="ACTIVE", status="ACTIVE").count()
            if count >= MAX_CHILDREN:
                raise forms.ValidationError("You can manage at most 5 active children.")  # BR-08
        return data


class CaregiverForm(forms.Form):
    email = forms.EmailField(label="Caregiver's email")
    relationship = forms.CharField(max_length=30, required=False)


class ZoneForm(forms.ModelForm):
    class Meta:
        model = SafetyZone
        fields = ("zone_name", "zone_type", "address", "latitude", "longitude", "radius_m", "is_active")

    def __init__(self, *args, child=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.child = child

    def clean(self):
        data = super().clean()
        name = data.get("zone_name")
        qs = SafetyZone.objects.filter(child=self.child)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if name and qs.filter(zone_name__iexact=name).exists():
            raise forms.ValidationError("This child already has a zone with that name.")  # BR-12
        if not self.instance.pk and qs.filter(is_active=True).count() >= MAX_ZONES:
            raise forms.ValidationError("A child can have at most 10 active zones.")  # BR-12
        return data

class CheckinForm(forms.ModelForm):
    class Meta:
        model = CheckinRecord
        fields = ("zone", "event_type", "activity_type")

    def __init__(self, *args, child=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.child = child
        self.fields["zone"].queryset = SafetyZone.objects.filter(child=child, is_active=True)  # BR-18

    def clean(self):
        data = super().clean()
        zone, event = data.get("zone"), data.get("event_type")
        if zone and event:
            last = CheckinRecord.objects.filter(child=self.child, zone=zone).first()
            is_open = last is not None and last.event_type == "CHECK_IN"
            if event == "CHECK_IN" and is_open:
                raise ValidationError("This child is already checked in at this zone.")   # BR-19
            if event == "CHECK_OUT" and not is_open:
                raise ValidationError("This child has no open check-in at this zone.")    # BR-19
        return data