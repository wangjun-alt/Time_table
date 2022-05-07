import uuid

from django.contrib.sites import requests
import json, requests, hashlib
from django.http import JsonResponse
from subjectapp import models
import datetime
from subjectapp import getCourseInfo
import time


# Create your views here.

def examineSession(func):
    """
    装饰器：验证Session
    """

    def wrapper(request, *args, **kwargs):
        sessionOpenId = request.session.get("SessionOpenId", None)
        response = {"status": "fail", "errMsg": "", "data": ""}
        if not sessionOpenId:
            response["errMsg"] = "用户未登录或登录已过期"
            # SessionId过期或未登录
            return JsonResponse(data=response, safe=False)
        else:
            return func(request, sessionOpenId, *args, **kwargs)

    return wrapper


def login(request):
    """
    创建用户openid 更新Session
    :return: response [fail or succees]
    response = {"status": "fail", "errMsg": "", "data": ""}
    """
    response = {"status": "fail", "errMsg": "", "data": ""}
    if request.method == "POST":
        body = json.loads(request.body)
        code = body.get("code")
        response = {"status": "fail", "errMsg": "", "data": ""}
        reqUrl = "https://api.weixin.qq.com/sns/jscode2session?appid=wxffa946aa7b91fe34&secret=a861fe13bcef4bc5cc26d87b94f91cd0&js_code=" + code + "&grant_type=authorization_code"
        identityInfo = requests.get(reqUrl).json()  # 向微信接口申请openId
        print(identityInfo)
        if not ("errcode" in identityInfo.keys()):
            openIdMd5 = md5(identityInfo.get("openid"))
            # 如果用户不存在,使用openid创建
            oldUser = models.BasicUser.objects.filter(open_id=openIdMd5)
            if not oldUser:
                newUser = models.BasicUser.objects.create(open_id=openIdMd5)
            else:
                pass
            # SessionId失效了,重新登录更新下,SessionId在header中
            request.session["SessionOpenId"] = openIdMd5
            response["status"] = "succeed"
            response["data"] = "1"
            return JsonResponse(data=response, safe=False)
        # 获取失败,存在errmsg
        response["status"] = "fail"
        response["errMsg"] = identityInfo["errmsg"]
        return JsonResponse(data=response, safe=False)
    # get方法,默认成功 可有可无
    response["status"] = "succeed"
    return JsonResponse(data=response, safe=False)


def md5(str):
    """
    对字符串进行md5加密封装
    :param str: 原始字符串
    :return: md5字符串
    """
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    return m.hexdigest()


@examineSession
def getInformation(request, sessionOpenId):
    """
    获取用户信息
    :param sessionOpenId:
    :param request:
    :return: status:[succeed,fail]
    """
    response = {"status": "fail", "errMsg": "", "data": ""}
    body = json.loads(request.body)
    user_name = body.get("user_name")
    avatarUrl = body.get("avatarUrl")
    user_city = body.get("user_city")
    user_province = body.get("user_province")
    user_country = body.get("user_country")
    user = models.BasicUser.objects.filter(open_id=sessionOpenId)[0]
    user.user_nick_name = user_name
    user.user_head_img = avatarUrl
    user.user_city = user_city
    user.user_province = user_province
    user.user_country = user_country
    user.save()
    response["status"] = "succeed"
    return JsonResponse(data=response, safe=False)


@examineSession
def getSecretCode(request, sessionOpenId):
    img_src = getCourseInfo.getCodeimg()
    response = {"status": "fail", "errMsg": "", "data": ""}
    response["status"] = "succeed"
    response["data"] = img_src
    return JsonResponse(data=response, safe=False)


@examineSession
def changeSecretCode(request, sessionOpenId):
    img_src = getCourseInfo.getCodeimg()
    response = {"status": "fail", "errMsg": "", "data": ""}
    response["status"] = "succeed"
    response["data"] = img_src
    return JsonResponse(data=response, safe=False)


