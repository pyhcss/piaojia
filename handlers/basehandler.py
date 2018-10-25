# coding=utf-8

import json
from libs.session import Session
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    """基础处理类"""
    @property
    def db(self):
        return self.application.db

    @property
    def redis(self):
        return self.application.redis

    def prepare(self):
        pass

    def write_error(self, status_code, **kwargs):
        pass

    def initialize(self):
        self.xsrf_token
        if self.request.headers.get("Content-Type","").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None

    def set_default_headers(self):
        self.set_header("Content-Type","application/json;charset=utf-8")

    def get_current_user(self):
        self.session = Session(self)
        return self.session.data

    def on_finish(self):
        pass