"""Subject_table URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from subjectapp import views, test2
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
                  path('admin/', admin.site.urls),
                  # path('login/', views.login),  # 登录
                  path('getInformation/', views.getInformation),  # 完善个人信息
                  path('upload/', views.upload),  # 静态图片上传

                  path('autoIntoTimetable/', views.autoIntoTimetable),  # 教务处导入课表

                  path('manualInfoTimetable/', views.manualInfoTimetable),  # 手动添加课程
                  path('deleteCourse/', views.deleteCourse),  # 删除添加课程
                  path('infoSchedule/', views.infoSchedule),  # 手动添加日程
                  path('deleteSchedule/', views.deleteSchedule),  # 删除日程
                  path('clearSchedule/', views.clearSchedule),  # 清空日程

                  path('chooseWeekSchedule/', views.chooseWeekSchedule),  # 查看某个周的日程

                  path('chooseWeekCourse/', views.chooseWeekCourse),  # 查看某个周的课程
                  path('changeImg/', views.changeImg),  # 更换背景图片
                  path('allCourseOneDay/', views.allCourseOneDay),  # 查看某一学期某一天的课程
                  path('setNowWeek/', views.setNowWeek),  # 设置当前周数
                  path('getSecretCode/', views.getSecretCode),  # 获取验证码
                  path('changeSecretCode/', views.changeSecretCode),  # 点击更换验证码
                  path('userLogin/', test2.user_login),
                  path('getInfo/', test2.get_info),
                  path('login/', test2.post)

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
