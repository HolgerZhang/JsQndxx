#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:yuzai holger
@file:main.py
@time:2022/03/24
"""
import re
import sys
import traceback
import warnings

import requests
import urllib3
from bs4 import BeautifulSoup


class QndxxBot:
    def __init__(self, laravel_session: str):
        self._session = requests.session()
        self._laravel_session = laravel_session

    def _header(self):
        return {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) MicroMessenger/6.8.0(0x16080000) MacWechat/3.7(0x13070010) Safari/605.1.15 NetType/WIFI",
            'Cookie': "laravel_session=" + self._laravel_session
        }

    def get_latest_lessons(self):
        url = "https://service.jiangsugqt.org/api/cjdList"  # 江苏省青年大学习成绩单接口
        res = self._session.post(url=url, headers=self._header(), params=dict(page="1", limit="5"))
        try:
            res = res.json()  # 返回结果转json
            return res['data']
        except requests.exceptions.JSONDecodeError:
            return None

    def learn_lesson(self, lesson_id):
        url = "https://service.jiangsugqt.org/api/doLesson"  # 江苏省青年大学习接口
        res = self._session.post(url=url, headers=self._header(), params=dict(lesson_id=lesson_id))  # 发送请求
        try:
            res = res.json()  # 返回结果转json
            return res
        except requests.exceptions.JSONDecodeError:
            return None

    def user_info(self):
        url = 'https://service.jiangsugqt.org/api/my'
        res = self._session.get(url=url, headers=self._header())  # 发送请求
        try:
            res = res.json()  # 返回结果转json
            return res['data']
        except requests.exceptions.JSONDecodeError:
            return None


def main(laravel_session):  # 参数为cookie里的laravel_session 自行抓包获取
    warnings.warn("this method is deprecated", DeprecationWarning)
    ret = {'laravel_session': laravel_session}
    s = requests.session()  # 创建会话
    loginurl = "https://service.jiangsugqt.org/youth/lesson"  # 江苏省青年大学习接口
    # 参数
    params = {
        "s": "/youth/lesson",
        "form": "inglemessage",
        "isappinstalled": "0"
    }
    # 构造请求头
    headers = {
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.18(0x18001234) NetType/WIFI Language/zh_CN",
        'Cookie': "laravel_session=" + laravel_session  # 抓包获取
    }
    urllib3.disable_warnings()  # 不然会有warning
    login = s.get(url=loginurl, headers=headers, params=params, verify=False)  # 登录

    login_soup = BeautifulSoup(login.text, 'html.parser')  # 解析信息确认页面
    userinfo = login_soup.select(".confirm-user-info p")  # 找到用户信息div 课程姓名编号单位

    mapping = {}  # 构建用户信息字典

    for i in userinfo:
        info_soup = BeautifulSoup(str(i), 'html.parser')  # 分布解析课程姓名编号单位信息
        item = info_soup.get_text()  # 用户信息
        mapping[item[:4]] = item[5:]
    token = re.findall(r'var token ?= ?"(.*?)"', login.text)  # 获取js里的token
    lesson_id = re.findall(r"'lesson_id':(.*)", login.text)  # 获取js里的token
    print("token:%s" % token[0])
    ret['token'] = token[0]
    print("lesson_id:%s" % lesson_id[0])
    ret['lesson_id'] = lesson_id[0]
    mapping['token'] = token[0]
    mapping['lesson_id'] = lesson_id[0]

    print('mapping:%s' % mapping)
    ret['mapping'] = mapping
    confirmurl = "https://service.jiangsugqt.org/youth/lesson/confirm"
    params = {
        "_token": token[0],
        "lesson_id": lesson_id[0]
    }
    res = s.post(url=confirmurl, params=params)
    res = res.json()  # 返回结果转json
    print("返回结果:%s" % res)
    ret['返回结果'] = res
    if res["status"] == 1 and res["message"] == "操作成功":
        print("青年大学习已完成")
        ret['success'] = True
    else:
        print("error")
        ret['success'] = False
    return ret


def learn(laravel_session):
    result = {
        'success': False,
        'message': '',
        'user': '',
        'lesson': '',
    }
    bot = QndxxBot(laravel_session)
    user = bot.user_info()
    if user is None:
        result['message'] = '获取用户信息失败'
        return result
    result['user'] = f"用户编号 {user['user_num']}, 用户名 {user['username']}, 所属组织 {user['orga']}"
    lesson_dict = bot.get_latest_lessons()
    print(lesson_dict)
    if lesson_dict is None:
        result['message'] = '获取课程信息失败'
        return result
    lesson_id = lesson_dict[0]['id']
    learn_result = bot.learn_lesson(lesson_id)
    print(learn_result)
    if learn_result is None:
        result['message'] = 'Qndxx执行失败'
        return result
    result['success'] = learn_result["status"] == 1 and learn_result["message"] == "操作成功"
    result['message'] = learn_result["message"]
    lesson_dict = bot.get_latest_lessons()
    print(lesson_dict)
    if lesson_dict is None or lesson_id != lesson_dict[0]['id']:
        result['message'] += ' 课程校验失败，请尝试重新执行'
        if lesson_dict is not None:
            result['lesson'] = f"课程 {lesson_dict[0]['title']}, ID={lesson_dict[0]['id']}!={lesson_id}, 学习状态 {lesson_dict[0]['has_learn']}"
        return result
    result['lesson'] = f"课程 {lesson_dict[0]['title']}, ID={lesson_dict[0]['id']}, 学习状态 {lesson_dict[0]['has_learn']}"
    return result


if __name__ == '__main__':
    for i, laravel in enumerate(sys.argv[1:]):
        print('[%d] 青年大学习开始执行 laravel_session = %s' % (i, laravel))
        try:
            print(learn(laravel))
        except Exception:
            print('[%d] 运行异常：\n%s' % (i, traceback.format_exc()))
        print('[%d] 青年大学习运行结束\n' % i)
