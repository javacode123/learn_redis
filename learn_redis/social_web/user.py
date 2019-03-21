# coding: utf-8
import time
from learn_redis.social_web.lock import acquire_lock, release_lock


def create_user(conn, login, name):  # 注册用户
    llogin = login.lower()
    lock = acquire_lock(conn, 'user:' + llogin, 1)  # 将次注册名称锁起来，防止两个人用同一个名称同时注册

    if not lock:
        return None  # 加锁失败，表示用户名已经被其他用户占用

    if conn.hget('user:', llogin):  # 用户名已经存在
        release_lock(conn, 'user:' + llogin, lock)
        return None

    id = conn.incr('user:id:')  # id 自增, 单独的 key 用于存储 id 自增, conn.get('user:id') 查看, 有可能 id 自增，但是注册失败，造成 id 浪费
    pipeline = conn.pipeline(True)  # 原子操作
    pipeline.hset('user:', llogin, id)  # 存储用户
    pipeline.hmset('user:%s' % id, {  # 存储用户信息
        'login': login,  # 登录名
        'id': id,
        'name': name,
        'followers': 0,  # 被关注数目
        'following': 0,  # 关注数目
        'posts': 0,  # 发送状态树
        'signup': time.time()
    })
    pipeline.execute()
    release_lock(conn, 'user:' + llogin, lock)  # 释放锁
    return id


def login_user(conn, login):  # 用户登录
    llogin = login.lower()
    uid = conn.hget('user:', llogin)
    if uid:
        return uid
    else:
        return False


def info_user(conn, uid):  # 获取用户信息
    return conn.hgetall('user:%s' % uid)


