CMPUT 391
Project Unit 1
Owner: Noah Kryzanowsi

Instructions

1. Load all of the files in from the git repository, you only truly need project.py (the rest of the files were for testing purposes)

2. In the directory that you have downloaded the project.py file into, ensure that the OSM data is in the same directory

3. Open up the file project.py and navigate to line 48 and make sure that the variable 'inputFile' is the same as the OSM data file that is being used

4. You can now run the command below:
python3 project.py

5. This will parse through the XML, which takes an average of 1 minute and 45 seconds
   This will also insert all of the required data into the SQL database. This takes about 10 minutes, due to the amount of data

6. Everything should be in the database now, and all of the constraints should be enforced