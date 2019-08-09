from flask import Blueprint, jsonify, request
from api import make_response_ok, make_response_error, validsign
from models import UserInfo, db
import logging
import redis_helper
import re
from datetime import datetime

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')
pattern_nickname = '[a-zA-Z0-9]{5,64}'

bp = Blueprint('user', __name__, url_prefix='/api/user')

r_cache = redis_helper.Redis.connect(db=5)


@bp.route('/show', endpoint='show')
@validsign(require_token=True, require_sign=False)
def show_user_info():
    uid = request.args.get('userId')
    peer_id = request.args.get('peerId')

    show_id = uid

    if peer_id:
        show_id = peer_id

    user = get_user_with_cache(show_id)

    if not user:
        return make_response_error(501, 'user not found')

    data = {'user_id': user.id, 'nickname': user.nickname, 'birthday': user.birthday, 'gender': user.gender,
            'avatar': user.avatar, 'height': user.height, 'sexual': user.sexual, 'education': user.education,
            'salary': user.salary, 'emotion': user.emotion}
    if show_id == uid:
        data['phone'] = user.phone

    return make_response_ok(data)


@bp.route('/hot/list', endpoint='list')
@validsign(require_token=True, require_sign=False)
def list_hot_user():
    page = request.args.get('page', 1)
    per_page = request.args.get('pageCount', 10)
    pagination = UserInfo.query.paginate(page=page, per_page=per_page)
    items = pagination.items
    data = []
    if items:
        data = [
            {'user_id': user.id, 'nickname': user.nickname, 'birthday': user.format_birthday(), 'gender': user.gender,
             'avatar': user.avatar, 'height': user.height, 'sexual': user.sexual, 'education': user.education,
             'salary': user.salary, 'emotion': user.emotion} for user in items]
    obj = {'total': pagination.total, 'list': data, 'has_next': pagination.has_next}
    return make_response_ok(obj)


@bp.route('/update', methods=["POST"], endpoint="update")
@validsign(require_token=False, require_sign=False)
def update_user():
    uid = request.form.get('userId', '')

    nickname = request.form.get('nickname')
    if not check_nickname(nickname):
        return make_response_error(505, 'the length of nickname must larger than 5 and less thad 8')

    email = request.form.get('email')
    gender = request.form.get('gender', default=0, type=int)
    if gender > 2 or gender < 0:
        gender = 0
    sexual = request.form.get('sexual', default=0, type=int)
    if sexual > 2 or sexual < 0:
        sexual = 0
    height = request.form.get('height', type=int)
    education = request.form.get('education', type=int)
    emotion = request.form.get('emotion', type=int)
    salary = request.form.get('salary', type=int)
    birthday = request.form.get('birthday', type=str)
    avatar = request.form.get('avatar', type=str)
    if birthday:
        birthday = datetime.strptime(birthday, "%Y-%m-%d")

    user: UserInfo = get_user_with_cache(uid)
    user.nickname = nickname
    user.emotion = emotion
    user.email = email
    user.gender = gender
    user.sexual = sexual
    user.height = height
    user.education = education
    user.salary = salary
    user.birthday = birthday
    user.avatar = avatar

    db.session.commit()
    return make_response_ok(data={"data": user.id})


@bp.route('/nearby/list')
def list_nearby_user():
    latlng = request.args.get('latlng', '')
    logging.info(f'remote ip : {request.remote_addr}')

    location = latlng.split(',')
    if len(location) <= 1:
        return make_response_error(502, 'lat,lng error')
    lat, lng = location
    data = {'longitude': lng, 'latitude': lat}
    return make_response_ok(data)


@bp.route('/search')
def search_user():
    resp = {'code': 0, 'msg': 'success'}
    return jsonify(resp)


def get_user_with_cache(uid):
    if not uid:
        return None
    user = r_cache.get('user-{}'.format(uid))
    if not user:
        user = UserInfo.query.filter_by(id=uid).first()
    return user


def check_nickname(nickname):
    if not nickname:
        return True
    m = re.match(pattern_nickname, nickname)
    return True if m else False