#
# @examineSession
# def certificate(request,sessionOpenId):
#     """
#     学生信息认证
#     :param request:请求对象
#     :param sessionOpenId:身份验证
#     :return:成功状态、学生信息
#     """
#     response = {"status": "fail", "errMsg": "", "data": ""}
#     body = json.loads(request.body)
#     student_id = body.get("student_id")
#     password = body.get("password")
#     code = body.get("code")
#     responses = getCourseInfo.certificate(code=code, student_id=student_id, pw=password)
#     if not responses :
#         response["errMsg"] = "账号密码或验证码错误"
#         return  JsonResponse(data=response,safe=False)
#     student_info =models.StudentInfo()
#     student_info.student_id = student_id
#     student_info.open_id = sessionOpenId
#     student_info.student_major = responses[5].text
#     student_info.student_grade = responses[2].text
#     student_info.student_school = "西安工程大学"
#     student_info.student_college = responses[3].text
#     student_info.student_name =responses[6].split("同学")[0]
#     student_info.student_status = 1
#     student_info.save()
#     models.BasicUser.objects.filter(open_id=sessionOpenId).update(authentication=1)
#     response["status"] = "succeed"
#     response["data"] = {
#         "student_name":responses[6].split("同学")[0],
#         "student_id":student_id,
#         "student_major":responses[5].text,
#         "student_grade":responses[2].text,
#         "student_school":student_info.student_school,
#         "student_college":student_info.student_college
#     }
#     return JsonResponse(data=response,safe=False)


@examineSession
def autoIntoTimetable(request, sessionOpenId):
    response = {"status": "fail", "errMsg": "", "data": ""}
    body = json.loads(request.body)
    student_id = body.get("student_id")
    password = body.get("password")
    code = body.get("code")
    school_year = body.get("school_year")
    term = body.get("term")
    # student_id = 41709060208
    # password = "wnwf990216"
    # code = request.GET['code']
    # school_year = "2019-2020"
    # term = '2'
    info = getCourseInfo.getCourseInfo(code=code, student_id=student_id, password=password, school_year=school_year, term=term)
    if not info:
        response["errMsg"] = "账号密码或验证码错误"
        return JsonResponse(data=response, safe=False)
    else:
        school_courses = []
        info_student = info[-1]
        info.pop()
        for course in info:
            course_info = models.CourseInfo()
            course_info.course_name = course["course_name"]
            course_info.course_weeks = str(course['course_weeks'][0]) + '-' + str(course['course_weeks'][-1])
            course_info.course_teacher = course['course_teacher']
            course_info.cours_room = course['course_room']
            times = course['course_times']
            split = times.split("-")
            course_info.time = split[0]
            course_info.len = int(split[1]) - int(split[0]) + 1
            course_info.course_days = course['course_days']
            course_info.school_year = school_year
            course_info.term = term
            course_info.student_school = "西安工程大学"
            course_info.course_major = info_student[5].text
            objects_filter = models.CourseInfo.objects.filter(time=split[0], len=int(split[1]) - int(split[0]) + 1,
                                                              course_days=course['course_days'],
                                                              school_year=school_year, term=term,
                                                              student_school="西安工程大学",
                                                              course_major=info_student[5].text)
            if not objects_filter:
                course_info.save()
            infos = {"course_name": course["course_name"],
                     "course_teacher": course['course_teacher'], "cours_room": course['course_room'],
                     "course_days": course['course_days'], "course_time": split[0],
                     "course_len": int(split[1]) - int(split[0]) + 1,
                     "course_weeks": str(course['course_weeks'][0]) + '-' + str(course['course_weeks'][-1]),
                     "school_year": school_year, "term": term
                     }
            school_courses.append(infos)
        student_info = models.StudentInfo()
        student_info.student_id = student_id
        student_info.open_id = sessionOpenId
        student_info.student_major = info_student[5].text
        student_info.student_grade = info_student[2].text
        student_info.student_school = "西安工程大学"
        student_info.student_college = info_student[3].text
        student_info.student_name = info_student[6].split("同学")[0]
        student_info.student_status = 1
        student_info.save()
        models.BasicUser.objects.filter(open_id=sessionOpenId).update(authentication=1)
        student_info = {
            "student_name": info_student[6].split("同学")[0],
            "student_id": student_id,
            "student_major": info_student[5].text,
            "student_grade": info_student[2].text,
            "student_school": "西安工程大学",
            "student_college": info_student[3].text
        }
        response["status"] = "succeed"
        response["data"] = {
            "courses": school_courses,
            "student_info": student_info

        }
        return JsonResponse(data=response, safe=False)


