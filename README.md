## NetWarden - network automation controller
This is the repository for the code written live on the [streams](https://www.youtube.com/playlist?list=PLSwGHYY8t8JgyCPH6IMq6B6_KPU-4Q_p_). This controller is going to be built over many streams.  
The goal of this project is to build a network automation controller using state-of-the-art technologies: Python asyncio / FastAPI web framework / RESTCONF/NETCONF / Vue.JS.  
Unlike other open-source NMS/controllers (e.g. [eNMS](https://github.com/eNMS-automation/eNMS)), this project is not planned to be released on PyPi and maintained. Instead, it is a sample code to show what is possible and how hard/easy it is to build your custom network controller from scratch.

### License
Please note that this application is [AGPLv3](https://tldrlegal.com/license/gnu-affero-general-public-license-v3-(agpl-3.0)) licensed.

### Controller functions
Once finished, controller should be able to do the following (wishlist):
- Display overview of the inventory
- Gather some operational statistics from the whole network on-demand
- Make configuration changes either high-level services or some low-level details
- Perform network testing on schedule or on-demand to verify the network health
- Provision new devices (ZTP)
- Manage software images on the devices


## Usage
### Installation
You need:  
* Python 3.8+
* (optional) [poetry](https://python-poetry.org/) to install dependencies
* (optional) [go-task](https://taskfile.dev/#/) to simplify running of the commands
* Node.js (tested on v15.8.0) + yarn
* Lab with IOS-XE network devices (controller has capability to be extended with more NOSes, but tests are done only for IOS-XE)
* NetBox instance with lab devices populated (they must contain: site, management interface with primary IP address, platform slug: "cisco_iosxe")

#### Backend installation
In the `backend` folder, create Python virtual environment and install dependencies:
```
cd backend
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools
pip install -r requirements.txt
cd ..
```

#### Frontend installation
In the `frontend` folder, install Node.js dependencies:
```
cd frontend
rm -rf node_modules
yarn install
cd ..
```

If you are using `poetry` and `go-task`, then simply do `task install` in the root folder to install both

### Configuration
Change the following parameters in `backend/settings.toml`:
* [default.device] section, username and password to access network devices
* [development.netbox] section, host and token to access NetBox instance
* (optional) [default] section, domain_name - will be appended to device name and site


### Running
1) Make sure that the NetBox instance is running
2) To start backend, execute this in `backend` folder:  
`.venv/bin/uvicorn netwarden.app:app --host 0.0.0.0 --port 5000 --reload`  
Backend is accessible at [http://localhost:5000](http://localhost:5000), openapi docs are available at [http://localhost:5000/api/docs](http://localhost:5000/api/docs)  
Alternatively, if you are using `poetry` and `go-task`, you can execute `task backend` in the project root directory
3) To start frontend, execute this in `frontend` folder:  
`yarn serve --host 0.0.0.0 --port 8000`  
Frontend is accessible at [http://localhost:8000](http://localhost:8000)  
Alternatively, if you are using  `go-task`, you can execute `task frontend` in the project root directory.

Currently, the following features have been implemented:
* inventory list with some general information about the devices + serial/sw version pulled from the devices
* network topology built based on LLDP

