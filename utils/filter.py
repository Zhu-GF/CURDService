#搜索主键

class FilterList(object):
    '操作FilterOption对象'
    def __init__(self,option,data_list):
        self.option=option
        self.data_list=data_list

    def __iter__(self):
        yield '开始---'
        # for i in self.option.big_filter():
        yield self.option.big_filter()


class FilterOption(object):
    '筛选对象，models字段'
    def __init__(self,name,age):
        self.name=name
        self.age=age
    def big_filter(self):
        if self.age>15:
            return self.name+'大'
        else:
            return self.name+'小'

filter_list_obj1=FilterList(FilterOption('ender',10),[1,2,3,4,5])
filter_list_obj2=FilterList(FilterOption('ender',18),[1,2,3,4,5])
filter_list_obj3=FilterList(FilterOption('ender',18),[1,2,3,4,5])
for filter_list in [filter_list_obj1,filter_list_obj2,filter_list_obj3]:
    print('\t')
    for obj in filter_list:
        print(obj,end=' ')