@examineSession
def manualInfoTimetable(request, sessionOpenId):
    """
    手动添加课程,若存在完全相同信息的课程拒绝添加，否则添加
    :param request:
    :param sessionOpenId:cookie中的openid用户标识符
    :return: status[succeed,fail] errormsg["","已存在该课程"]
    """
    response = {"status": "fail", "errMsg": "", "data": ""}
    body = json.loads(request.body)
    course_name = body.get("course_name")
    course_teacher = body.get("course_teacher")
    course_room = body.get("course_room")
    course_time = body.get("course_times")
    course_len = body.get("course_len", "45")
    course_weeks = body.get("course_weeks")
    course_days = body.get("course_days")
    # 若已经存在完全相同信息的课程,拒绝添加
    if models.PersonalCourse.objects.filter(
            pcourse_name=course_name,
            pcourse_teacher=course_teacher,
            pcours_room=course_room,
            pcourse_days=course_days,
            pcourse_time=course_time,
            pcourse_len=course_len,
            pcourse_weeks=course_weeks,
            open_id=sessionOpenId
    ):
        response["errMsg"] = "已存在该课程"
        return JsonResponse(data=response, safe=False)
    # 若不存在,则添加
    else:
        personl_course = models.PersonalCourse()
        personl_course.open_id = sessionOpenId
        personl_course.pcours_room = course_room
        personl_course.pcourse_days = course_days
        personl_course.pcourse_name = course_name
        personl_course.pcourse_teacher = course_teacher
        personl_course.pcourse_time = course_time
        personl_course.pcourse_len = course_len
        personl_course.pcourse_weeks = course_weeks
        personl_course.save()
        response["status"] = "succeed"
        response["data"] = {
            "personl_course_id": personl_course.pcourse_id
        }
        return JsonResponse(data=response, safe=False)


@examineSession
def deleteCourse(request, sessionOpenId):
    """
    删除指定的手动添加课程
    :param request: pcourse_id
    :param sessionOpenId:  用户标识符
    :return:statuc[fail,succeed]
    """
    response = {"status": "fail", "errMsg": "", "data": ""}
    body = request.GET
    pcourse_id = body.get("pcourse_id")
    if not models.PersonalCourse.objects.filter(pcourse_id=pcourse_id, open_id=sessionOpenId, effect=1):
        response["errMsg"] = "查无此课程"
        return JsonResponse(data=response, safe=False)
    else:
        pcourse = models.PersonalCourse.objects.filter(pcourse_id=pcourse_id, open_id=sessionOpenId)[0]
        pcourse.effect = 0
        pcourse.save()
        response["status"] = "succeed"
        return JsonResponse(data=response, safe=False)


@examineSession
def infoSchedule(request, sessionOpenId):
    """
    添加日程
    :param request: pcourse_id
    :param sessionOpenId:  用户标识符
    :return:statuc[fail,succeed]  data[sche_id]
    """
    response = {"status": "fail", "errMsg": "", "data": ""}
    body = json.loads(request.body)
    # 获得名称、地点、时间参数
    sche_name = body.get("sche_name")
    sche_datetime = body.get("sche_datetime")
    sche_address = body.get("sche_address")
    # 新建日程对象，添加信息
    sche = models.Schedule()
    sche.open_id = sessionOpenId
    sche.sche_address = sche_address
    sche.sche_datetime = sche_datetime
    sche.sche_name = sche_name
    # 解析日程时间，计算周数
    user_fir = str(models.BasicUser.objects.filter(open_id=sessionOpenId)[0].firstdays)
    user_firsp = user_fir.split("-")
    user_firtday_week = datetime.datetime(int(user_firsp[0]), int(user_firsp[1]), int(user_firsp[2])).isocalendar()[1]
    sche_datesp = str(sche_datetime).split(" ")[0].split("-")
    sche_date_week = datetime.datetime(int(sche_datesp[0]), int(sche_datesp[1]), int(sche_datesp[2])).isocalendar()[1]
    sche.sche_week_num = datetime.datetime(int(sche_datesp[0]), int(sche_datesp[1]), int(sche_datesp[2])).isocalendar()[
        2]
    sche.sche_week = sche_date_week - user_firtday_week + 1
    sche.save()
    response["status"] = "succeed"
    return JsonResponse(data=response, safe=False)


