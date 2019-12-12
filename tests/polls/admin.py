from django.contrib import admin
from polls.models import Address
from polls.models import NonInlinePerson
from polls.models import Person
from polls.models import PersonWithTwoAddresses
from polls.models import PhoneNumber
from django_reverse_admin import ReverseModelAdmin


SITE_HEADER = 'Reverse Admin Site Header'
SITE_TITLE = 'Reverse Admin Site Title'


class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('number',)


class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber


class PersonAdmin(ReverseModelAdmin):
    inline_type = "stacked"
    list_display = ('name', 'age', 'home_addr')
    readonly_fields = ('age',)
    inlines = [
        PhoneNumberInline
    ]
    inline_reverse = [
        ('home_addr', {
            'fields': ['street', 'city', 'state', 'zipcode'],
            'readonly_fields': ('street',)
        }),
    ]


class PersonWithTwoAddressesAdmin(ReverseModelAdmin):
    inline_type = 'tabular'
    list_display = ('name', 'age', 'cur_addr', 'oth_addr')
    inline_reverse = [
        ('cur_addr', {'fields': ['street', 'city', 'state', 'zipcode']}),
        ('oth_addr', {'fields': ['street', 'city', 'state', 'zipcode']}),
    ]


class NonInlinePersonAdmin(admin.ModelAdmin):
    pass


class AddressAdmin(admin.ModelAdmin):
    readonly_fields = ('street',)
    list_display = ('created_at', 'updated_at', 'street', 'zipcode', 'city', 'state',
                    'home_addr_person',
                    'cur_addr_person',
                    'oth_addr_person',
                    )


admin.site.register(Person, PersonAdmin)
admin.site.register(PersonWithTwoAddresses, PersonWithTwoAddressesAdmin)
admin.site.register(PhoneNumber, PhoneNumberAdmin)
admin.site.register(NonInlinePerson, NonInlinePersonAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.site_header = SITE_HEADER
admin.site.site_title = SITE_TITLE
