from django.shortcuts import render

# Create your views here.

from django.views import View
from apps.users.models import User
from django.http import JsonResponse
import re
import json
class UsernameCountView(View):
    
    def get(self,request,username):
            
        count=User.objects.filter(username=username).count()
        return JsonResponse({'code':0,'count':count,'errmsg':'ok'})
    
class MobileCountView(View):
    
    def get(self,request,mobile):
            
        count=User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code':0,'count':count,'errmsg':'ok'})
   

#front :user input username,password,mobile    
class RegisterView(View):
    
    def post(self,request):
        #get request:post-----json
        body_bytes = request.body
        body_str = body_bytes.decode()
        body_dict = json.loads(body_str)

        #get datas
        username = body_dict.get('username')
        password = body_dict.get('password')
        passwword2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        allow=body_dict.get('allow')

        #verify data
        if not all([username,password,passwword2,mobile,allow]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})
        
        if not re.match('[a-zA-Z_-]{5,20}',username):
            return JsonResponse({'code':400,'errmsg':'用户名不满足规则'})
        
        # user = User(username = username,password = password,mobile = mobile)
        # user.save()

        #create user and encryption password
        User.objects.create_user(username=username,password=password,mobile=mobile)

        #set session
        from django.contrib.auth import login
        
        login(request.user)
        
        
        return JsonResponse({'code':0,'errmsg':'ok'})
 
class LoginView(View):

    def post(self,request):
        # 1. 接收数据
        data=json.loads(request.body.decode())
        username=data.get('username')
        password=data.get('password')
        remembered=data.get('remembered')
        # 2. 验证数据
        if not all([username,password]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})


        # 确定 我们是根据手机号查询 还是 根据用户名查询

        # USERNAME_FIELD 我们可以根据 修改 User. USERNAME_FIELD 字段
        # 来影响authenticate 的查询
        # authenticate 就是根据 USERNAME_FIELD 来查询
        if re.match('1[3-9]\d{9}',username):
            User.USERNAME_FIELD='mobile'
        else:
            User.USERNAME_FIELD='username'

        # 3. 验证用户名和密码是否正确
        # 我们可以通过模型根据用户名来查询
        # User.objects.get(username=username)


        # 方式2
        from django.contrib.auth import authenticate
        # authenticate 传递用户名和密码
        # 如果用户名和密码正确，则返回 User信息
        # 如果用户名和密码不正确，则返回 None
        user=authenticate(username=username,password=password)

        if user is None:
            return JsonResponse({'code':400,'errmsg':'账号或密码错误'})

        # 4. session
        from django.contrib.auth import login
        login(request,user)

        # 5. 判断是否记住登录
        if remembered:
            # 记住登录 -- 2周 或者 1个月 具体多长时间 产品说了算
            request.session.set_expiry(None)

        else:
            #不记住登录  浏览器关闭 session过期
            request.session.set_expiry(0)

        # 6. 返回响应
        response = JsonResponse({'code':0,'errmsg':'ok'})
        # 为了首页显示用户信息
        response.set_cookie('username',username)

        # 必须是登录后 合并
        # from apps.carts.utils import merge_cookie_to_redis
        # response = merge_cookie_to_redis(request, response)

        return response
