class MyPagination():
    def __init__(self,current_page,data_sum,base_url,params_dict,per_page=10,per_page_num=11):
        """
        :param current_page:当前页的页码
        :param data_sum:总的数据个数
        :param base_url:要传递到的url
        :param per_page:每页显示的数据数目
        :param per_page_num:每页显示的页码数目
        """
        self.data_sum=data_sum
        self.base_url=base_url
        self.per_page=per_page
        self.per_page_num=per_page_num
        self.params_dict=params_dict    #用于保存GET的参数，使得不修改原来的GET值
        try:
            self.current_page = int(current_page)     #current_page 可能会为None
        except Exception as e:
            self.current_page = 1                     #如果出错，则令current_page=1
        self.total_page_num, b = divmod(data_sum, per_page_num)
        if b:
            self.total_page_num = self.total_page_num + 1  # 计算总共有多少的分页页码（标签）

    def pager(self):
        if self.total_page_num < self.per_page_num:  # 如果当前总的页码数小于每页要显示的页码数，就令起始页码为1，终止页的页码为总页码
            start_page = 1
            stop_page = self.total_page_num
        else:
            part = int(self.per_page_num / 2)       #当前页码往前数一半每页显示的页码，往后数一半
            if self.current_page <= part + 1:       #如果当前页码小于等于页码数的一半+1 则起始页码为1，终止 页码为每页显示的页码数
                start_page = 1
                stop_page = self.per_page_num
            else:
                start_page = self.current_page - part   #否则，起始页码为当前页码减去页码的一半
                stop_page = self.current_page + part     #终止页码为当前页码加上页码的一半

                if stop_page >self.total_page_num:    #如果终止页码超过了总页码，那么终止页码等于总页码
                    stop_page = self.total_page_num
                if start_page>self.total_page_num-self.per_page_num:
                    start_page=self.total_page_num-self.per_page_num
        page_list = []                                  #用于存放页码标签的
        # 上一页
        if self.current_page <= 1:
            prev = "<li><a href='#'>上一页</a></li>"
        else:
            self.params_dict['page']=self.current_page-1
            prev = "<li><a href='%s?%s'>上一页</a></li>" % (self.base_url, self.params_dict.urlencode(),)
        page_list.append(prev)
        # 中间页
        for i in range(start_page, stop_page+1):
            self.params_dict['page'] = i
            if i == self.current_page:
                temp = "<li class='active'><a  href='%s?%s'>%s</a></li>" % (self.base_url, self.params_dict.urlencode(), i,)
            else:
                temp = "<li><a href='%s?%s'>%s</a></li>" % (self.base_url, self.params_dict.urlencode(), i,)
            page_list.append(temp)
        # 下一页
        if self.current_page >=self.total_page_num:
            nex = "<li><a href='#'>下一页</a></li>"
        else:
            self.params_dict['page'] = self.current_page + 1
            nex = "<li><a href='%s?%s'>下一页</a></li>" % (self.base_url,self.params_dict.urlencode(),)
        page_list.append(nex)
        tags = ''.join(page_list)
        return tags

    @property
    def start_data(self):                #要从总数据截取的范围的起始点
        data_start = (self.current_page - 1) * self.per_page
        return data_start

    @property
    def data_end(self):
        data_end = self.current_page * self.per_page             #要从总数据截取的终止点
        return data_end
