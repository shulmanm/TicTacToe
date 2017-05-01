''' File to create a local server for Tic-Tac-Toe. Best way to run: in terminal,
navigate to this file and  call "python3 Server.py" You should see 
"STARTING SERVER ON LOCALHOST Host:Port (localhost:8000):".
You can choose the server attributes or just press enter for a default of localhost:8000.'''

import PodSixNet.Channel
import PodSixNet.Server
from time import sleep
from enum import Enum

# enum for turns
class Turn(Enum):
	PLAYER0 = 0
	PLAYER1 = 1


class ClientChannel(PodSixNet.Channel.Channel):

	# receive data
	def Network(self, data):
		print(data)

	# get all of the data from the dictionary
	def Network_place(self, data):
		#x of placed piece
		x = data["x"]
		#y of placed piece
		y = data["y"]
		#player number (1 or 0)
		num = data["num"]
		#id of game given by server at start of game
		self.gameid = data["gameid"]
		#tells server to place line
		self._server.placePiece(x, y, data, self.gameid, num)

	# receive close
	def Close(self):
		self._server.close(self.gameid)

class TicServer(PodSixNet.Server.Server):
 
	channelClass = ClientChannel

	def __init__(self, *args, **kwargs):
		# call PodSixNet init, pass args through
		PodSixNet.Server.Server.__init__(self, *args, **kwargs)
		self.games = []
		self.queue = None
		# keeps track of existing games
		self.currentIndex = 0

	def Connected(self, channel, addr):
		print('new connection:', channel)
		#check if theres a game in queue, else make one, connect new clients to it
		if self.queue == None:
			self.currentIndex += 1
			channel.gameid = self.currentIndex
			self.queue = Game(channel, self.currentIndex)
		else:
			channel.gameid = self.currentIndex
			self.queue.player1 = channel
			self.queue.player0.Send({"action": "startgame","player": 0, "gameid": self.queue.gameid})
			self.queue.player1.Send({"action": "startgame","player": 1, "gameid": self.queue.gameid})
			self.games.append(self.queue)
			self.queue = None

	# find game with right gameid then placeLine
	def placePiece(self, x, y, data, gameid, num):
		# find game with correct gameid
		game = [a for a in self.games if a.gameid == gameid]
		game[0].placePiece(x, y, data, num)

	# close game for both if one closes
	def close(self, gameid):
		try:
			game = [a for a in self.games if a.gameid == gameid][0]
			game.player0.Send({"action":"close"})
			game.player1.Send({"action":"close"})
		except:
			pass


# server Game state
class Game:

	def __init__(self, player0, currentIndex):
		# whose turn (1 or 0)
		self.turn = Turn.PLAYER0
		#owner map
		self.owner = [[False for x in range(3)] for y in range(3)]
		# Seven lines in each direction to make a six by six grid.
		self.board = [[False for x in range(3)] for y in range(3)]
		#initialize the players including the one who started the game
		self.player0 = player0
		self.player1 = None
		#gameid of game
		self.gameid = currentIndex

	# if you can place piece, do so for for both clients and send data
	def placePiece(self, x, y, data, num):
		# make sure it's their turn
		if num == self.turn.value:

			if self.turn == Turn.PLAYER1:
				self.player1.Send({"action": "win", "x": x, "y": y})
				self.player0.Send({"action": "lose", "x": x, "y": y})
			else:
				self.player0.Send({"action": "win", "x": x, "y": y})
				self.player1.Send({"action": "lose", "x": x, "y": y})

			self.turn = Turn.PLAYER0 if self.turn.value else Turn.PLAYER1
			self.owner[y][x] = num
			self.player1.Send({"action": "yourturn", "torf": True if self.turn == Turn.PLAYER1 else False})
			self.player0.Send({"action": "yourturn", "torf": True if self.turn == Turn.PLAYER0 else False})

			#place line in game
			self.board[y][x] = True
			#send data and turn data to each player
			self.player0.Send(data)
			self.player1.Send(data)

print("STARTING SERVER ON LOCALHOST")
# try:
address = input("Host:Port (localhost:8000): ")
if not address:
	host, port="localhost", 8000
else:
	host,port=address.split(":")
ticServe = TicServer(localaddr=(host, int(port)))

while True:
	ticServe.Pump()
	sleep(0.01)








