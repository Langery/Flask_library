def test():
  print('test')
test()

def text_dealSQL(*key):
   valueS = ''
   keyS = ''
   newAdd = ''
   for index, everyOne in enumerate(key):
      keyS += everyOne+','
      valueS += '%s,'
      newAdd += everyOne + '=%s and '

   # keyS = keyS[:-1]
   # valueS = valueS[:-1]
   newAdd = newAdd[:-5]
   print('INSERT INTO (' + keyS + ')' + ' VALUES (' + valueS + ')')
   print('SELECT * FROM WHERE ' + newAdd)

user = 'user'
id = 'id'
name = 'name'
text_dealSQL(user, id, name)
