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

        