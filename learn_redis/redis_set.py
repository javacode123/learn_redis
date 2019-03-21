# coding: utf-8
import redis


conn = redis.Redis()
conn.sadd('set', 'num1')  # 添加元素
conn.sadd('set', 'num2')
conn.sadd('set', 'num3')
print conn.srem('set', 'num1')  # 移除元素
print conn.sismember('set', 'num2')  # 集合是否存在元素
print conn.smembers('set')  # 返回所有元素
conn.sadd('set', 'num4')
print conn.scard('set')  # 返回集合数量
