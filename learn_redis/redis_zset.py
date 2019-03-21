# coding: utf-8
import redis


conn = redis.Redis()
conn.zadd('z-key', {'a': 3, 'b': 0})  # 有序集合添加数据
print conn.zcard('z-key')  # 大小
conn.zadd('z-key', {'c': 2})
print conn.zrange('z-key', 0, -1, withscores=True)  # 获取全部的值
print conn.zrank('z-key', 'b')  # 排名
