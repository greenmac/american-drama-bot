from django.shortcuts import render

# import 必要的函式庫
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
import requests
import json
# 這邊是Linebot的授權TOKEN(等等註冊LineDeveloper帳號會取得)，我們為DEMO方便暫時存在settings裡面存取，實際上使用的時候記得設成環境變數，不要公開在程式碼裡喔！
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

@csrf_exempt
def callback(request):

    if request.method == 'POST':
        signature = request.META['HTTPS_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                # 此處我們呼叫get_answer函數，從QnAMaker服務取得答案
                answer = get_answer(event.message.text)
                line_bot_api.reply_message(
                    event.reply_token,
                #    TextSendMessage(text=event.message.text)
                   TextSendMessage(text=answer)
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

def get_answer(message_text):
    
    url = "https://americandrama.azurewebsites.net/qnamaker/knowledgebases/46f10b99-04c3-4a9c-a367-3c08096ad460/generateAnswer"

    # 發送request到QnAMaker Endpoint要答案
    response = requests.post(
                   url,
                   json.dumps({'question': message_text}),
                   headers={
                       'Content-Type': 'application/json',
                       'Authorization': 'EndpointKey 66715a53-f4e4-4e99-9c23-bd202d051059'
                   }
               )

    data = response.json()

    try: 
        #我們使用免費service可能會超過限制（一秒可以發的request數）
        if "error" in data:
            return data["error"]["message"]
        #這裡我們預設取第一個答案
        answer = data['answers'][0]['answer']

        return answer

    except Exception:

        return "Error occurs when finding answer"