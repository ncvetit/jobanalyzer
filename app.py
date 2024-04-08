from flask import Flask, render_template, request, jsonify
import pandas as pd
import openai
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import math
import time
import random
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import json

app = Flask(__name__, static_folder='static')


def remove_html_tags(text):
    clean_text = re.sub(r'<.*?>', '', text)
    return clean_text

openai = OpenAI(
        api_key="QJVGdaEIcM2eHApwvCR7tXIqEe8hAbjc",
        base_url="https://api.deepinfra.com/v1/openai",
    )

prompt = '''Provide detailed subpoints for the following aspects based on the given job descriptions:

1.Technical Skills,
Subpoints: Enumerate the specific technical skills necessary for the role, such as programming languages, software proficiency, hardware knowledge, etc.

2. Professional Theoretical Knowledge,
Subpoints: Outline the theoretical knowledge areas essential for the role, which may include industry-specific concepts, frameworks, or methodologies.

3. Educational Qualifications,
Subpoints: Specify the educational qualifications sought for the position, including degrees, certifications, and any specialized training.

4. Aptitude & Entrepreneurship Skills,
Subpoints: Highlight specific aptitudes and entrepreneurial skills required, such as problem-solving, innovation, leadership, etc.

5. Responsibilities,
Subpoints: Break down the key responsibilities associated with the job, detailing specific tasks, projects, and expected outcomes.'''

# Set your OpenAI API key
# openai.api_key = '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'

@app.route('/', methods=['GET'])
def index():
    # return open('./index.html').read()
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    job_title = data['job_title']
    location = data['location']
    exp = data['experience']

    job_title.replace(" ", "-")

    header = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')

    driver = webdriver.Chrome()
    driver.set_window_position(-10000, 0)
    driver.get(f"https://www.naukri.com/{job_title}-jobs-in-{location}")
    timeDelay = random.randrange(7, 10)
    time.sleep(timeDelay)
    soup = BeautifulSoup(driver.page_source)

    try:
        script_tag = soup.findAll('script', type='application/ld+json')
        json_data = json.loads(script_tag[1].string)
        job_urls = [item["url"] for item in json_data["itemListElement"]]
    except:
        pass

    title = []
    description = []
    skills = []

    if len(job_urls) > 10:
        job_urls = job_urls[:10]
    else :
        job_urls = job_urls

    for i in range(len(job_urls)):
        driver.get(job_urls[i])
        timeDelay = random.randrange(3, 10)
        time.sleep(timeDelay)
        soup2 = BeautifulSoup(driver.page_source)
        script_tag2 = soup2.findAll('script', type='application/ld+json')
        try:
            cont = script_tag2[0].contents
            job_posting_json = json.loads(cont[0])
            job_description = job_posting_json.get("description", "")
            job_title = job_posting_json.get("title", "")
            job_skills = job_posting_json.get("skills", "")
            job_description = remove_html_tags(job_description)
            title.append(job_title)
            description.append(job_description)
            skills.append(job_skills)
        except:
            pass


    jobs: pd.DataFrame =  pd.DataFrame({
    'Job Title': title,
    'description': description,
    'Skills': skills})

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)

    t_text = ''.join(description for description in jobs['description'] if description is not None) + prompt
    text = prompt + t_text
    # client = OpenAI(api_key='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')

    completion = openai.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[
            {"role": "system", "content": "You are an assistant to a consultant working for a vocational training regulator"},
            {"role": "user", "content": text}
        ],
        max_tokens= 25000,
        temperature=0.2,
        presence_penalty=1
        )
    t = completion.choices[0].message
    gen = str(t.content)
    g = {
        "prediction": gen
    }
    return jsonify(g)

if __name__ == '__main__':
    app.run(port=8000, debug=True)


# from flask import Flask, render_template, request, jsonify
# import pandas as pd
# from jobspy import scrape_jobs
# import openai
# from openai import OpenAI
#
#
# app = Flask(__name__, static_folder='static')
# # app = Flask(__name__)
#
# openai = OpenAI(
#         api_key="QJVGdaEIcM2eHApwvCR7tXIqEe8hAbjc",
#         base_url="https://api.deepinfra.com/v1/openai",
#     )
#
# prompt = '''Provide detailed subpoints for the following aspects based on the given job descriptions:
#
# 1.Technical Skills,
# Subpoints: Enumerate the specific technical skills necessary for the role, such as programming languages, software proficiency, hardware knowledge, etc.
#
# 2. Professional Theoretical Knowledge,
# Subpoints: Outline the theoretical knowledge areas essential for the role, which may include industry-specific concepts, frameworks, or methodologies.
#
# 3. Educational Qualifications,
# Subpoints: Specify the educational qualifications sought for the position, including degrees, certifications, and any specialized training.
#
# 4. Aptitude & Entrepreneurship Skills,
# Subpoints: Highlight specific aptitudes and entrepreneurial skills required, such as problem-solving, innovation, leadership, etc.
#
# 5. Responsibilities,
# Subpoints: Break down the key responsibilities associated with the job, detailing specific tasks, projects, and expected outcomes.'''
#
# # Set your OpenAI API key
# # openai.api_key = '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'
#
# @app.route('/', methods=['GET'])
# def index():
#     # return open('./index.html').read()
#     return render_template("index.html")
#
# @app.route('/predict', methods=['POST'])
# def predict():
#     data = request.get_json()
#     job_title = data['hash']
#     location = data['time']
#     exp= data['exp']
#
#     # gen = job_title + location
#
#     jobs: pd.DataFrame = scrape_jobs(
#              site_name=["indeed","linkedin"],
#              search_term= job_title,
#              location= location,
#              results_wanted=15,
#              country_indeed='India'  # only needed for indeed
#          )
#
#     pd.set_option('display.max_columns', None)
#     pd.set_option('display.max_rows', None)
#     pd.set_option('display.width', None)
#     pd.set_option('display.max_colwidth', 50)
#
#     t_text = str("".join(description for description in jobs['description'] if type(description) is str))
#     text = t_text + prompt + "Also see the result in accordance with someone with an experience of" +str(exp)+"years"
#
#     # client = OpenAI(api_key='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')
#
#     completion = openai.chat.completions.create(
#         model="mistralai/Mixtral-8x7B-Instruct-v0.1",
#         messages=[
#             {"role": "system", "content": "You are an assistant to a consultant working for a vocational training regulator"},
#             {"role": "user", "content": text}
#         ]
#         )
#     t = completion.choices[0].message
#     gen = str(t.content)
#     g = {
#         "prediction": gen
#     }
#     return jsonify(g)
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=3000)
