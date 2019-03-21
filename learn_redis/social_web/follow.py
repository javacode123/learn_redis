# coding: utf-8
import time
"""执行关注操作"""
HOME_TIMELINE_SIZE = 1000


def follow_user(conn, uid, other_uid):
    """
    关注操作:
        更新操作者的关注有序集合, 更新被关注者的有序集合, 修改用户信息的关注和被关注数量, 复制被关注者状态信息到操作者时间线
    :param conn:
    :param uid: 操作者 id
    :param other_uid:  被关注者
    :return:
    """
    fkey1 = 'following:%s' % uid  # 操作者
    fkey2 = 'followers:%s' % other_uid  # 被关注者

    if conn.zscore(fkey1, other_uid):  # 是否已经关注了 other_id
        return None

    now = time.time()
    pipeline = conn.pipeline(True)
    pipeline.zadd(fkey1, {other_uid: now})  # 添加关注有序列表
    pipeline.zadd(fkey2, {uid: now})  # 添加被关注列表
    pipeline.zrevrange('profile:%s' % other_uid, 0, HOME_TIMELINE_SIZE-1, withscores=True)  # 从被关注者的时间线里获取最新的
    following, followers, status_and_score = pipeline.execute()[-3:]

    pipeline.hincrby('user:%s' % uid, 'following', int(following))  # 修改两个用户信息的散列，更新关注数和被关注数
    pipeline.hincrby('user:%s' % other_uid, 'followers', int(followers))
    if status_and_score:  # 更新关注操作的的时间线
        pipeline.zadd('home:%s' % uid, dict(status_and_score))
    pipeline.zremrangebyrank('home:%s' % uid, 0, -HOME_TIMELINE_SIZE-1)  # 保留时间线上面最新的 1000 条状态

    pipeline.execute()
    return True  # 关注操作完成


def unfollow_user(conn, uid, other_uid):  # 取消关注
    fkey1 = 'following:%s' % uid
    fkey2 = 'followers:%s' % other_uid

    if not conn.zscore(fkey1, other_uid):  # 是否已经关注 other_id
        return None

    pipieline = conn.pipeline(True)
    pipieline.zrem(fkey1, other_uid)  # 关注列表移除
    pipieline.zrem(fkey2, uid)  # 被关注列表移除
    pipieline.zrevrange("profile:%s" % other_uid, 0, HOME_TIMELINE_SIZE-1)  # 获取被取消用户最近发布的 HOME_TIMELINE_SIZE条状态消息
    following, followers, statuses = pipieline.execute()[-3:]

    pipieline.hincrby('user:%s' % uid, 'following', -int(following))  # 更新关注数目
    pipieline.hincrby('user:%s' % other_uid, 'followers', -int(followers))

    if statuses:
        pipieline.zrem('home:%s' % uid, *statuses)  # 对执行取消关注操作的用户的主页时间线进行更新，移除被取消关注用户发布的状态信息

    pipieline.execute()
    return True


def follow_list(conn, uid):  # 查看关注列表
    return conn.zrange('following:%s' % uid, 0, -1)


def follower_list(conn, uid):  # 被关注列表
    return conn.zrange('followers:%s' % uid, 0, -1)
