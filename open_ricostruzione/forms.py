from django.forms import forms
from django.utils.translation import ugettext_lazy as _
from open_ricostruzione.fields import InterventoProgrammaChoices, ImpresaChoices


class InterventoProgrammaSearchFormNavbar(forms.Form):
    intervento_programma = InterventoProgrammaChoices(
        to_field_name='slug',
        required=True,
        label='',
        widget=InterventoProgrammaChoices.widget(
            select2_options={
                'width': '48em',
                'placeholder': _(u"CERCA UN INTERVENTO"),
            }
        )
    )


class ImpresaSearchFormNavbar(forms.Form):
    impresa = ImpresaChoices(
        to_field_name='slug',
        required=True,
        label='',
        widget=ImpresaChoices.widget(
            select2_options={
                'width': '48em',
                'placeholder': _(u"CERCA UN'IMPRESA"),
            }
        )
    )