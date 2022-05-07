from django.contrib import admin
from subjectapp.models import BasicUser,StudentInfo,PersonalCourse,Schedule,CourseInfo
# Register your models here.

admin.site.register(BasicUser)
admin.site.register(StudentInfo)
admin.site.register(PersonalCourse)
admin.site.register(Schedule)
admin.site.register(CourseInfo)
