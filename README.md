# NasaJobFinder
A docker container that will send you a notification to your cell phone when a new job listing appears on https://stemgateway.nasa.gov/public/s/explore-opportunities/internships

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)


## How It Works
![alt text](https://github.com/MBarc/NasaJobFinder/blob/main/WorkFlowDiagram.png?raw=true)

## Instructions On How To Use

### Prerequisites:

It is reccomended that you have the following items before continuing.

* Docker installed
* Docker-compose installed
* A Twilio SID
* A Twilio AUTH token
* A Twilio-assigned phone number
* A phone number where you would like to send notifications to

### Step 1.)
  
  Download this repostiory and navigate to NasaJobFinder directory.
  
### Step 2.)
 
  Run the following command:
  
    ''' docker compose up -d --build  '''
  
### Step 3.)

  Voila! The phone number you specified should start receiving text messages.
