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
    time.sleep(5)
    url = "https://www.codechef.com/api/rankings/"+ contestcode + div +"?itemsPerPage=100&order=asc&page=1&sortBy=rank"
    response = requests.get(url,headers=headers)
    
    if response.status_code == 200:
      contest_details = json.loads(response.text)
      print(contest_details)
      total_no_pages = contest_details['availablePages']
      for page in range(1,total_no_pages+1):
        time.sleep(5)
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
  headers['Cookie'] = 'uid=2591902; _ga_0F9XESWZ11=GS1.2.1699290821.1.0.1699290821.60.0.0; SESS93b6022d778ee317bf48f7dbffe03173=f0a85fd17ca66d76bfe557313628bef1; Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJjb2RlY2hlZi5jb20iLCJzdWIiOiIyNTkxOTAyIiwidXNlcm5hbWUiOiJjaGFyYW4wNCIsImlhdCI6MTY5OTI5Mjg2NywibmJmIjoxNjk5MjkyODY3LCJleHAiOjE3MDEyODcyNjd9.NxS9IR2YJHzBFJEhH2pJ15nYgq-y8OXSctvu-QsxTYk; _gid=GA1.2.530585547.1699425162; _clck=lr6tzx|2|fgj|0|1402; _gat_UA-141612136-1=1; _clsk=50fcy7|1699428507342|4|1|q.clarity.ms/collect; _ga_C8RQQ7NY18=GS1.1.1699427936.6.1.1699428515.50.0.0; _ga=GA1.2.1753313708.1699006727; userkey=56a7ba633e70a409025ae6f4d029a938'
  headers["X-Csrf-Token"]  = "b03012b1c0d6827b4f3aff29f743e9924fd2fb54f26d1a34f4bfa30735886254"
  batchusers = request.files['batchusers']
  if batchusers:
      batchusers = pd.read_csv(batchusers)
      contestcode = request.form['contestcode']
      users = get_codechef_participation(contestcode, batchusers,headers)
      print(users)
      if users:
        dataframe = pd.DataFrame(users)
        all_handles = batchusers
        all_handles.rename(columns={'Roll No': 'rollNum'}, inplace=True)
        all_handles.rename(columns={'CODECHEF': 'username'}, inplace=True)
        codechef_handles = all_handles[['Name', 'rollNum', "username","Email Id"]]
        
        merged_df = pd.merge(codechef_handles, dataframe, on='username', how="left")
        merged_df = merged_df[['Name','rollNum','username','Email Id','div','rating','rank','score','plag','solved_count','problem_solved']]
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
