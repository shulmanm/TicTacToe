README Tic-Tac-Toe
Written by Matthew Shulman
Python3

First install the dependencies in terminal with "pip3 install -r requirements.txt"

Navigate to the unzipped folder in terminal and type "./run.sh” to get everything set up easily - if you see “permission denied” run “chmod 755 run.sh” and try “./run.sh” again. If you are still having issues, they might be from it trying to start the server with that name again, even though tis running. If it’s a problem you can try using the commands individually to start the server and then the clients - see below


Server.py is a file to create a local server for Tic-Tac-Toe.

Best way to run: 
In terminal, navigate to this file and  call "python3 Server.py" You should see 
"STARTING SERVER ON LOCALHOST Host:Port (localhost:8000):".
You can choose the server attributes or just press enter for a default of localhost:8000.'''



TicTacToe_client.py is a file to create a TicTacToe client.
Best way to run:

Start the server (see Server.py file), then open 2 more terminal windows.
In each, type "python3 TicTacToe_client.py".
You should see "Address of Server: ", type server name here. likely (localhost:xxxx)
If done in both windows, you should be able to play the game.
