# IntruderX - An alternative to Burp's intruder

I got really annoyed by the slowness and limitations on burp suite community's intruder, so i decided to try and make my version of it.

## Setup

- git clone https://github.com/Giardi77/IntruderX.git
- cd IntruderX
- pip install -r requirements.txt

## How does it work

![IntruderX menu](https://github.com/Giardi77/IntruderX/blob/main/Screenshot%202024-03-01%20alle%2011.59.15.png?raw=true)

I've tried my best to make it super easy and comprehesible, the main feature of this tool is that you can easily add more stuff.

The easiest thing you can do it's sending a request with: 

python3 IntruderX.py -t http://localhost/ -m GET

this will send a simple get request to the TARGET (-t),as i mentioned previously you can add more stuff like parameters, headers or application/x-www-form-urlencoded data in the body (JSON for POST requests).
Let's add all of that.

python3 intruderx.py -t http://localhost/ -m GET --params param1:example,param2:example --headers h1:example --data a:1 -v 4

Request will look like:

GET /?param1=example&param2=example<br />
host: localhost:3000<br />
h1: example<br />
content-length: 3<br />
content-type: application/x-www-form-urlencoded<br />

a=1<br />

Now the fun part.
You can use the -sc switch (--special_char) followed by a key-value pair where key is the special char and the value is the list of objects to iterate by replacing his special char.
Special char can be ranges of numbers like "range(10)" (from 0 to 9) or list of char like "abcde" or list of lines of a file .txt (must put the file on lists folder).
special chars can be used anywhere except for the target.

example:

python3 intruderx.py -t http://localhost:3000/ -m POST --headers exapleheader:$ --data a:# -sc $:range(3),#:abc -v 4

this will send from: 

POST http://localhost:3000/<br />
host: localhost:3000<br />
exapleheader: 0       <----<br />
content-type: application/json<br />
content-length: 10<br />

{"a": "a"}  <--- <br />


to:


POST http://localhost:3000/<br />
host: localhost:3000<br />
exapleheader: 2       <----<br />
content-type: application/json<br />
content-length: 10<br />

{"a": "c"}     <----<br />
