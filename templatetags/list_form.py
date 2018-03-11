from django.forms.models import ModelMultipleChoiceField, ModelChoiceField
from CURDService.CURDCore.core_func import site
from django.urls import reverse
from django import template

register = template.Library()


@register.inclusion_tag('my_curd/add_edit_data_self_defineForm.html')
def list_forms(add_modelform_obj):
    forms_list = []
    for form_obj in add_modelform_obj:
        row_list = {'is_popup': False, 'item': None, 'popup_url': None}
        if isinstance(form_obj.field, ModelChoiceField):  # 说明字段带有ForeignKey或ManytoMany字段
            row_list['is_popup'] = True
            info = form_obj.field.queryset.model._meta.app_label, form_obj.field.queryset.model._meta.model_name
            url_name = '%s_%s_add' % info
            popup_base_name = '%s:%s' % (site.namespace, url_name)
            popup_base_url = reverse(popup_base_name)
            popup_url = '%s?popup_id=%s' % (popup_base_url, form_obj.auto_id)
            row_list['popup_url'] = popup_url
            row_list['item'] = form_obj
        else:
            row_list['item'] = form_obj
        forms_list.append(row_list)
    return {'forms_list': forms_list}
