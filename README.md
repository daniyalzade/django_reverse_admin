# Django Reverse Admin

Module that makes django admin handle OneToOneFields in a better way. A common use case for one-to-one relationships is to "embed" a model inside another one. For example, a Person may have multiple foreign keys pointing to an Address entity, one home address, one business address and so on. Django admin displays those relations using select boxes, letting the user choose which address entity to connect to a person. A more natural way to handle the relationship is using inlines. However, since the foreign key is placed on the owning entity, django admins standard inline classes can't be used. Which is why I created this module that implements "reverse inlines" for this use case.

Fix/extension of:
* [adminreverse](https://github.com/rpkilby/django-reverse-admin)
* [reverseadmin](http://djangosnippets.org/snippets/2032/)

[![CircleCI](https://circleci.com/gh/daniyalzade/django_reverse_admin.svg?style=svg)](https://circleci.com/gh/daniyalzade/django_reverse_admin)

# Requirements

* **Python**: 3.4, 3.5, 3.6, 3.7
* **Django**: 2.0

From Version 2.0 Django Filter is Python 3 only. If you need to support Python 2.7 use the version 1.0 release.

# Installation

Install using pip:

```sh
pip install django_reverse_admin
```

# Testing

Use `tox` for testing.

```sh
tox
```

## Testing Manually Using Django Admin

Run the following commands to make sure that db.sqlite3 has all the data that you need

```sh
cd tests
python manage.py makemigrations
python manage.py makemigrations polls
python manage.py migrate
python manage.py loaddata fixtures/init_data.json
python manage.py runserver
```

Admin user username is `reverse` and password is `reverseadmin`

# Usage

`models.py` file

```py
from django.db import models

class Address(models.Model):
    street = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=10)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)

class Person(models.Model):
    name = models.CharField(max_length=255)
    business_addr = models.ForeignKey(Address,
                                      related_name='business_addr')
    home_addr = models.OneToOneField(Address, related_name='home_addr')
    other_addr = models.OneToOneField(Address, related_name='other_addr')
```

`admin.py` file

```py
from django.contrib import admin
from django.db import models
from models import Person
from django_reverse_admin import ReverseModelAdmin

class PersonAdmin(ReverseModelAdmin):
    inline_type = 'tabular'
    inline_reverse = ['business_addr',
                      ('home_addr', {'fields': ['street', 'city', 'state', 'zipcode']}),
                      ]
admin.site.register(Person, PersonAdmin)
```

inline_type can be either "tabular" or "stacked" for tabular and stacked inlines respectively.

The module is designed to work with Django 2+ Since it hooks into the internals of the admin package, it may not work with later Django versions.

# Demo

Below is what an admin change_view with reverse inline looks like
![reverse inline](/images/admin_with_reverse_inline.png)

Below is what the same change_view would look like WITHOUT reverse inline
![no reverse inline](/images/admin_without_reverse_inline.png)

# Contribtion

* Make sure that the tests are passing before opening up the PR
* Create a PR for feature enhancements
* Once a PR is merged, update version with the following commands:

```
bumpversion patch
git push origin master --tags
```

# Packaging

`tox` creates a package in `.tox/dist`. Use twine to upload it to pypi:

```sh
twine upload .tox/dist/django_reverse_admin-*.zip
```
