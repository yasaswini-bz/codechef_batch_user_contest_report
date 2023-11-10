from flask import Flask, request, render_template
import requests
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time

MAX_RETRIES = 5

def make_request(url, headers):
    time.sleep(1)
    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            time.sleep(20)
    print(f"Failed to make request after {MAX_RETRIES} retries")
    return None

def get_codechef_participation(contestcode, div, headers):
    RANK = []
    USERNAME = []
    RATING = []
    SCORE = []
    DIV = []
    COUNT = []
    PROBLEM_SOLVED = []
    PLAG = []
   
    url = "https://www.codechef.com/api/rankings/" + contestcode + div + "?filterBy=Country%3DIndia&itemsPerPage=150&order=asc&page=1&sortBy=rank"
    response = make_request(url, headers)

    if response is not None and response.status_code == 200:
        contest_details = json.loads(response.text)
        total_no_pages = contest_details['availablePages']

        for page in range(1, total_no_pages + 1):
            time.sleep(1)
            url = "https://www.codechef.com/api/rankings/" + contestcode + div + "?filterBy=Country%3DIndia&itemsPerPage=150&order=asc&page=" + str(page) + "&sortBy=rank"
            response = make_request(url, headers)
            if response is not None and response.status_code == 200:
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
                        PLAG.append('involved in plag')
                   
                    c = 0
                    p = []
                    problems = pageuser['problems_status']
                   
                    for problem in problems:
                        c += 1
                        p.append(problem + " (" + str(problems[problem]['score']) + ")")
                   
                    COUNT.append(str(c))
                    PROBLEM_SOLVED.append(" ".join(p))
                    

    d = {"username": USERNAME, "div": DIV, "rating": RATING, "rank": RANK, "score": SCORE, "plag": PLAG,
         "solved_count": COUNT, "problem_solved": PROBLEM_SOLVED}
    
    return d
def merge_data(batchusers, users):
    dataframe = pd.DataFrame(users)
    all_handles = batchusers
    all_handles.rename(columns={'Roll No': 'rollNum'}, inplace=True)
    all_handles.rename(columns={'CODECHEF': 'username'}, inplace=True)
    codechef_handles = all_handles[['Name', 'rollNum', "username", "Email Id"]]
    merged_df = pd.merge(codechef_handles, dataframe, on='username', how="left")
    merged_df = merged_df[['Name', 'rollNum', 'username', 'Email Id', 'div', 'rating', 'rank', 'score', 'plag', 'solved_count', 'problem_solved']]
    merged_df["div"].fillna("Not participated", inplace=True)
    merged_df["rating"].fillna("Not participated", inplace=True)
    merged_df["rank"].fillna("Not participated", inplace=True)
    merged_df["score"].fillna("Not participated", inplace=True)
    merged_df["plag"].fillna("Not participated", inplace=True)
    merged_df["solved_count"].fillna("Not participated", inplace=True)
    merged_df["problem_solved"].fillna("Not participated", inplace=True)
    merged_df.loc[merged_df['username'] == "NOT FILLED", ['div', 'rating','rank','score','plag','solved_count','problem_solved']] = ['NOT FILLED']
    return merged_df
app = Flask(__name__)

@app.route('/get_participate', methods=['POST'])
def get_participate():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }

    headers['Cookie'] = 'SESS93b6022d778ee317bf48f7dbffe03173=617255d5f1aefa775e037a0c9aac56c4; Authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJjb2RlY2hlZi5jb20iLCJzdWIiOiIyNTE8MTAwIiwidXNlcm5hbWUiOiJ5YXNhc3dpbiIsImlhdCI6MTY5OTQyNDI0MSwibmJmIjoxNjk5NDI0MjQxLCJleHAiOjE3MDE0MTg2NDF9.jwc9x5GiWW25mTCjpWQkIyWzza7UtvZmEYpHz_Z5Ymk; uid=2518100; userkey=56a7ba633e70a409025ae6f4d029a938; mp_d7f79c10b89f9fa3026f2fb08d3cf36d_mixpanel=%7B%22distinct_id%22%3A%20%22%24device%3A18bad93e297930-0dbb0c27b12361-26031051-df602-18bad93e297930%22%2C%22%24device_id%22%3A%20%2218bad93e297930-0dbb0c27b12361-26031051-df602-18bad93e297930%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22%24search_engine%22%3A%20%22google%22%7D'
    headers["X-Csrf-Token"] = "b7e815b87cb8171de2714446d089b103246bdf6eee8d895ec35931bd78c6bac2"

    batchusers = request.files['batchusers']

    if batchusers:
        batchusers = pd.read_csv(batchusers)
        contestcode = request.form['contestcode']
        users = {}
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(get_codechef_participation, contestcode, div, headers) for div in ['A', 'B', 'C', 'D']]
            for future in futures:
                users.update(future.result())
        
        if users:
            merged_df = merge_data(batchusers, users)
            return render_template('home.html', output=merged_df.to_dict(orient='records'))

    data = {
        'Name': [''],
        'rollNum': [''],
        'username': [''],
        'Email Id': [''],
        'div': [''],
        'rating': [''],
        'rank': [''],
        'score': [''],
        'plag': [''],
        'solved_count': [''],
        'problem_solved': ['']
    }
    df = pd.DataFrame(data)
    return render_template('home.html', output=df.to_dict(orient='records'))


@app.route('/')
def hello_world():
    data = {
        'Name': [''],
        'rollNum': [''],
        'username': [''],
        'Email Id': [''],
        'div': [''],
        'rating': [''],
        'rank': [''],
        'score': [''],
        'plag': [''],
        'solved_count': [''],
        'problem_solved': ['']
    }
    df = pd.DataFrame(data)
    return render_template('home.html', output=df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')
