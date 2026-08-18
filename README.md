Things to do when dowload the code:
I: Install all the nesesary libraries and a MUST is to have a python not bigger than version: 3.13.14. 
Beacuse with updated python pygame is not working :)
Open the project, go to the Terminal and Run: 
	pip install uvicorn fastapi requests python-dotenv sqlalchemy
	python reset_and_seed.py 
	python -m uvicorn api:app --reload --port 8000
II:
Start the game by running the main_adventure.py file

Or just open the Docker Desktop app. Open CMD or terminal. Go to the folder of this game. Run this command: python run_all.py  
If you have 3.14 on your PC, this should be run on somwthing lower. So, if you don't have lower version, download that and then run this command in the terminal: py -3.version run_all.py

If there are some errors after pulling the project. Please try to solve by closing the project, then delete the folder .idea,reopen the project again 
This may occur especcially if you had the pervios version. 
