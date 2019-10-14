import hmac
import hashlib
def get_md5(password,token):
        return hmac.new(token.encode(), password.encode(), hashlib.md5).hexdigest()
def get_sha1(value):
        return hashlib.sha1(value.encode()).hexdigest()



