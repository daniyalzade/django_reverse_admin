from django.contrib import admin
from django.db import models
from polls.models import Address
from polls.models import NonInlinePerson
from polls.models import Person
from django_reverse_admin import ReverseModelAdmin

class PersonAdmin(ReverseModelAdmin):
    inline_type = 'tabular'
    inline_reverse = [('home_addr', {'fields': ['street', 'city', 'state', 'zipcode']}),
                      ]
admin.site.register(Person, PersonAdmin)

class NonInlinePersonAdmin(admin.ModelAdmin):
    pass
admin.site.register(NonInlinePerson, NonInlinePersonAdmin)

class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'zipcode', 'city', 'state', '_person')

admin.site.register(Address, AddressAdmin)
