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

        data = json.loads(request.body.decode())
        username=data.get('username')
        password=data.get('password')
        remembered = data.get('remembered')

        if not all([username,password]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})
        
        if re.match('1[3-9]\d{9}',username):
            User.USERNAME_FIELD='mobile'
        else:
            User.USERNAME_FIELD='username'

        from django.contrib.auth import authenticate

        user = authenticate(username = username,password = password)

        if user is None:
            return JsonResponse({'code':400,'errmsg':'账号或者密码错误'})

        from django.contrib.auth import login

        login(request,user)

        if remembered:

            request.session.set_expiry(None)

        else:

            request.session.set_expiry(0)

        response = JsonResponse({'code':0,'errmsg':'ok'})

        response.set_cookie('username',username)

        return response