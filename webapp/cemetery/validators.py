from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


name_validator = RegexValidator('^[a-zA-Z-]+$', _('A name can contain only letters or a dash (-)'))
