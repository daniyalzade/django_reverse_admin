from django.contrib import admin
from polls.models import Address
from polls.models import NonInlinePerson
from polls.models import Person
from django_reverse_admin import ReverseModelAdmin


class PersonAdmin(ReverseModelAdmin):
    inline_type = 'tabular'
    inline_reverse = [('home_addr', {'fields': ['street', 'city', 'state', 'zipcode']}),
                      ]


class NonInlinePersonAdmin(admin.ModelAdmin):
    pass


class AddressAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at', 'street', 'zipcode', 'city', 'state', '_person')


admin.site.register(Person, PersonAdmin)
admin.site.register(NonInlinePerson, NonInlinePersonAdmin)
admin.site.register(Address, AddressAdmin)
