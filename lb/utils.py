from lb.models import Submission, User
from random import randint
import math
import functools

def get_leaderboard():
    """
    Get the current leaderboard
    :return: list[dict]
    """

    # 坏了，我似乎已经忘了 ORM 中该怎么调 API 了
    # 在这里你可选择
    #    1. 看一眼数据表, 然后后裸写 SQL
    #    2. 把所有数据一股脑取回来然后手工选出每个用户的最后一次提交
    #    3. 学习 Django API 完成这个查询

    # 方案1: 直接裸写 SQL 摆烂，注意，由于数据库类型等因素，这个查询未必能正确执行，如果使用这种方法可能需要进行调整
    # subs = list(Submission.objects.raw(
    #         """
    #         SELECT
    #             `lb_submission`.`id`,
    #             `lb_submission`.`avatar`,
    #             `lb_submission`.`score`,
    #             `lb_submission`.`subs`,
    #             `lb_submission`.`time`
    #         FROM `lb_submission`, (
    #             SELECT `user_id`, MAX(`time`) AS mt FROM `lb_submission` GROUP BY `user_id`
    #         ) `sq`
    #         WHERE
    #             `lb_submission`.`user_id`=`sq`.`user_id` AND
    #             `time`=`sq`.`mt`;
    #         ORDER BY
    #             `lb_submission`.`subs` DESC,
    #             `lb_submission`.`time` ASC
    #         ;
    #         """
    # ))
    # return [
    #     {
    #         "user": obj.user.username,
    #         "score": obj.score,
    #         "subs": [int(x) for x in obj.subs.split()],
    #         "avatar": obj.avatar,
    #         "time": obj.time,
    #         "votes": obj.user.votes
    #     }
    #     for obj in subs
    # ]

    # 方案2：一股脑拿回本地计算
    all_submission = Submission.objects.all()
    subs = {}
    for s in all_submission:
        if s.user_id not in subs or (s.user_id in subs and s.time > subs[s.user_id].time):
            subs[s.user_id] = s

    subs = sorted(subs.values(), key=lambda x: (-x.score, x.time))
    return [
        {
            "user": obj.user.username,
            "score": obj.score,
            "subs": [int(x) for x in obj.subs],
            "avatar": obj.avatar,
            "time": obj.time,
            "votes": obj.user.votes
        }
        for obj in subs
    ]

    # 方案3：调用 Django 的 API (俺不会了
    # ...

def judge(content: str):
    """
    Convert submitted content to a main score and a list of sub scors
    :param content: the submitted content to be judged
    :return: main score, list[sub score]
    """

    # TODO: Use `ground_truth.txt` and the content to calculate scores.
    #  If `content` is invalid, raise an Exception so that it can be
    #  captured in the view function.
    #  You can define the calculation of main score arbitrarily.
    def interpolate(x1: float, x2: float, y1: float, y2: float, x: float):
        if x < x1:
            return y1
        if x > x2:
            return y2
        return math.sqrt((x-x1) / (x2-x1)) * (y2-y1) + y1
    
    def main_score(result: list):
        mean_result = sum(result) / 3
        return round(114 * interpolate(0.5, 0.8, 0, 1, mean_result) +
                     514 * interpolate(0.5, 0.7, 0, 1, result[0]) +
                     1919 * interpolate(0.5, 0.9, 0, 1, result[1]) +
                     810 * interpolate(0.5, 0.75, 0, 1, result[2])
                    ) #池沼分数计算法则（喜）
        
    with open("./ground_truth.txt", "r") as f:
        ans = [['1' if x == "True" else '0' for x in l.split(",")[1:]] for l in f.read().split()[1:]]
    '''
    ans = []
    with open("./ground_truth.txt", "r") as f:
        for contents in f.read().split()[1:]:
            temp = []
            for res in contents.split(",")[1:]:
                temp.append(res == "True")
            
            ans.append(temp)
            引以为戒，以后多写列表生成式
    '''
    submits = [temp.split(",") for temp in content.split()]
    '''
    submits=[]
    for line in content.split():
        temp=[]
        for x in line.split(","):
            temp.append(x)
            
        submits.append(temp)
        引以为戒，以后多写列表生成式
    '''
    if len(ans) != len(submits):
        raise RuntimeError("你是一个，一个一个错误提交啊啊啊啊啊啊")
    
    total = len(ans)
    
    try:
        subs = [sum([ans[i][j] == submits[i][j] for i in range(total)]) / total for j in range(3)]
    except:
        raise RuntimeError("你又是一个，一个一个池沼提交啊啊啊啊啊啊")
    
    subs_new = [x * 100 for x in subs]
    return main_score(subs), subs_new
