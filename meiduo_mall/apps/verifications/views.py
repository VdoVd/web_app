from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
# Create your views here.
from django.views import View

class ImageCodeView(View):
    
    def get(self,request,uuid):
        
        from libs.captcha.captcha import captcha

        text,image=captcha.generate_captcha()

        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')

        redis_cli.setex(uuid,100,text)

        return HttpResponse(image,content_type='image/jpeg')

class SmsCodeView(View):

    def get(self,request,mobile):
        # 1. 获取请求参数
        image_code=request.GET.get('image_code')
        uuid=request.GET.get('image_code_id')
        # 2. 验证参数
        if not all([image_code,uuid]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})
        # 3. 验证图片验证码
        # 3.1 连接redis
        from django_redis import get_redis_connection
        redis_cli=get_redis_connection('code')
        # 3.2 获取redis数据
        redis_image_code=redis_cli.get(uuid)
        if redis_image_code is None:
            return JsonResponse({'code':400,'errmsg':'图片验证码已过期'})
        # 3.3 对比
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code':400,'errmsg':'图片验证码错误'})

        # 提取发送短信的标记，看看有没有
        send_flag=redis_cli.get('send_flag_%s'%mobile)

        if send_flag is not None:
            return JsonResponse({'code':400,'errmsg':'不要频繁发送短信'})

        # 4. 生成短信验证码
        from  random import randint
        sms_code= '%06d'%randint(0,999999)

        # 管道 3步
        # ① 新建一个管道
        pipeline=redis_cli.pipeline()
        # ② 管道收集指令
        # 5. 保存短信验证码
        pipeline.setex(mobile, 300, sms_code)
        # 添加一个发送标记.有效期 60秒 内容是什么都可以
        pipeline.setex('send_flag_%s' % mobile, 60, 1)
        # ③ 管道执行指令
        pipeline.execute()

        # # 5. 保存短信验证码
        # redis_cli.setex(mobile,300,sms_code)
        # # 添加一个发送标记.有效期 60秒 内容是什么都可以
        # redis_cli.setex('send_flag_%s'%mobile,60,1)

        # 6. 发送短信验证码
        # from libs.yuntongxun.sms import CCP
        # CCP().send_template_sms(mobile,[sms_code,5],1)

        from celery_tasks.sms.tasks import celery_send_sms_code
        # delay 的参数 等同于 任务（函数）的参数
        celery_send_sms_code.delay(mobile,sms_code)

        # 7. 返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})

