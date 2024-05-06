# IntruderX - An alternative to Burp's intruder


![IntruderX menu](https://github.com/Giardi77/IntruderX/blob/main/IntruderX%20Tutorial%20images/LOGO.png?raw=true)

I got really annoyed by the slowness and limitations on burp suite community's intruder, so i decided to try and make my version of it.


## Setup

- git clone https://github.com/Giardi77/IntruderX.git
- cd IntruderX
- pip install -r requirements.txt

## How does it work

I've tried my best to make it super easy and comprehesible, the main feature of this tool is that you can easily add more stuff.

The easiest thing you can do it's sending a request with -m (method) and -t (target) switches


![simple req](https://github.com/Giardi77/IntruderX/blob/main/IntruderX%20Tutorial%20images/-m%20switch.png)


this will send a simple get request to the TARGET.

As i mentioned previously you can add more stuff like parameters, headers or application/x-www-form-urlencoded data in the body (JSON for POST requests).
Let's add all of that.


![custom req](https://github.com/Giardi77/IntruderX/blob/main/IntruderX%20Tutorial%20images/Custom%20params%2C%20headers%20and%20body.png?raw=true)


Now the fun part.
You can use the -sc switch (--special_char) followed by a key-value pair where key is the special char and the value is the list of objects to iterate by replacing his special char.

Special char can be ranges of numbers like "range(10)" (from 0 to 9) or list of char like "abcde" or list of lines of a file .txt (just give the right path to it).
special chars can be used anywhere except for the target.


![](https://github.com/Giardi77/IntruderX/blob/main/IntruderX%20Tutorial%20images/Combinations%20first.png?raw=true)


to this last combination


![](https://github.com/Giardi77/IntruderX/blob/main/IntruderX%20Tutorial%20images/Combinantions%20last.png?raw=true)


you can also use the --inclues or --omits switch to check i a certain string in present or not in a response, if the condition is reached the request it get's saved in a file (under outputs dir). 


![](https://github.com/Giardi77/IntruderX/blob/main/IntruderX%20Tutorial%20images/--includes%20switch.png?raw=true)


![](https://github.com/Giardi77/IntruderX/blob/main/IntruderX%20Tutorial%20images/Found%20matches.png?raw=true)
