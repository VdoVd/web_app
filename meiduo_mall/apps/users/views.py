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

from django.contrib.auth import logout

class LogoutView(View):

    def delete(self,request):

        logout(request)

        response = JsonResponse({"code":0,"errmsg":"ok"})

        response.delete_cookie('username')

        return response

from utils.views import LoginRequiredJSONMixin
class CenterView(LoginRequiredJSONMixin,View):

    def get(self,request):
        # request.user 就是 已经登录的用户信息
        # request.user 是来源于 中间件
        # 系统会进行判断 如果我们确实是登录用户，则可以获取到 登录用户对应的 模型实例数据
        # 如果我们确实不是登录用户，则request.user = AnonymousUser()  匿名用户
        info_data = {
            'username':request.user.username,
            'email':request.user.email,
            'mobile':request.user.mobile,
            'email_active':request.user.email_active,
        }

        return JsonResponse({'code':0,'errmsg':'ok','info_data':info_data})

class EmailView(LoginRequiredJSONMixin,View):

    def put(self,request):
        # 1. 接收请求
        #ｐｕｔ post －－－　ｂｏdy
        data=json.loads(request.body.decode())
        # 2. 获取数据
        email=data.get('email')
        # 验证数据
        # 正则　
        # 3. 保存邮箱地址
        user=request.user
        # user / request.user 就是　登录用户的　实例对象
        # user --> User
        user.email=email
        user.save()
        # 4. 发送一封激活邮件
        # 一会单独讲发送邮件
        from django.core.mail import send_mail
        # subject, message, from_email, recipient_list,
        # subject,      主题
        subject='美多商城激活邮件'
        # message,      邮件内容
        message=""
        # from_email,   发件人
        from_email='美多商城<qi_rui_hua@163.com>'
        # recipient_list, 收件人列表
        recipient_list = ['qi_rui_hua@126.com','qi_rui_hua@163.com']

        # 邮件的内容如果是 html 这个时候使用 html_message
        # 4.1 对a标签的连接数据进行加密处理
        # user_id=1
        from apps.users.utils import generic_email_verify_token
        token=generic_email_verify_token(request.user.id)

        verify_url = "http://www.meiduo.site:8080/success_verify_email.html?token=%s"%token
        # 4.2 组织我们的激活邮件
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)


        # html_message="点击按钮进行激活 <a href='http://www.itcast.cn/?token=%s'>激活</a>"%token

        # send_mail(subject=subject,
        #           message=message,
        #           from_email=from_email,
        #           recipient_list=recipient_list,
        #           html_message=html_message)
        from celery_tasks.email.tasks import celery_send_email
        celery_send_email.delay(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message
        )

        # 5. 返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})
