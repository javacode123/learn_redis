# coding: utf-8
import time
import uuid
import json

from learn_redis.social_web.follow import HOME_TIMELINE_SIZE
from learn_redis.social_web.lock import acquire_lock, release_lock
"""
    用户的时间线，主页用户获取的 feed 流
"""
POSTS_PER_PASS = 1000  # 每次推送最大人数


def get_status_message(conn, uid, timeline='home', page=1, count=30):  # 获取状态信息
    statuses = conn.zrevrange('%s:%s' % (timeline, uid), (page-1)*count, page*count-1, withscores=True)  # 获取时间线上最新的状态消息的 id
    pipeline = conn.pipeline(True)
    for id in statuses:
        pipeline.hgetall('status:%s' % id[0])  # 执行 execute() 才获取

    return filter(None, pipeline.execute())  # 使用过滤器移除那些已经被删除了的状态信息


def create_status(conn, uid, message, **data):  # 时间流, 先获取用户名，获取新状态的 id, 最后存储
    pipeline = conn.pipeline(True)
    pipeline.hget('user:%s' % uid, 'login')  # 根据 id 获取用户名
    pipeline.incr('status:id:')  # 为这条状态消息创建一个新的 id, 通过 string 存储自增 id （'status:id' -> id）
    login, id = pipeline.execute()

    if not login:  # 发消息之前，验证账号是否存在
        return None

    data.update({
        'message': message,
        'posted': time.time(),  # 发送时间
        'id': id,
        'uid': uid,
        'login': login  # 登录名
    })
    pipeline.hmset('status:%s' % id, data)
    pipeline.hincrby('user:%s' % uid, 'posts')  # 更新用户已发送状态消息数量
    pipeline.execute()
    return id


def post_status(conn, uid, message, **data):  # 发送状态
    id = create_status(conn, uid, message, **data)  # 创建一个 status

    if not id:  # 创建失败
        return None

    posted = conn.hget('status:%s' % id, 'posted')  # 获取创建时间

    if not posted:
        return None

    post = {str(id): float(posted)}
    conn.zadd('profile:%s' % uid, post)  # 添加到个人时间线
    conn.zadd('home:%s' % uid, post)  # 添加个人主页

    syndicate_status(conn, uid, post)  # 将状态推送给用户的关注者
    return id


def syndicate_status(conn, uid, post, start=0):  # 向关注者推送消息
    followers = conn.zrangebyscore('followers:%s' % uid, start, 'inf'
                                   , start=0, num=POSTS_PER_PASS, withscores=True)  # 获取 POST_PER_PASS 关注者
    pipeline = conn.pipeline(False)

    for follower in followers:
        pipeline.zadd('home:%s' % follower[0], post)  # 更新关注者主页
        pipeline.zremrangebyrank('home:%s' % follower[0], 0, -HOME_TIMELINE_SIZE)  # 限制关注者的主线长度

    pipeline.execute()

    if len(followers) > POSTS_PER_PASS:  # 如果关注者的数量大于 POSTS_PER_PASS, 在延迟任务里面继续执行剩余的更新操作
        execute_later(conn, 'default', 'syndicate_status',
                      [conn, uid, post, start])


def delete_status(conn, uid, status_id):  # 删除状态
    key = 'status:%s' % status_id
    lock = acquire_lock(conn, key, 1)  # 对状态消息加锁，防止两个程序同时删除同一条状态消息
    if not lock:
        return None  # 加锁失败

    if conn.hget(key, 'uid') != str(uid):  # uid 不是状态的发布人
        release_lock(conn, key, lock)
        return None

    pipeline = conn.pipeline(True)
    pipeline.delete(key)  # 删除状态
    pipeline.zrem('profile:%s' % uid, status_id)  # 时间线移除
    pipeline.zrem('home:%s' % uid, status_id)  # 主页删除
    pipeline.hincrby('user:%s' % uid, 'posts', -1)  # 发布消息总数
    pipeline.zrange('followers:%s' % uid, 0, -1)  # 获取关注者
    followers = pipeline.execute()[-1]

    for follow in followers:  # 关注者中删除
        pipeline.zrem('home:%s' % follow, status_id)

    release_lock(conn, key, lock)

    return True


def execute_later(conn, queue, name, args, delay=0):  # 延迟任务
    identifier = str(uuid.uuid4())  # 唯一标识符
    item = json.dumps([identifier, queue, name, args])  # 需要入队的任务

    if delay > 0:
        conn.zdd('delayed:', item, time.time() + delay)  # 延迟执行这个任务
    else:
        conn.rpush('queue:' + queue, item)

    return identifier


def get_status_by_uid(conn, uid, time_line='profile'):  # 获取状态列表
    return conn.zrangebyscore('%:%s' % (time_line, uid), 0, -1)
