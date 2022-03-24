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

import requests
import urllib3
from bs4 import BeautifulSoup


def main(laravel_session):  # 参数为cookie里的laravel_session 自行抓包获取
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


if __name__ == '__main__':
    for i, laravel_session in enumerate(sys.argv[1:]):
        print('-' * 40)
        print('[%d] 青年大学习开始执行 laravel_session = %s' % (i, laravel_session))
        try:
            main(laravel_session)
        except Exception:
            print('[%d] 运行异常：\n%s' % (i, traceback.format_exc()))
        print('[%d] 青年大学习运行结束\n' % i)
