from flask import request;

import json;


class TalkRequest():
  def __init__(self):
    print("success use talk request");
    data = request.get_data();
    self.data = data;
  def talkMess(self, config):
    print("This is talk messages");
    conn = config.connection();
    cursor = conn.cursor();

    data = json.loads(self.data);
