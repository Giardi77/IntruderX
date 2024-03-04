from itertools import product
from termcolor import colored
from datetime import datetime
from time import sleep
import argparse
import sys
import httpx
import json


DATA={}
TARGET=None
HEADERS={}
PARAMS={}
COOKIES={}
LEVEL='3'
METHOD='GET'
LOGO= "\n\n    _____         _                     _           __   __\n   |_   _|       | |                   | |          \ \ / /\n     | |   _ __  | |_  _ __  _   _   __| |  ___  _ __\ V /\n     | |  | '_ \ | __|| '__|| | | | / _` | / _ \| '__|> <\n    _| |_ | | | || |_ | |   | |_| || (_| ||  __/| |  / . \ \n   |_____||_| |_| \__||_|    \__,_| \__,_| \___||_| /_/ \_\            by Giardi :)\n\n\n\n"
WAIT=None
INCLUDES=None
OMITS=None
DEFAULTUSERAGENT = {'User-Agent':'IntruderX 1.0'}


parser = argparse.ArgumentParser(prog=LOGO,
                    description='\t𝐀𝐥𝐭𝐞𝐫𝐧𝐚𝐭𝐢𝐯𝐞 𝐭𝐨 𝐁𝐮𝐫𝐩\'𝐬 𝐈𝐧𝐭𝐫𝐮𝐝𝐞𝐫 𝐛𝐮𝐢𝐥𝐭 𝐨𝐧 𝐭𝐨𝐩 𝐨𝐟 𝐡𝐭𝐭𝐩𝐱',)

parser.add_argument('-t','--target',help='Set the target (-u https://localhost:1234)',required=True)
parser.add_argument('-m','--method', help='set GET or POST request')
parser.add_argument('-H','--headers', help='Headers (key:value,key:value...)')
parser.add_argument('--params', help='GET request parametes (key:value,key:value...)')
parser.add_argument('-sc','--special_char',help='special char and file or list')
parser.add_argument('--cookies',help='add cookies (key:value,key:value...')
parser.add_argument('-v','--verbouse',help='set verbousity: 1 to 4 (default 3)')
parser.add_argument('-d','--data',help='Add data to request body')
parser.add_argument('-w','--wait',help='delay in seconds after sending a request')
parser.add_argument('--includes',help='check if a string is included')
parser.add_argument('--omits',help='check if a string is omitted')

args = parser.parse_args()

