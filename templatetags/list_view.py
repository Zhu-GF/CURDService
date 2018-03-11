from django.template import Library
from django import template
from types import FunctionType

register = template.Library()


def table_body(list_dispaly, data_list, base_curd_admin_obj):
    for row in data_list:  # 使用列表生成器写
        if list_dispaly == '__all__':
            yield [str(row), ]
        else:
            yield [name(base_curd_admin_obj, row) if isinstance(name, FunctionType) else getattr(row, name) for name in
                   list_dispaly]


def table_head(list_dispaly, data_list, base_curd_admin_obj):
    '定义表头，并能够显示verbose_name'
    table_head_list = base_curd_admin_obj.list_display
    if list_dispaly == '__all__':
        yield '对象列表'
    else:
        for item in list_dispaly:
            if isinstance(item, FunctionType):  # 如果item是函数
                yield item(base_curd_admin_obj, is_header=True)
            else:
                model_class = base_curd_admin_obj.model_class._meta.get_field(item)  # 表的类
                yield base_curd_admin_obj.model_class._meta.get_field(item).verbose_name
                # return table_head_list


# inclusion_tag用法，返回值是给'my_curd/table_body.html'使用，在此子模板中写入数据，并将此模板嵌入到使用 include func 的父模板中

@register.inclusion_tag('my_curd/table_body.html')
def func(list_dispaly, data_list, base_curd_admin_obj):
    table_body_list = table_body(list_dispaly, data_list, base_curd_admin_obj)
    table_head_list = table_head(list_dispaly, data_list, base_curd_admin_obj)
    return {'result': table_body_list, 'table_head_list': table_head_list}


def action_list():
    pass
