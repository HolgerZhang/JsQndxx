#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:yuzai holger
@file:server.py
@time:2022/03/24
"""

import uvicorn
from fastapi import FastAPI

from main import learn

app = FastAPI()


@app.get("/")
async def index():
    return {"info": "欢迎使用JsQndxx，运行后请自行检查！"}


@app.get("/session/{laravel_session}")
async def session(laravel_session: str):
    try:
        ret = learn(laravel_session)
    except Exception as e:
        ret = {'success': False, 'message': ';'.join(map(str, e.args)), 'user': '', 'lesson': '', }
    return ret


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=5555)
