from modeltranslation.translator import translator, TranslationOptions
from .models import Address

class AddressTranslationOptions(TranslationOptions):
    fields = ('street', 'city', 'state')

translator.register(Address, AddressTranslationOptions)
