import json
import requests
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views import View
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings

from Subject_table import settings
from subjectapp import models


def user_login(request):
    obj = request.GET
    username = obj.get('username')
    password = obj.get('password')
    print(username)
    print(password)
    if username is None or password is None:
        return JsonResponse({'code': 500, 'message': '请求参数错误'})

    is_login = authenticate(request, username=username, password=password)


    if is_login is None:
        return JsonResponse({'code': 500, 'message': '账号或密码错误'})

    login(request, is_login)

    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(is_login)
    token = jwt_encode_handler(payload)

    return JsonResponse(
        {
            'code': 200,
            'message': '登录成功',
            'data': {'token': token}
        }
    )


# 下面的3个装饰器全部来自from引用，相当与给接口增加了用户权限校验和token校验
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JSONWebTokenAuthentication,))
def get_info(request):
    data = 'some info'

    return JsonResponse(
        {
            'code': 200,
            'message': '请求成功',
            'data': data
        }
    )

def post(request):
    # 前端发送code到后端,后端发送网络请求到微信服务器换取openid
    code = request.data.get('code')
    print(code)
    if not code:
        return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

    url = "https://api.weixin.qq.com/sns/jscode2session?appid=wxffa946aa7b91fe34&secret=a861fe13bcef4bc5cc26d87b94f91cd0&js_code=" + code + "&grant_type=authorization_code"
    r = requests.get(url)
    res = json.loads(r.text)
    openid = res['openid'] if 'openid' in res else None
    # session_key = res['session_key'] if 'session_key' in res else None
    if not openid:
        return Response({'message': '微信调用失败'})

        # 判断用户是否第一次登录
    try:
        user = models.BasicUser.objects.get(openid=openid)
    except Exception:
            # 微信用户第一次登陆,新建用户
        user_nick_name = request.data.get('nickname')
        user_sex = request.data.get('sex')
        user_head_img = request.data.get('avatar')
        user = models.BasicUser.objects.create(username=user_nick_name, sex=user_sex, avatar=user_head_img)
        user.set_password(openid)

        # 手动签发jwt
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)

    resp_data = {
        "username": user.username,
        "token": token,
    }

    return Response(resp_data)

