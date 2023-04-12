class HttpStatus(object):
    code = 0
    msg = ''


class HttpStatus200(HttpStatus):
    code = 200
    msg = 'OK'


class HttpStatus400(HttpStatus):
    code = 400
    msg = 'Bad Request'


class HttpStatus401(HttpStatus):
    code = 401
    msg = 'Unauthorized'
        

class HttpStatus403(HttpStatus):
    code = 403
    msg = 'Forbidden'


class HttpStatus404(HttpStatus):
    code = 404
    msg = 'Not Found'


class HttpStatus405(HttpStatus):
    code = 405
    msg = 'Method Not Allowed'


class HttpStatus500(HttpStatus):
    code = 500
    msg = 'Internal Server Error'


class HttpStatus503(HttpStatus):
    code = 503
    msg = 'Server Unavailable'