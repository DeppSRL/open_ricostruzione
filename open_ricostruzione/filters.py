from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

class HasProgetto(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Associata a un Progetto')
    parameter_name = 'has_progetto'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', _('si')),
            ('no', _('no')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'yes':
            return queryset.exclude(progetto__isnull=True)

        if self.value() == 'no':
            return queryset.filter(progetto__isnull=True)
