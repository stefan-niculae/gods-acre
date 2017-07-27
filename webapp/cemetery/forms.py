from django.utils.translation import ugettext_lazy as _
from django.forms import Form, ModelForm, ModelMultipleChoiceField, BooleanField, FileField
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import Spot, Deed,  Owner, Construction, Authorization
from .widgets import AddAnotherWidgetWrapper


def many_to_many_field(model, required=False, name=None, is_stacked=False):
    if name is None:
        name = _(model.__name__ + 's')
    return ModelMultipleChoiceField(
        queryset=model.objects.all(),
        required=required,
        label=name,
        widget=AddAnotherWidgetWrapper(
            widget=FilteredSelectMultiple(is_stacked=is_stacked, verbose_name=name),
            model=model
        )
    )


class SpotForm(ModelForm):
    deeds          = many_to_many_field(Deed)
    constructions  = many_to_many_field(Construction)
    authorizations = many_to_many_field(Authorization)

    class Meta:
        model = Spot
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SpotForm, self).__init__(*args, **kwargs)

        # workaround for https://code.djangoproject.com/ticket/897
        # based on https://gist.github.com/Grokzen/a64321dd69339c42a184
        # which is based on https://snipt.net/chrisdpratt/symmetrical-manytomany-filter-horizontal-in-django-admin/#L-26
        if self.instance and self.instance.pk:
            self.fields['deeds'].initial          = self.instance.deeds.all()
            self.fields['constructions'].initial  = self.instance.constructions.all()
            self.fields['authorizations'].initial = self.instance.authorizations.all()

    def save(self, commit=True):
        spot = super(SpotForm, self).save(commit=False)

        if commit:
            spot.save()
        if spot.pk:
            spot.deeds          = self.cleaned_data['deeds']
            spot.constructions  = self.cleaned_data['constructions']
            spot.authorizations = self.cleaned_data['authorizations']
            self.save_m2m()

        return spot


class DeedForm(ModelForm):
    owners = many_to_many_field(Owner)

    class Meta:
        model = Deed
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DeedForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['owners'].initial = self.instance.owners.all()

    def save(self, commit=True):
        deed = super(DeedForm, self).save(commit=False)

        if commit:
            deed.save()
        if deed.pk:
            deed.owners = self.cleaned_data['owners']
            self.save_m2m()

        return deed


class ImportForm(Form):
    document = FileField(label=_('Document'))
    wipe_beforehand = BooleanField(required=False, label=_('Wipe beforehand'))
