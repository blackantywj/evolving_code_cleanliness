import random
import time
import traceback
import warnings

import pymongo
import requests

session = requests.Session()
warnings.filterwarnings("ignore")
# client = pymongo.MongoClient(host="101.43.6.64", port=27017, username="root", password="123456", authSource='admin')
client = pymongo.MongoClient(host="127.0.0.1", port=27017)
github_commit = client['github']['github_commit']
file_analyse = client['github']['file_analyse']

TOKENS = ["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"]  # api token 可以添加多个，提高访问速度


def get_response(url, params=None, retry=3):
  if retry == 0:
    return None
  token = random.choice(TOKENS)
  headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {token}"
  }
  time.sleep(1)
  try:
    if params:
      response = session.get(url, headers=headers, params=params)
      print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]|get_response| {url} | {params} | {response.status_code}")
    else:
      response = session.get(url, headers=headers)
      print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]|get_response| {url} | {response.status_code}")
  except Exception:
    print(traceback.print_exc())
    time.sleep(1)
    return get_response(url, params)
  if response.status_code != 200:
    print(response.text)
    if response.status_code == 403:
      print(response.json())
      time.sleep(60)
      return get_response(url, params)
    else:
      return get_response(url, params, retry - 1)
  return response


class GithubSpider:

  def update_all_committer(self):
    cursor = github_commit.find({}, {"repository": 1, "commit_sha": 1})
    total = github_commit.count_documents({})
    count = 0
    for r in cursor:
      mongo_id = r["_id"]
      repository = r["repository"]
      commit_sha = r["commit_sha"]
      url = f"https://api.github.com/repos/{repository}/commits/{commit_sha}"
      response = get_response(url)
      result = response.json()
      author = result["commit"]["author"]
      committer = result["commit"]["committer"]
      count += 1
      github_commit.update_one({"_id": mongo_id}, {"$set": {"download": time.strftime("%Y-%m-%d %H:%M:%S"), "author": author, "committer": committer}})
      print(f"当前进度 => {count * 100 / total :.2f}%")


def main():
  spider = GithubSpider()
  spider.update_all_committer()


if __name__ == '__main__':
  main()
