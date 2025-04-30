# JWT Reverse Shell
This is a modified version of IppSec's forward-shell, designed to exploit command injection vulnerabilities via JWT tokens. Command output is displayed directly on the web page.

## Background
While testing a web application, I discovered a JWT token containing a `cmd` parameter and had access to the JWT secret key. By injecting commands directly into the `cmd` parameter (without spaces), signing the JWT with the HS256 key, and sending a GET request to the server, the command output would appear on the website.

Due to a strict firewall policy, obtaining a traditional reverse shell was not feasible—so I built this solution as an alternative.

## Internal Workflow
- **JWT-based Command Execution**  
The server executes any command passed via the `cmd` parameter in the JWT, and returns the output in the HTTP response.

- **Named Pipe (mkfifo) for Shell Emulation**

  - Commands are written into `/dev/shm/ip`.
  - A background thread on the server reads /dev/shm/ip, executes the commands, and writes the output to /dev/shm/op.
  - The client periodically reads from /dev/shm/op to fetch the command output and clears the file afterward.

- [BETA] File Upload Feature  
  A basic file upload mechanism is included. It streams files using base64 encoding and sends them to the target system.

## mkfifo Pipe Mechanics
- Two files are used in `/dev/shm/`:

  - `ip`: input commands

  - `op`: output results

- The flow works as follows:

  - A named pipe is created to handle input/output.

  - Commands are echoed into `/dev/shm/ip`.

  - The pipe executes the commands and writes the results into `/dev/shm/op`.

  - The client polls `/dev/shm/op` for output and clears it after reading.
