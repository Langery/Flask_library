from flask import request, make_response

class First():
  def __init__(self):
    print('success')
  def first(self):
    name = request.args.get('name')
    print(name)
    if name:
      print(name)
      res = make_response('Hello Ajax ' + name)
      return res
