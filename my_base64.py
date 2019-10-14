# array = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
array = 'LVoJPiCN2R8G90yg+hmFHuacZ1OWMnrsSTXkYpUq/3dlbfKwv6xztjI7DeBE45QA'
def encode_three(s0, s1, s2):
    d = s2 & 63
    d = array[d]
    c1 = (s1 & 15) << 2
    c2 = (s2 & 192) >> 6
    c = c1 + c2
    c = array[c]
    b1 = (s0 & 3) << 4
    b2 = (s1 & 240) >> 4
    b = b1 + b2
    b = array[b]
    a =  (s0 & 252) >> 2
    a = array[a]
    return ''.join([a,b,c,d])

def loop(length, str, result):
    for i in range(0, length, 3):
         en = encode_three(ord(str[i]), ord(str[i+1]), ord(str[i+2]))
         result += en
    return result
    
def my_encode(str):
    result = ''
    if len(str) % 3 == 0:
        need = 0
    else:
        need = 3 - len(str) % 3

    length = len(str) + need
    str += '\x00' * need

    result = loop(length, str, result)          # encode
    if need != 0:
        result = result[:-need] + '=' * need        # replace with '='
    return result