@examineSession
def deleteSchedule(request, sessionOpenId):
    """
    删除指定的日程
    :param request:
    :param sessionOpenId:
    :return: statuc[succeed,fail]
    """
    response = {"status": "fail", "errMsg": "", "data": ""}
    body = request.GET
    sche_id = body.get("sche_id")
    if not models.Schedule.objects.filter(sche_id=sche_id, open_id=sessionOpenId, effect=1):
        response["errMsg"] = "查无此日程"
        return JsonResponse(data=response, safe=False)
    else:
        schedule = models.Schedule.objects.filter(sche_id=sche_id, open_id=sessionOpenId)[0]
        schedule.effect = 0
        schedule.save()
        response["status"] = "succeed"
        return JsonResponse(data=response, safe=False)


@examineSession
def chooseWeekSchedule(request, sessionOpenId):
    """
    查看某个周的日程
    :param request:
    :param sessionOpenId:
    :return:
    """
    response = {"status": "fail", "errMsg": "", "data": ""}
    body = request.GET
    week_num = body.get("week_num")
    if not models.Schedule.objects.filter(sche_week=week_num, effect=1, open_id=sessionOpenId):
        response["errMsg"] = "查无日程"
        return JsonResponse(data=response, safe=False)
    else:
        Schedules = []
        sches = models.Schedule.objects.filter(sche_week=week_num, effect=1, open_id=sessionOpenId)

        for sche in sches:
            time = str(sche.sche_datetime).split("+")[0]
            DD = time.split(" ")[0]
            HH = time.split(" ")[1].split(":")[0]
            MM = time.split(" ")[1].split(":")[1]
            week_dict = {
                "1": "周一",
                "2": "周二",
                "3": "周三",
                "4": "周四",
                "5": "周五",
                "6": "周六",
                "7": "周日"
            }
            scheInfo = {
                "sche_week": sche.sche_week,
                "sche_id": sche.sche_id, "sche_name": sche.sche_name,
                "sche_address": sche.sche_address, "sche_day_num": DD.split("-")[2], "sche_detail_time": HH + ":" + MM
                , "week_num": week_dict[sche.sche_week_num]
            }
            Schedules.append(scheInfo)
        response["status"] = "succeed"
        response["data"] = Schedules
        return JsonResponse(data=response, safe=False)


@examineSession
def clearSchedule(request, sessionOpenId):
    """
    清空日程
    :param request:
    :param sessionOpenId:
    :return:
    """
    response = {"status": "fail", "errMsg": "", "data": ""}
    if not models.Schedule.objects.filter(open_id=sessionOpenId, effect=1):
        response["errMsg"] = "日程为空"
        return JsonResponse(data=response, safe=False)
    else:
        sches = models.Schedule.objects.filter(open_id=sessionOpenId, effect=1)
        for sche in sches:
            sche.effect = 0
            sche.save()
        response["status"] = "succeed"
        return JsonResponse(data=response, safe=False)


@examineSession
def chooseWeekCourse(request, sessionOpenId):
    """
    查看某个周的课程
    :param request:
    :param sessionOpenId:
    :return:
    """
    response = {"status": "fail", "errMsg": "", "data": ""}
    body = request.GET
    week_num = body.get("week_num")
    term = body.get("term")
    year = body.get("year")
    first_day = str(models.BasicUser.objects.filter(open_id=sessionOpenId)[0].firstdays)
    day_split = first_day.split("-")
    datetime_datetime = datetime.datetime(int(day_split[0]), int(day_split[1]), int(day_split[2]))
    now_day = datetime_datetime + datetime.timedelta(days=(int(week_num) - 1) * 7)

    # 检索专业课表
    school = models.StudentInfo.objects.filter(open_id=sessionOpenId)[0].student_school
    major = models.StudentInfo.objects.filter(open_id=sessionOpenId)[0].student_major
    courses = models.CourseInfo.objects.filter(term=term, student_school=school, course_major=major, school_year=year)
    pcourses = models.PersonalCourse.objects.filter(open_id=sessionOpenId, effect=1)
    # allCourse = {
    #     "星期一":[],
    #     "星期二":[],
    #     "星期三":[],
    #     "星期四":[],
    #     "星期五":[],
    #     "星期六":[],
    #     "星期日":[]
    # }
    allCourse = []
    for course in courses:
        split = str(course.course_weeks).split("-")
        start = int(split[0])
        end = int(split[1])
        if int(week_num) >= start and int(week_num) <= end:
            allCourse.append({
                "course_id": course.course_id, "course_name": course.course_name,
                "course_teacher": course.course_teacher, "cours_room": course.cours_room,
                "course_days": course.course_days, "course_time": course.time, "course_len": course.len,
                "course_weeks": course.course_weeks, "course_major": course.course_major,
                "school_year": course.school_year, "term": course.term
            })
    for course in pcourses:
        split = str(course.pcourse_weeks).split("-")
        start = int(split[0])
        end = int(split[1])
        if int(week_num) >= start and int(week_num) <= end:
            allCourse[course.pcourse_days].append({
                "course_id": course.pcourse_id, "course_name": course.pcourse_name,
                "course_teacher": course.pcourse_teacher, "cours_room": course.pcours_room,
                "course_days": course.pcourse_days, "course_time": course.pcourse_time,
                "course_len": course.pcourse_len,
                "course_weeks": course.pcourse_weeks
            })
    alldata = {
        "course_data": allCourse,
        "Monday_data": str(now_day).split(" ")[0],
        "month": str(now_day).split(" ")[0].split("-")[1]
    }
    response["data"] = alldata
    response["status"] = "succeed"
    return JsonResponse(data=response, safe=False)


