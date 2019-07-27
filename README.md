# 基于Flask开发企业级API应用系列

>关于我  
>编程界的一名小小程序猿，目前在一个创业团队任team lead，技术栈涉及Android、Python、Java和Go，这个也是我们团队的主要技术栈。  
Github：https://github.com/hylinux1024  
微信公众号：angrycode  

前面对`Python WEB`框架`Flask`的源码进行走读，对服务的[启动流程](https://juejin.im/post/5d341ea36fb9a07ed6580f10)、[路由原理](https://juejin.im/post/5d3713cc51882548de1e6be7)和[模板渲染](https://juejin.im/post/5d38fc1af265da1bb31c7b31)有了一个宏观的认识。不过说了那么多理论，接下来就利用`Flask`开发一个企业级的`API`应用。  

我选用团队最近开发的一个企业应用作为案例。这是一个恋爱交友应用，本来是使用`Java`的`SpringBoot`框架进行开发的，不过为了避免不必要的麻烦，我会使用`Flask`进行改造，当然这个案例我还会精简一下，保持核心业务的同时，重点关注其中涉及到的**技术和工具库**的使用，最大限度的还原项目开发的完整流程。  

#### 0x00 技术栈

这里我们使用`Python`版本为3.7，`WEB`框架当然就是`Flask`，数据库使用`MySql`，`ORM`使用`SqlAlchemy`，使用`Redis`作为缓存，可能还会使用到序列化工具库`marshmallow`。  

开发环境使用`venv`，部署服务环境会使用`nginx+gunicorn+supervisord`

因此整个技术栈为
```
# 开发技术栈
Python3.7+venv+Flask+MySql+SqlAlchemy+Redis+marshmallow
# 部署技术栈
Python3.7+venv+nginx+gunicorn+supervisord
```

当然企业实际开发中还需要编写接口文档，用于各端同学的交互。我们可以使用`postman`或者淘宝的[API文档服务](http://rap2.taobao.org)。  

#### 0x01 项目设计

技术选型做好之后，先不急于写代码，而是先把项目前期的设计做好，根据业务需求理清功能模块、数据库表结构、接口文档等。

我们的需求是做一个**恋爱交友**的应用，那么它**主要功能模块**就应该有

- **登录注册**    
这里使用用户手机号进行登录注册
- **用户列表**  
用户登录后，可以查看当前热门推荐的用户
- **联系人列表**  
联系过的用户，会出现在联系人列表中
- **聊天模块**  
给用户发送消息，消息类型包括文本、语音等
- **附近的人**  
根据用户登录的地理位置，查看附近的人
- **谁看过我**  
查看谁看过我，这个可以作为`VIP`功能
- **个人信息**  
包括用户基本信息、用户相册和用户标签等
- **VIP模块**  
当用户充值为`VIP`后可以解锁一些功能，比如查看**谁看过我的列表**等

**注意为了避免项目开发周期过长我们主要关注前台`api`的开发，对于后台管理功能暂时不考虑。**

根据这些功能模块，我们对项目中的**实体进行抽象**主要有

- **登录授权`user_auth`**
- **用户基本信息`user_info`**
- **用户位置`location`**
- **用户相册`user_album`**
- **用户标签`user_label`**
- **标签`label`**
- **联系人`contacts`**
- **消息`message`**
- **访问足迹`visitor`**  
- **充值`VIP`的商品`product`**  
有月度`VIP`、季度`VIP`和年度`VIP`三种
- **订单`user_order`**  
- **用户`VIP`信息`vip_info`**  

这些实体在**数据库建模**中分别对应各自的表。避免代码篇幅太长，这里就不再贴出各表脚本代码。关于`sql`表结构会在后面的项目地址中给出。  

#### 0x02 数据库

我这里使用的是腾讯云的数据库，当然使用本地的数据库也是可以的。

各表的字段如下图

![](https://i.loli.net/2019/07/27/5d3bb9de3ca5841090.png)

注意这些表我都没有加外键约束。

#### 0x03 项目框架搭建

我使用`PyCharm`作为开发环境的`IDE`，创建了一个名为`DatingToday`项目，结构如下

```Python
(venv) ➜  DatingToday tree -L 1
.
├── app.py
├── datingtoday.sql
├── requirements.txt
├── static
├── templates
└── venv
```
注意到我已经把数据库脚本文件放在项目根目录了。  
`venv`环境安装了以下依赖库

```Python
(venv) ➜  DatingToday pip list
Package                Version
---------------------- -------
Click                  7.0    
Flask                  1.1.1  
flask-marshmallow      0.10.1 
Flask-SQLAlchemy       2.4.0  
itsdangerous           1.1.0  
Jinja2                 2.10.1 
MarkupSafe             1.1.1  
marshmallow            2.19.5 
marshmallow-sqlalchemy 0.17.0 
pip                    10.0.1 
setuptools             39.1.0 
six                    1.12.0 
SQLAlchemy             1.3.6  
Werkzeug               0.15.5 
```
可以使用命令
```Python
(venv) ➜ pip freeze > requirements.txt
```
生成`requirements.tx`文件。

使用命令
```
(venv) ➜ pip install -r requirements.txt
```
还原虚拟环境中的依赖。

#### 0x04 总结

本篇是基于Flask开发企业级API应用的第一篇，主要是对项目开发前期的准备工作，包括项目设计、数据库设计以及项目结构搭建，当然实际工作中可能还会先出`API`文档，让前端的同学可以先动起来，但我这里因为已经是在*写文档*了，所以`API`文档就省略了。磨刀不误砍柴工，这些工作都是必需的。

#### 0x05 项目地址

https://github.com/hylinux1024/datingtoday

#### 0x06 学习资料

- https://palletsprojects.com/p/flask/
- https://realpython.com/flask-connexion-rest-api-part-2/