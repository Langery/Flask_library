from flask import request

import json
from classStore.server.dataLab import SQLFun

class Upload():
  def __init__(self):
    print('success use upload')
    data = request.get_data();
    self.data = data;
  def uploadImg(self, config):
    print('This is the loadImg');
    # TODO: upload image