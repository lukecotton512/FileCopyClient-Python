# FileCopyClient.py
# Luke Cotton
# Our client for FileCopy.

import sys;
import os;
import socket;

# Fills a string with extra null bytes to 512 bytes for sending.
def fillStringToBlock(stringToFill):
	strLength = len(stringToFill)
	strNumFill = 512 - strLength
	
	for index in range(0, strNumFill):
		stringToFill = stringToFill + "\0"
	
	return stringToFill
	
# Connects to the server.
def connToServer(serverName):
	# Say that we are trying to connect.
	print("Attempting to connect to {}.".format(serverName))
	# Get the information about our server.
	try:
		# Get the server information.
		serverInfo = socket.getaddrinfo(serverName, 7979, socket.AF_UNSPEC, socket.SOCK_STREAM, socket.IPPROTO_TCP, socket.AI_PASSIVE)
	except socket.gaierror as e:
		# Print an error message.
		print("Error: {}.".format(e.strerror))
	else:
		# We are successful, so go through and loop through the connection info.
		for infoItem in serverInfo:
			# Try to connect.
			try:
				# Create a socket with the information from our serverInfo list.
				sockfd = socket.socket(infoItem[0], infoItem[1], infoItem[2])
				sockfd.connect(infoItem[4])
			except OSError as e:
				# We have an error, so print an error and continue on.
				print("Error: {}: {}.".format(infoItem[4][0], e.strerror))
				return None
			else:
				# Print that we are connected.
				print("Connected to {}({}).".format(serverName, infoItem[4][0]))
				# Return the socket object.
				return sockfd
	
# Our function to connect and copy to the server.
def copyToServer(serverName, filePath):
	# Connect to our server.
	sockfd = connToServer(serverName)
	
	# Check for errors
	if sockfd is not None:
		# Check to make sure the file exists and isn't a directory.
		if os.path.exists(filePath) and (not os.path.isdir(filePath)):
			# Open our file for reading.
			fileObj = open(filePath, "rb")
			
			# We have a connection, so now, get the size of the file using stat.
			statInfo = os.stat(filePath)
			
			# Get the file size and the number of blocks and remainder.
			fileSize = statInfo.st_size
			fileNumBlocks = fileSize // 512
			fileRemainder = fileSize % 512
			
			# Get the base file path.
			baseName = os.path.basename(filePath)
			
			# Print the file name.
			print("Sending {}: {} bytes.".format(baseName, fileSize))
			
			# Fill up the baseName with extra bytes for sending.
			baseNameFill = fillStringToBlock(baseName)
				
			# Send the base file path to the server.
			bytesSent = 0
			baseNameBytes = baseNameFill.encode('utf-8')
			while bytesSent != len(baseNameBytes):
				bytesSent += sockfd.send(baseNameBytes)
			
			# Send the number of blocks in the file.
			bytesSent = 0
			fileNumBlocksStr = str(fileNumBlocks)
			fileNumBlocksFill = fillStringToBlock(fileNumBlocksStr)
			fileNumBlocksBytes = fileNumBlocksFill.encode('utf-8')
			while bytesSent != len(fileNumBlocksBytes):
				bytesSent += sockfd.send(fileNumBlocksBytes)
				
			# Send the remainder.
			bytesSent = 0
			fileRemainderStr = str(fileRemainder)
			fileRemainderFill = fillStringToBlock(fileRemainderStr)
			fileRemainderBytes = fileRemainderFill.encode('utf-8')
			while bytesSent != len(fileRemainderBytes):
				bytesSent += sockfd.send(fileRemainderBytes)
			
			# Loop through and send each block.
			for blockNum in range(0, fileNumBlocks):
				# Read a block in.
				fileBlock = fileObj.read(512)
				# Send it to the server.
				bytesSent = 0
				while bytesSent != len(fileBlock):
					bytesSent += sockfd.send(fileBlock)
				
			# Send the remainder.
			fileBlock = fileObj.read(fileRemainder)
			bytesSent = 0
			while bytesSent != len(fileBlock):
				bytesSent += sockfd.send(fileBlock)
			
			# Print we are done.
			print("Done!")
			
			# Close the connection.
			sockfd.close()
			
			# Close the file.
			fileObj.close()
			
		else:
			# Print an error.
			print("Error: path is not a file.")
	
# Our main function.
def main():
	# Check the number of arguments.
	if len(sys.argv) == 3:
		# Our file path.
		filePath = sys.argv[2]
		# Our server name
		serverName = sys.argv[1]
		# Call the copy to server method.
		copyToServer(serverName, filePath)
	else:
		# Get our program name.
		programName = sys.argv[0]
		# Print out usage message.
		print("Usage: {} <server> <file path>".format(programName))
		
	
# Run our main function
if __name__ == "__main__":
	main();