from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserInfo(db.Model):
    """用户基本信息"""
    __tablename__ = 'user_info'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64))  # email
    nickname = db.Column(db.String(64))
    phone = db.Column(db.String(16))
    gender = db.Column(db.String(2))  # 1男2女
    birthday = db.Column(db.Date)
    avatar = db.Column(db.String(128))
    emotion = db.Column(db.String(2))  # 情感状态 0 单身 1 已婚 2 离异 3保密
    height = db.Column(db.Integer)
    sexual = db.Column(db.String(2))  # 性取向 1 男 2女 3都有
    education = db.Column(db.String(64))  # 0 未知; 1 高中及以下; 2中专; 3大学; 4硕士; 5 博士
    salary = db.Column(db.Integer)  # 1: 3000以下；2: 3000-5000；3: 5000-8000; 4: 8000-10000; 5: 10000-20000; 6: 20000以上
    authority = db.Column(db.Integer)  # 个人资料可见性（0：所有用户不可见，1：所有用户可见，2：仅我关注的人可见）

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id}, {self.nickname})'


class UserAuth(db.Model):
    """授权登录表"""
    __tablename__ = 'user_auth'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    user_basic = db.relationship(UserInfo, backref=db.backref('user_auth', lazy=True, uselist=False))

    open_id = db.Column(db.String(128))
    session_key = db.Column(db.String(255))
    token = db.Column(db.String(255))
    expired_time = db.Column(db.DateTime)
    login_type = db.Column(db.String(16))  # 登录类型：phone,third_login
    login_time = db.Column(db.DateTime)  # 最近登录时间
    create_time = db.Column(db.DateTime)  # 注册时间

    # activate_code = db.Column(db.String(128))  # 激活码

    # def __str__(self):
    #     login_time = self.login_time.strftime("%Y-%m-%d %H:%M:%S") if self.login_time else ''
    #     created_at = self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ''
    #     return str({'id': self.id, 'uid': self.uid, 'openid': self.openid, 'session_key': self.session_key,
    #                 'token': self.token, 'login_time': login_time, 'created_at': created_at,
    #                 'user': self.user_basic, 'expired_at': self.expired_at, 'login_type': self.login_type,
    #                 })


class Message(db.Model):
    """
    用户消息
    """
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_uid = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    from_user = db.relationship(UserInfo, backref=db.backref('from_message', lazy=True), foreign_keys=from_uid)

    to_uid = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    to_user = db.relationship(UserInfo, backref=db.backref('to_message', lazy=True), foreign_keys=to_uid)

    msg_type = db.Column(db.String(16))  # text,audio,image,video
    audio = db.Column(db.String(128))
    image = db.Column(db.String(128))
    content = db.Column(db.String(128))
    send_time = db.Column(db.DateTime)  # 消息发送时间
    read = db.Column(db.Integer)  # 1 已读 0 未读

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id},from_uid={self.from_uid},' \
            f'to_uid={self.to_uid},msg_type={self.msg_type},content={self.content})'


class Product(db.Model):
    """
    商品
    """
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(64))
    vip_time = db.Column(db.Integer)
    price = db.Column(db.Float)

    def __repr__(self):
        return str({"id": self.id, "product": self.product_name})
