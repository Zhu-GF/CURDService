#搜索条件的创建
from types import FunctionType
import copy

class FilterOption(object):
    '筛选对象，models字段'
    def __init__(self,field_or_func,is_multiple=False,text_func_name=None,val_func_name=None):
        '''

        :param field_or_func: models字段或者是定义的函数名称，
        :param is_multiple: 条件是否是多选
        :param text_func_name: 函数的名称
        :param val_func_name: 函数的值的名称
        '''
        self.field_or_func=field_or_func
        self.is_multiple=is_multiple
        self.text_func_name=text_func_name
        self.val_func_name=val_func_name

    @property
    def is_func(self):
        '判断字段是否是函数'
        if isinstance(self.field_or_func,FunctionType):
            return True

    @property
    def name(self):
        if self.is_func:
            return self.field_or_func.__name__               #如果是函数，则返回函数的名字
        else:
            return self.field_or_func     #否则返回字段的名称

class FilterList(object):
    '返回搜索的条件'
    def __init__(self,option,queryset,request):
        '''

        :param option:FilterOption对象
        :param queryset: queryset对象
        :param request: django request
        '''
        self.option=option
        self.queryset=queryset
        self.params_dict=copy.deepcopy(request.GET)                   #前端的GET请求的参数
        self.path_info=request.path_info                             #前端访问过来的url

    def __iter__(self):
        '产生a标签'
        from django.utils.safestring import mark_safe
        #‘全部的a标签’，如果用户选择的是全部，则将该用户
        #print('self.option.name',self.option.name)
        yield mark_safe("<div class='all-area'>")
        if self.option.name in self.params_dict:
            pop_val=self.params_dict.pop(self.option.name)         #是全部都搜索，则删除掉该条件
            url='%s?%s'%(self.path_info,self.params_dict.urlencode())
            self.params_dict.setlist(self.option.name,pop_val)   #为什么要设置回去呢？将删除的值添加进去，留着下面yield其他细项使用
            yield mark_safe('<a href="{0}" >全部</a>'.format(url))
        else:
            url='%s?%s'%(self.path_info,self.params_dict.urlencode())
            yield mark_safe('<a href="{0}" class="active">全部</a>'.format(url))
        yield mark_safe("</div><div class='others-area'>")

        for queryset_obj in self.queryset:
            params_dict=copy.deepcopy(self.params_dict)
            val=str(getattr(queryset_obj,self.option.val_func_name)() if self.option.val_func_name else queryset_obj.pk)       #搜索条件的值,
            #如果在models中定义了val_func_name，text_func_name函数，则会获取这两个函数返回的值
            text=getattr(queryset_obj,self.option.text_func_name)() if self.option.text_func_name else str(queryset_obj)     #搜索条件显示的文本
            active=False
            if self.option.is_multiple:
                val_list=params_dict.getlist(self.option.name)
                if val in val_list:        #如果该项内容已经在GET参数里面，则添加active，并删除该值，表示不需要再添加进去了
                    val_list.remove(val)
                    active=True
                else:
                    #active = True
                    params_dict.appendlist(self.option.name,val)     #否则将值添加进去
            else:
                val_list=params_dict.getlist(self.option.name)
                if val in val_list:
                    active=True
                params_dict[self.option.name]=val
            url='%s?%s'%(self.path_info,params_dict.urlencode())
            if active:
                temp_a='<a href="{0}" class="active">{1}</a>'.format(url,text)
            else:
                temp_a = '<a href="{0}">{1}</a>'.format(url, text)
            yield mark_safe(temp_a)
        yield mark_safe("</div>")