@examineSession
def changeImg(request, sessionOpenId):
    """
    更换背景图片
    :param request:
    :param sessionOpenId:
    :return:
    """
    response = {"status": "fail", "errMsg": "", "data": ""}
    body = json.loads(request.body)
    user_background = body.get("user_background")
    user = models.BasicUser.objects.filter(open_id=sessionOpenId)[0]
    user.user_background = user_background
    user.save()
    response["status"] = "succeed"
    return JsonResponse(data=response, safe=False)


@examineSession
def allCourseOneDay(request, sessionOpenId):
    """
    查看某一天的全部课程
    :param request:
    :param sessionOpenId:
    :return:
    """
    response = {"status": "fail", "errMsg": "", "data": ""}
    body = json.loads(request.body)
    school_year = body.get("school_year")
    term = body.get("school_term")
    course_day = body.get("course_days")
    allCourse = []
    Pcourses = models.PersonalCourse.objects.filter(open_id=sessionOpenId, pcourse_days=course_day, effect=1)
    student = models.StudentInfo.objects.filter(open_id=sessionOpenId)[0]
    courses = models.CourseInfo.objects.filter(student_school=student.student_school,
                                               course_major=student.student_major,
                                               term=term, school_year=school_year, course_days=course_day)

    for pcourse in Pcourses:
        course_info = {
            "course_id": pcourse.pcourse_id, "course_name": pcourse.pcourse_name,
            "course_teacher": pcourse.pcourse_teacher, "cours_room": pcourse.pcours_room,
            "course_days": pcourse.pcourse_days, "course_time": pcourse.pcourse_time, "course_len": pcourse.pcourse_len,
            "course_weeks": pcourse.pcourse_weeksp
        }
        allCourse.append(course_info)
    for course in courses:
        course_info = {
            "course_id": course.course_id, "course_name": course.course_name,
            "course_teacher": course.course_teacher, "cours_room": course.cours_room,
            "course_days": course.course_days, "course_time": course.time, "course_len": course.len,
            "course_weeks": course.course_weeks, "course_major": course.course_major,
            "school_year": course.school_year, "term": course.term
        }
        allCourse.append(course_info)
    response["status"] = "succeed"
    response["data"] = allCourse
    return JsonResponse(data=response, safe=False)


@examineSession
def setNowWeek(request, sessionOpenId):
    response = {"status": "fail", "errMsg": "", "data": ""}
    body = json.loads(request.body)
    cur_week = body.get("cur_week")
    cureent_date = datetime.date.today()
    cur_week_num = datetime.datetime.weekday(datetime.datetime.now())
    firstday = cureent_date - datetime.timedelta(days=cur_week_num + (int(cur_week) - 1) * 7)
    user = models.BasicUser.objects.filter(open_id=sessionOpenId)
    if not user:
        response["errMsg"] = "查无此用户，清重新登录"
    else:
        user[0].firstdays = firstday
        user[0].save()
    response["status"] = "succeed"
    return JsonResponse(data=response, safe=False)


@examineSession
def upload(request):
    if request.method == 'POST':
        image_ = request.FILES['image']
        uid = str(uuid.uuid1())
        with open("media/" + uid + ".jpg", 'wb') as fp:
            fp.write(image_.read())
            fp.close()
        data = "http://118.190.215.157:8000/media/" + uid + ".jpg"
        return JsonResponse(data=data, safe=False)

