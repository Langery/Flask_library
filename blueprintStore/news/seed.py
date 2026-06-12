"""News seed 数据。模仿 jsonplaceholder 风格,启动时幂等注入 100 条。"""

from datetime import datetime, timezone, timedelta


_REAL_POSTS_1_10 = [
    {
        'title': 'sunt aut facere repellat provident occaecati excepturi optio reprehenderit',
        'body': 'quia et suscipit suscipit recusandae consequuntur expedita et cum reprehenderit molestiae ut ut quas totam nostrum rerum est autem sunt rem eveniet architecto',
    },
    {
        'title': 'qui est esse',
        'body': 'est rerum tempore vitae sequi sint nihil reprehenderit dolor beatae ea dolores neque fugiat blanditiis voluptate porro vel nihil molestiae ut reiciendis qui aperiam non debitis possimus qui neque nisi nulla',
    },
    {
        'title': 'ea molestias quasi exercitationem repellat qui ipsa sit aut',
        'body': 'et iusto sed quo iure et voluptatem officiis necessitatibus aliquam et voluptas dicta autem voluptatum architecto eos voluptatem quia et quam occaecati qui debitis ea voluptas delectus blanditiis repudiandae quaerat placeat sint consequatur voluptatem expedita deleniti accusamus nostrum aut exercitationem repellendus qui ratione aut eaque doloremque',
    },
    {
        'title': 'eum et est occaecati',
        'body': 'ullam et saepe reiciendis voluptatem adipisci sit amet autem assumenda provident rerum culpa quis hic commodi nesciunt rem tenetur doloremque ipsam iure quis sunt voluptatem rerum illo velit',
    },
    {
        'title': 'nesciunt quas odio',
        'body': 'repudiandae veniam quaerat sunt sed alias aut fugiat sit autem sed est voluptatem omnis possimus esse voluptatibus quis est aut tenetur dolor neque',
    },
    {
        'title': 'dolorem eum magni eos aperiam quia',
        'body': 'ut aspernatur corporis harum nihil quis provident sequi mollitia nobis aliquid molestiae perspiciatis et ea nemo ab reprehenderit accusantium quas voluptate dolores velit et doloremque molestiae',
    },
    {
        'title': 'magnam facilis autem',
        'body': 'dolore placeat quibusdam ea quo vitae magni quis enim qui quis quo nemo aut saepe quidem mollitia delectus saepe quia sunt eligendi praesentium amet consectetur adipisci earum labore ea aut sed quia voluptas enim quasi quibusdam',
    },
    {
        'title': 'dolorem dolore est ipsam',
        'body': 'dignissimos aperiam dolorem qui eum facilis quia aspernatur sunt hic sint odit sint molestiae qui in exercitationem tenetur minus expedita voluptas dignissimos voluptate in perferendis at reprehenderit modi molestiae',
    },
    {
        'title': 'nesciunt iure omnis dolorem tempora et accusantium',
        'body': 'consectetur animi nesciunt iure dolore enim accusantium ut aliquam delectus consequatur similique totam mollitia veritatis quam exercitationem necessitatibus earum voluptatem doloremque ipsum reprehenderit sunt qui aut ullam tenetur culpa cupiditate rerum quia architecto unde corrupti autem',
    },
    {
        'title': 'optio molestias id quia eum',
        'body': 'quo et expedita modi cum officia vel magni doloribus qui repudiandae vero nisi sit quos veniam quod sed accusamus veritatis error consectetur quidem tenetur magnam eos voluptatem ratione ipsam molestias expedita aperiam rerum voluptas libero quia voluptas ut voluptatum quisquam voluptatem in perferendis pariatur officiis voluptate non sit',
    },
]


_LOREM_WORDS = [
    'lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing', 'elit',
    'sed', 'do', 'eiusmod', 'tempor', 'incididunt', 'ut', 'labore', 'et', 'dolore',
    'magna', 'aliqua', 'enim', 'ad', 'minim', 'veniam', 'quis', 'nostrud',
    'exercitation', 'ullamco', 'laboris', 'nisi', 'aliquip', 'ex', 'ea', 'commodo',
    'consequat', 'duis', 'aute', 'irure', 'in', 'reprehenderit', 'voluptate',
    'velit', 'esse', 'cillum', 'fugiat', 'nulla', 'pariatur', 'excepteur', 'sint',
    'occaecat', 'cupidatat', 'non', 'proident', 'sunt', 'culpa', 'qui', 'officia',
    'deserunt', 'mollit', 'anim', 'id', 'est', 'laborum',
]

_ACTIONS = [
    'overview', 'update', 'release', 'launch', 'announcement', 'milestone',
    'feature', 'integration', 'highlight', 'breakthrough', 'review', 'roundup',
]

_BODY_TEMPLATES = [
    'quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt',
    'neque porro quisquam est qui dolorem ipsum quia dolor sit amet consectetur adipisci velit sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem ut enim ad minima veniam quis nostrum exercitationem',
    'ullam corporis suscipit laboriosam nisi ut aliquid ex ea commodi consequatur quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident',
    'similique sunt in culpa qui officia deserunt mollitia animi id est laborum et dolorum fuga et harum quidem rerum facilis est et expedita distinctio nam libero tempore cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus omnis voluptas assumenda est omnis dolor repellendus',
]


def _generate_post(post_id):
    """生成第 11..100 条的伪数据。"""
    w1 = _LOREM_WORDS[post_id % len(_LOREM_WORDS)]
    w2 = _LOREM_WORDS[(post_id * 3) % len(_LOREM_WORDS)]
    action = _ACTIONS[post_id % len(_ACTIONS)]

    body_idx = post_id % len(_BODY_TEMPLATES)
    body1 = _BODY_TEMPLATES[body_idx]
    body2 = _BODY_TEMPLATES[(body_idx + 1) % len(_BODY_TEMPLATES)]
    body3 = _BODY_TEMPLATES[(body_idx + 2) % len(_BODY_TEMPLATES)]

    return {
        'title': f'News #{post_id}: {w1} {w2} {action}',
        'body': f'{body1} {body2} {body3}',
    }


def _all_posts():
    """返回 100 条 post 字典。"""
    posts = []
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(1, 101):
        if i <= 10:
            data = _REAL_POSTS_1_10[i - 1]
        else:
            data = _generate_post(i)
        posts.append({
            'id': i,
            'user_id': (i % 10) + 1,
            'title': data['title'],
            'body': data['body'],
            'created_at': (base_time + timedelta(hours=i * 6)).isoformat(),
        })
    return posts


def seed_news_if_empty():
    """如果 news 表是空的,注入 100 条 seed。启服务时调用,幂等。"""
    from classStore.common.db import query_one, execute

    existing = query_one('SELECT COUNT(*) AS c FROM news')
    if existing and existing['c'] > 0:
        return 0

    posts = _all_posts()
    for p in posts:
        execute(
            'INSERT INTO news (id, user_id, title, body, created_at) VALUES (?, ?, ?, ?, ?)',
            (p['id'], p['user_id'], p['title'], p['body'], p['created_at'])
        )
    return len(posts)
