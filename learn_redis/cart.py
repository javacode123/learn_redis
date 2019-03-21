# coding: utf-8
import time

QUIT = False
LIMIT = 1000


def add_to_cart(conn, session, item, count):  # 添加购物车
    if count < 0:
        conn.hrem('cart:' + session, item)
    else:
        conn.hadd('cart:' + session, item, count)


def clean_full_sessions(conn):  # 清楚购物车

    while not QUIT:
        size = conn.zcard('cart:')  # 获取总量

        if size <= LIMIT:
            time.sleep(1)
            continue

        end_index = min(size - LIMIT, 100)
        sessions = conn.zrange("recent:", 0, end_index - 1)
        sessions_keys = []

        for sess in sessions:
            sessions_keys.append('viewed:' + sess)
            sessions_keys.append('cart:' + sess)

        conn.delete(*sessions_keys)
        conn.hdel("login", *sessions)
        conn.zrem('recent', *sessions)
