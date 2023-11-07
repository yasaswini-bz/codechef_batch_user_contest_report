
from flask import Flask, request, render_template,jsonify
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import concurrent.futures
import time
def get_codechef_participation(contestcode,batchusers,headers):
  RANK = []
  USERNAME = []
  RATING = []
  SCORE = []
  DIV = []
  COUNT = []
  PROBLEM_SOLVED = []
  PLAG = []
  alldiv = ['A' , 'B','C','D']
  for div in alldiv:
    url = "https://www.codechef.com/api/rankings/"+ contestcode + div +"?itemsPerPage=100&order=asc&page=1&sortBy=rank"
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
      contest_details = json.loads(response.text)
      print(contest_details)
      total_no_pages = contest_details['availablePages']
      for page in range(1,total_no_pages+1):
        url = "https://www.codechef.com/api/rankings/"+ contestcode + div +"?itemsPerPage=100&order=asc&page= "+ str(page) + "&sortBy=rank"
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
          page_contest_details = json.loads(response.text)
          pageusers = page_contest_details['list']
          for pageuser in pageusers:
            if div == 'A':
              DIV.append('1')
            elif div == 'B':
              DIV.append('2')
            elif div == 'C':
              DIV.append('3')
            elif div == 'D':
              DIV.append('4')
            
            RANK.append(str(pageuser['rank']))
            RATING.append(str(pageuser['rating']))
            USERNAME.append(str(pageuser['user_handle']))
            SCORE.append(str(pageuser['score']))
            if pageuser['penalty'] == 0:
              PLAG.append('-')
            else:
              PLAG.append('involed in plag')
            c = 0
            p = []
            problems = pageuser['problems_status']
            for problem in problems:
              c += 1
              p.append(problem + " (" + str(problems[problem]['score']) + ")")
            COUNT.append(str(c))
            PROBLEM_SOLVED.append(" ".join(p))

  d = {"username":USERNAME,"div" : DIV,"rating" : RATING,"rank" : RANK,"score":SCORE,"plag":PLAG,
       "solved_count" : COUNT,"problem_solved":PROBLEM_SOLVED}
  return d

app = Flask(__name__)

@app.route('/get_participate', methods=['POST'])
def get_participate():
  headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
  }
  headers['Cookie'] = 'SESS93b6022d778ee317bf48f7dbffe03173=e672c9f3db690962c4a7bd6cbfc58ea0; Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJjb2RlY2hlZi5jb20iLCJzdWIiOiIyNTE4MTAwIiwidXNlcm5hbWUiOiJ5YXNhc3dpbiIsImlhdCI6MTY5OTI1OTUwNSwibmJmIjoxNjk5MjU5NTA1LCJleHAiOjE3MDEyNTM5MDV9.WsFPb6SVkAKPCgzsLi5o4OHWTGBVp7Q0kPBxo-RjCw8; uid=2518100; mp_d7f79c10b89f9fa3026f2fb08d3cf36d_mixpanel=%7B%22distinct_id%22%3A%20%22%24device%3A18ba3c23409906-0e14b78d4183a6-26031051-df8ea-18ba3c2340a906%22%2C%22%24device_id%22%3A%20%2218ba3c23409906-0e14b78d4183a6-26031051-df8ea-18ba3c2340a906%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22%24search_engine%22%3A%20%22google%22%7D'
  headers["X-Csrf-Token"]  = "b87326f688a97feb8cc58d7388c800ee186f5150f56185633e3cc9bbaeb87ed7"
  batchusers = request.files['batchusers']
  if batchusers:
      batchusers = pd.read_csv(batchusers)
      contestcode = request.form['contestcode']
      users = get_codechef_participation(contestcode, batchusers,headers)
      if users:
          dataframe = pd.DataFrame(users)
          all_handles = batchusers
          all_handles.rename(columns={'Roll No': 'rollNum'}, inplace=True)
          all_handles.rename(columns={'CODECHEF': 'username'}, inplace=True)
          codechef_handles = all_handles[['Name', 'rollNum', "username","Email Id"]]
          merged_df = pd.merge(codechef_handles, dataframe, on='username', how="left")
          merged_df = merged_df[['Name','rollNum','username','Email Id','div','rating','rank','score','plag','solved_count','problem_solved']]
          merged_df['div'].fillna('did not participated', inplace=True)
          merged_df['rating'].fillna('did not participated', inplace=True)
          merged_df['rank'].fillna('did not participated', inplace=True)
          merged_df['score'].fillna('did not participated', inplace=True)
          merged_df['plag'].fillna('did not participated', inplace=True)
          merged_df['solved_count'].fillna('did not participated', inplace=True)
          merged_df['problem_solved'].fillna('did not participated', inplace=True)
          return render_template('home.html', output=merged_df.to_dict(orient='records'))
    
  data = {
        'Name': [''],
        'rollNum': [''],
        'username': [''],
        'Email Id' : [''],
        'div' : [''],
        'rating':[''],
        'rank': [''],
        'score': [''],
        'plag':[''],
        'solved_count' : [''],
        'problem_solved' : ['']
  }
  df = pd.DataFrame(data)
  return render_template('home.html', output=df.to_dict(orient='records'))

@app.route('/')
def hello_world():
    data = {
        'Name': [''],
        'rollNum': [''],
        'username': [''],
        'Email Id' : [''],
        'div' : [''],
        'rating':[''],
        'rank': [''],
        'score': [''],
        'plag':[''],
        'solved_count' : [''],
        'problem_solved' : ['']
    }
    df = pd.DataFrame(data)
    return render_template('home.html', output=df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')