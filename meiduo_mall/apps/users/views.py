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
        