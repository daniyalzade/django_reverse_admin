from django.db import models

class Address(models.Model):
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

class Person(models.Model):
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

