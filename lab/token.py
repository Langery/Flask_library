import base64
import hmac
import json
import time


def generate_token(username, user_id, secret_key='123'):
    header = {"typ": "JWT", "alg": "HS256"}
    header_encode = base64.urlsafe_b64encode(
        json.dumps(header).encode()
    ).replace(b"=", b"")

    payload = {
        "username": username,
        "uid": user_id,
        "exp": time.time() + 300
    }
    payload_encode = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).replace(b"=", b"")

    temp = header_encode + b"." + payload_encode
    temp_hash = hmac.new(secret_key.encode(), temp, digestmod="SHA256")

    signature = base64.urlsafe_b64encode(temp_hash.digest()).replace(b"=", b"")

    jwt_token = (header_encode + b"." + payload_encode + b"." + signature).decode()
    return jwt_token


if __name__ == '__main__':
    token = generate_token('demo', 3)
    print("Token:", token)