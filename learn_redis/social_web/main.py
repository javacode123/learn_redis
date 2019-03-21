# coding: utf-8
import redis
import json
import time

from learn_redis.social_web.user import create_user, login_user, info_user
from learn_redis.social_web.follow import follow_user, unfollow_user, follow_list, follower_list
from learn_redis.social_web.status import post_status, get_status_message, syndicate_status, delete_status
"""
    基于 redis 实现简单的社交网站，充分发挥 redis 的 K-V 存储方式, 其中主要涉及个人信息(hash), 登录状态(hash), 状态(hash）, 主页时间线(zset), 个人时间线(zset), 关注被关注(zset)

        1: 创建用户, 使用 hash 存储 'user:%s' % uid -> {'login': login, 'id': id, 'name': name, 'followers': 0,
            'following': 0, 'posts': 0, 'signup': time.time()

        2: 登录用户, 使用 hash 存储 'user:' -> {'login': login, 'id': uid}

        3: 关注操作, 使用 zset 存储, 关注信息 'following:%s' % uid -> other_idx,
                    使用 zset 存储, 被关注信息 'followers%s' % other_id -> other_idx
                    使用 zset 存储, 主页流 'home%s' % uid -> u_status_id, following_status_id

        4: 取消关注, 更新 'following:%s' % uid, 更新 'followers%s' % other_id, 更新 'user:%s' % uid, 'user%s' % other_id
                    更新 'home:%s' % uid

        5: 发送状态, 使用 hash 存储, 'status:%s' % status_id -> {'message': message, 'posted': time.time(), 'id': id, 'uid': uid, 'login': login},
                    更新 'user:%s' % uid, 更新 'home:%s' % follower_id
                    更细 'profile:%s' % uid, 更新 'home:%s' % uid

        6: 删除状态, 更新 'status:%s' % status_id, 更新 'user:%s' % uid, 更新 'profile:%s' % uid, 更新 'home:%s' % follower_id
                    更新 'home"%s' % uid
"""


def show_info(conn, uid):
    print 'user:%s' % uid, '关注人数:' + info_user(conn, uid).get('following'), '分别为:', follow_list(conn, uid)
    print 'user:%s' % uid, '被关注人数:' + info_user(conn, uid).get('followers'), '分别为:', follower_list(conn, uid)
    print 'user:%s' % uid, '状态数:' + info_user(conn, uid).get('posts')
    print '个人主页:', get_status_message(conn, uid, 'home')
    print '个人发布:', get_status_message(conn, uid, 'profile')
    print ''


if __name__ == '__main__':

    conn = redis.Redis()

    ''' 测试登录失败
    login_name = 'zjl'
    user_info = login_user(conn, login_name)

    if not user_info:
        print '用户名不存在'
    else:
        print user_info
    '''

    ''' 测试注册成功和失败
    login_name = 'zjl'
    real_name = '张佳洛'
    uid = create_user(conn, login_name, real_name)
    print conn.hgetall('user:')  # {'zjl': '1', 'zjl1': '2', 'zjl2': '3'}
    print conn.get('user:id:') # 用于记录 ID
    '''

    # ---------------登录---------------
    login_name = 'zjl1'
    uid = login_user(conn, login_name)

    if not uid:
        print '登录失败'
    else:
        print '登录成功'

    # ----------------关注操作----------- 1 关注 2, 3,  2 关注 1, 3
    '''
    follow_user(conn, 1, 2)
    follow_user(conn, 1, 3)
    follow_user(conn, 2, 1)
    follow_user(conn, 2, 3)
    '''

    # ----------------状态操作----------
    # print post_status(conn, 1, 'i am zjl')  # 1 发送了一个状态, 2 需要接收
    # print post_status(conn, 2, 'i am zjl1')  # 2 发送一个状态, 1 需要接收
    # print post_status(conn, 3, 'i am zjl2')  # 3 发送一个状态, 1 2 需要接收
    # print follow_user(conn, 3, 1)  # 3 关注 1
    # print follow_user(conn, 3, 2)  # 3 关注 2
    # print post_status(conn, 3, 'i am zjl3')  # 3 发送一个状态, 1 2 需要接收
    # print unfollow_user(conn, 1, 2)  # 1 取关 2
    # print delete_status(conn, 2, 2)  # 3 删除状态 4

    for i in range(1, 4):
        show_info(conn, i)

