from flask import Blueprint, jsonify, request
from api import make_response_ok, make_response_error, validsign
from models import UserInfo, db
import logging
import redis_helper
import re

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')
pattern_nickname = '\w[a-zA-Z0-9]{8,64}'

bp = Blueprint('user', __name__, url_prefix='/api/user')

r_cache = redis_helper.Redis.connect(db=5)


@bp.route('/show', endpoint='show')
@validsign
def show_user_info():
    user_id = request.args.get('userId')
    peer_id = request.args.get('peerId')
    if not user_id:
        return make_response_error(500, 'params error')

    show_id = user_id

    if peer_id:
        show_id = peer_id

    user = get_user_with_cache(show_id)

    if not user:
        return make_response_error(501, 'user not found')

    data = {'user_id': user.id, 'nickname': user.nickname, 'birthday': user.birthday, 'gender': user.gender,
            'avatar': user.avatar, 'height': user.height, 'sexual': user.sexual, 'education': user.education,
            'workplace': user.workplace, 'salary': user.salary, 'emotion': user.emotion}
    if show_id == user_id:
        data['phone'] = user.phone

    return make_response_ok(data)


@bp.route('/hot/list', endpoint='list')
@validsign
def list_hot_user():
    page = request.args.get('page', 1)
    per_page = request.args.get('pageCount', 10)
    pagination = UserInfo.query.paginate(page=page, per_page=per_page)
    items = pagination.items
    data = []
    if items:
        data = [{'user_id': user.id, 'nickname': user.nickname, 'birthday': user.birthday, 'gender': user.gender,
                 'avatar': user.avatar, 'height': user.height, 'sexual': user.sexual, 'education': user.education,
                 'salary': user.salary, 'emotion': user.emotion} for user in items]
    obj = {'total': pagination.total, 'list': data, 'has_next': pagination.has_next}
    return make_response_ok(obj)


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


@bp.route('/update', methods=["POST"], endpoint="update")
@validsign
def update_user():
    uid = request.form.get('userId', '')
    token = request.form.get('token', '')
    user = get_user_with_cache(uid)

    if not user:
        return make_response_error(503, 'user not found')
    if user.user_auth.token != token:
        return make_response_error(504, 'no operation permission')

    nickname = request.args.get('nickname')
    if not check_nickname(nickname):
        return make_response_error(504, 'you set the wrong nickname')

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
    user.nickname = nickname
    user.email = email
    user.gender = gender
    user.sexual = sexual
    user.height = height
    user.education = education
    user.emotion = emotion
    user.salary = salary
    db.session.bulk_save_objects([user])
    db.session.commit()
    return make_response_ok(data={"data": user.id})


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
