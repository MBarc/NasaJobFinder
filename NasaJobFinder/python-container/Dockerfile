FROM python:3.7
RUN apt-get update && apt-get -y install cron
WORKDIR /SCRIPT

# Copying local files into the container
COPY crontab /etc/cron.d/crontab
COPY requirements.txt /SCRIPT/requirements.txt
COPY main.py /SCRIPT/main.py

# Simplying upgrading pip
RUN pip install --upgrade pip

# Having pip install all of the dependencies for this project
RUN pip install -r /SCRIPT/requirements.txt

# Assigning the appropriate permissions to the cron file
# For more information -> https://chmodcommand.com/chmod-0644/
RUN chmod 0644 /etc/cron.d/crontab

RUN /usr/bin/crontab /etc/cron.d/crontab

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install the Google Chrome package
RUN apt-get -y update

# Actually installing Google Chrome
RUN apt-get install -y google-chrome-stable

# Copying over all the environmental variables and starting cron as the main process of the container
CMD ["/bin/bash", "-c", "printenv > /etc/environment && cron -f"]
