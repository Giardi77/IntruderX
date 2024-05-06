#! /user/bin/python3
from itertools import product
from time import sleep
import argparse
import json
import sys
import httpx
from termcolor import colored
import os
import multiprocessing
import random

DATA=None
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
CODES={} # -> just for level 1 verbosity 
STATUS=None
PROCESSES=1
SAVE=False
LOADEDUSERAGENTS=[]


parser = argparse.ArgumentParser(prog=LOGO,
                    description='\t𝐀𝐥𝐭𝐞𝐫𝐧𝐚𝐭𝐢𝐯𝐞 𝐭𝐨 𝐁𝐮𝐫𝐩\'𝐬 𝐈𝐧𝐭𝐫𝐮𝐝𝐞𝐫 𝐛𝐮𝐢𝐥𝐭 𝐨𝐧 𝐭𝐨𝐩 𝐨𝐟 𝐡𝐭𝐭𝐩𝐱',)

parser.add_argument('-t','--target', required=True, help='Set the target (-u https://localhost:1234)')
parser.add_argument('-m','--method', help='set GET or POST request')
parser.add_argument('-H','--headers', help='Headers (key:value,key:value...)')
parser.add_argument('--params', help='GET request parametes (key:value,key:value...)')
parser.add_argument('-sc','--special_char', help='special char and file or list')
parser.add_argument('--cookies', help='add cookies (key:value,key:value...')
parser.add_argument('-v','--verbouse', help='set verbousity: 1 to 4 (default 3)')
parser.add_argument('-d','--data', help='Add data to request body')
parser.add_argument('-w','--wait', help='delay in seconds after sending a request')
parser.add_argument('--includes', help='check if a string is included')
parser.add_argument('--omits', help='check if a string is omitted',)
parser.add_argument('-s','--status', help='check for a stats code in order to save the req/res in the file')
parser.add_argument('-pr','--processes', help='divide the requests in different processes to achieve more speed, you can use \'max\' to use the maximum available on your system')
parser.add_argument('--save',action='store_true', help='save the requests the responses that meet the requirements from switches like --omits, --includes and --status')
parser.add_argument('--random','--random-user-agent', action='store_true', help='use a random user agent from file \'user-agents.txt\'')

args = parser.parse_args()


def dump_queue(queue) -> list:
    """
    Empties all pending items in a queue and returns them in a list.
    """
    result = []

    for i in iter(queue.get, 'STOP'):
        result.append(i)
    return result

def combos(chars)-> list:
    """
    returns all the combinations in a list from the input given on the argument
    """
    char = stringtodict(chars)
    perms = {}

    for value in char.values():
        thiskey = [key for key, thisvalue in char.items() if thisvalue == value][0]
        if value.startswith('range(') :
            RANGES = eval(value)
            perms[thiskey] = []
            for n in RANGES:
                perms[thiskey].append(n)
        elif value.endswith('.txt'):
            with open(f'{value}', 'r') as file:
                lines = file.readlines()
                perms[thiskey]= [line.strip() for line in lines]
                perms[thiskey] = [line for line in perms[thiskey] if line != '']
        else:
            perms[thiskey] = list(value)

    tot_keys = list(perms.keys())
    iterables = list(perms.values())

    result = list(product(*iterables))

    return result,tot_keys

def stringtodict(input_string)-> dict:
    """
    Converts a string of comma-separated (key:value) pairs into a dictionary.

    Example:
    >>> x = stringtodict("name:John, age:30, city:New York")
    x is -> {'name': 'John', 'age': '30', 'city': 'New York'}
    """
    pairs = input_string.split(',')
    result_dict = {}
    for pair in pairs:
        key, value = pair.split(':',1)
        result_dict[key.strip()] = value.strip()
    return result_dict

def replace_substring(original_str, replace_dict)-> str:
    """
    Replaces specific part from a string based on a dictionary of replacements.

    Example:
    >>> replace_substring("Hello, [is] [name]!", {"[name]": "John", "[is]":"Mr."})
    'Hello, Mr. John!'
    """
    for key, value in replace_dict.items():
        original_str = original_str.replace(key, str(value))
    return original_str

