from django.db import models

class TemporalBase(models.Model):
    """
    A base class that adds useful created_at and updated_at fields
    to the classes inheriting from it
    """
    created_at = models.DateTimeField("created at", auto_now_add=True, editable=False)
    updated_at = models.DateTimeField("updated at", auto_now=True, editable=False)

    class Meta:
        abstract = True


class Address(TemporalBase):
    street = models.CharField(max_length=255)
    street_2 = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.CharField(max_length=10)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)

    def _person(self):
        return self.person

    def __str__(self):
        street_2 = ''
        if self.street_2:
            street_2 = ' - {}'.format(self.street_2)
        return '{}{}, {}, {}'.format(self.street, street_2, self.city, self.zipcode)


class Person(TemporalBase):
    name = models.CharField(max_length=255)
    home_addr = models.OneToOneField(Address,
                                     blank=True,
                                     null=True,
                                     related_name='person',
                                     on_delete=models.CASCADE
                                     )

    def __str__(self):
        return self.name


class NonInlinePerson(Person):
    class Meta:
        proxy = True
