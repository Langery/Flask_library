from flask import request, make_response;
import json;
import time;
import base64;
import hmac;

from classStore.server.dataLab import SQLFun

class Login():
  def __init__(self):
    print('success use login')
    data = request.get_data()
    self.data = data
  def select(self, config):
    data = json.loads(self.data)
    username = data['username']
    password = data['password']
    conn = config.connection()
    cursor = conn.cursor()
    # select
    loginSQL = SQLFun('*', 'usertable')
    sqlName = loginSQL.select('nickname')
    sqlPwd = loginSQL.select('password')
    rowName = cursor.execute(sqlName, username)
    rowPws = cursor.execute(sqlPwd, password)
    print(rowName, rowPws)
    conn.commit()
    # conn.close() # false closure
    if rowName >= 1:
      nameData = True
    else:
      nameData = False
    if rowPws >= 1:
      pwdData = True
    else:
      pwdData = False
    res = {}
    if nameData and pwdData:
      res['backData'] = True
    else:
      res['backData'] = False
    print(res);
    token = TokenFun(self);
    return json.dumps(res)

# TODO: add id and key
def TokenFun(self):
  data = json.loads(self.data);
  username = data['username'];
  password = data['password'];
  # id ???
  # header
  header = {"typ": "JWT", "alg": "HS256"};
  header_str = json.dumps(header);
  header_encode = base64.urlsafe_b64encode(header_str.encode());

  print('base64:', header_encode);
  header_p1 = header_encode.replace(b"=", b"");

  payload = {"username": username, "uid": 0, "exp": time.time() + 300};

  payload_p2 = base64.urlsafe_b64encode(json.dumps(payload).encode()).replace(b"=", b"");

  temp = header_p1 + b"." + payload_p2;

  temp_hash = hmac.new(b"", temp, digestmod="SHA256"); # b key&id

  print("二进制:", temp_hash.digest());
  print("十六进制:", temp_hash.hexdigest());

  signature = base64.urlsafe_b64encode(temp_hash.digest()).replace(b"=", b"");

  jwt_token = (header_p1 + b"." + payload_p2 + b"." + signature).decode()

  print("token:", jwt_token);

  return jwt_token;
