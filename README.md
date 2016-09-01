# Django Reverse Admin

Module that makes django admin handle OneToOneFields in a better way.
A common use case for one-to-one relationships is to "embed" a model
inside another one. For example, a Person may have multiple foreign
keys pointing to an Address entity, one home address, one business
address and so on. Django admin displays those relations using select
boxes, letting the user choose which address entity to connect to a
person. A more natural way to handle the relationship is using
inlines. However, since the foreign key is placed on the owning
entity, django admins standard inline classes can't be used. Which is
why I created this module that implements "reverse inlines" for this
use case.

Work "shamelessly copied from":
* [adminreverse](https://github.com/rpkilby/django-reverse-admin)
* [reverseadmin](http://djangosnippets.org/snippets/2032/)

Made to work with django 1.10

## Example

`models.py` file
```py

from django.db import models
class Address(models.Model):
    street = models.CharField(max_length = 255)
    zipcode = models.CharField(max_length=10)
    city = models.CharField(max_length=255)
class Person(models.Model):
    name = models.CharField(max_length = 255)
    business_addr = models.ForeignKey(Address,
                                         related_name = 'business_addr')
    home_addr = models.OneToOneField(Address, related_name = 'home_addr')
    other_addr = models.OneToOneField(Address, related_name = 'other_addr')
```

`admin.py` file
```py
    from django.contrib import admin
    from django.db import models
    from models import Person
    from django_reverse_admin import ReverseModelAdmin
    class AddressForm(models.Form):
        pass
    class PersonAdmin(ReverseModelAdmin):
        inline_type = 'tabular'
        inline_reverse = ('business_addr', ('home_addr', AddressForm), ('other_addr' (
            'form': OtherForm
            'exclude': ()
        )))
    admin.site.register(Person, PersonAdmin)
```

inline_type can be either "tabular" or "stacked" for tabular and
stacked inlines respectively.

The module is designed to work with Django 1.10. Since it hooks into
the internals of the admin package, it may not work with later Django
versions.
