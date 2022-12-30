from django.shortcuts import render

# Create your views here.
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
class QQLoginURLView(View):

    def get(self,request):
        
        qq = OAuthQQ(client_id = None,
                     client_secret = None,
                     redirect_url = None,
                     state = None)
                     