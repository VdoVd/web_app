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
        user=User.objects.create_user(username=username,password=password,mobile=mobile)

        #set session
        from django.contrib.auth import login
        
        login(request,user)
        
        
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
        print('email:'+email)
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
        message="meiduo_mall"
        # from_email,   发件人
        from_email='15360606636@163.com'
        # recipient_list, 收件人列表
        recipient_list = ['15360606636@163.com']

        # 邮件的内容如果是 html 这个时候使用 html_message
        # 4.1 对a标签的连接数据进行加密处理
        # user_id=1
        from apps.users.utils import generic_email_verify_token
        token=generic_email_verify_token(request.user.id)
        print('token:'+token)
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
        # from celery_tasks.p import p
        # p()
        celery_send_email.delay(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message
        )

        # 5. 返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})


class EmailVerifyView(View):

    def put(self, request):
        # 1. 接收请求
        params = request.GET
        # 2. 获取参数
        token = params.get('token')
        # 3. 验证参数
        if token is None:
            return JsonResponse({'code': 400, 'errmsg': '参数缺失'})
        # 4. 获取user_id
        from apps.users.utils import check_verify_token
        user_id = check_verify_token(token)
        if user_id is None:
            return JsonResponse({'code': 400, 'errmsg': '参数错误'})
        # 5. 根据用户id查询数据
        user = User.objects.get(id=user_id)
        # 6. 修改数据
        user.email_active = True
        user.save()
        # 7. 返回响应JSON
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


"""
请求
业务逻辑（数据库的增删改查）
响应


增 （注册）
    1.接收数据
    2.验证数据
    3.数据入库
    4.返回响应

删 
    1.查询到指定记录
    2.删除数据（物理删除，逻辑删除）
    3.返回响应

改  （个人的邮箱）
    1.查询指定的记录
    2.接收数据
    3.验证数据
    4.数据更新
    5.返回响应

查   （个人中心的数据展示，省市区）
    1.查询指定数据
    2.将对象数据转换为字典数据
    3.返回响应
"""

"""
需求：
    新增地址

前端：
        当用户填写完成地址信息后，前端应该发送一个axios请求，会携带 相关信息 （POST--body）

后端：

    请求：         接收请求，获取参数,验证参数
    业务逻辑：      数据入库
    响应：         返回响应

    路由：     POST        /addresses/create/
    步骤： 
        1.接收请求
        2.获取参数，验证参数
        3.数据入库
        4.返回响应

# """
from apps.users.models import Address


class AddressCreateView(LoginRequiredJSONMixin, View):

    def post(self, request):
        # 1.接收请求
        data = json.loads(request.body.decode())
        # 2.获取参数，验证参数
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')

        user = request.user
        # 验证参数 （省略）
        # 2.1 验证必传参数
        # 2.2 省市区的id 是否正确
        # 2.3 详细地址的长度
        # 2.4 手机号
        # 2.5 固定电话
        # 2.6 邮箱

        # 3.数据入库
        address = Address.objects.create(
            user=user,
            title=receiver,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            place=place,
            mobile=mobile,
            tel=tel,
            email=email
        )

        address_dict = {
            'id': address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 4.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'address': address_dict})


class AddressView(LoginRequiredJSONMixin, View):

    def get(self, request):
        # 1.查询指定数据
        user = request.user
        # addresses=user.addresses

        addresses = Address.objects.filter(user=user, is_deleted=False)
        # 2.将对象数据转换为字典数据
        address_list = []
        for address in addresses:
            address_list.append({
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            })
        # 3.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'addresses': address_list})

#
# #################################################
#
# """
# 一 根据页面效果，分析需求（细心+经验）
#     1. 最近浏览记录 只有登录用户才可以访问。 我们只记录登录用户的浏览记录
#     2. 浏览记录应该有顺序
#     3. 没有分页
# 二  功能
# ① 在用户访问商品详情的时候， 添加浏览记录
# ② 在个人中心，展示浏览记录
#
# 三 分析
# 问题1： 保存哪些数据？ 用户id，商品id,顺序（访问时间）
# 问题2： 保存在哪里？   一般要保存在数据库 （缺点： ① 慢 ② 频繁操作数据库） 授课
#                     最好保存在redis中
#
# 都可以。看公司具体的安排。 服务器内存比较大。 mysql + redis
#
#
# user_id,sku_id,顺序
#
# key: value
#
# redis:
#     string:   x
#     hash:     x
#     list:     v
#     set:      x
#     zset:     v
#             权重：值
# """
#
# """
# 添加浏览记录
#     前端：
#             当登录用户，访问某一个具体SKU页面的时候，发送一个axios请求。 请求携带 sku_id
#     后端：
#          请求：        接收请求，获取请求参数，验证参数
#          业务逻辑；    连接redis，先去重，在保存到redsi中，只保存5条记录
#          响应：        返回JSON
#
#         路由：     POST        browse_histories
#         步骤：
#             1. 接收请求
#             2. 获取请求参数
#             3. 验证参数
#             4. 连接redis    list
#             5. 去重
#             6. 保存到redsi中
#             7. 只保存5条记录
#             8. 返回JSON
# 展示浏览记录
#      前端：
#            用户在访问浏览记录的时候，发送axios请求。 请求会携带session信息
#     后端：
#          请求：
#          业务逻辑；    连接redis,获取redis数据（[1,2,3]）.根据商品id进行数据查询，将对象转换为字典
#          响应：        JSON
#
#         路由：    GET
#         步骤：
#             1. 连接redis
#             2. 获取redis数据（[1,2,3]）
#             3. 根据商品id进行数据查询
#             4. 将对象转换为字典
#             5. 返回JSON
# """
# from apps.goods.models import SKU
from django_redis import get_redis_connection


class UserHistoryView(LoginRequiredJSONMixin, View):

    def post(self, request):
        user = request.user

        # 1. 接收请求
        data = json.loads(request.body.decode())
        # 2. 获取请求参数
        sku_id = data.get('sku_id')
        # 3. 验证参数
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '没有此商品'})
        # 4. 连接redis    list
        redis_cli = get_redis_connection('history')
        # 5. 去重(先删除 这个商品id 数据，再添加就可以了)
        redis_cli.lrem('history_%s' % user.id, 0, sku_id)
        # 6. 保存到redsi中
        redis_cli.lpush('history_%s' % user.id, sku_id)
        # 7. 只保存5条记录
        redis_cli.ltrim("history_%s" % user.id, 0, 4)
        # 8. 返回JSON
        return JsonResponse({'code': 0, 'errmsg': 'ok'})

    def get(self, request):
        # 1. 连接redis
        redis_cli = get_redis_connection('history')
        # 2. 获取redis数据（[1,2,3]）
        ids = redis_cli.lrange('history_%s' % request.user.id, 0, 4)
        # [1,2,3]
        # 3. 根据商品id进行数据查询
        history_list = []
        for sku_id in ids:
            sku = SKU.objects.get(id=sku_id)
            # 4. 将对象转换为字典
            history_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })

        # 5. 返回JSON
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'skus': history_list})

