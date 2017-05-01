'''File to create attributes Tic-Tac-Toe client. Best way to run: 
Start the server (see Server.py file), then open 2 more terminal windows.
In each, type "python3 TicTacToe_client.py".
You should see "Address of Server: ", type server name here. likely (localhost:xxxx)
If done in both windows, you should be able to play the game.'''

import pygame
import math
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep



# create Tic-Tac-Toe Game, extends ConnectionListener
class TicGame(ConnectionListener):
		
	def __init__(self):

		# init pygame, font, width, height
		pygame.init()
		pygame.font.init()
		self.width, self.height = 400, 500
		# init the screen, title
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption("Tic-Tac-Toe")
		# init pygame clock
		self.clock = pygame.time.Clock()
		#init the graphics
		self.initGraphics()
		# init turn
		self.turn = True
		# init board, 2D array of bool
		self.board = [[False for x in range(3)] for y in range(3)]
		# init ownerboard, same 2D array but of 0s
		self.owner = [[0 for x in range(3)] for y in range(3)]
		# init win states
		self.didiwin = False
		self.didilose = False

		# get server address, default: localhost:8000, connect to it
		address = input("Address of Server: ")
		try:
			if not address:
				host, port = "localhost", 8000
			else:
				host,port = address.split(":")
			self.Connect((host, int(port)))
		except:
			print("Error Connecting to Server")
			print("Usage:", "host:port")
			print("e.g.", "localhost:31425")
			print("Default:", "localhost:8000")
			exit()
		print("Boxes client started")

		# set running state to False initially
		self.running = False

		# keep checking if it should start
		while not self.running:
			self.Pump()
			connection.Pump()
			sleep(0.01)

		# determine attributes from player, if 0, player0, X, else player1, O
		if self.num == 0:
			self.turn = True
			self.marker = self.xplayer
			self.othermarker = self.oplayer
		else:
			self.turn = False
			self.marker = self.oplayer
			self.othermarker = self.xplayer

	# draws the grid
	def drawBoard(self):
		self.screen.blit(self.background, [0, 0])
	
	# draws the HUD			
	def drawHUD(self):
		#draw the background for the bottom:
		self.screen.blit(self.score_panel, [0, 400])
		#create font
		myfont = pygame.font.SysFont(None, 32)
		#create text surface
		label = myfont.render("Your Turn:", 1, (255,255,255))
		#draw surface
		self.screen.blit(label, (10, 410))
		self.screen.blit(self.greenindicator if self.turn else self.redindicator, (130, 416))

	# updates the game state
	def update(self):
		#check win
		if self.winCheck(self.owner) == self.num:
			self.didiwin = True
			return 1
		#check lose
		if self.loseCheck(self.owner) == self.num:
			self.didilose = True
			return 1
		# check tie
		if self.isTie(self.owner):
			return 1

		# make the game 60 fps
		self.clock.tick(60)
		connection.Pump()
		self.Pump()

		#clear the screen
		self.screen.fill(0)
		# redraw everything
		self.drawBoard()
		self.drawHUD()
		self.drawOwnermap()

		# quit if quit was pressed
		for event in pygame.event.get():
			#quit if the quit button was pressed
			if event.type == pygame.QUIT:
				exit()
	 
		# get mouse position
		mouse = pygame.mouse.get_pos()
		xpos = int(math.ceil(mouse[0] / 133.4))
		ypos = int(math.ceil(mouse[1] / 133.4))
		ypos = ypos - 1 if mouse[1] - ypos * 133.4 < 0 else ypos
		xpos = xpos - 1 if mouse[0] - xpos * 133.4 < 0 else xpos

		board = self.board
		# set is out of bounds
		isoutofbounds = False
		 
		# try to hover a piece if its not out of bounds
		try: 
			if not board[ypos][xpos]:
				self.screen.blit(self.marker, [xpos * 133.4 + 20, ypos * 133.4 + 20])
		except:
			isoutofbounds = True
			pass

		# check if a piece is already placed there
		if not isoutofbounds:
			alreadyplaced = board[ypos][xpos]
		else:
			alreadyplaced = False

		# place a piece on mouse press if its not already placed or out of bounds and it's your turn
		if pygame.mouse.get_pressed()[0] and not alreadyplaced and not isoutofbounds and self.turn:
		
			self.board[ypos][xpos] = True
			connection.Send({"action": "place", "x": xpos, "y": ypos, "num": self.num, "gameid": self.gameid})
		
		#update display
		pygame.display.flip()


	# init graphics
	def initGraphics(self):
		self.background = pygame.transform.scale(pygame.image.load("background.png"), (int(self.width), int(self.width)))
		self.redindicator = pygame.image.load("redindicator.png")
		self.greenindicator = pygame.image.load("greenindicator.png")
		self.xplayer = pygame.transform.scale(pygame.image.load("x.png"), (int(self.width *.7 *.3), int(self.height * .7 *.3)))
		self.oplayer = pygame.transform.scale(pygame.image.load("o.png"), (int(self.width *.7 *.3), int(self.height * .7 *.3)))
		self.winningscreen = pygame.transform.scale(pygame.image.load("youwin.png"), (int(self.width), int(self.height)))
		self.gameover = pygame.transform.scale(pygame.image.load("gameover.png"), (int(self.width), int(self.height)))
		self.tie = pygame.transform.scale(pygame.image.load("tie.png"), (int(self.width), int(self.height)))
		self.score_panel=pygame.image.load("score_panel.png")

	# draws owner 2D array
	# draw marker at "win", othermarker at "lose", nothing at 0
	def drawOwnermap(self):
		for y in range(3):
			for x in range(3):
				if self.owner[y][x] != 0:
					if self.owner[y][x] == "win":
						self.screen.blit(self.marker, (x * 133.4 + 20, y * 133.4 + 20))
					if self.owner[y][x] == "lose":
						self.screen.blit(self.othermarker, (x * 133.4 + 20, y * 133.4 + 20))

	# check if there's a win, return winner num, 2 if none
	def winCheck(self, board):

		#check if previous move was on vertical line and caused a win
		if board[0][0] == "win" and board[1][0] == "win" and board[2][0] == "win":
			return self.num
		if board[0][1] == "win" and board[1][1] == "win" and board[2][1] == "win":
			return self.num
		if board[0][2] == "win" and board[1][2] == "win" and board[2][2] == "win":
			return self.num

		#check if previous move was on horizontal line and caused a win
		if board[0][0] == "win" and board[0][1] == "win" and board[0][2] == "win":
			return self.num
		if board[1][0] == "win" and board[1][1] == "win" and board[1][2] == "win":
			return self.num
		if board[2][0] == "win" and board[2][1] == "win" and board[2][2] == "win":
			return self.num

		#check if previous move was on the main diagonal and caused a win
		if board[0][0] == "win" and board[1][1] == "win" and board[2][2] == "win":
			return self.num
		#check if previous move was on the secondary diagonal and caused a win
		if board[0][2] == "win" and board[1][1] == "win" and board[2][0] == "win":
			return self.num

		return 2

	def loseCheck(self, board):

		#check if previous move was on vertical line and caused a win
		if board[0][0] == "lose" and board[1][0] == "lose" and board[2][0] == "lose":
			return self.num
		if board[0][1] == "lose" and board[1][1] == "lose" and board[2][1] == "lose":
			return self.num
		if board[0][2] == "lose" and board[1][2] == "lose" and board[2][2] == "lose":
			return self.num

		#check if previous move was on horizontal line and caused a win
		if board[0][0] == "lose" and board[0][1] == "lose" and board[0][2] == "lose":
			return self.num
		if board[1][0] == "lose" and board[1][1] == "lose" and board[1][2] == "lose":
			return self.num
		if board[2][0] == "lose" and board[2][1] == "lose" and board[2][2] == "lose":
			return self.num

		#check if previous move was on the main diagonal and caused a win
		if board[0][0] == "lose" and board[1][1] == "lose" and board[2][2] == "lose":
			return self.num
		#check if previous move was on the secondary diagonal and caused a win
		if board[0][2] == "lose" and board[1][1] == "lose" and board[2][0] == "lose":
			return self.num

		return 2

	# check if there's tie, if any value is still 0, there's not a tie
	# note: its possible for the board to be filled and there be a win but thats checked in update function
	def isTie(self, board):
		for y in range(3):
			for x in range(3):
				if board[y][x] == 0:
					return False
		return True
		
	# display correct screens to each player when the gane is finished
	def finished(self):
		if self.didiwin:
			self.screen.blit(self.winningscreen, (0,0))
		elif self.isTie(self.owner) and not self.didilose:
			self.screen.blit(self.tie, (0,0))
		else:
			self.screen.blit(self.gameover, (0,0))

		while 1:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					exit()
			pygame.display.flip()

	#receive exit
	def Network_close(self, data):
		exit()

	#receive turn attributes
	def Network_yourturn(self, data):
		#torf = short for true or false
		self.turn = data["torf"]

	#receive startgame attributes
	def Network_startgame(self, data):
		self.running = True
		self.num = data["player"]
		self.gameid = data["gameid"]

	#receive place attributes
	def Network_place(self, data):
		x = data["x"]
		y = data["y"]
		self.board[y][x]=True

	# receive square win information
	def Network_win(self, data):
		self.owner[data["y"]][data["x"]] = "win"
		self.board[data["y"]][data["x"]] = True

	# receive square lose information
	def Network_lose(self, data):
		self.owner[data["y"]][data["x"]] = "lose"
		self.board[data["y"]][data["x"]] = True

# init game
tg = TicGame()
# update loop
while 1:
	if tg.update() == 1:
		break
# do finished behavior
tg.finished()

