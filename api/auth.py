from flask import Blueprint, request
from models import UserAuth, UserInfo, db
from api import make_response_ok, make_response_error, validsign
import re
import hashlib
import os
import datetime
import redis

bp = Blueprint("auth", __name__, url_prefix='/api/auth')

pattern_phone = "(\\+[0-9]+[\\- \\.]*)?(\\([0-9]+\\)[\\- \\.]*)?([0-9][0-9\\- \\.]+[0-9])"
pattern_email = "[a-zA-Z0-9\\+\\.\\_\\%\\-\\+]{1,256}\\@[a-zA-Z0-9][a-zA-Z0-9\\-]{0,64}(\\.[a-zA-Z0-9][a-zA-Z0-9\\-]{0,25})+"

redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
r = redis.Redis(connection_pool=redis_pool)


@bp.route("/login", methods=['POST'], endpoint='login')
@validsign
def login():
    phone = request.form.get('phone')
    code = request.form.get('code')
    key = f'{phone}-{code}'
    sms_code = r.get(key)
    if sms_code:
        sms_code = sms_code.decode()
    if code != sms_code:
        return make_response_error(503, 'sms code error')
    auth_info = UserAuth.query.filter_by(open_id=phone).first()
    if not auth_info:
        auth_info = register_by_phone(phone)
    else:
        auth_info = login_by_phone(auth_info)

    data = {'token': auth_info.token,
            'expire_time': auth_info.expired_time.strftime("%Y-%m-%d %H:%M:%S"),
            'user_id': auth_info.user_basic.id}

    r.set(f'auth_info_{auth_info.user_id}', str(data))
    return make_response_ok(data)


def register_by_phone(phone):
    nickname = f"u-{phone}"
    user = UserInfo(phone=phone, nickname=nickname, authority=1, create_time=datetime.datetime.now())
    token, expire = generate_token()
    auth_info = UserAuth(open_id=phone, token=token, expired_time=expire, login_type='phone',
                         login_time=datetime.datetime.now(), create_time=datetime.datetime.now(),
                         user_basic=user)
    db.session.add_all([user, auth_info])
    db.session.commit()
    return auth_info


@bp.route("/sendsms", methods=['POST'], endpoint="sendsms")
@validsign
def send_sms():
    phone = request.form.get('phone')
    m = re.match(pattern_phone, phone)
    if not m:
        return make_response_error(300, 'phone number format error.')
    # 这里需要修改为对接短信服务
    code = '97532'
    key = f'{phone}-{code}'
    r.set(key, code, 60)
    return make_response_ok({'phone': phone, 'code': code})


def login_by_phone(auth_info):
    token, expire = generate_token()
    auth_info.token = token
    auth_info.expired_time = expire
    db.session.add(auth_info)
    db.session.commit()
    return auth_info


def generate_token():
    """
    生成token以及过期时间
    :return:
    """
    md5 = hashlib.md5()
    rand = os.urandom(32)
    md5.update(str(rand).encode('UTF-8'))
    token = md5.hexdigest()
    delta = datetime.timedelta(days=7)
    expired = datetime.datetime.utcnow() + delta

    return token, expired
