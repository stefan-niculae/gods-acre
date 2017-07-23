from django.forms import Form, ModelForm, ModelMultipleChoiceField, IntegerField, BooleanField, FileField
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext_lazy as _

from .models import Spot, Deed, Payment, Owner, Construction, Authorization, PaymentReceipt, Operation, NrYear
from .utils import title_case, year_shorthand_to_full


class NrYearForm(ModelForm):
    class Meta:
        model = NrYear
        fields = '__all__'

    def clean_year(self):
        return year_shorthand_to_full(self.cleaned_data['year'])


# workaround for https://code.djangoproject.com/ticket/897
# based on https://gist.github.com/Grokzen/a64321dd69339c42a184
# which is based on https://snipt.net/chrisdpratt/symmetrical-manytomany-filter-horizontal-in-django-admin/#L-26
class SpotForm(ModelForm):
    deeds = ModelMultipleChoiceField(
        queryset=Deed.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Deeds'),
            is_stacked=False
        )
    )
    constructions = ModelMultipleChoiceField(
        queryset=Construction.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Constructions'),
            is_stacked=False
        )
    )
    authorizations = ModelMultipleChoiceField(
        queryset=Authorization.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Authorizations'),
            is_stacked=False
        )
    )
    # payments = ModelMultipleChoiceField(
    #     queryset=Payment.objects.all(),
    #     required=False,
    #     widget=FilteredSelectMultiple(
    #         verbose_name=_('Payments'),
    #         is_stacked=False
    #     )
    # )

    # add_deed_button = add_link('deed')  # TODO add button
    # add_deed_button.allow_tags = True

    class Meta:
        model = Spot
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SpotForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['deeds'].initial          = self.instance.deeds.all()
            self.fields['constructions'].initial  = self.instance.constructions.all()
            self.fields['authorizations'].initial = self.instance.authorizations.all()
            # self.fields['payments'].initial       = self.instance.payments.all()

    def save(self, commit=True):
        spot = super(SpotForm, self).save(commit=False)

        if commit:
            spot.save()

        if spot.pk:
            spot.deeds          = self.cleaned_data['deeds']
            spot.constructions  = self.cleaned_data['constructions']
            spot.authorizations = self.cleaned_data['authorizations']
            # spot.payments       = self.cleaned_data['payments']
            self.save_m2m()

        return spot


class DeedForm(NrYearForm):
    owners = ModelMultipleChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Owners'),
            is_stacked=False
        )
    )

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


# class PaymentForm(ModelForm):
#     receipts = ModelMultipleChoiceField(
#         queryset=PaymentReceipt.objects.all(),
#         required=False,
#         widget=FilteredSelectMultiple(
#             verbose_name=_('Receipts'),
#             is_stacked=False
#         )
#     )
# 
#     class Meta:
#         model = Payment
#         fields = '__all__'
# 
#     def __init__(self, *args, **kwargs):
#         super(PaymentForm, self).__init__(*args, **kwargs)
# 
#         if self.instance and self.instance.pk:
#             self.fields['receipts'].initial = self.instance.receipts.all()
# 
#     def save(self, commit=True):
#         payment = super(PaymentForm, self).save(commit=False)
# 
#         if commit:
#             payment.save()
# 
#         if payment.pk:
#             payment.receipts = self.cleaned_data['receipts']
#             self.save_m2m()
# 
#         return payment


class OwnerForm(ModelForm):
    class Meta:
        model = Owner
        fields = '__all__'

    def clean_name(self):
        return title_case(self.cleaned_data['name'])


class OperationForm(ModelForm):
    class Meta:
        model = Operation
        fields = '__all__'

    def clean_name(self):
        return title_case(self.cleaned_data['name'])


class AuthorizationForm(NrYearForm):
    class Meta:
        model = Authorization
        fields = '__all__'


class PaymentReceiptForm(NrYearForm):
    class Meta:
        model = PaymentReceipt
        fields = '__all__'


class MaintenanceBulkForm(Form):
    year = IntegerField()
    only_with_active_deed = BooleanField(initial=True)
    unkept_spots = ModelMultipleChoiceField(
        queryset=Spot.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Spots'),
            is_stacked=False
        )
    )

    # TODO


class ImportForm(Form):
    document = FileField()
    wipe_beforehand = BooleanField(required=False)