print(parser.prog + '\n' + parser.description + '\n' + '\n')

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
        key, value = pair.split(':',1)
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
    level 1: only status code
    level 2: status code & response headers
    level 3, code,response headers & body
    level 4: full request and response
    """
    if level == '1':
        if res.status_code == 200:
            print(colored(f'[{str(res.status_code)}]\n','green',))
        else:
            print(colored(f'[{str(res.status_code)}]\n','red',))

    elif level == '2':
        if res.status_code == 200:
            print(colored(f'[{str(res.status_code)}]\n','green',))
        else:
            print(colored(f'[{str(res.status_code)}]\n','red',))
        for name, value in res.headers.items():
            print(f"{name}: {value}")
        print('\n<+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+>\n')

    elif level == '3':
        if res.status_code == 200:
            print(colored(f'[{str(res.status_code)}]\n','green',))
        else:
            print(colored(f'[{str(res.status_code)}]\n','red',))
        for name, value in res.headers.items():
            print(f"{name}: {value}")
        print('\n')
        print(res.content.decode())
        print('\n<+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+>\n')

    elif level == '4':
        print(req.method+' '+str(req.url),end='\n')
        try:
            if req.params:
                print(f'{req.params}\n')
        except AttributeError:
            pass
        for name, value in req.headers.items():
            print(f"{name}: {value}")
        try:
            if req.read() is not None:
                print(f'\n{req.read().decode()}\n')
        except AttributeError:
            print('error')
            pass
        if res.status_code == 200:
            print(colored(f'[{str(res.status_code)}]\n','green',))
        else:
            print(colored(f'[{str(res.status_code)}]\n','red',))
        for name, value in res.headers.items():
            print(f"{name}: {value}")
        print('\n')
        print(res.content.decode())
        print('\n<+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+>\n')

def save_found_match(req,res):
    current_date_time = datetime.now()
    formatted_date_time = current_date_time.strftime("%Y-%m-%d|%H-%M-%S")
    filename= f'./outputs/{formatted_date_time}.txt'
    with open(filename, 'a') as file:
        file.write(str(req.url) + '\n')
        try:
            if req.params:
                file.write(f'{req.params}\n')
        except AttributeError:
            pass
        for name, value in req.headers.items():
            file.write(f"{name}: {value}\n")
        try:
            if req.read() is not None:
                file.write(f'\n{req.read().decode()}\n\n')
        except AttributeError:
            print('error')
            pass
        file.write('\n')
        file.write(f'[{str(res.status_code)}]\n')
        for name, value in res.headers.items():
            file.write(f"{name}: {value}\n")
        file.write('\n')
        file.write(res.content.decode())
        file.write('\n<+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+>\n')

if args.target is None:
    print("\n Set a target with -t switch (-t https://127.0.0.1/)")
    sys.exit()

else:
    TARGET=args.target

if args.method is not None:
    METHOD = args.method

if args.verbouse is not None:
    LEVEL=args.verbouse

if args.cookies is not None:
    COOKIES = stringtodict(args.cookies)
    print(COOKIES)

if args.headers:
    HEADERS=stringtodict(args.headers)
    if 'user-agent' not in [k.lower() for k in HEADERS.keys()]:
        HEADERS.update(DEFAULTUSERAGENT)
else:
    HEADERS = DEFAULTUSERAGENT

if args.params is not None:
    PARAMS=stringtodict(args.params)

if args.data is not None:
    DATA=stringtodict(args.data) 

if args.wait is not None:
    WAIT=int(args.wait)

if args.includes is not None:
    INCLUDES=args.includes

if args.omits is not None:
    OMITS=args.omits

if args.special_char is not None:
    MATCHING=0
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
        elif value.endswith('.txt'):
            with open(f'./lists/{value}', 'r') as file:
                lines = file.readlines() 
                perms[thiskey]= [line.strip() for line in lines]
                perms[thiskey] = [line for line in perms[thiskey] if line != '']
        else:
            perms[thiskey] = list(value)

    keys = list(perms.keys())
    iterables = list(perms.values())

    result_product = list(product(*iterables))

    for combination in result_product:
        result_dict = dict(zip(keys, combination))

        newHeaders = {key: replace_substring(value, result_dict) for key, value in HEADERS.items()}
        newParams = {key: replace_substring(value, result_dict) for key, value in PARAMS.items()}
        newCookies = {key: replace_substring(value, result_dict) for key, value in COOKIES.items()}
        newData = {key: replace_substring(value, result_dict) for key, value in DATA.items()}

        if METHOD == 'POST':
            newHeaders['content-type'] = 'application/json'
            newData = json.dumps(newData)

        request = httpx.Request(METHOD,url=TARGET,headers=newHeaders,params=newParams,cookies=newCookies,data=newData)
        
        try:
            response = client.send(request)
            print_based_on_verbousity(LEVEL,response,request)
            if OMITS:
                if OMITS not in response.content.decode():
                    save_found_match(request,response)
                    MATCHING+=1
            if INCLUDES:
                if INCLUDES in response.content.decode():
                    save_found_match(request,response)
                    MATCHING+=1

            if WAIT is not None:
                sleep(WAIT)
        except ConnectionError:
            print(colored("CONNECTION ERROR!",'red'))
        
    if MATCHING > 0:
        print(f"GOOD NEWS FOUND {MATCHING} MATCHINGS")
    client.close()

else:
    client = httpx.Client()

    try:
        request = httpx.Request(method=METHOD,url=TARGET,headers=HEADERS,params=PARAMS,cookies=COOKIES,data=DATA)
        response = client.send(request)
        print_based_on_verbousity(LEVEL,response,request)

    except httpx.ConnectError:
        print(colored("CONNECTION ERROR!",'red'))

    client.close()
