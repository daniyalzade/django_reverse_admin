from django.contrib.admin import helpers, ModelAdmin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin.utils import (flatten_fieldsets, unquote)
from django.db import models
from django.db.models import OneToOneField, ForeignKey
from django.forms import ModelForm
from django.forms.formsets import all_valid
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.utils.encoding import force_text
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
    parent_fk_name = ''

    def __init__(self,
                 data=None,
                 files=None,
                 instance=None,
                 prefix=None,
                 queryset=None,
                 save_as_new=False):
        object = getattr(instance, self.parent_fk_name, None)
        if object:
            qs = self.model.objects.filter(pk=object.pk)
        else:
            qs = self.model.objects.none()
            self.extra = 1
        super(ReverseInlineFormSet, self).__init__(data, files,
                                                   prefix=prefix,
                                                   queryset=qs)
        for form in self.forms:
            form.empty_permitted = False


def _formsets_are_blank(request, obj, formsets):
    """
    This function handles the blank/null inlines by checking whether the
    non-valid formsets are both unchanged and are for inline fields.
    """

    for formset in formsets:
        if isinstance(formset, ReverseInlineFormSet):
            field = next((f for f in obj._meta.fields if f.name == formset.parent_fk_name), None)
            if not field.blank or formset.has_changed():
                return False
        elif formset.has_changed():
            return False
    return True


def reverse_inlineformset_factory(parent_model,
                                  model,
                                  parent_fk_name,
                                  form=ModelForm,
                                  fields=None,
                                  exclude=None,
                                  formfield_callback=lambda f: f.formfield()):

    if fields is None and exclude is None:
        related_fields = [f for f in model._meta.get_fields() if
                          (f.one_to_many or f.one_to_one) and f.auto_created and not f.concrete]
        fields = [f.name for f in model._meta.get_fields() if f not in
                  related_fields]  # ignoring reverse relations
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
        if 'fields' in kwargs:
            fields = kwargs.pop('fields')
        elif self.get_fieldsets(request, obj):
            fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        else:
            fields = None

        # want to combine exclude arguments - can't do that if they're None
        # also, exclude starts as a tuple - need to make it a list
        exclude = list(kwargs.get("exclude", []))
        exclude_2 = self.exclude or []
        non_editable_fields = [f for f in self.model._meta.fields if not f.editable]
        exclude.extend(list(exclude_2))
        exclude.extend(non_editable_fields)
        # but need exclude to be None if result is an empty list
        exclude = exclude or None

        defaults = {
            "form": self.form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
        }
        kwargs.update(defaults)
        return reverse_inlineformset_factory(self.parent_model,
                                             self.model,
                                             self.parent_fk_name,
                                             **kwargs)


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
        self.exclude = list(self.exclude)

        inline_instances = []
        for field_name in self.inline_reverse:

            kwargs = {}
            admin_class = None
            if isinstance(field_name, tuple):
                kwargs = field_name[1]
                field_name = field_name[0]
            elif isinstance(field_name, dict):
                kwargs = field_name.get('kwargs', kwargs)
                admin_class = field_name.get('admin_class', admin_class)
                field_name = field_name['field_name']

            field = model._meta.get_field(field_name)
            if isinstance(field, (OneToOneField, ForeignKey)):
                if admin_class:
                    admin_class = type(
                        str('DynamicReverseInlineModelAdmin'),
                        (admin_class, ReverseInlineModelAdmin),
                        dict(ReverseInlineModelAdmin.__dict__),
                    )
                else:
                    admin_class = ReverseInlineModelAdmin

                name = field.name
                parent = field.remote_field.model
                inline = admin_class(model,
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
        return self._changeform_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        return self._changeform_view(request, None, form_url, extra_context)

    def _changeform_view(self, request, object_id, form_url, extra_context):
        add = object_id is None

        model = self.model
        opts = model._meta
        if not self.has_add_permission(request):
            raise PermissionDenied

        model_form = self.get_form(request)
        formsets = []

        if add:
            if not self.has_add_permission(request):
                raise PermissionDenied
            obj = None

        else:
            obj = self.get_object(request, unquote(object_id))

            if not self.has_view_permission(request, obj) and not self.has_change_permission(request, obj):
                raise PermissionDenied

            if obj is None:
                return self._get_obj_does_not_exist_redirect(request, opts, object_id)

        if request.method == 'POST':
            form = model_form(request.POST, request.FILES, instance=obj)
            form_validated = form.is_valid()
            if form_validated:
                new_object = self.save_form(request, form, change=not add)
            else:
                new_object = form.instance
            prefixes = {}
            for FormSet, inline in self.get_formsets_with_inlines(request):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(data=request.POST, files=request.FILES,
                                  instance=new_object,
                                  save_as_new="_saveasnew" in request.POST,
                                  prefix=prefix)
                formsets.append(formset)
            if form_validated and _formsets_are_blank(request, new_object, formsets):
                self.save_model(request, new_object, form, change=not add)
                return self.response_add(request, new_object)
            elif form_validated and all_valid(formsets):
                # Here is the modified code.
                for formset, inline in zip(formsets, self.get_inline_instances(request)):
                    if not isinstance(inline, ReverseInlineModelAdmin):
                        continue
                    # The idea or this piece is coming from https://stackoverflow.com/questions/50910152/inline-formset-returns-empty-list-on-save.
                    # Without this, formset.save() was returning None for forms that
                    # haven't been modified
                    forms = [f for f in formset]
                    if not forms:
                        continue
                    obj = forms[0].save()
                    setattr(new_object, inline.parent_fk_name, obj)
                self.save_model(request, new_object, form, change=not add)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=not add)

                # self.log_addition(request, new_object)
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
            if add:
                form = model_form(initial=initial)
                prefixes = {}
                for FormSet, inline in self.get_formsets_with_inlines(request):
                    prefix = FormSet.get_default_prefix()
                    prefixes[prefix] = prefixes.get(prefix, 0) + 1
                    if prefixes[prefix] != 1:
                        prefix = "%s-%s" % (prefix, prefixes[prefix])
                    formset = FormSet(instance=self.model(), prefix=prefix)
                    formsets.append(formset)
            else:
                form = model_form(instance=obj)
                formsets, inline_instances = self._create_formsets(request, obj, change=True)

        readonly_fields = self.get_readonly_fields(request, obj)
        adminForm = helpers.AdminForm(form,
                                      list(self.get_fieldsets(request)),
                                      self.prepopulated_fields,
                                      readonly_fields=readonly_fields,
                                      model_admin=self
                                      )
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(self.get_inline_instances(request), formsets):
            fieldsets = list(inline.get_fieldsets(request))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        # Inherit the default context from admin_site
        context = self.admin_site.each_context(request)
        reverse_admin_context = {
            'title': _(('Change %s', 'Add %s')[add] % force_text(opts.verbose_name)),
            'adminform': adminForm,
            # 'is_popup': '_popup' in request.REQUEST,
            'is_popup': False,
            'show_delete': False,
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            # 'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(reverse_admin_context)
        context.update(extra_context or {})
        return self.render_change_form(request, context, form_url=form_url, add=add)
