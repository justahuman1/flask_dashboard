# Flask Dashboard

A dashboard for integrating Python, Tableau, and Google Sheets for automated data collection and visualization. Built in with a full webscraper for the top 100 crypto coins and scikit-learn models for continous integration of new bitcoin data.

[Live Site](https://scm315-honors-app-prod.herokuapp.com)


<img src="https://i.imgur.com/yiFsbRE.jpg"/>

## Config
  1) Clone Repo
  ```
     git clone https://github.com/justahuman1/flask_dashboard.git
  ```
  2) Set up and activate a venv
  ```
     cd ./flask_dashboard
     python -m venv venv
     source venv/Scripts/activate
  ```
  3) Install requirements and build flask dev server
  ```
     pip install -r requirments.txt
     export FLASK=app.py
  ```
  4) Run flask
  ```
     flask run
  ```
  5) Open the localhost (http://127.0.0.1:5000/)

<hr/>

### Stack:
* Flask
* Scikit-Learn
* Google Sheets API
* Google Apps Scripts
* Clasp/ Webpack
* Tableau API
* SCSS
