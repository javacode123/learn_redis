# coding: utf-8

import redis


conn = redis.Redis()
print conn.get('key')  # 不存在，输出 None
print conn.incr('key')  # 增加 1，输出 1
print conn.incr('key', 15)  # 增加 15，输出 16
print conn.decr('key', 5)  # 减少 5，输出 11
print conn.get('key')  # 输出 11
conn.delete('key')  # 删除

print '=============='
conn.set('key1', 'a')
print conn.get('key1')
conn.append('key1', 'bcd')  # 追加 bcd
print conn.get('key1')
print conn.getrange('key1', 0, 2)  # 输出下标位于 0，1，2
