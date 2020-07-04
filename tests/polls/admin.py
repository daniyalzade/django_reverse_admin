from django.contrib import admin
from polls.models import Address
from polls.models import NonInlinePerson
from polls.models import Person
from polls.models import PersonWithAddressNonId
from polls.models import PersonWithTwoAddresses
from polls.models import PhoneNumber
from django_reverse_admin import ReverseModelAdmin
from modeltranslation.admin import TranslationInlineModelAdmin
from modeltranslation.admin import TranslationAdmin


SITE_HEADER = 'Reverse Admin Site Header'
SITE_TITLE = 'Reverse Admin Site Title'


class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber


class AddressAdmin(TranslationAdmin):
    readonly_fields = ('street',)
    list_display = ('created_at', 'updated_at', 'street', 'zipcode', 'city', 'state',
                    'home_addr_person',
                    'cur_addr_person',
                    'oth_addr_person',
                    )

class AddressInlineAdmin(TranslationInlineModelAdmin):
    model = Address

class PersonAdmin(ReverseModelAdmin):
    inline_type = "stacked"
    list_display = ('name', 'age', 'home_addr')
    readonly_fields = ('age',)
    inlines = [
        PhoneNumberInline
    ]
    inline_reverse = [
        {
            'field_name': 'home_addr',
            'kwargs': {
                'fields': ['street', 'city', 'state', 'zipcode'],
            },
            'admin_class': AddressInlineAdmin
        }
    ]


admin.site.register(Person, PersonAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.site_header = SITE_HEADER
admin.site.site_title = SITE_TITLE
