import requests
from lxml import etree
import datetime
import re
import uuid
# 西安工程大学教务处IP
school_base_url = "http://202.200.206.54/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

# 拿Location字段，如果后期加入Cookie可避免Expection
session = requests.Session()
login_page = session.get(url=school_base_url, headers=headers, allow_redirects=False)
location_url = login_page.headers.get("Location")
have_location_url = "http://202.200.206.54" + location_url

def getCodeimg():
    # 拿验证码图片
    new_page_text = session.get(url=have_location_url, headers=headers).text
    tree = etree.HTML(new_page_text)
    # 随机字符
    location_word = location_url.split('/')[1]
    code_img_src = 'http://202.200.206.54/' + location_word + '/' + tree.xpath('//*[@id="icode"]/@src')[0]
    img_data = requests.get(url=code_img_src, headers=headers).content
    # 将验证码存入static下 命名:时间戳+用户id
    md = str(uuid.uuid1())
    with open("media/code.jpg", 'wb') as fp:
        fp.write(img_data)
    return "http://127.0.0.1:8000/media/code.jpg"



def certificate(code,student_id,pw):
    code_text = code
    data = {
        '__VIEWSTATE': 'dDwtNDIxNzMzOTAwOzs+g0BQaxHSfmI9ahFvm/8gQAFC1cY=',  # 固定
        'txtUserName': student_id,  # 学号
        'Textbox1': '',
        'TextBox2':pw,  # 密码
        'txtSecretCode': code_text,  # 验证码
        'RadioButtonList1': '(unable to decode value)',  # 固定
        'Button1': '',
        'lbLanguage': '',
        'hidPdrs': '',
        'hidsc': '',
    }
    # 登录必须带的头
    new_headers = {
        'Referer': 'http:/' + location_url,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    }
    # 必须请求登录一下，才能记录状体
    response = session.post(url=have_location_url, headers=new_headers, data=data)

    if len(response.history) ==0:
        return False
    html = etree.HTML(response.text)
    name = html.xpath('.//span[(@id="xhxm")]')[0].text
    location_word = location_url.split('/')[1]
    # 学号
    id = int(student_id)
    # 请求课程表地址(固定)
    kb_url = 'http://202.200.206.54/' + location_word + '/tjkbcx.aspx?xh=' + str(id) + '&xm=%CE%E2%E9%AA&gnmkdm=N121601'
    # 请求课程表必须带的头
    headers = {
        'Referer': 'http://202.200.206.54/' + location_word + '/tjkbcx.aspx?xh=' + str(id) + '&xm=%CE%E2%E9%AA&gnmkdm=N121601',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    }
    # 去隐藏验证值
    before_courese_content = session.get(headers=headers, url=kb_url).text
    tree = etree.HTML(before_courese_content)
    md5 = tree.xpath('.//input[@name="__VIEWSTATE"]/@value')[0]
    data = {
        '__EVENTTARGET': 'kb',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': md5,
        'xn': str(datetime.datetime.now().year-1)+"-"+str(datetime.datetime.now().year) ,  # 学年 41809050201
        'xq': '1',  # 学期
        'nj': '20'+student_id[1:3],  # 年级
        'xy': student_id[3:5],  # 学院
        'zy': student_id[3:7],  # 专业
        'kb': str(datetime.datetime.now().year-1)+student_id[3:7]+str(datetime.datetime.now().year-1)+'-'+str(datetime.datetime.now().year)+'1'+student_id[3:7]+student_id[1:3]+student_id[7:9],  # 专业班级(xn(2017)+学号部分+xn(2017) - xn(2018)+学号部分+学号解析) 找下规律
    }
    courese_content = requests.post(url=kb_url, headers=headers, data=data).text
    tree = etree.HTML(courese_content)
    info = tree.xpath('.//option[(@selected="selected")]')
    info.append(name)
    return info


