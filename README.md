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

After you grab that information, download this respository and navigate to NasaJobFinder/python-container. Open main.env and fill out the variable information where necessary.

### Step 1.)
  
  Navigate to the NasaJobFinder directory via Terminal or Command Prompt.
  
### Step 2.)
 
  Run the following command:
  
    docker compose up -d --build
  
### Step 3.)

  Voila! The phone number you specified should start receiving text messages.


## Important To Note

* Within main.py, lines 105-107 filter the results to only include listings that are (1) in Florida, (2) virtual/remote work, and (3) for Master level students. Feel free to edit these lines to fit your needs.
  *  If you decide to edit the filters to where more results are presented, you must increase the value of 20 on line 78 within main.py. This is because the NASA website does not load all listings into the DOM and we must scroll down in order to generate the rest of the results.
