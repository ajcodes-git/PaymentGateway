from bcrypt import checkpw, hashpw, gensalt

def hash(api_key: str):
    return hashpw(api_key.encode('utf-8'), gensalt()).decode('utf-8')

def verify(plain_api_key: str, hashed_api_key):
    return checkpw(plain_api_key.encode('utf-8'), hashed_api_key.encode('utf-8'))
