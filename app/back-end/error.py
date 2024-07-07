#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json
import time
from typing import Any, Dict, Optional

from fastapi.responses import JSONResponse


class ApiResponse(JSONResponse):
    http_status_code = 200
    api_code = 0
    result: Optional[Dict[str, Any]] = None
    message = "Success"
    success = True
    timestamp = int(time.time() * 1000)

    def __init__(
        self,
        success=None,
        http_status_code=None,
        api_code=None,
        result=None,
        message=None,
        **options
    ):
        if result:
            self.result = result
        if message:
            self.message = message

        if api_code:
            self.api_code = api_code

        if success != None:
            self.success = success

        if http_status_code:
            self.http_status_code = http_status_code

        body = dict(
            message=self.message,
            code=self.api_code,
            success=self.success,
            result=self.result,
            timestamp=self.timestamp,
        )
        # if options:
        #     body = {**body, **options}
        #     [options.pop(key) for key in [itemkey for itemkey in options.keys() if itemkey not in ['content', 'status_code', 'headers', 'media_type', 'background']]]
        super(ApiResponse, self).__init__(
            status_code=self.http_status_code, content=body, **options
        )

    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=json.JSONEncoder,
        ).encode("utf-8")


class BadRequestException(ApiResponse):
    http_status_code = 400
    api_code = 10001
    result = None
    message = "Bad request"
    success = False


class LimitedResException(ApiResponse):
    http_status_code = 429
    api_code = 10002
    result = None
    message = "Limited access"
    success = False


class ParameterException(ApiResponse):
    http_status_code = 400
    api_code = 10003
    result = {}
    message = "Parameter error"
    success = False


class UnauthorizedException(ApiResponse):
    http_status_code = 401
    api_code = 10004
    result = {}
    message = "Unauthorized"
    success = False


class ForbiddenException(ApiResponse):
    http_status_code = 403
    api_code = 10005
    result = {}
    message = "Access Forbidden"
    success = False


class NotfoundException(ApiResponse):
    http_status_code = 404
    api_code = 10006
    result = {}
    message = "Not Found"
    success = False


class MethodNotAllowedException(ApiResponse):
    http_status_code = 405
    api_code = 10007
    result = {}
    message = "Method not allowed"
    success = False


class FileTooLargeException(ApiResponse):
    http_status_code = 413
    api_code = 10008
    result = None
    message = "File size is too large"
    success = False


class FileTooManyException(ApiResponse):
    http_status_code = 413
    api_code = 10009
    result = None
    message = "Too many files"
    success = False


class FileExtensionException(ApiResponse):
    http_status_code = 401
    api_code = 10010
    result = None
    message = "File extension error"
    success = False


class UnknownException(ApiResponse):
    http_status_code = 800
    api_code = 11000
    result = {}
    message = "Unknown HTTP error"
    success = False


class InternalErrorException(ApiResponse):
    http_status_code = 500
    api_code = 12000
    result = {}
    message = "Internal error"
    success = False


class OpenaiException(ApiResponse):
    http_status_code = 600
    api_code = 13000
    result = {}
    message = "OpenAI error"
    success = False


class Success(ApiResponse):
    http_status_code = 200
    api_code = 10000
    result = None
    message = "Success"
    success = True
