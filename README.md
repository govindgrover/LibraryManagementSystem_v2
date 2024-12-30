# Library Management System (LMS) v2.0

## Table of contents
1. [General Information](#general-information)
2. [Introduction](#introduction)
3. [Technology & Methodology](#technology--methodology)
	1. [Backend](#backend)
	2. [Frontend](#frontend)
4. [New Features](#new-features)
5. [Application Depenencies & Installation](#application-depenencies--installation)
	1. [Installing Necessary Services](#installing-necessary-services)
	2. [App Dependencies](#app-dependencies)
6. [How to Run](#how-to-run)
7. [Dummy Data - Info.](#dummy-data---info)

## General Information
The project, **Library Management System (LMS) v2.0** is an academic project created by me under the **Bachelors of Science (BS) Data Science and Applications** program of **Indian Institute of Technology Madras (IIT Madras)**. I hope you will find it interesting and you are welcome to make comments so that together we could make something more interesting and effective out of this.

Furthermore, this project is a updated version of [LMS v1.0](https://github.com/govindgrover/LibraryManagementSystem) and the new features introduced in this version are detailed below.

## Introduction
This updated system leverages the inclusivity and interaction through from Monthly Reports sent on emails to Dua-Date Reminders and some custom downloadable csv reports from the librarians. Offering robust features such as real-time availability checks and detailed reporting all that is done with the latest **Vue.js 3** to establishing the wider scope for PWAs and ease. The objective was to enhance user experience, improve library operational efficiency, and provide a scalable solution that could adapt to growing educational needs.

## Technology & Methodology
### Backend
This layer of abstraction proves to be of significant use when the fronted was upgraded. Consisting of Flask-Restful, SQLAlchemy and Celery-Redis combi., the system handles the pivitol operations with its new version, *API-AMS v2.0*. Moreover, we have added Flask-Cache wherever needed but didn't calculated the effectiveness! ...(*￣０￣)ノ.

All the uploaded media will be stored in the folder `lms2/static/uploads`. 

### Frontend
As the Project has been evolved, we have chosen to move to Vue.js Dynamic UI. One of popular yet not so easy to understand model makes it easy for load processors primarly the servers to reduce their load of rendering the HTML manier times and transmissing over internet. We have kept almost (not all) UI components to be as it is while integrating from Jinja2.

More precisely, the `lms2-api` folder contains all the business logic and model's controllers whereas the `lms2-frontend` folder contains the views along with their controllers enabling them to have interaction with the business logic layer.


## Application Depenencies & Installation
The app interacts with the services like Celery, Redis and MailHog so we need to install them before anything else. Then, there are depenencies of the modules used in the app which you can find in `lms2/requirements.txt`.

### Installing Necessary Services

Install Python3 and pip (if not already have done)
```
$ sudo apt install python-is-python3
$ sudo apt install python3-pip
```

Since, Python here does not containts additional modules including `venv`, we need to install it seprately
```
$ sudo apt install python3.12-venv
```

Installing Redis
```
sudo apt install redis-tools
sudo apt install redis-server
```

Installing [MailHog](https://github.com/mailhog/MailHog)
```
$ sudo apt-get -y install golang-go
$ go install github.com/mailhog/MailHog@latest
```

Additionally, if you face any errors while installing the above you can try these commands before installing the services,
```
$ sudo apt update
$ sudo apt upgrade
```

### App Dependencies
These will be taken care by the application itself, you don't need to worry about this.

## How to Run
> [!IMPORTANT]
> Here all the instructions are made with respect to WSL (Linux basically). If another is used kindly alter the commandline inputs accordingly.

Open the folder named `lms2` using `cd /path/to/folder/lms2`.

Please pay attention here, we have to run four consecutive shells to unlock the full potential of the app where each for the specified task,
#|Process/Service Name|Command(s)|Note
---|---|---|---
0|Redis|`redis-cli`|Must be started before the main application
1|MailHog|`~/go/bin/MailHog   -api-bind-addr 127.0.0.1:8025   -ui-bind-addr 127.0.0.1:8025   -smtp-bind-addr 127.0.0.1:1025`| changing *smtp-bind-addr* should also be done in `lms2-api/config.json`
2|Main application|`python main.py`|The Virtual Environment (VE) will be created here and the app will get started
3|Celery|`source .lms2-env/bin/activate`<br>`cd lms2-api`<br>`celery -A app.celery worker -l info`|This will handle the schedules and should strictly be run after creating and activating the VE (from main.py only)

```
$ python main.py
```

## Dummy Data - Info.
We have made some dummy data pre-processed into the system and the same has been mentioned below to get glimpse on the first run.

- For _Admin_, use the following
```
	E-Mail:    admin@lms.com
	Password:  admin@lms.com
```

- For _Librarian_, use the following
```
	E-Mail:    librarian@lms.com
	Password:  librarian@lms.com
```

- For _Student_, use the following
```
	E-Mail:    user@lms.com
	Password:  user@lms.com

	E-Mail:    user2@lms.com
	Password:  user2@lms.com
```

## New Features
Facilities for the librarians and readers are enhanced, they now will get an E-Mail about their last month interactions on the portal. Librarians can choose to request download the csv of books issued or sold while the readers are provided to choose between monthly report format (PDF or HTML). As any library should have a reminding clock to send reminders for books due, we also have one, it sends emails (N = 1 in api.config) *N* days prior to due of eBooks. We have relentlessly worked upon the deployment of Vue.js v3 where-ever possible to reduce the server load while making our users more confortable with data loading onto the page dynamically without reloading the page and/or showing those irritating toasts.

---
Made with Intelligence by [Govind Grover](https://github.com/govindgrover) ^_+

[Back to top?](#table-of-contents) 
