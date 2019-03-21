# coding: utf-8
import uuid
import time
import redis


def acquire_lock(conn, lockname, acquire_timeout=10):
    identifier = str(uuid.uuid4())  # 128 位随机标识符
    end = time.time() + acquire_timeout

    while time.time() < end:
        if conn.setnx('lock:' + lockname, identifier):  # 尝试取得锁, setnx() 保证方法的原子性
            return identifier
        time.sleep(.001)

    return False


def release_lock(conn, lockname, identifier):
    pipe = conn.pipeline(True)
    lockname = 'lock:' + lockname

    while True:
        try:
            pipe.watch(lockname)  # 监视 key 是否变化
            if pipe.get(lockname) == identifier:  # 检查进程是否持有锁
                pipe.multi()  # 开启一个事务
                pipe.delete(lockname)
                pipe.execute()  # 执行
                return True
            pipe.unwatch()
            break

        except redis.exceptions.WatchError:
            pass

    return False