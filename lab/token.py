# https://blog.csdn.net/m0_56477185/article/details/124616865

import base64;
import hmac;
import json;
import time;

header = {"typ": "JWT", "alg": "HS256"};

header_str = json.dumps(header)

header_encode = base64.urlsafe_b64encode(header_str.encode())

print('结果:', header_encode);

header_p1 = header_encode.replace(b"=", b"");

payload = {"username": "demo", "uid": 3, 'exp': time.time() + 300 }

payload_p2 = base64.urlsafe_b64encode(json.dumps(payload).encode()).replace(b"=", b"");

temp = header_p1 + b"." + payload_p2;

temp_hash = hmac.new(b"123", temp, digestmod="SHA256");

print("二进制:", temp_hash.digest());
print("十六进制:", temp_hash.hexdigest());

signature = base64.urlsafe_b64encode(temp_hash.digest()).replace(b"=", b"");

jwt_token = (header_p1 + b"." + payload_p2 + b"." + signature).decode()

print("token:", jwt_token);
