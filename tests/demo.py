def deal_sql(*keys):
    value_s = ''
    key_s = ''
    new_add = ''
    for index, every_one in enumerate(keys):
        key_s += every_one + ','
        value_s += '%s,'
        new_add += every_one + '=%s and '

    new_add = new_add[:-5]
    print('INSERT INTO (' + key_s + ')' + ' VALUES (' + value_s + ')')
    print('SELECT * FROM WHERE ' + new_add)


if __name__ == '__main__':
    user = 'user'
    user_id = 'id'
    name = 'name'
    deal_sql(user, user_id, name)