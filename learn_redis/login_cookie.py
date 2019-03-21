# coding: utf-8
import time
import redis


def check_token(conn, token):
    """
    :param conn:
    :param token:
    :return: 对应令牌的用户
    """
    return conn.hget('login', token)


def update_token(conn, token, user, item=None):
    """

    :param conn:
    :param token:
    :param user:
    :param item:
    :return:
    """
    timestamp = time.time()  # 获取时间戳
    conn.hset('login', token, user)  # 维持令牌与以登录用户之间的映射
    conn.zadd('recent', token, timestamp)  # 记录令牌最后一次出现的时间
    if item:
        conn.zadd('viewed:' + token, item, timestamp)  # 记录浏览过的商品
        conn.zremrangebyrank('viewed:' + token, 0, -26)  # 移除旧的记录，只保留最近浏览过的 25 个商品


QUIT = False
LIMIT = 100000


def clean_sessions(conn):
    while not QUIT:
        size = conn.zcard('recent:')  # 找出目前已有令牌数量
        if size <= LIMIT:  # 令牌数没有超过限制，休眠之后重新检查
            time.sleep(1)
            continue

        end_index = min(size - LIMIT, 100)  # 获取移除令牌数目的 id
        tokens = conn.zrange("recent:", 0, end_index-1)
        session_keys = []

        for token in tokens:
            session_keys.append('viewed:' + token)

        conn.delete(*session_keys)
        conn.hdel('login', *tokens)
        conn.zrem('recent:', *tokens)

