# JWT Reverse Shell

This is a modified version of [IppSec's Forward Shell](https://github.com/IppSec/forward-shell) which does the command injection via JWT Token and command output is displayed on the webpage.

I encountered an webapp which had JWT which had a `cmd` parameter and I also had the JWT Secret Key.
Which on adding commands to it without a space and signing with the `JWT HS256 Key` and then sending a GET Request on the webserver gave me the results on the webpage.
Now, The obious choice was to get a reverse shell which I was unable to due to the presence of a strong firewall policy.

# Internal Working
- You have the JWT Secret and the JWT has a `cmd` parameter which takes any command and executes on the server and presents us the output on the website.
- We have an mkfifo pipe which is working by placing commands in the `/dev/shm/ip` and using threading to `cat /dev/shm/op` perodically and prints the output of the commands incase we have some and then clears the `/dev/shm/op` file.
- [BETA]I also, added an file upload feature incase you want to upload files which uses base64 stream to upload files

# MkFifo Pipe's Working
- It create's two files `/dev/shm/ip` which is the input file and the `/dev/shm/op` which is the output file.
- Now, A `mkfifo` pipe is created which take's any linux commands in the `/dev/shm/ip` and executes them and place's their output in the `/dev/shm/op` file.
- Our job is to echo any command into the `/dev/shm/ip` file and perodically `cat /dev/shm/op` file to get the output of our commands.
