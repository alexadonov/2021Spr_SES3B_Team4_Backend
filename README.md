# CrisisMgmt - UTS Software Studio 3A 2020 - Group 4

CrisisMgmt is a Flask API for handling user authentication and app functionality.

## Dev Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all dependencies required for development using the `requirements.txt` file in the project's root folder:

```bash
pip install -r requirements.txt
```

## Running the Chatbot locally

Java 8 is needed to run the chatbot. On Linux you can install it by running
```bash
    sudo apt install openjdk-8-jdk
```

If using Linux, install `sox` by running this command
```bash
    sudo apt install sox
```
If using Mac
```bash
    brew install sox
```
If using Windows, Download it [here](https://sourceforge.net/projects/sox/files/sox/)

1. You will need download all the follwoing libraries using your terminal

(import nltk
import numpy
import tensorflow
import random
import json
import tflearn
import pickle)

Once following libraries have been downlaoded, all errors should go away. 

2. I am currently running my chatbot on python 3.9.6 64-bit (you might need to do the same)
3. Following will the steps will run the chatbot: 

 cd crisismgmt-api
 crisismgmt
 python chatbot.py

7. After inputting the following above commands into the terminal chatbot now should be running and you shoudl be able to interact with it. 

## Running the API locally
Execute the following bash command from the project root folder to start the API server on `localhost:5000/api/`. Note you need to have Python and all dependencies installed first.
```bash
python appserver.py
```

## Making database migrations using SQLAlchemy ORM
Create an initial migration file to translate the classes in models.py to SQL that will generate corresponding tables
```bash
python manage.py db migrate
```
Run the migration to upgrade the database with the tables described in the prior step
```bash
python manage.py db upgrade
```

## Training and running the chatbot
CD to the 'crisismgmt-api/crisismgmt' folder
If you want to retrain the chatbot AI after it has been trained, delete 'pickle.data' and the three 'model.tflearn' files
If you want to run it without retraining, keep the files
run
```bash
python .\chatbot.py
```

### Modifying the patterns the AI learns from
Add intents into the 'intents.json' file
Patterns added in the intents.json file must have no punctuation or capitalisation as this will make it more confusing for the AI
Everything is converted to lowercase for the input from the user.
Responses is what the AI says back to the user, and therefore you can include correct grammer here for the user to read
After making modifications delete the pickle.data file - chatbot AI will need retraining and will need to reread the intents file
You can then run and train the chatbot AI

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
