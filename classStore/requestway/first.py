# 测试接口
from flask import request, make_response

class First():
  def __init__(self):
    print('success')
  def first(self):
    print(request)
    name = request.args.get('name')
    # print(name)
    # if name:
    #   # print(name)
    #   res = make_response('Hello Ajax ' + name)
    #   return res

    if name:
      print(name)

    else:
      print("Error~")
      return 'Nothing data'