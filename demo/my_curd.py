from django.urls import reverse
from django.utils.safestring import mark_safe

from CURDCore import core_func


# from app01 import models   #从app中导入models


class UserCurdAdmin(core_func.BaseCurdAdmin):
    def edit(self, model_obj=None, is_header=False):
        '编辑数据的函数，推荐使用'
        if is_header:
            return '编辑'
        else:
            from django.http.request import QueryDict
            parms_dict = QueryDict(mutable=True)
            if self.request.method == 'GET':
                parms_dict['_changelistfilter'] = self.request.GET.urlencode()
            name = '{0}:{1}_{2}_change'.format(self.site.namespace, model_obj._meta.app_label,
                                               model_obj._meta.model_name)
            url = reverse(name, args=(model_obj.pk,))  # s生成的结果同上方的edit   pk和id同样
            edit_url = '{0}?{1}'.format(url, parms_dict.urlencode())
            edit_tag = '<a href="%s">编辑</a>' % edit_url
            return mark_safe(edit_tag)

    def delete(self, model_obj=None, is_header=False):
        '删除数据的函数，推荐使用'
        if is_header:
            return '删除'
        else:
            from django.http.request import QueryDict
            parms_dict = QueryDict(mutable=True)
            if self.request.method == 'GET':
                parms_dict['_changelistfilter'] = self.request.GET.urlencode()
            name = '{0}:{1}_{2}_delete'.format(self.site.namespace, model_obj._meta.app_label,
                                               model_obj._meta.model_name)
            url = reverse(name, args=(model_obj.pk,))  # s生成的结果同上方的edit   pk和id同样
            delete_url = '{0}?{1}'.format(url, parms_dict.urlencode())
            delete_tag = '<a href="%s">删除</a>' % delete_url
            return mark_safe(delete_tag)

    def reverse_produce_url(self, model_obj=None, is_header=False):
        '练习反向生成url'
        if is_header:
            return '反向生成url练习'
        else:
            # 取namespace的方式
            from CURDCore import core_func
            info = model_obj._meta.app_label, model_obj._meta.model_name
            name = '{0}:{1}_{2}_change'.format(self.site.namespace, model_obj._meta.app_label,
                                               model_obj._meta.model_name)
            url = reverse(name, args=(model_obj.pk,))  # s生成的结果同上方的edit   pk和id同样
            return url

    def combine_username_email(self, model_obj=None, is_header=False):
        '自定制列，将字段名连接起来，供参考'
        if is_header:
            return '定制列'
        else:
            v = '%s--%s' % (model_obj.username, model_obj.email)
            return v

    def checkbox(self, model_obj=None, is_header=False):
        '提供选择框，推荐使用'
        if is_header:
            return '选择'
        else:
            a_tag = '<input type="checkbox" name="pk" value="{0}">'.format(model_obj.pk)
            return mark_safe(a_tag)

    # action函数定义
    def init_data(self, request):
        'action动作 init_data'
        received_data = request.POST.getlist('pk')
        return True

    init_data.text = '初始化数据'  # action动作的定制名称

    def del_data(self, request):
        'action动作 del_data'
        return True

    del_data.text = '删除数据'
    action_list = [init_data, del_data]  # action动作的函数名，添加到此处可以生效
    list_display = [checkbox, 'id', 'username', 'email', 'role', 'usergroup', edit, delete, reverse_produce_url,
                    combine_username_email]  # 定制数据展示的内容，可以是字段名，也可以是函数名，函数必须定义在本类中
    from utils.search_conditions import FilterOption
    filter_list = [
        FilterOption('username', is_multiple=True, text_func_name='text_username', val_func_name='val_username'),
        FilterOption('role', is_multiple=False),
        FilterOption('usergroup', is_multiple=True),
    ]  # 搜索条件的定制


core_func.site.register(models.User, UserCurdAdmin)  # 注册models中的字段
core_func.site.register(models.Role)
core_func.site.register(models.UserGroup)
