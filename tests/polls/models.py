import uuid

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


class AddressBase(TemporalBase):
    street = models.CharField(max_length=255)
    street_2 = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.CharField(max_length=10)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)

    class Meta:
        abstract = True

    def __str__(self):
        street_2 = ''
        if self.street_2:
            street_2 = ' - {}'.format(self.street_2)
        return '{}{}, {}, {}'.format(self.street, street_2, self.city, self.zipcode)


class Address(AddressBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class AddressNonId(AddressBase):
    address_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Person(TemporalBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    age = models.IntegerField(blank=True, null=True)
    home_addr = models.OneToOneField(Address,
                                     blank=True,
                                     null=True,
                                     related_name='home_addr_person',
                                     on_delete=models.CASCADE
                                     )

    def __str__(self):
        return self.name


class PersonWithAddressNonId(TemporalBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    age = models.IntegerField(blank=True, null=True)
    home_addr = models.OneToOneField(AddressNonId,
                                     blank=True,
                                     null=True,
                                     related_name='home_addr_person',
                                     on_delete=models.CASCADE
                                     )

    def __str__(self):
        return self.name


class PersonWithTwoAddresses(TemporalBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    age = models.IntegerField(blank=True, null=True)
    cur_addr = models.OneToOneField(Address,
                                    blank=True,
                                    null=True,
                                    related_name='cur_addr_person',
                                    on_delete=models.CASCADE
                                    )
    oth_addr = models.OneToOneField(Address,
                                    blank=True,
                                    null=True,
                                    related_name='oth_addr_person',
                                    on_delete=models.CASCADE
                                    )

    def __str__(self):
        return self.name


class PhoneNumber(TemporalBase):
    person = models.ForeignKey(Person,
                               on_delete=models.CASCADE
                               )
    number = models.CharField(max_length=255)

    def __str__(self):
        return self.number


class NonInlinePerson(Person):
    class Meta:
        proxy = True
