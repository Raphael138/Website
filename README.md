# First Website

I made this website during April and May of 2021. There templates files are the html files for the website and the css formating file is in the static folder. The website was coded using multiple libraries, flask, json and requests. The main file that compiles all the .html files together and makes the website is creatingWebsite.py. The other .py file, runQueries.py, can be imported in the cmd with the following lines:
```python```
Then:
```python
from runQueries import *
```
Then you should be able to make queries in the database of the website without having to use SQL, but rather the functions written in python in the runQueries.py file(ie. printUserInfo(), deletUser(usernm)).
