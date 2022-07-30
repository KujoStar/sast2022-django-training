from distutils.log import info
from django.http import (
    HttpRequest,
    JsonResponse,
    HttpResponseNotAllowed,
)
from lb.models import Submission, User
from django.forms.models import model_to_dict
from django.db.models import F
import json
from lb import utils
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_http_methods as method
import time

def hello(req: HttpRequest):
    return JsonResponse({
        "code": 0,
        "msg": "hello"
    })

# TODO: Add HTTP method check
@method(["GET"])
def leaderboard(req: HttpRequest):
    return JsonResponse(
        utils.get_leaderboard(),
        safe=False,
    )


@method(["GET"])
def history(req: HttpRequest, username: str):
    # TODO: Complete `/history/<slug:username>` API
    sub_history = Submission.objects.filter(user__username = username).order_by("time")
    if len(sub_history) == 0:
        return JsonResponse({
            "code": -1,
            "msg": "你是一个，一个一个不存在的用户啊啊啊啊啊"
        })
    datas = list(sub_history.values("score", "subs", "time"))
    for data in datas:
        data["subs"] = data["subs"].split()
    return JsonResponse({
        "code": 1,
        "data": datas,
        "msg": "美好的提交记录（赞赏）"
    })
    #raise NotImplementedError


@method(["POST"])
@csrf_exempt
def submit(req: HttpRequest):
    # TODO: Complete `/submit` API
    try:
        infomation = json.loads(req.body)
        #print(114514)
    except:
        #print(114514)
        return JsonResponse({
            "code": 1145141919810,
            "msg": "这不是一个一个一个json，让我雷普，三回啊三回！"
        })
    if not all(key in infomation.keys() for key in ("user", "avatar", "content")):
        return JsonResponse({
            "code": 1,
            "msg": "噗叽啪（参数不全的声音）"
        })
    if len(infomation["user"]) > 255:
        return JsonResponse({
            "code": -1,
            "msg": "嗯嘛啊（用户名太长的声音）"
        })
    if len(infomation["avatar"]) > 100000:
        return JsonResponse({
            "code": -2,
            "msg": "鸭蛋冇鸭蛋（图像太大的声音）"
        })
    try:
        main_score, sub_score = utils.judge(infomation["content"])
    except:
        return JsonResponse({
            "code": -3,
            "msg": "牡蛎冇牡蛎（提交内容非法的声音）"
        })  
    
    current_user = User.objects.filter(username = infomation["user"]).first()
    if not current_user:
        User.objects.create(username = infomation["user"])
    
    Submission.objects.create(user = current_user, avatar = infomation["avatar"], time = time.time(), score = main_score, subs = sub_score)
    return JsonResponse({
        "code": 0,
        "msg": "提交成功力！（赞赏）",
        "data":{
            "leaderboard": utils.get_leaderboard()
        }
    })
    #raise NotImplementedError


@method(["POST"])
@csrf_exempt
def vote(req: HttpRequest):
    if 'User-Agent' not in req.headers \
            or 'requests' in req.headers['User-Agent']:
        return JsonResponse({
            "code": -1
        })
    try:
        current_user = User.objects.filter(username = json.loads(req.body)["user"]).first()
        if not current_user:
            return JsonResponse({
                "code": -1,
                "msg": "你还没注册呢（恼）"
            })
        current_user.votes += 1
        current_user.save()
    except:
        return JsonResponse({
            "code": -1,
            "msg": "寄寄寄寄摆摆摆摆"
        })
    
    return JsonResponse({
        "code": 0,
        "data":{
            "leaderboard": utils.get_leaderboard()
        }
    })
    # TODO: Complete `/vote` API

    # raise NotImplementedError
