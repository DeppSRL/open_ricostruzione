from django.forms import forms
from django.utils.translation import ugettext_lazy as _
from open_ricostruzione.fields import InterventoProgrammaChoices

class InterventoProgrammaSearchFormHome(forms.Form):

    territori = InterventoProgrammaChoices(
        to_field_name = 'slug',
        required=True,
        label='',
        widget=InterventoProgrammaChoices.widget(
            select2_options={
                'width': '48em',
                'placeholder': _(u"CERCA UN INTERVENTO"),
            }
        )
    )