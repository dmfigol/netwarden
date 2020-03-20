## NetWarden - network automation controller written in Python
This is the repository with the code written live on the [streams](https://www.youtube.com/playlist?list=PLSwGHYY8t8JgyCPH6IMq6B6_KPU-4Q_p_).It is going to be build over multiple streams.  
The goal of this project is to build a network automation controller using state-of-the-art technologies: Python asyncio / FastAPI web framework / RESTCONF/NETCONF / Vue.JS.  
Unlike other open-source NMS/controllers (e.g. [eNMS](https://github.com/eNMS-automation/eNMS)), this project is not planned to be released on PyPi and maintained. It serves as a sample code to show you what is possible and how hard/easy it is to build your controller from scratch.


### Controller functions
This controller should be able to do the following:
- Display overview of the inventory
- Gather some operational statistics from the whole network on-demand
- Make configuration changes either high-level services or some low-level details
- Perform network testing on schedule or on-demand to verify the network health
- Provision new devices (ZTP)
- Manage software images on the devices


### Running
To start backend, execute this in `backend` folder:  
`poetry run uvicorn netwarden.app:app --host 0.0.0.0 --port 8000 --reload`  
To start frontend, execute this in `frontend` folder: `yarn serve`  