def print_based_on_verbousity(level,res,req) -> None:
    """
    Just print based-off verbousity level (-v switch)
    level 1: only status codes
    level 2: status code & response headers
    level 3, code,response headers & body
    level 4: full request and response
    """

    if res.status_code in CODES:
        CODES[res.status_code] += 1
    else:
        CODES[res.status_code] = 1

    if level == '1':
        sys.stdout.write('\r' + ' ' * 50 + '\r')
        sys.stdout.flush()
        for key, value in CODES.items():
            print(f"[{key}] x {value}\t",end='',flush=True)

    elif level == '2':
        print(req.method+' '+str(req.url),end='\n')
        if res.status_code == 200:
            print(colored(f'[{str(res.status_code)}]\n','green',))
        else:
            print(colored(f'[{str(res.status_code)}]\n','red',))
        for name, value in res.headers.items():
            print(f"{name}: {value}")
        print('\n<+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+>\n')

    elif level == '3':
        print(req.method+' '+str(req.url),end='\n')
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

def save_found_match(req,res)-> None:
    """
    Just takes request and responses and saves them on a file named as the url or the target
    """
    if TARGET.startswith('http://'):
        url =  TARGET[len('http://'):]
    elif TARGET.startswith('https://'):
        url = TARGET[len('https://'):]

    url = url.replace("/","|")
    
    filename= f'./outputs/{url}.txt'

    with open(filename, 'a') as file:
        file.write(str(req.url) + '\n\n\n')
        try:
            if req.params:
                file.write(f'{req.params}\n')
        except AttributeError:
            pass
        for name, value in req.headers.items():
            file.write(f"{name}: {value}\n")
        try:
            if req.read() is not None:
                file.write(f'\n{req.read().decode()}\n')
        except AttributeError:
            print('error')
        file.write(f'[{str(res.status_code)}]\n')
        for name, value in res.headers.items():
            file.write(f"{name}: {value}\n")
        file.write('\n')
        file.write(res.content.decode())
        file.write('\n<+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+><+>\n')

def statustolist(s) -> list:
    """
    Gets a comma separated list of values as single string and returns a List of Strings
    """
    StatusList= s.split(',')
    return StatusList

def printer(queue) -> None:
    '''
    Reads from the Queue and calls print_based_on_verbosity for every item
    '''

    try:
        while True:
            if not queue.empty():
                req_res_packed = queue.get()
                
                if OMITS or INCLUDES or STATUS:
                    if OMITS:
                        if OMITS not in req_res_packed[0].content.decode():
                            if STATUS :
                                if req_res_packed[0].status_code in STATUS:
                                    print_based_on_verbousity(LEVEL,req_res_packed[0],req_res_packed[1])
                            else:
                                print_based_on_verbousity(LEVEL,req_res_packed[0],req_res_packed[1])
                    if INCLUDES:
                        if INCLUDES in req_res_packed[0].content.decode():
                            print_based_on_verbousity(LEVEL,req_res_packed[0],req_res_packed[1])
                            if STATUS :
                                if req_res_packed[0].status_code in STATUS:
                                    print_based_on_verbousity(LEVEL,req_res_packed[0],req_res_packed[1])
                            else:
                                print_based_on_verbousity(LEVEL,req_res_packed[0],req_res_packed[1])
                    if INCLUDES is None and OMITS is None and STATUS:
                        if str(req_res_packed[0].status_code) in STATUS:
                            print_based_on_verbousity(LEVEL,req_res_packed[0],req_res_packed[1])
                else:
                    print_based_on_verbousity(LEVEL,req_res_packed[0],req_res_packed[1])

    except KeyboardInterrupt:
        sys.exit(0)

