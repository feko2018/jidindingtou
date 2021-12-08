# 导入需要的模块
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import matplotlib
from datetime import datetime

###用处：获取周一到周日


# 处理乱码
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['axes.unicode_minus'] = False


def get_html(code, start_date, end_date, page=1, per=20):
    url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={0}&page={1}&sdate={2}&edate={3}&per={4}'.format(
        code, page, start_date, end_date, per)
    rsp = requests.get(url)
    html = rsp.text
    return html



def get_fund(code, start_date, end_date, page=1, per=20):
    # 获取html
    html = get_html(code, start_date, end_date, page, per)
    soup = BeautifulSoup(html, 'html.parser')
    # 获取总页数
    pattern = re.compile('pages:(.*),')
    result = re.search(pattern, html).group(1)
    total_page = int(result)
    # 获取表头信息
    heads = []
    for head in soup.findAll("th"):
        heads.append(head.contents[0])

    # 数据存取列表
    records = []
    # 获取每一页的数据
    current_page = 1
    while current_page <= total_page:
        html = get_html(code, start_date, end_date, current_page, per)
        soup = BeautifulSoup(html, 'html.parser')
        # 获取数据
        for row in soup.findAll("tbody")[0].findAll("tr"):
            row_records = []
            for record in row.findAll('td'):
                val = record.contents
                # 处理空值
                if val == []:
                    row_records.append(np.nan)
                else:
                    row_records.append(val[0])
            # 记录数据
            records.append(row_records)
        # 下一页
        current_page = current_page + 1

    return  records


if __name__ == '__main__':
    code='012414'    ##基金代号
    start_date='2021-01-01' ##开始日期
    end_date = '2021-12-31' ##接受日期

    fund_df = get_fund(code,start_date,end_date)

    ret_dist={}
    for i in fund_df:
        if "%"  in str(i[3]):
            var=float(i[3].strip('%'))
            ret_dist[i[0]]=var

    week_dist={}
    for i in range(1,7):
        week_dist["星期%s"%(i)]=0
    week_dist["星期日"]=0

    for k,v in ret_dist.items():
        week = datetime.strptime(k,"%Y-%m-%d").weekday()
        if week == 6:
            week='星期日'
        else:
            week='星期%s'%(week+1)
        week_dist[week] +=v

    print(week_dist)
    ##输出
    print("--------定投基金涨幅--------")
    print("基金代号：%s"%(code))
    print("查询时间段：%s 至 %s "%(start_date,end_date))
    print("按周涨幅如下：")
    for k,v in  week_dist.items():
        print("%s：%s"%(k,"%.2f%%" % (v)))
