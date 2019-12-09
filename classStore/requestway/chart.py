from flask import request, make_response
import json
from classStore.server.dataLab import SQLFun

class Chart():
  def __init__(self):
    print('chart data')
