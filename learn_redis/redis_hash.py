# coding: utf-8
import redis


conn = redis.Redis()
conn.hset('hash', 'key1', 'value1')  # 为键添加键值对
conn.hmset('hash', {'key2': 'value2', 'key3': 'value3', 'key4': 'value4'})  # 批量添加键值对
print conn.hmget('hash', ['key1', 'key2'])  # 批量获取键对应的值
print conn.hlen('hash')  # 获取对应键的长度
conn.hdel('hash', 'key3')  # 删除
print conn.hlen('hash')
print conn.hget('hash', 'key1')  # 获取
print conn.hexists('hash', 'key2')  # 指定的键是否存在与散列中
print conn.hgetall('hash')  # 获取全部键值对
print conn.hkeys('hash')  # 全部的键
