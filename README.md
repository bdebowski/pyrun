# pyrun
Remote Python Execution via REST API

# About
Provides a server with a REST API that remotely executes Python code.  Use it to run untrusted code safely.

**WARNING**: Run this server on a VM to protect against malicious code that could ruin the machine.

**Note**: Containerization software like Docker does not necessarily use hardware/machine virtualization, and therefore would not protect the host machine running the container.  It is recommended you use a true virtual machine and that you save an image of this VM that you can use to restore the VM at any time.

# Setup
1. Create a Linux VM
2. Install Python 3.7 or higher on the VM
3. run setup.sh

# Usage
* POST
* GET