def getCourseInfo(code, student_id, password, school_year, term):
    school_year = str(school_year)
    location_word = location_url.split('/')[1]
    data = {
        '__VIEWSTATE': 'dDwtNDIxNzMzOTAwOzs+g0BQaxHSfmI9ahFvm/8gQAFC1cY=',  # 固定
        'txtUserName': student_id,  # 学号
        'Textbox1': '',
        'TextBox2': password,  # 密码
        'txtSecretCode': code,  # 验证码
        'RadioButtonList1': '(unable to decode value)',  # 固定
        'Button1': '',
        'lbLanguage': '',
        'hidPdrs': '',
        'hidsc': '',
    }
    # data = {
    #     '__VIEWSTATE': 'dDwtNDIxNzMzOTAwOzs+g0BQaxHSfmI9ahFvm/8gQAFC1cY=',  # 固定
    #     'txtUserName': '41709060208',  # 学号
    #     'TextBox2': 'wnwf990216',  # 密码
    #     'txtSecretCode': code,  # 验证码
    #     'RadioButtonList1': '(unable to decode value)',  # 固定
    #     'Button1': '',
    #     'lbLanguage': '',
    #     'hidPdrs': '',
    #     'hidsc': '',
    # }
    # 登录必须带的头
    new_headers = {
        'Referer': 'http:/' + location_url,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    }
    # 必须请求登录一下，才能记录状体
    response = session.post(url=have_location_url, headers=new_headers, data=data)
    print(response.text)
    if len(response.history) == 0:
        return False
    # 学号
    html = etree.HTML(response.text)
    name = html.xpath('.//span[(@id="xhxm")]')[0].text
    id = int(student_id)

    # 请求课程表地址(固定)
    kb_url = 'http://202.200.206.54/' + location_word + '/tjkbcx.aspx?xh=' + str(id) + '&xm=%CE%E2%E9%AA&gnmkdm=N121601'
    # 请求课程表必须带的头
    headers = {
        'Referer': 'http://202.200.206.54/' + location_word + '/tjkbcx.aspx?xh=' + str(id) + '&xm=%CE%E2%E9%AA&gnmkdm=N121601',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    }
    # 去隐藏验证值
    before_courese_content = session.get(headers=headers, url=kb_url).text
    tree = etree.HTML(before_courese_content)
    md5 = tree.xpath('.//input[@name="__VIEWSTATE"]/@value')[0]
    my_class = '0'+str(int(student_id[7:9])+1)
    data = {
        '__EVENTTARGET': 'kb',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': md5,
        'xn': school_year+'-'+str(int(school_year)+1),  # 学年
        'xq': term,  # 学期
        'nj': '20'+student_id[1:3],  # 年级
        'xy': student_id[3:5],  # 学院
        'zy': student_id[3:7],  # 专业
        'kb': '20'+student_id[1:3]+student_id[3:7]+school_year+'-'+str(int(school_year)+1)+term+student_id[3:7]+student_id[1:3]+my_class
    }
    # data = {
    #     '__EVENTTARGET': 'kb',
    #     '__EVENTARGUMENT': '',
    #     '__VIEWSTATE': md5,
    #     'xn': '2019-2020',  # 学年
    #     'xq': '2',  # 学期
    #     'nj': '2017',  # 年级
    #     'xy': '09',  # 学院
    #     'zy': '0906',  # 专业
    #     'kb': '201709062019-2020209061701',  # 专业班级(xn(2017)+学号部分+xn(2017) - xn(2018)+学号部分+学号解析) 找下规律
    # }
    courese_content = requests.post(url=kb_url, headers=headers, data=data).text
    tree = etree.HTML(courese_content)


    #------------------------------------------------------------------------------------------------------------------------------
    infos = tree.xpath('.//option[(@selected="selected")]')
    infos.append(name)
    # noinspection PyBroadException
    table = tree.xpath('//*[@id="Table6"]/tr')
    try:
        week = table[0].xpath('./td[@align="Center"]//text()')
    except Exception as e:
        tree = etree.HTML(response.text)
        error = tree.xpath('//*[@id="form1"]/script/text()')[0]
        # 匹配错误信息返回给前端
        rule = re.compile(r'[(](.*?)[)]', re.S)
        error_msg = re.findall(rule, error)
        return error_msg[0]
    new_table = []
    # 整个课表
    for index, value in enumerate(table):
        if index != 0 and (index % 2 == 0):
            new_table.append(value)
    # 最终课表信息
    course_info = []
    for index, br in enumerate(new_table):
        centers = br.xpath('./td[@align="Center"]')
        for index, center in enumerate(centers):
            try:
               str_list = center.xpath(".//text()")
            except BaseException:
                pass
            try:
                findall = str(re.findall(r"\d+,\d+", str_list[1])[0])
                split = findall.split(",")
                start_num = split[0]
                end_num = split[1]
            except BaseException:
                pass
            try:
                findall2 = str(re.findall(r"\d+,\d+", str_list[5])[0])
                findall__split = findall2.split(",")
                start1_num = findall__split[0]
                end1_num = findall__split[1]
            except BaseException:
                pass
            length = len(str_list)
            try:
                start = re.findall(r"\d+",str_list[1].split("(")[0].split("-")[0])[0]
            except BaseException:
                pass
            try:
                end = re.findall(r"\d+",str_list[1].split("(")[0].split("-")[1])[0]
            except BaseException:
                pass
            # 正常课表类型
            if length == 4 and (str_list[3] != ' '):
                course_weeks = [i for i in range(int(start),
                                                 int(end)+ 1)]
                info = {
                    "course_name": str_list[0],
                    "course_weeks": course_weeks,
                    "course_teacher": str_list[2],
                    "course_room": str_list[3],
                    "course_times": start_num + "-" + end_num,
                    "course_days": week[index],
                }
                course_info.append(info)
            elif length == 8 and (str_list[3] != ' '):
                start = re.findall(r"\d+", str_list[1].split("(")[0].split("-")[0])[0]
                try:
                    end = re.findall(r"\d+", str_list[1].split("(")[0].split("-")[1])[0]
                except Exception:
                    end = start
                start1 = re.findall(r"\d+", str_list[5].split("(")[0].split("-")[0])[0]
                try:
                    end1 = re.findall(r"\d+", str_list[5].split("(")[0].split("-")[1])[0]
                except Exception:
                    end1 = start1
                course_weeks = [i for i in range(int(start),
                                                 int(end)+ 1)]
                info = {
                    "course_name": str_list[0],
                    "course_weeks": course_weeks,
                    "course_teacher": str_list[2],
                    "course_room": str_list[3],
                    "course_times": start_num + "-" + end_num,
                    "course_days": week[index],
                }
                course_info.append(info)
                course_weeks = [i for i in range(int(start1),
                                                 int(end1)+ 1)]
                info = {
                    "course_name": str_list[4],
                    "course_weeks": course_weeks,
                    "course_teacher": str_list[6],
                    "course_room": str_list[7],
                    "course_times": start1_num + "-" + end1_num ,
                    "course_days": week[index],
                }
                course_info.append(info)
            # 没课
            elif length == 1:
                continue
            # 特殊课表类型
            elif length == 4:
                rule = re.compile(r'[(](.*?)[)]', re.S)
                course_weeks = [i for i in range(int(start),
                                                 int(end)+ 1)]
                info = {
                    "course_name": str_list[0],
                    "course_weeks": course_weeks,
                    "course_teacher": str_list[2],
                    "course_room": str_list[3],
                    "course_times": start_num + "-" + end_num,
                    "course_days": week[index],
                }
                course_info.append(info)
            elif length == 8:
                start = re.findall(r"\d+", str_list[1].split("(")[0].split("-")[0])[0]
                end = re.findall(r"\d+", str_list[1].split("(")[0].split("-")[1])[0]
                start1 = re.findall(r"\d+", str_list[5].split("(")[0].split("-")[0])[0]
                try:
                    end1 = re.findall(r"\d+", str_list[5].split("(")[0].split("-")[1])[0]
                except Exception:
                    end1=start1
                course_weeks = [i for i in range(int(start), int(end)+1)]
                info = {
                    "course_name": str_list[0],
                    "course_weeks": course_weeks,
                    "course_teacher": str_list[2],
                    "course_room": str_list[3],
                    "course_times": start_num + "-" + end_num,
                    "course_days": week[index],
                }
                course_info.append(info)
                rule = re.compile(r'[(](.*?)[)]', re.S)
                course_weeks = [i for i in range(int(start1), int(end1)+1)]
                info = {
                    "course_name": str_list[4],
                    "course_weeks": course_weeks,
                    "course_teacher": str_list[6],
                    "course_room": str_list[7],
                    "course_times": start1_num + "-" + end1_num,
                    "course_days": week[index],
                }
                course_info.append(info)
    course_info.append(infos)
    return course_info




