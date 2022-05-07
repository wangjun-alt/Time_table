from lxml import etree
import time
import re
import requests


def getCourseInfo():
    # 西安工程大学教务处IP
    school_base_url = "http://202.200.206.54/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    }

    # 拿Location字段，如果后期加入Cookie可避免Expection
    session = requests.Session()
    login_page = session.get(url=school_base_url, headers=headers, allow_redirects=False)
    location_url = login_page.headers.get("Location")

    # 拿验证码图片
    have_location_url = "http://202.200.206.54" + location_url
    new_page_text = session.get(url=have_location_url, headers=headers).text
    tree = etree.HTML(new_page_text)
    # 随机字符
    location_word = location_url.split('/')[1]
    code_img_src = 'http://202.200.206.54/' + location_word + '/' + tree.xpath('//*[@id="icode"]/@src')[0]
    img_data = requests.get(url=code_img_src, headers=headers).content
    # 将验证码存入static下 命名:时间戳+用户id
    with open("code.jpg", 'wb') as fp:
        fp.write(img_data)

    code_text = input("请输入验证码")

    data = {
        '__VIEWSTATE': 'dDwtNDIxNzMzOTAwOzs+g0BQaxHSfmI9ahFvm/8gQAFC1cY=',  # 固定
        'txtUserName': '41709060208',  # 学号
        'TextBox2': 'wnwf990216',  # 密码
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
    response = session.post(url=have_location_url, headers=new_headers, data=data).text
    print(response)

    # 学号
    id = 41909070107
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
        'xn': '2020-2021',  # 学年
        'xq': '2',  # 学期
        'nj': '2019',  # 年级
        'xy': '09',  # 学院
        'zy': '0906',  # 专业
        'kb': '201709062019-2020209061701',  # 专业班级(xn(2017)+学号部分+xn(2017) - xn(2018)+学号部分+学号解析) 找下规律
    }

    courese_content = requests.post(url=kb_url, headers=headers, data=data).text
    tree = etree.HTML(courese_content)
    # noinspection PyBroadException
    table = tree.xpath('//*[@id="Table6"]/tr')
    print(table)
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
            str_list = center.xpath(".//text()")
            length = len(str_list)
            # 正常课表类型
            if length == 4 and (str_list[3] != ' '):
                course_weeks = [i for i in range(int(str_list[1].split("(")[0].split("-")[0]),
                                                 int(str_list[1].split("(")[0].split("-")[1]) + 1)]
                info = {
                    "course_name": str_list[0],
                    "course_weeks": course_weeks,
                    "course_teacher": str_list[2],
                    "course_room": str_list[3],
                    "course_times": str(2 * index + 1) + "-" + str(2 * index + 2),
                    "course_days": week[index],
                }
                course_info.append(info)
            elif length == 8 and (str_list[3] != ' '):
                course_weeks = [i for i in range(int(str_list[1].split("(")[0].split("-")[0]),
                                                 int(str_list[1].split("(")[0].split("-")[1]) + 1)]
                info = {
                    "course_name": str_list[0],
                    "course_weeks": course_weeks,
                    "course_teacher": str_list[2],
                    "course_room": str_list[3],
                    "course_times": str(2 * index + 1) + "-" + str(2 * index + 2),
                    "course_days": week[index],
                }
                course_info.append(info)
                course_weeks = [i for i in range(int(str_list[5].split("(")[0].split("-")[0]),
                                                 int(str_list[5].split("(")[0].split("-")[1]) + 1)]
                info = {
                    "course_name": str_list[4],
                    "course_weeks": course_weeks,
                    "course_teacher": str_list[6],
                    "course_room": str_list[7],
                    "course_times": str(2 * index + 1) + "-" + str(2 * index + 2),
                    "course_days": week[index],
                }
                course_info.append(info)
            # 没课
            elif length == 1:
                continue
            # 特殊课表类型
            elif length == 4:
                rule = re.compile(r'[(](.*?)[)]', re.S)
                course_weeks = re.findall(rule, str_list[1])[0].split('-')
                info = {
                    "course_name": str_list[0],
                    "course_weeks": course_weeks,
                    "course_teacher": str_list[2],
                    "course_room": str_list[3],
                    "course_times": str(2 * index + 1) + "-" + str(2 * index + 2),
                    "course_days": week[index],
                }
                course_info.append(info)
            elif length == 8:
                try:
                    rule = re.compile(r'[(](.*?)[)]', re.S)
                    course_weeks = re.findall(rule, str_list[1])[0].split('-')
                    course_weeks = [i for i in range(int(course_weeks[0]), int(course_weeks[1]))]
                except Exception as e:
                    course_weeks = [i for i in range(int(str_list[5].split("(")[0].split("-")[0]),
                                                     int(str_list[5].split("(")[0].split("-")[1]) + 1)]
                info = {
                    "course_name": str_list[0],
                    "course_weeks": course_weeks,
                    "course_teacher": str_list[2],
                    "course_room": str_list[3],
                    "course_times": str(2 * index + 1) + "-" + str(2 * index + 2),
                    "course_days": week[index],
                }
                course_info.append(info)
                try:
                    rule = re.compile(r'[(](.*?)[)]', re.S)
                    course_weeks = re.findall(rule, str_list[5])[0].split('-')
                    course_weeks = [i for i in range(int(course_weeks[0]), int(course_weeks[1]))]
                except Exception as e:
                    course_weeks = [i for i in range(int(str_list[5].split("(")[0].split("-")[0]),
                                                     int(str_list[5].split("(")[0].split("-")[1]) + 1)]
                info = {
                    "course_name": str_list[4],
                    "course_weeks": course_weeks,
                    "course_teacher": str_list[6],
                    "course_room": str_list[7],
                    "course_times": str(2 * index + 1) + "-" + str(2 * index + 2),
                    "course_days": week[index],

                }
                course_info.append(info)
    return course_info

if __name__ == "__main__":
    print(getCourseInfo())
