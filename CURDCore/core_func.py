import copy

from django.conf.urls import url
from django.shortcuts import HttpResponse, render, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe


class ChangeList(object):
    '封装传到前端的值和方法'

    def __init__(self, request, base_curd_admin_obj, model_class, result_lists, filter_list, list_display, action_list):
        self.request = request
        self.base_curd_admin_obj = base_curd_admin_obj
        self.filter_list = filter_list
        self.list_display = list_display
        self.action_list = action_list
        self.model_class = model_class

        # ---------------分页开始------------------------
        changlist_name = '%s_%s_changelist' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        changlist_url = reverse('%s:%s' % (self.base_curd_admin_obj.site.namespace, changlist_name))
        from CURDService.utils import my_pager
        page_params_dict = copy.deepcopy(request.GET)
        page_params_dict._mutable = True
        pagers = my_pager.MyPagination(request.GET.get('page'), result_lists.count(), changlist_url, page_params_dict)
        self.result_list = result_lists[pagers.start_data:pagers.data_end]
        self.pager_tags = pagers.pager()
        # --------------分页结束-------------------------

    def add_button(self):
        # 添加的url  add_url,添加数据的按钮
        from django.http.request import QueryDict
        parms_dict = QueryDict(mutable=True)
        name = '%s_%s_add' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        add_url_temp = reverse('%s:%s' % (self.base_curd_admin_obj.site.namespace, name))

        parms_dict['_changelistfilter'] = self.request.GET.urlencode()
        add_url = '{0}?{1}'.format(add_url_temp, parms_dict.urlencode())
        return mark_safe(add_url)

    def gen_list_filter(self):
        '产生搜索数据'
        # --------------多条件搜索 ----------------
        filter_list = []
        from utils.search_conditions import FilterList
        for option in self.filter_list:
            if option.is_func:
                data_list = option.field_or_func()  # 如果是函数，则执行该函数，并获取返回的结果
            else:
                from django.db.models import ForeignKey, ManyToManyField
                field = self.model_class._meta.get_field(option.field_or_func)
                if isinstance(field, ForeignKey):  # 如果是ForeignKey 或者是ManyToMany，则查找器关联的表
                    data_list = FilterList(option, field.rel.model.objects.all(), self.request)
                elif isinstance(field, ManyToManyField):
                    data_list = FilterList(option, field.rel.model.objects.all(), self.request)
                else:
                    data_list = FilterList(option, field.model.objects.all(), self.request)
                filter_list.append(data_list)
        return filter_list
        # --------------组合条件筛选结束-------------------


