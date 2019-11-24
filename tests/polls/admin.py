from django.contrib import admin
from polls.models import Address
from polls.models import NonInlinePerson
from polls.models import Person
from polls.models import PersonWithTwoAddresses
from django_reverse_admin import ReverseModelAdmin


class PersonAdmin(ReverseModelAdmin):
    inline_type = 'tabular'
    list_display = ('name', 'home_addr')
    inline_reverse = [
        ('home_addr', {'fields': ['street', 'city', 'state', 'zipcode']}),
    ]


class PersonWithTwoAddressesAdmin(ReverseModelAdmin):
    inline_type = 'tabular'
    list_display = ('name', 'cur_addr', 'oth_addr')
    inline_reverse = [
        ('cur_addr', {'fields': ['street', 'city', 'state', 'zipcode']}),
        ('oth_addr', {'fields': ['street', 'city', 'state', 'zipcode']}),
    ]


class NonInlinePersonAdmin(admin.ModelAdmin):
    pass


class AddressAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at', 'street', 'zipcode', 'city', 'state',
                    'home_addr_person',
                    'cur_addr_person',
                    'oth_addr_person',
                    )


admin.site.register(Person, PersonAdmin)
admin.site.register(PersonWithTwoAddresses, PersonWithTwoAddressesAdmin)
admin.site.register(NonInlinePerson, NonInlinePersonAdmin)
admin.site.register(Address, AddressAdmin)
