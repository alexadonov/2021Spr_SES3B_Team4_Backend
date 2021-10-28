# CrisisMgmt - UTS Software Studio 3A 2020 - Group 4

CrisisMgmt is a Flask API for handling user authentication and app functionality.

## Dev Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all dependencies required for development using the `requirements.txt` file in the project's root folder:

If using Linux, install `sox` by running this command
```bash
    sudo apt install sox
```
If using Mac
```bash
    brew install sox
```
If using Windows, Download it [here](https://sourceforge.net/projects/sox/files/sox/)

```bash
    pip install -r requirements.txt
```
## If running Windows

Download the Windows version of OpenJDK from [here](https://adoptopenjdk.net/upstream.html?variant=openjdk8&jvmVariant=hotspot)
- Make sure you extract it to a directory where its path has NO spaces. e.g. C:\Users\User\Desktop and NOT C:\Program Files...
- Add the JAVA_HOME environment variable to the root directory of the java extraction (C:\Users\User\Desktop\OpenJDK\openjdk-8u312-b07)
- Add the bin directory to PATH variable (C:\Users\User\Desktop\OpenJDK\openjdk-8u312-b07\bin)

Download HADOOP [here](https://downloads.apache.org/hadoop/common/hadoop-3.3.1/hadoop-3.3.1.tar.gz)
- using 7-zip, right click extract here to get a .tar
- right click extract here again to get the directory
- same with Java, do not extract it to a path that contains spaces. Use (C:\Users\User\Desktop\Downloads\)
- Add the HADOOP_HOME environment variable (C:\Users\User\Downloads\hadoop-3.3.1)

Once environment variables are set up, restart you PC

## Running the Chatbot locally

```bash
    cd crisismgmt-api
    crisismgmt
    python chatbot.py
```

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
