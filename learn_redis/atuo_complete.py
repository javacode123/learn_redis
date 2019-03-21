# coding: utf-8
import redis
"""
    自动补全联系人:
        使用列表存储最近联系人, 当进行自动补全的时候, 从列表遍历, 查找符合的前缀
"""


def add_update_contact(conn, user, contact):
    ac_list = 'recent:' + user
    pipeline = conn.pipeline(True)  # 准备执行原子操作
    pipeline.lrem(ac_list, 0, contact)  # 如果联系人已经存在，那么移除他
    pipeline.lpush(ac_list, contact)  # 将联系人推入列表的最前端
    pipeline.ltrim(ac_list, 0, 10)  # 只保留列表里面的前 10 个联系人
    pipeline.execute()  # 执行以上命令


def remove_contact(conn, user, contact):
    conn.lrem('recent:' + user, contact)


def fetch_autocomplete_list(conn, user, prefix):
    candidates = conn.lrange('recent:' + user, 0, -1)  # 获取自动补全列表
    matches = []

    for candidate in candidates:
        if candidate.lower().startswith(prefix):  # 循环检查每个候选联系人
            matches.append(candidate)

    return matches  # 返回匹配的联系人


if __name__ == '__main__':
    conn = redis.Redis()
    user = 'user1'
    add_update_contact(conn, user, 'zjl0')
    add_update_contact(conn, user, 'zjl1')
    add_update_contact(conn, user, 'zjl3')
    print fetch_autocomplete_list(conn, user, 'zjl')