def request_from_combinations(result_product,keys,req_queue,matching_queue) -> None:
    matching = 0
    client = httpx.Client()

    for combination in result_product:
            result_dict = dict(zip(keys, combination))

            if args.random:
                HEADERS['user-agent'] = random.choice(LOADEDUSERAGENTS)

            newHeaders = {key: replace_substring(value, result_dict) for key, value in HEADERS.items()}
            newParams = {key: replace_substring(value, result_dict) for key, value in PARAMS.items()}
            newCookies = {key: replace_substring(value, result_dict) for key, value in COOKIES.items()}

            if METHOD == 'POST':
                newHeaders['content-type'] = 'application/json'

            if DATA:
                newData = {key: replace_substring(value, result_dict) for key, value in DATA.items()}
                newData = json.dumps(newData)
                request = httpx.Request(METHOD,url=TARGET,headers=newHeaders,params=newParams,cookies=newCookies,data=newData)
            else:
                request = httpx.Request(METHOD,url=TARGET,headers=newHeaders,params=newParams,cookies=newCookies)

            try:
                response = client.send(request)
                req_queue.put([response,request])
                
                if OMITS:
                    if OMITS not in response.content.decode():
                        if STATUS :
                            if response.status_code in STATUS:
                                if SAVE:
                                    save_found_match(request,response)
                                matching+=1
                        else:
                            if SAVE:
                                save_found_match(request,response)
                            matching+=1
                if INCLUDES:
                    if INCLUDES in response.content.decode():
                        if SAVE:
                            save_found_match(request,response)
                        matching+=1
                        if STATUS :
                            if response.status_code in STATUS:
                                if SAVE:
                                    save_found_match(request,response)
                                matching+=1
                        else:
                            if SAVE:
                                save_found_match(request,response)
                            matching+=1
                if INCLUDES is None and OMITS is None and STATUS:
                    if str(response.status_code) in STATUS:
                        if SAVE:
                            save_found_match(request,response)
                        matching+=1

                if WAIT is not None:
                    sleep(WAIT)

            except ConnectionError:
                print(colored("CONNECTION ERROR!",'red'))
                sys.exit(1)
            except KeyboardInterrupt:
                sys.exit(0)
    
    client.close()
    matching_queue.put(matching)

def divide_requests(result_product) -> list:
    result_product_sliced = list()
    n_comb = len(result_product)
    to_each_thread = [0] * PROCESSES
    chunk = int(n_comb // PROCESSES)

    for i in range(PROCESSES):
        to_each_thread[i] += chunk
        n_comb -= chunk

    while n_comb > 0:
        for x in range(PROCESSES):
            to_each_thread[x] += 1
            n_comb -= 1
            if n_comb <= 0:
                break

    index = 0

    for n in range(PROCESSES):
        until = index + to_each_thread[n]
        to_append = result_product[index:until]
        result_product_sliced.append(to_append)
        index = index + to_each_thread[n]

    return result_product_sliced

def handleProcesses(result_product,keys) -> list:
    result_product_sliced = divide_requests(result_product)
    req_queue = multiprocessing.Queue()
    matching_queue = multiprocessing.Queue()
    
    printerprocess = multiprocessing.Process(target=printer,args=(req_queue,))
    printerprocess.start()

    senders = list()

    for slice in result_product_sliced:
        sender = multiprocessing.Process(target=request_from_combinations, args=(slice, keys,req_queue,matching_queue,))
        sender.start()
        senders.append(sender)

    for sender in senders:
        sender.join()

    matching_queue.put('STOP')

    printerprocess.terminate()

    return sum(dump_queue(matching_queue))

#region ARGS TO VARS
if args.target is None:
    print("\n Set a target with -t switch (-t https://127.0.0.1/)")
    sys.exit(2)

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
    if 'user-agent' not in [k.lower() for k in HEADERS.keys()] and not args.random:
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

if args.status is not None:
    STATUS = statustolist(args.status)

if args.special_char is None:
    print('\n Consider to use curl if you want to make just 1 request. \n')
    sys.exit("coglione")

if args.processes != 1:
    if args.processes == "max" or args.processes == "MAX":
        PROCESSES = os.cpu_count()
    else:
        PROCESSES = int(args.processes)

if args.save:
    SAVE = args.save

if args.random:
    with open('./user-agents.txt', 'r') as file:
        for line in file:
            LOADEDUSERAGENTS.append(str(line.strip()))


    

#endregion

def main():
    try: 
        result_product,keys = combos(args.special_char)
        MATCHING = handleProcesses(result_product,keys)

        if MATCHING > 0: print(f"\n\nGOOD NEWS FOUND {MATCHING} MATCHINGS\n")
        else: print("\nNO MATCHINGS\n")

        sys.exit(0)

    except KeyboardInterrupt:
        print("\r\n\n\nExit ...")
        sys.exit()

if __name__ == "__main__":
    print(parser.prog + '\n' + parser.description + '\n' + '\n')
    main()