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
        # 1.get request params
        image_code = request.Get.get('image_code')
        uuid=request.Get.get('image_code_id')
        # 2.verify the Image_code
        if not all([image_code,uuid]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})
        
        # 3.1 connect redis
        
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')

        # 3.2 get redis data
        redis_image_code = redis_cli.get(uuid)
        if redis_image_code is None:
            return JsonResponse({'code':400,'errmsg':'图片验证码已经过期'})
        
        if redis_image_code.decode().lower()!=image_code.lower():
            return JsonResponse({'code':400,'errmsg':'图片验证码错误'})
        
        send_flag = redis_cli.get('send_flag_%s'%mobile)

        if send_flag is not None:
            return JsonResponse({'code':400,'errmsg':'不要频繁发送短信'})
        
        from random import randint
        sms_code = '%o6d'%randint(0,999999)

        pipeline = redis_cli.pipeline()

        pipeline.setex(mobile,300,sms_code)

        pipeline.setex('send_flag_%s'%mobile,60,1)

        pipeline.execute()

        from celery_tasks.sms.tasks import celery_send_sms_code
        
        celery_send_sms_code.delay(mobile,sms_code)

        return JsonResponse({'code':0,'errmsg':'ok'})