class BaseCurdAdmin():
    '用于根据model生成url及数据的增删改查'
    list_display = '__all__'
    # list_display = ['username','email']

    add_edit_modelform = None
    filter_list = []  # filter搜索条件列表，需要在注册models的时候去配置

    def __init__(self, model_class, site):
        self.model_class = model_class
        self.site = site
        self.request = None

    # def del_data(self,request,queryset):
    #     del_list = request.POST.getlist('pk')
    #     queryset.filter(id__in=del_list).delete()
    #     return True
    #
    # del_data.text = '删除数据'
    action_list = []  # action列表

    @property
    def another_urls(self):
        '定义一个可以自己添加url的钩子'
        return []

    @property
    def urls(self):
        info = self.model_class._meta.app_label, self.model_class._meta.model_name  # model下的表的类（先前被封装了）会被传到此处
        # print(info,'info=---------')
        urlpatterns = [
            url(r'^$', self.changelist_view, name='%s_%s_changelist' % info),
            url(r'^add/$', self.add_view, name='%s_%s_add' % info),
            url(r'^(.+)/delete/$', self.delete_view, name='%s_%s_delete' % info),
            url(r'^(.+)/change/$', self.change_view, name='%s_%s_change' % info),
            url(r'^(.+)/detail/$', self.detail_view, name='%s_%s_detail' % info),
        ]
        urlpatterns += self.another_urls
        return urlpatterns

    def edit(self, model_obj=None, is_header=False):
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

    def get_condition(self):
        'GET传递的搜索条件'
        condition = {}
        filter_condition_list = [item.name for item in self.filter_list]
        for key in self.request.GET:
            if key in filter_condition_list:
                condition[key + '__in'] = self.request.GET.getlist(key)
        return condition

    def changelist_view(self, request):
        self.request = request
        result_lists = self.model_class.objects.filter(**self.get_condition()).all()

        # -----------Action操作开始------------------------
        # 返回到前端select框里面的数据
        action_list = []
        for action in self.action_list:
            temp = {'name': action.__name__, 'text': action.short_description}  # name指的是函数名，text指的是函数定制的中文名称
            action_list.append(temp)
        if request.method == 'POST':
            action_func_str = request.POST.get('action')
            ret = getattr(self, action_func_str)(request)
            action_response_url = reverse('{2}:{0}_{1}_changelist'.format(
                self.model_class._meta.app_label,
                self.model_class._meta.model_name, self.site.namespace))
            if ret:  # 执行函数，若返回True则跳转到当前页，否则返回到首页
                action_response_url = '%s?%s' % (action_response_url, request.GET.urlencode())
            return redirect(action_response_url)
        change_list_obj = ChangeList(request, self, self.model_class, result_lists, self.filter_list, self.list_display,
                                     action_list)
        content = {'change_list_obj': change_list_obj}
        return render(request, 'my_curd/changlist_view.html', content)

    def get_add_edit_modelform(self):
        from django.forms import ModelForm
        if self.add_edit_modelform:  # 如果用户有自定义的modelform则使用用户自定义的
            return self.add_edit_modelform
        else:
            class DataModelForm(ModelForm):  # 创建一个ModelForm用于增加和修改数据
                class Meta:
                    model = self.model_class
                    fields = "__all__"

            return DataModelForm

    def add_view(self, request):  # 新增数据
        if request.method == 'GET':
            add_modelform_obj = self.get_add_edit_modelform()()
        else:
            add_modelform_obj = self.get_add_edit_modelform()(data=request.POST, files=request.FILES)
            if add_modelform_obj.is_valid():
                add_obj = add_modelform_obj.save()  # 保存
                popup_id = request.GET.get('popup_id')
                if popup_id:  # 如果存在，说明是通过popup添加的数据
                    data_dict = {'pk': add_obj.pk, 'text': str(add_obj), 'popup_id': popup_id}
                    return render(request, 'my_curd/popup_response.html', {'data_dict': data_dict})
                else:  # 正常的添加数据，不使用popup
                    name = '%s_%s_changelist' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
                    changelist_url_temp = reverse('%s:%s' % (self.site.namespace, name))
                    changelist_url = '{0}?{1}'.format(changelist_url_temp, request.GET.get('_changelistfilter'))
                    return redirect(changelist_url)  # '重定向到changlist_view页面'
        return render(request, 'my_curd/add_data.html', {'form': add_modelform_obj})

    def change_view(self, request, pk):  # 编辑数据
        obj = self.model_class.objects.filter(id=pk).first()
        if request.method == 'GET':  # 返回带有数据的modelform
            edit_model_form_obj = self.get_add_edit_modelform()(instance=obj)
        else:
            edit_model_form_obj = self.get_add_edit_modelform()(instance=obj, data=request.POST, files=request.FILES)
            if edit_model_form_obj.is_valid():
                edit_model_form_obj.save()
                name = '%s_%s_changelist' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
                changelist_url_temp = reverse('%s:%s' % (self.site.namespace, name))
                changelist_url = '{0}?{1}'.format(changelist_url_temp, request.GET.get('_changelistfilter'))
                return redirect(changelist_url)  # '重定向到changlist_view页面'
        return render(request, 'my_curd/edit_data.html', {'form': edit_model_form_obj})

    def delete_view(self, request, pk):
        '删除某条数据'
        if pk:
            self.model_class.objects.filter(id=pk).delete()
            name = '%s_%s_changelist' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
            changelist_url_temp = reverse('%s:%s' % (self.site.namespace, name))
            changelist_url = '{0}?{1}'.format(changelist_url_temp, request.GET.get('_changelistfilter'))
            return redirect(changelist_url)  # '重定向到changlist_view页面'
        else:
            return HttpResponse('没有找到id值')

    def detail_view(self, request, pk):
        '显示某条数据的详细信息'
        obj = self.model_class.objects.filter(pk=pk).first()
        fields = self.model_class._meta.get_fields()
        detail_dict = {}
        for field in fields:
            detail_dict[field.name] = getattr(obj, field.name)
        return render(request, 'my_curd/detail_view.html', {'detail_dict': detail_dict})


class BaseCurdSite():  # 用于注册model
    def __init__(self):
        self._registry = {}
        self.namespace = 'curd'
        self.app_name = 'curd'

    def register(self, model_class, reg=BaseCurdAdmin):
        self._registry[model_class] = reg(model_class,
                                          self)  # self._registry={'User':BaseCurdAdmin(User,BaseCurdSite),....}

    def get_urls(self):
        from django.conf.urls import url, include
        ret = [
            url('login/', self.login, name='login'),
            url('logout/', self.logout, name='logout'),
        ]
        # 使用include生成url
        for model_cls, base_curd_admin_obj in self._registry.items():
            app_label = model_cls._meta.app_label
            model_name = model_cls._meta.model_name  # model_cls._meta 是app下的表名
            temp = url(r'^%s/%s/' % (app_label, model_name), include(base_curd_admin_obj.urls))
            ret.append(temp)
        return ret

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace

    def login(self, request):
        '登录'
        return HttpResponse('login')

    def logout(self, request):
        '登出'
        return HttpResponse('logout')


site = BaseCurdSite()
