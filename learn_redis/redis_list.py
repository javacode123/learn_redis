# coding: utf-8
import redis


conn = redis.Redis()
conn.rpush('lis', 'last')  # 右边加入
conn.lpush('lis', 'first')  # 左边加入
conn.rpush('lis', 'last-est')
print conn.lrange('lis', 0, -1)
print conn.llen('lis')  # 双向链表长度
conn.delete('lis')  # 清空
