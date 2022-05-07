from django.db import models
from datetime import datetime
import django
# Create your models here.
class BasicUser(models.Model):
    open_id = models.CharField(verbose_name="用户标识符",max_length=64,primary_key=True,unique=True)
    user_nick_name = models.CharField(verbose_name="用户昵称",max_length=32,null=True,unique=False)
    user_country = models.CharField(verbose_name="所在国家或地区",max_length=32,null=False,unique=False,default="中国")
    user_city = models.CharField(verbose_name="所在城市",max_length=32,null=False,unique=False,default="西安")
    user_province = models.CharField(verbose_name="所在省份",max_length=32,null=False,unique=False,default="陕西")
    user_phone = models.CharField(verbose_name="手机号",max_length=15,null=True,unique=False)
    user_head_img = models.CharField(verbose_name="头像",max_length=150,null=True,unique=False)
    user_sex = models.CharField(verbose_name="性别(0男1女)",max_length=1,null=False,unique=False,default="0")
    user_subscribe = models.CharField(verbose_name="用户是否订阅公众号",max_length=1,null=False,unique=False,default="1")
    user_subscribe_way = models.CharField(verbose_name="用户订阅公众号来源",max_length=10,null=False,unique=False,default="1")
    user_qrcode = models.CharField(verbose_name="二维码名片存储地址",max_length=64,null=True,unique=False)
    user_background = models.CharField(verbose_name="背景图片url",max_length=64,null=True,unique=False)
    authentication = models.CharField(verbose_name="认证字段", max_length=1, null=False, unique=False, default=0)
    firstdays = models.DateField(verbose_name="开学第一天",null=False,unique=False,default=datetime.now().date())

    class Meta:
        db_table ="BasicUser"

class StudentInfo(models.Model):
    open_id = models.CharField(verbose_name="用户标识符", max_length=64, primary_key=True, unique=True)
    student_id = models.CharField(verbose_name="学生学号",max_length=16,null=True,unique=True)
    student_name = models.CharField(verbose_name="学生姓名",max_length=32,null=True,unique=False)
    student_status = models.CharField(verbose_name="学生基础信息状态",max_length=1,null=False,unique=False,default="0")
    student_school = models.CharField(verbose_name="学生学校",max_length=32,null=True,unique=False)
    student_college = models.CharField(verbose_name="学生学院",max_length=32,null=True,unique=False)
    student_major = models.CharField(verbose_name="学生专业班级",max_length=32,null=True,unique=False)
    student_credent = models.CharField(verbose_name="学生证件URL",max_length=128,null=True,unique=False)
    student_grade = models.CharField(verbose_name="学生年级",max_length=8,null=True,unique=False)

    class Meta:
        db_table ="StudentInfo"

class CourseInfo(models.Model):
    student_school = models.CharField(verbose_name="学生学校", max_length=32, null=True, unique=False)
    course_id = models.AutoField(verbose_name="主键自增",primary_key=True, null=False, unique=True)
    course_name = models.CharField(verbose_name="课程名称",max_length=32,null=False,unique=False)
    course_teacher = models.CharField(verbose_name="授课老师",max_length=16,null=False,unique=False)
    cours_room = models.CharField(verbose_name="授课地点",max_length=16,null=False,unique=False)
    course_days = models.CharField(verbose_name="星期一～星期五",max_length=16,null=False,unique=False)
    course_weeks = models.CharField(verbose_name="上课的周[1,2,3,4,5]",max_length=32,null=False,unique=False)
    course_major = models.CharField(verbose_name="专业班级",max_length=32,null=False,unique=False)
    school_year = models.CharField(verbose_name="学年",max_length=16,null=False,unique=False,default=datetime.now().year)
    term = models.CharField(verbose_name="学期",max_length=1,null=False,unique=False,default=1)
    time = models.CharField(verbose_name="第几节",max_length=4,null=False,unique=False)
    len = models.CharField(verbose_name="长度",max_length=4,null=False,unique=False)

    class Meta:
        db_table ="CourseInfo"

class PersonalCourse(models.Model):
    pcourse_id = models.AutoField(verbose_name="主键自增",primary_key=True, null=False, unique=True)
    pcourse_name = models.CharField(verbose_name="课程名称",max_length=32,null=False,unique=False)
    pcourse_teacher = models.CharField(verbose_name="授课老师",max_length=16,null=False,unique=False)
    pcours_room = models.CharField(verbose_name="授课地点",max_length=16,null=False,unique=False)
    pcourse_days = models.CharField(verbose_name="星期一～星期五",max_length=16,null=False,unique=False)
    pcourse_time = models.CharField(verbose_name="课程是第几节",max_length=16,null=False,unique=False)
    pcourse_len = models.CharField(verbose_name="一节课的长度",max_length=4,null=False,unique=False)
    pcourse_weeks = models.CharField(verbose_name="上课的周[1,2,3,4,5]",max_length=32,null=False,unique=False)
    open_id = models.CharField(verbose_name="用户标识符",max_length=64,null=False,unique=False)
    effect = models.CharField(verbose_name="该课程是否有效,1有效,0无效",max_length=1,null=False,unique=False,default="1")

    class Meta:
        db_table ="PersonalCourse"

class Schedule(models.Model):
    sche_week_num = models.CharField(verbose_name="周几",max_length=6,null=False,unique=False)
    sche_week = models.CharField(verbose_name="日期所属周",max_length=4,null=False,unique=False)
    sche_id = models.AutoField(verbose_name="主键自增",primary_key=True, null=False, unique=True)
    sche_name = models.CharField(verbose_name="日程名称",max_length=32,null=False,unique=False)
    sche_address = models.CharField(verbose_name="日程地点",max_length=32,null=True,unique=False)
    sche_datetime = models.DateTimeField(verbose_name="日程日期",null=False,unique=False,default=datetime.now())
    open_id = models.CharField(verbose_name="用户标识符",max_length=64,null=False,unique=False)
    effect = models.CharField(verbose_name="该课程是否有效,1有效,0无效",max_length=1,null=False,unique=False,default="1")

    class Meta:
        db_table ="Schedule"


class User(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=50, null=False,unique=False)
    password = models.CharField(verbose_name="密码", max_length=50, null=False, unique=False)

    class Meta:
        db_table ="User"