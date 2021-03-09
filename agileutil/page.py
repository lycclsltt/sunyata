#coding=utf-8

def page_by_result(res_list, pagenum, perpage):
    ret = []
    total_count = len(res_list)
    if total_count == 0:
        return []
    if pagenum == 0:
        pagenum = 1
    if perpage < 0:
        perpage = 30
    begin = (pagenum - 1 ) * perpage
    end = begin + perpage
    if begin > total_count:
        return []
    elif end < total_count:
        return res_list[begin:end]
    elif end >= total_count:
        return res_list[begin:]
    else:
        return []


class PageLimit(object):
    
    def __init__(self, totalCount, perPage, curPage):
        self.totalCount = totalCount
        self.perPage = perPage
        self.curPage = curPage

    def page(self):
        begin = self.curPage * self.perPage - self.perPage
        end = begin + self.perPage
        if begin > self.totalCount:
            begin = 0
            end = self.perPage
        return begin, end