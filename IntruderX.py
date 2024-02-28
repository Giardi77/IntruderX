from itertools import product
import argparse
import sys
import httpx

TARGET=None
HEADERS={}
PARAMS={}
COOKIES={}
LEVEL=3
METHOD=str
LOGO= "\n\n    _____         _                     _           __   __\n   |_   _|       | |                   | |          \ \ / /\n     | |   _ __  | |_  _ __  _   _   __| |  ___  _ __\ V /\n     | |  | '_ \ | __|| '__|| | | | / _` | / _ \| '__|> <\n    _| |_ | | | || |_ | |   | |_| || (_| ||  __/| |  / . \ \n   |_____||_| |_| \__||_|    \__,_| \__,_| \___||_| /_/ \_\            by Giardi :)\n\n\n\n"

parser = argparse.ArgumentParser(prog=LOGO,
                    description='\t𝐀𝐥𝐭𝐞𝐫𝐧𝐚𝐭𝐢𝐯𝐞 𝐭𝐨 𝐁𝐮𝐫𝐩\'𝐬 𝐈𝐧𝐭𝐫𝐮𝐝𝐞𝐫 𝐛𝐮𝐢𝐥𝐭 𝐨𝐧 𝐭𝐨𝐩 𝐨𝐟 𝐡𝐭𝐭𝐩𝐱',)

parser.add_argument('-t','--target',help='Set the target (-u https://localhost:1234)')
parser.add_argument('-m','--method', help='set GET or POST request')
parser.add_argument('-H','--headers', help='Headers (key:value,key:value...)')
parser.add_argument('--params', help='GET request parametes (key:value,key:value...)')
parser.add_argument('-sc','--special_char',help='special char and file or list')
parser.add_argument('--cookies',help='add cookies (key:value,key:value...')
parser.add_argument('-v','--verbouse',help='set verbousity: 1-http status code, 2-headers, 3-full response')

args = parser.parse_args()

def stringtodict(input_string)->dict:
    """
    Converts a string of comma-separated key-value pairs into a dictionary.

    Example:
    >>> stringtodict("name:John, age:30, city:New York")
    {'name': 'John', 'age': '30', 'city': 'New York'}
    """
    pairs = input_string.split(',')
    result_dict = {}
    for pair in pairs:
        key, value = pair.split(':')
        result_dict[key.strip()] = value.strip()
    return result_dict

def replace_substring(original_str, replace_dict):
    """
    Replaces substrings in a given string based on a dictionary of replacements.

    Returns:
    str: The modified string after performing the specified substitutions.

    Example:
    >>> replace_substring("Hello, [name]!", {"[name]": "John"})
    'Hello, John!'
    """
    for key, value in replace_dict.items():
        original_str = original_str.replace(key, str(value))
    return original_str

def print_based_on_verbousity(level,res,req):
    """
    Just print based-off verbousity level (-v switch)
    """
    if level == '1':
        print(str(res.status_code))
    elif level == '2':
        print(str(res.status_code))
        for name, value in res.headers.items():
            print(f"{name}: {value}")
    elif level == '3':
        print(str(res.status_code))
        for name, value in res.headers.items():
            print(f"{name}: {value}")
        print(res.content.decode())
    elif level == '4':
        print(req.method+' '+str(req.url),end='')
        try:
            if req.params:
                print(req.params)
        except AttributeError:
            pass
        print("\nRequest Headers:")
        for name, value in req.headers.items():
            print(f"{name}: {value}")
        for name, value in res.headers.items():
            print(f"{name}: {value}")
        print(res.content.decode())
    else:
        print(str(res.status_code))
        for name, value in res.headers.items():
            print(f"{name}: {value}")
        print(res.content.decode())

print(parser.prog + '\n' + parser.description + '\n' + '\n')

if args.target is None:
    print("\n Set a target with -t switch (-t https://127.0.0.1/)")
    sys.exit()

else:
    TARGET=args.target

if args.method != '':
    METHOD = args.method
    
else:
    METHOD = 'GET'

if args.verbouse is not None:
    LEVEL=args.verbouse

if args.cookies is not None:
    COOKIES = stringtodict(args.cookies)
    print(COOKIES)

if args.headers is not None:
    HEADERS=stringtodict(args.headers)

if args.params is not None:
    PARAMS=stringtodict(args.params)

if args.special_char is not None:
    client = httpx.Client()
    RANGES = None
    char = stringtodict(args.special_char)
    perms = {}
    for value in char.values():
        thiskey = [key for key, thisvalue in char.items() if thisvalue == value][0]
        if value.startswith('range(') :
            RANGES = eval(value)
            perms[thiskey] = []
            for n in RANGES:
                perms[thiskey].append(n)
        else:
            perms[thiskey] = list(value)

    payloads = []

    keys = list(perms.keys())
    iterables = list(perms.values())

    result_product = list(product(*iterables))

    for combination in result_product:
        result_dict = dict(zip(keys, combination))

        newHeaders = {key: replace_substring(value, result_dict) for key, value in HEADERS.items()}
        newParams = {key: replace_substring(value, result_dict) for key, value in PARAMS.items()}
        newCookies = {key: replace_substring(value, result_dict) for key, value in COOKIES.items()}

        request = httpx.Request(METHOD,url=TARGET,headers=newHeaders,params=newParams,cookies=newCookies)
        response = client.send(request)
        print_based_on_verbousity(LEVEL,response,request)
    client.close()

else:
    client = httpx.Client()
    request = httpx.Request(METHOD,url=TARGET,headers=HEADERS,params=PARAMS,cookies=COOKIES)
    response = client.send(request)
    print_based_on_verbousity(LEVEL,response,request)
    client.close()
