# First Website

I began making this website during April and May of 2021 and added some during December 2021/ Januray 2022. There templates files are the html files for the website and the css formating file is in the static folder. The website was coded using multiple libraries: flask, json and requests. The main file that compiles all the .html files together and makes the website is creatingWebsite.py. In order to go to the website, you need to first open the CMD and enter:
```
python creatingWebsite.py
```
Then go to a browser and enter 
```
http://127.0.0.1:5000/
```
The other .py file, runQueries.py, can be imported in the cmd with the following lines:

```python
python
```

Then:

```python
from runQueries import *
```
Then you should be able to make queries in the database of the website without having to use SQL, but rather the functions written in python in the runQueries.py file(ie. printUserInfo(), deletUser(usernm)).

The website includes a database, with ability to sign in, sign up and remove your account. There is also a homepage. I also added the ability to text between user. Just like you can do queries for the user database, you can also do the same for the texting feature. Instead of importing `runQueries`, import `creatingChatDataframe`. Finally, I also added a weather page which uses `geopy` and OpenWeather.
