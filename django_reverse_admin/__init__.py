#pylint: skip-file
from django.contrib.admin import helpers, ModelAdmin
from django.contrib.admin.options import InlineModelAdmin
from django.db import models
from django.db.models import OneToOneField, ForeignKey
from django.forms import ModelForm
from django.forms.formsets import all_valid
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.utils.encoding import force_unicode
from django.utils.functional import curry
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied

class ReverseInlineFormSet(BaseModelFormSet):
    '''
    A formset with either a single object or a single empty
    form. Since the formset is used to render a required OneToOne
    relation, the forms must not be empty.
    '''
    model = None
    parent_fk_name = ''
    def __init__(self,
                 data=None,
                 files=None,
                 instance=None,
                 prefix=None,
                 queryset=None,
                 save_as_new=False):
        object = getattr(instance, self.parent_fk_name)
        if object:
            qs = self.model.objects.filter(pk=object.id)
        else:
            qs = self.model.objects.filter(pk=-1)
            self.extra = 1
        super(ReverseInlineFormSet, self).__init__(data, files,
                                                   prefix=prefix,
                                                   queryset=qs)
        for form in self.forms:
            form.empty_permitted = False

def reverse_inlineformset_factory(parent_model,
                                  model,
                                  parent_fk_name,
                                  form=ModelForm,
                                  fields=None,
                                  exclude=None,
                                  formfield_callback=lambda f: f.formfield()):
    kwargs = {
        'form': form,
        'formfield_callback': formfield_callback,
        'formset': ReverseInlineFormSet,
        'extra': 0,
        'can_delete': False,
        'can_order': False,
        'fields': fields,
        'exclude': exclude,
        'max_num': 1,
    }
    FormSet = modelformset_factory(model, **kwargs)
    FormSet.parent_fk_name = parent_fk_name
    return FormSet

class ReverseInlineModelAdmin(InlineModelAdmin):
    '''
    Use the name and the help_text of the owning models field to
    render the verbose_name and verbose_name_plural texts.
    '''
    def __init__(self,
                 parent_model,
                 parent_fk_name,
                 model, admin_site,
                 inline_type):
        self.template = 'admin/edit_inline/%s.html' % inline_type
        self.parent_fk_name = parent_fk_name
        self.model = model
        field_descriptor = getattr(parent_model, self.parent_fk_name)
        field = field_descriptor.field

        self.verbose_name_plural = field.verbose_name.title()
        self.verbose_name = field.help_text
        if not self.verbose_name:
            self.verbose_name = self.verbose_name_plural
        super(ReverseInlineModelAdmin, self).__init__(parent_model, admin_site)

    def get_formset(self, request, obj=None, **kwargs):
        fields = None
        self.exclude = []
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        # if exclude is an empty list we use None, since that's the actual
        # default
        exclude = (exclude + kwargs.get("exclude", [])) or None
        defaults = {
            "form": self.form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
        }
        defaults.update(kwargs)
        return reverse_inlineformset_factory(self.parent_model,
                                             self.model,
                                             self.parent_fk_name,
                                             **defaults)

class ReverseModelAdmin(ModelAdmin):
    '''
    Patched ModelAdmin class. The add_view method is overridden to
    allow the reverse inline formsets to be saved before the parent
    model.
    '''
    def __init__(self, model, admin_site):

        super(ReverseModelAdmin, self).__init__(model, admin_site)
        if self.exclude is None:
            self.exclude = []

        inline_instances = []
        for field_name in self.inline_reverse:

            kwargs = {}
            if isinstance(field_name, tuple):
                kwargs['form'] = field_name[1]
                field_name = field_name[0]

            field = model._meta.get_field(field_name)
            if isinstance(field, (OneToOneField, ForeignKey)):
                name = field.name
                parent = field.remote_field.model
                inline = ReverseInlineModelAdmin(model,
                                                 name,
                                                 parent,
                                                 admin_site,
                                                 self.inline_type)
                if kwargs:
                    inline.__dict__.update(kwargs)
                inline_instances.append(inline)
                self.exclude.append(name)
        self.tmp_inline_instances = inline_instances

    def get_inline_instances(self, request, obj=None):
        return self.tmp_inline_instances + super(ReverseModelAdmin, self).get_inline_instances(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return self.changeform_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        "The 'add' admin view for this model."
        model = self.model
        opts = model._meta
        if not self.has_add_permission(request):
            raise PermissionDenied

        model_form = self.get_form(request)
        formsets = []
        if request.method == 'POST':
            form = model_form(request.POST, request.FILES)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=False)
            else:
                form_validated = False
                new_object = self.model()
            prefixes = {}
            for FormSet, inline in self.get_formsets_with_inlines(request):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(data=request.POST, files=request.FILES,
                                  instance=new_object,
                                  save_as_new=request.POST.has_key("_saveasnew"),
                                  prefix=prefix)
                formsets.append(formset)
            if all_valid(formsets) and form_validated:
                # Here is the modified code.
                for formset, inline in zip(formsets, self.get_inline_instances(request)):
                    if not isinstance(inline, ReverseInlineModelAdmin):
                        continue
                    obj = formset.save()[0]
                    setattr(new_object, inline.parent_fk_name, obj)
                self.save_model(request, new_object, form, change=False)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=False)

                #self.log_addition(request, new_object)
                return self.response_add(request, new_object)
        else:
            # Prepare the dict of initial data from the request.
            # We have to special-case M2Ms as a list of comma-separated PKs.
            initial = dict(request.GET.items())
            for k in initial:
                try:
                    f = opts.get_field(k)
                except models.FieldDoesNotExist:
                    continue
                if isinstance(f, models.ManyToManyField):
                    initial[k] = initial[k].split(",")
            form = model_form(initial=initial)
            prefixes = {}
            for FormSet, inline in self.get_formsets_with_inlines(request):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=self.model(), prefix=prefix)
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)), self.prepopulated_fields)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(self.get_inline_instances(request), formsets):
            fieldsets = list(inline.get_fieldsets(request))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            #'is_popup': request.REQUEST.has_key('_popup'),
            'is_popup': False,
            'show_delete': False,
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            #'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, form_url=form_url, add=True)
