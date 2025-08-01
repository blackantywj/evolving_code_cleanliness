import base64
import json
import random
import re
import time
import traceback
from collections import Counter, defaultdict
from pprint import pprint
from parser_javascript import parse_code as parse_js
from parser_python import parse_code as parse_python
from parser_java import parse_code as parse_java
from parser_cpp import parse_code as parse_cpp
from parser_c import parse_code as parse_c
from connections import get_collection
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import warnings
import threading
import argparse
from datetime import datetime
from py4j.java_gateway import JavaGateway
session = requests.Session()
stop_event = threading.Event()  # Create a threading event

warnings.filterwarnings("ignore")
commit_collection = get_collection('github_commit')

TOKENS = [
          ]  # api token 可以添加多个，提高访问速度

token_remaining = {token: 5000 for token in TOKENS} 

# Replace with your actual token
user_agents = [
    # Windows User-Agents
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.48 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",

    # macOS User-Agents
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",

    # Linux User-Agents
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    
    # Android User-Agents
    "Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; Pixel 2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.85 Mobile Safari/537.36",

    # iPhone/iPad User-Agents
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",

    # Miscellaneous
    "Mozilla/5.0 (Linux; U; Android 4.1.2; en-us; GT-N7100 Build/JZO54K) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
    "Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; Microsoft; RM-1116) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.15254",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
    "Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18"
]

suffix_list = ["py", "java", "c", "cpp", "js", "h"]
keyword_list = ["py", "java", "c", "cpp", "js", "h", "all"]


def get_response(url, params=None, retry=3):
    if retry == 0:
        return None
    token = get_available_token()
    update_token_remaining(token)
    headers = {
        "Accept"       : "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}",
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

def update_token_remaining(token):
    url = "https://api.github.com/rate_limit"
    headers = {
        "Authorization": f"token {token}",
        "User-Agent": random.choice(user_agents)
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        rate_limit_data = response.json()
        remaining = rate_limit_data['resources']['core']['remaining']
        token_remaining[token] = remaining  # Update remaining requests for the token
        print(f"Token: {token[:8]}... | Remaining requests: {remaining}")
    except requests.RequestException as e:
        print(f"Error fetching rate limit for token {token[:8]}...: {e}")
        token_remaining[token] = 0  # Set to 0 if error occurs (as a fail-safe)

# Function to check rate limit periodically
def check_rate_limit():
    while not stop_event.is_set():  # Keep checking until stop_event is set
        for token in TOKENS:
            update_token_remaining(token)
        time.sleep(60)  # Check every minute

def get_available_token():
    global token_remaining
    available_tokens = [token for token, remaining in token_remaining.items() if remaining > 0]
    
    # If no tokens have remaining requests, sleep for an hour
    if not available_tokens:
        print("All tokens have exhausted their rate limits. Waiting for an hour...")
        time.sleep(3600)  # Sleep for one hour
        return get_available_token()  # Retry after sleeping
    
    # Select a random available token
    selected_token = random.choice(available_tokens)
    
    return selected_token

def get_source_code(git_url):
    """
    获取源码
    """
    response = get_response(git_url)
    if not response:
        return "404"
    results = response.json()
    content = results.get('content', '')
    result = base64.b64decode(content).decode("utf-8", "ignore")
    return result


def get_first_commit(repository):
    """
    获取最新的一条commit的sha
    :param repository: 仓库名称
    :return: 最新的commit的sha
    """
    url = f"https://api.github.com/repos/{repository}/commits?per_page=1"
    response = get_response(url)
    results = response.json()
    data = results[0] if results else {}
    sha = data.get("sha", "")
    return sha


def download(repository):
    """
    下载commit的文件
    :param repository: 仓库名称
    """
    try:
        commits = commit_collection.find({"repository": repository, "download": {"$exists": False}})
        with ThreadPoolExecutor(max_workers=12) as executor:
            _ = {executor.submit(download_concurrent, commit): commit for commit in commits}
            # for future in as_completed(futures):
            #     repo = futures[future]
            #     try:
            #         future.result()
            #         # print(f"Processed repository: {repo['full_name']}")
            #     except Exception as e:
            #         # print(f"Error processing repository {repo['full_name']}: {e}")
            #         pass
        
    except Exception:
        print(traceback.print_exc())
        time.sleep(1)
        download(repository)

def download_concurrent(commit):
    # for commit in commits:
    mongo_id = commit["_id"]
    commit_sha = commit["commit_sha"]
    repository = commit["repository"]
    url = f"https://api.github.com/repos/{repository}/commits/{commit_sha}"
    response = get_response(url)
    result = response.json()
    message = result.get("commit", {}).get("message", "")
    parents = result.get("parents", [])
    parents_sha = [parent["sha"] for parent in parents]
    parents_sha = parents_sha[0] if parents_sha else ""
    files = result.get("files", [])
    datas = []
    datas = process_files_concurrently(files, parents_sha)
    # for file in files:
    #     fileName = file["filename"]
    #     patch = file.get("patch", "")
    #     fileUrl = file["raw_url"]
    #     newFileUrl = file["contents_url"]
    #     newFileContent = get_source_code(newFileUrl)
    #     suffix = fileName.split(".")[-1]
    #     if suffix not in suffix_list:
    #         # print(f"文件后缀不在列表中，跳过：{fileName} {newFileUrl}")
    #         continue
    #     if newFileContent == "404":
    #         break
    #     if not parents_sha:
    #         break
    #     oldFileUrl = newFileUrl[:newFileUrl.rfind("ref=")] + "ref=" + parents_sha
    #     oldFileContent = get_source_code(oldFileUrl)
    #     if newFileContent and oldFileContent:
    #         data = {
    #             "fileName"      : fileName,
    #             "patch"         : patch,
    #             "fileUrl"       : fileUrl,
    #             "newFileUrl"    : newFileUrl,
    #             "newFileContent": newFileContent,
    #             "oldFileUrl"    : oldFileUrl,
    #             "oldFileContent": oldFileContent
    #         }
    #         # pprint(data)
    #         datas.append(data)
    commit_collection.update_one({"_id": mongo_id}, {"$set": {"download": time.strftime("%Y-%m-%d %H:%M:%S"), "message": message, "datas": datas}})


def process_file(file, parents_sha):
    fileName = file["filename"]
    patch = file.get("patch", "")
    fileUrl = file["raw_url"]
    newFileUrl = file["contents_url"]
    newFileContent = get_source_code(newFileUrl)
    
    suffix = fileName.split(".")[-1]
    if suffix not in suffix_list:
        # print(f"文件后缀不在列表中，跳过：{fileName} {newFileUrl}")
        return None  # Skip this file

    if newFileContent == "404":
        return None  # Skip if file not found

    if not parents_sha:
        return None  # Skip if parents_sha is not defined

    oldFileUrl = newFileUrl[:newFileUrl.rfind("ref=")] + "ref=" + parents_sha
    oldFileContent = get_source_code(oldFileUrl)
    
    if newFileContent and oldFileContent:
        data = {
            "fileName"      : fileName,
            "patch"         : patch,
            "fileUrl"       : fileUrl,
            "newFileUrl"    : newFileUrl,
            "newFileContent": newFileContent,
            "oldFileUrl"    : oldFileUrl,
            "oldFileContent": oldFileContent
        }
        return data
    return None

def process_files_concurrently(files, parents_sha):
    datas = []
    for file in files:
        result = process_file(file, parents_sha)
        datas.append(result)
    # with ThreadPoolExecutor(max_workers=6) as executor:
    #     # Using a list comprehension to start the thread pool tasks
    #     futures = [
    #         executor.submit(process_file, file, parents_sha)
    #         for file in files
    #     ]
        
    #     # Wait for all threads to complete and process results
    #     for future in futures.as_completed(futures):
    #         result = future.result()
    #         if result is not None:
    #             datas.append(result)
    
    return datas

def get_commits(repository, sha, start_time=None, end_time=None):
    """
    获取commit
    :param repository: 仓库名称
    :param sha: commit的sha
    :param start_time: 开始时间 2021-01-01
    :param end_time: 结束时间 2022-01-01
    :return:
    """
    url = f"https://api.github.com/repos/{repository}/commits"
    params = {
        "per_page": 100,
        "sha"     : sha
    }
    response = get_response(url, params)
    results = response.json()
    # pprint(results)
    if not results:
        return
    for result in results:
        commit_sha = result.get("sha", "")
        release_time = result.get("commit", {}).get("committer", {}).get("date", "")[:10]
        if start_time:
            if release_time < start_time:
                return
        if end_time:
            if release_time > end_time:
                continue
                # author and committer
        github_author_name = result.get("author", {}).get("login") if result['author'] != None else None
        github_committer_name = result.get("committer", {}).get("login") if result['committer'] != None else None
        author = {"name": github_author_name, \
                  "email":result.get("commit", {}).get("author", {}).get("email"), \
                  "date":datetime.strptime(result.get("commit", {}).get("author", {}).get("date"), "%Y-%m-%dT%H:%M:%SZ")}
        committer = {"name": github_committer_name, \
                     "email":result.get("commit", {}).get("committer", {}).get("email"), \
                     "date":datetime.strptime(result.get("commit", {}).get("committer", {}).get("date"), "%Y-%m-%dT%H:%M:%SZ")}
        data = {
            "repository"  : repository,
            "commit_sha"  : commit_sha,
            "release_time": release_time,
            "author": author,
            "committer": committer
        }
        # pprint(data)
        origin = commit_collection.find_one({"repository": repository, "commit_sha": commit_sha})
        if not origin:
            commit_collection.insert_one(data)
    last_sha = results[-1]["sha"]
    last_parents_sha = results[-1]["parents"]
    if last_parents_sha:
        get_commits(repository, last_sha, start_time, end_time)

def get_commits_author_commit(repository, sha, start_time=None, end_time=None):
    """
    获取commit
    :param repository: 仓库名称
    :param sha: commit的sha
    :param start_time: 开始时间 2021-01-01
    :param end_time: 结束时间 2022-01-01
    :return:
    """
    url = f"https://api.github.com/repos/{repository}/commits"
    params = {
        "per_page": 100,
        "sha"     : sha
    }
    response = get_response(url, params)
    results = response.json()
    # pprint(results)
    if not results:
        return
    for result in results:
        commit_sha = result.get("sha", "")
        release_time = result.get("commit", {}).get("committer", {}).get("date", "")[:10]
        
        # author and committer
        github_author_name = result.get("author", {}).get("login") if result['author'] != None else None
        github_committer_name = result.get("committer", {}).get("login") if result['committer'] != None else None
        author = {"name": github_author_name, \
                  "email":result.get("commit", {}).get("author", {}).get("email"), \
                  "date":datetime.strptime(result.get("commit", {}).get("author", {}).get("date"), "%Y-%m-%dT%H:%M:%SZ")}
        committer = {"name": github_committer_name, \
                     "email":result.get("commit", {}).get("committer", {}).get("email"), \
                     "date":datetime.strptime(result.get("commit", {}).get("committer", {}).get("date"), "%Y-%m-%dT%H:%M:%SZ")}
        
        if start_time:
            if release_time < start_time:
                return
        if end_time:
            if release_time > end_time:
                continue
        data = {
            "repository"  : repository,
            "commit_sha"  : commit_sha,
            "release_time": release_time,

        }
        origin = commit_collection.find_one({"repository": repository, "commit_sha": commit_sha})
        if origin == None:
            continue
        commit_collection.update_one(
        {"_id": origin["_id"]},  # 根据 _id 更新
        {
            "$set": {
                "author": author,
                "committer": committer
                }
            }
        )
    last_sha = results[-1]["sha"]
    last_parents_sha = results[-1]["parents"]
    if last_parents_sha:
        get_commits_author_commit(repository, last_sha, start_time, end_time)

def parse_patch(patch, oldFileContent, newFileContent):
    """
    i.代码行数增加、减少、持平了多少，分别共计多少个
    ii.每行的字符数增加、减少、持平了多少，分别共计多少个
    :param patch:
    :param oldFileContent:
    :param newFileContent:
    :return: 行数变化、字符数变化
    """
    lines = patch.splitlines()
    add_lines = []
    del_lines = []
    for line in lines:
        if line.startswith("+"):
            add_lines.append(line)
        elif line.startswith("-"):
            del_lines.append(line)
    add_lines = [line[1:] for line in add_lines]
    del_lines = [line[1:] for line in del_lines]
    add_lines_count = len(add_lines)
    del_lines_count = len(del_lines)
    total_lines_count = add_lines_count - del_lines_count
    add_lines_char_count = sum([len(line) for line in add_lines])
    del_lines_char_count = sum([len(line) for line in del_lines])
    oldFileContent_lines = oldFileContent.splitlines()
    newFileContent_lines = newFileContent.splitlines()
    oldFileContent_lines_count = len(oldFileContent_lines)
    newFileContent_lines_count = len(newFileContent_lines)
    oldFileContent_char_count = sum([len(line) for line in oldFileContent_lines])
    newFileContent_char_count = sum([len(line) for line in newFileContent_lines])
    oldFileContent_lines_char_avg = oldFileContent_char_count / oldFileContent_lines_count
    newFileContent_lines_char_avg = newFileContent_char_count / newFileContent_lines_count
    add_lines_char_avg = add_lines_char_count / add_lines_count if add_lines_count else newFileContent_lines_char_avg
    del_lines_char_avg = del_lines_char_count / del_lines_count if del_lines_count else oldFileContent_lines_char_avg
    total_lines_char_avg = f"{int(del_lines_char_avg)}_{int(add_lines_char_avg)}"
    file_row_change = f"{oldFileContent_lines_count}_{newFileContent_lines_count}"
    return total_lines_count, total_lines_char_avg, file_row_change


def analysis(repository):
    """
    分析代码
    """
    commits = commit_collection.find({"repository": repository, "download": {"$exists": True}, "analysis": {"$exists": False}})
    # commits = commit_collection.find({"repository": repository, "download": {"$exists": True}})
    for commit in commits:
        mongo_id = commit["_id"]
        params_info = {}  # 参数信息
        circle_info = {}  # 圈复杂度信息
        total_lines_info = {}  # 行数变化信息
        total_char_info = {}  # 字符变化信息
        method_rows_info = {}  # 函数行数信息
        file_rows_info = {}  # 文件行数信息
        for keyword in keyword_list:
            params_info[keyword] = {}
            circle_info[keyword] = {}
            total_lines_info[keyword] = []
            total_char_info[keyword] = {}
            method_rows_info[keyword] = {}
            file_rows_info[keyword] = {}
        datas = commit.get("datas", [])
        for data in datas:
            if data == None:
                continue
            fileName = data["fileName"]
            fileType = fileName.split(".")[-1]
            patch = data.get("patch", "")
            newFileContent = data["newFileContent"]
            oldFileContent = data["oldFileContent"]
            # print(fileName)
            if fileType not in suffix_list:
                continue
            total_lines_count, total_lines_char_avg, file_row_change = parse_patch(patch, oldFileContent, newFileContent)
            # if fileType not in total_lines_info:
            #     total_lines_info[fileType] = []
            # if "all" not in total_lines_info:
            #     total_lines_info["all"] = []
            # 单commit中，所有文件修改的行数
            total_lines_info[fileType].append(total_lines_count)
            total_lines_info["all"].append(total_lines_count)
            # if fileType not in total_char_info:
            #     total_char_info[fileType] = {}
            # if "all" not in total_char_info:
            #     total_char_info["all"] = {}

            # 单commit中，所有文件的字符变化
            total_char_info[fileType].setdefault(total_lines_char_avg, 0)
            total_char_info[fileType][total_lines_char_avg] += 1
            total_char_info["all"].setdefault(total_lines_char_avg, 0)
            total_char_info["all"][total_lines_char_avg] += 1
            # 单commit中，所有文件的行数变化
            file_rows_info[fileType].setdefault(file_row_change, 0)
            file_rows_info[fileType][file_row_change] += 1
            file_rows_info["all"].setdefault(file_row_change, 0)
            file_rows_info["all"][file_row_change] += 1

            # if fileType == "py":
            #     newResult = parse_python(newFileContent)
            #     oldResult = parse_python(oldFileContent)
            if fileType == "java":
                newResult = parse_java(newFileContent)
                oldResult = parse_java(oldFileContent)
            # elif fileType == "c":
            #     newResult = parse_c(newFileContent)
            #     oldResult = parse_c(oldFileContent)
            # elif fileType == "cpp":
            #     newResult = parse_cpp(newFileContent)
            #     oldResult = parse_cpp(oldFileContent)
            # elif fileType == "js":
            #     newResult = parse_js(newFileContent)
            #     oldResult = parse_js(oldFileContent)
            else:
                continue
            # pprint(newResult)
            # pprint(oldResult)
            for method in oldResult:
                oldCircle = oldResult[method].get("circle", 1)
                oldParams = oldResult[method].get("params", [])
                oldMethodRows = oldResult[method].get("rows", 0)
                oldParamsCount = len(oldParams)
                if method in newResult:
                    newCircle = newResult[method].get("circle", 1)
                    newParams = newResult[method].get("params", [])
                    newMethodRows = newResult[method].get("rows", 0)
                    newParamsCount = len(newParams)
                    # if fileType not in params_info:
                    #     params_info[fileType] = {}
                    # if "all" not in params_info:
                    #     params_info["all"] = {}
                    # if fileType not in circle_info:
                    #     circle_info[fileType] = {}
                    # if "all" not in circle_info:
                    #     circle_info["all"] = {}
                    params_info_key = f"{oldParamsCount}_{newParamsCount}"
                    params_info[fileType].setdefault(params_info_key, 0)
                    params_info["all"].setdefault(params_info_key, 0)
                    params_info[fileType][params_info_key] += 1
                    params_info["all"][params_info_key] += 1

                    circle_info_key = f"{oldCircle}_{newCircle}"
                    circle_info[fileType].setdefault(circle_info_key, 0)
                    circle_info["all"].setdefault(circle_info_key, 0)
                    circle_info[fileType][circle_info_key] += 1
                    circle_info["all"][circle_info_key] += 1

                    row_info_key = f"{oldMethodRows}_{newMethodRows}"
                    method_rows_info[fileType].setdefault(row_info_key, 0)
                    method_rows_info["all"].setdefault(row_info_key, 0)
                    method_rows_info[fileType][row_info_key] += 1
                    method_rows_info["all"][row_info_key] += 1

        data = {
            "params_info"     : params_info,
            "circle_info"     : circle_info,
            "total_lines_info": total_lines_info,
            "total_char_info" : total_char_info,
            "method_rows_info": method_rows_info,
            "file_rows_info"  : file_rows_info,
            "analysis"        : time.strftime("%Y-%m-%d %H:%M:%S")
        }
        # pprint(data)
        commit_collection.update_one({"_id": mongo_id}, {"$set": data})


def summary(repository, language: str = "all", start_time: str = None, end_time: str = None):
    """
    :param repository: 仓库名称
    :param language: 语言
    :param start_time: 开始时间 2021-01-01
    :param end_time: 结束时间 2022-01-01
    """
    # 校验参数格式
    if start_time:
        assert re.match(r"\d{4}-\d{2}-\d{2}", start_time) is not None, "start_time格式错误"
    if end_time:
        assert re.match(r"\d{4}-\d{2}-\d{2}", end_time) is not None, "end_time格式错误"
    # 校验参数大小
    if start_time and end_time:
        assert start_time <= end_time, "start_time不能大于end_time"
    # 查询数据
    query = {"repository": repository, "analysis": {"$exists": True}}
    if start_time and not end_time:
        query["release_time"] = {"$gte": start_time}
    if end_time and not start_time:
        query["release_time"] = {"$lte": end_time}
    if start_time and end_time:
        query["$and"] = [
            {"release_time": {"$gte": start_time}},
            {"release_time": {"$lte": end_time}}
        ]
    # 统计数据
    all_params_info = {}
    all_circle_info = {}
    all_total_lines_info = []
    all_total_char_info = {}
    all_method_rows_info = {}
    all_file_rows_info = {}
    commits = commit_collection.find(query, {"params_info": 1, "circle_info": 1, "total_lines_info": 1, "total_char_info": 1, "method_rows_info": 1, "file_rows_info": 1})
    for commit in commits:
        params_info = commit.get("params_info", {}).get(language, {})
        circle_info = commit.get("circle_info", {}).get(language, {})
        total_lines_info = commit.get("total_lines_info", {}).get(language, [])
        total_char_info = commit.get("total_char_info", {}).get(language, {})
        method_rows_info = commit.get("method_rows_info", {}).get(language, {})
        file_rows_info = commit.get("file_rows_info", {}).get(language, {})
        for key in params_info:
            all_params_info.setdefault(key, 0)
            all_params_info[key] += params_info[key]
        for key in circle_info:
            all_circle_info.setdefault(key, 0)
            all_circle_info[key] += circle_info[key]
        all_total_lines_info.extend(total_lines_info)
        for key in total_char_info:
            all_total_char_info.setdefault(key, 0)
            all_total_char_info[key] += total_char_info[key]
        for key in method_rows_info:
            all_method_rows_info.setdefault(key, 0)
            all_method_rows_info[key] += method_rows_info[key]
        for key in file_rows_info:
            all_file_rows_info.setdefault(key, 0)
            all_file_rows_info[key] += file_rows_info[key]
    # 输出数据
    total_lines_info_counter = Counter(all_total_lines_info)
    total_lines_info_counter = sorted(total_lines_info_counter.items(), key=lambda x: x[0])
    # print("all_params_info", all_params_info)
    # print("all_circle_info", all_circle_info)
    # print("all_total_char_info", all_total_char_info)
    # print("total_lines_info_counter", total_lines_info_counter)
    # 计算函数参数变化百分比
    params_info_increase_count = 0
    params_info_decrease_count = 0
    params_info_no_change_count = 0
    for key in all_params_info:
        old_count, new_count = key.split("_")
        old_count = int(old_count)
        new_count = int(new_count)
        if old_count == new_count:
            params_info_no_change_count += all_params_info[key]
        elif old_count < new_count:
            params_info_increase_count += all_params_info[key]
        else:
            params_info_decrease_count += all_params_info[key]
    all_params_info_count = params_info_increase_count + params_info_decrease_count + params_info_no_change_count
    params_info_increase_percent = params_info_increase_count / all_params_info_count if all_params_info_count else 0
    params_info_decrease_percent = params_info_decrease_count / all_params_info_count if all_params_info_count else 0
    params_info_no_change_percent = params_info_no_change_count / all_params_info_count if all_params_info_count else 0

    # 计算圈复杂度变化百分比
    circle_info_increase_count = 0
    circle_info_decrease_count = 0
    circle_info_no_change_count = 0
    for key in all_circle_info:
        old_count, new_count = key.split("_")
        old_count = int(old_count)
        new_count = int(new_count)
        if old_count == new_count:
            circle_info_no_change_count += all_circle_info[key]
        elif old_count < new_count:
            circle_info_increase_count += all_circle_info[key]
        else:
            circle_info_decrease_count += all_circle_info[key]
    all_circle_info_count = circle_info_increase_count + circle_info_decrease_count + circle_info_no_change_count
    circle_info_increase_percent = circle_info_increase_count / all_circle_info_count if all_circle_info_count else 0
    circle_info_decrease_percent = circle_info_decrease_count / all_circle_info_count if all_circle_info_count else 0
    circle_info_no_change_percent = circle_info_no_change_count / all_circle_info_count if all_circle_info_count else 0

    # 计算修改行数变化百分比
    total_lines_info_counter_increase_count = 0
    total_lines_info_counter_decrease_count = 0
    total_lines_info_counter_no_change_count = 0
    for key, value in total_lines_info_counter:
        if key == 0:
            total_lines_info_counter_no_change_count += value
        elif key > 0:
            total_lines_info_counter_increase_count += value
        else:
            total_lines_info_counter_decrease_count += value
    total_lines_info_counter_all_count = sum([value for key, value in total_lines_info_counter])
    total_lines_info_counter_increase_percent = total_lines_info_counter_increase_count / total_lines_info_counter_all_count if total_lines_info_counter_all_count else 0
    total_lines_info_counter_decrease_percent = total_lines_info_counter_decrease_count / total_lines_info_counter_all_count if total_lines_info_counter_all_count else 0
    total_lines_info_counter_no_change_percent = total_lines_info_counter_no_change_count / total_lines_info_counter_all_count if total_lines_info_counter_all_count else 0

    # 计算字符变化百分比
    total_char_info_increase_count = 0
    total_char_info_decrease_count = 0
    total_char_info_no_change_count = 0
    for key in all_total_char_info:
        old_count, new_count = key.split("_")
        old_count = int(old_count)
        new_count = int(new_count)
        if old_count == new_count:
            total_char_info_no_change_count += all_total_char_info[key]
        elif old_count < new_count:
            total_char_info_increase_count += all_total_char_info[key]
        else:
            total_char_info_decrease_count += all_total_char_info[key]
    all_total_char_info_all_count = sum([total_char_info_increase_count, total_char_info_decrease_count, total_char_info_no_change_count])
    total_char_info_increase_percent = total_char_info_increase_count / all_total_char_info_all_count if all_total_char_info_all_count else 0
    total_char_info_decrease_percent = total_char_info_decrease_count / all_total_char_info_all_count if all_total_char_info_all_count else 0
    total_char_info_no_change_percent = total_char_info_no_change_count / all_total_char_info_all_count if all_total_char_info_all_count else 0

    # 计算函数行数百分比
    total_method_rows_info_increase_count = 0
    total_method_rows_info_decrease_count = 0
    total_method_rows_info_no_change_count = 0
    for key in all_method_rows_info:
        old_count, new_count = key.split("_")
        old_count = int(old_count)
        new_count = int(new_count)
        if old_count == new_count:
            total_method_rows_info_no_change_count += all_method_rows_info[key]
        elif old_count < new_count:
            total_method_rows_info_increase_count += all_method_rows_info[key]
        else:
            total_method_rows_info_decrease_count += all_method_rows_info[key]
    all_method_rows_info_all_count = sum([total_method_rows_info_increase_count, total_method_rows_info_decrease_count, total_method_rows_info_no_change_count])
    total_method_rows_info_increase_percent = total_method_rows_info_increase_count / all_method_rows_info_all_count if all_method_rows_info_all_count else 0
    total_method_rows_info_decrease_percent = total_method_rows_info_decrease_count / all_method_rows_info_all_count if all_method_rows_info_all_count else 0
    total_method_rows_info_no_change_percent = total_method_rows_info_no_change_count / all_method_rows_info_all_count if all_method_rows_info_all_count else 0

    # 计算文件行数百分比
    total_file_rows_info_increase_count = 0
    total_file_rows_info_decrease_count = 0
    total_file_rows_info_no_change_count = 0
    for key in all_file_rows_info:
        old_count, new_count = key.split("_")
        old_count = int(old_count)
        new_count = int(new_count)
        if old_count == new_count:
            total_file_rows_info_no_change_count += all_file_rows_info[key]
        elif old_count < new_count:
            total_file_rows_info_increase_count += all_file_rows_info[key]
        else:
            total_file_rows_info_decrease_count += all_file_rows_info[key]
    all_file_rows_info_all_count = sum([total_file_rows_info_increase_count, total_file_rows_info_decrease_count, total_file_rows_info_no_change_count])
    total_file_rows_info_increase_percent = total_file_rows_info_increase_count / all_file_rows_info_all_count if all_file_rows_info_all_count else 0
    total_file_rows_info_decrease_percent = total_file_rows_info_decrease_count / all_file_rows_info_all_count if all_file_rows_info_all_count else 0
    total_file_rows_info_no_change_percent = total_file_rows_info_no_change_count / all_file_rows_info_all_count if all_file_rows_info_all_count else 0

    all_methods_count = sum(all_params_info.values())
    print(f"仓库: {repository} 语言: {language} 相关函数总数: {all_methods_count}")
    if start_time:
        print(f"开始时间: {start_time}")
    if end_time:
        print(f"结束时间: {end_time}")

    print("\n函数层面统计:")
    print(f"参数个数增加: {params_info_increase_count} ({params_info_increase_percent:.2%})")
    print(f"参数个数减少: {params_info_decrease_count} ({params_info_decrease_percent:.2%})")
    print(f"参数个数不变: {params_info_no_change_count} ({params_info_no_change_percent:.2%})")
    all_params_info = sorted(all_params_info.items(), key=lambda x: x[1], reverse=True)
    for params, count in all_params_info:
        old_params, new_params = params.split("_")
        print(f"函数参数变化: {old_params} -> {new_params} 数量: {count}")

    print(f"\n函数圈复杂度增加: {circle_info_increase_count} ({circle_info_increase_percent:.2%})")
    print(f"函数圈复杂度减少: {circle_info_decrease_count} ({circle_info_decrease_percent:.2%})")
    print(f"函数圈复杂度不变: {circle_info_no_change_count} ({circle_info_no_change_percent:.2%})")
    all_circle_info = sorted(all_circle_info.items(), key=lambda x: x[1], reverse=True)
    for circle, count in all_circle_info:
        old_circle, new_circle = circle.split("_")
        print(f"函数圈复杂度变化: {old_circle} -> {new_circle} 数量: {count}")

    print(f"\n函数行数增加: {total_method_rows_info_increase_count} ({total_method_rows_info_increase_percent:.2%})")
    print(f"函数行数减少: {total_method_rows_info_decrease_count} ({total_method_rows_info_decrease_percent:.2%})")
    print(f"函数行数不变: {total_method_rows_info_no_change_count} ({total_method_rows_info_no_change_percent:.2%})")
    all_method_rows_info = sorted(all_method_rows_info.items(), key=lambda x: x[1], reverse=True)
    for rows, count in all_method_rows_info:
        old_rows, new_rows = rows.split("_")
        print(f"函数行数变化: {old_rows} -> {new_rows} 数量: {count}")

    print(f"\n代码层面统计 有{len(all_total_lines_info)}个文件进行了修改\n")
    print(f"代码行数增加: {total_lines_info_counter_increase_count} ({total_lines_info_counter_increase_percent:.2%})")
    print(f"代码行数减少: {total_lines_info_counter_decrease_count} ({total_lines_info_counter_decrease_percent:.2%})")
    print(f"代码行数不变: {total_lines_info_counter_no_change_count} ({total_lines_info_counter_no_change_percent:.2%})")
    for line_change, count in total_lines_info_counter:
        if line_change > 0:
            print(f"其中有{count}个文件行数新增了{line_change}行")
        elif line_change < 0:
            print(f"其中有{count}个文件行数减少了{-line_change}行")
        else:
            print(f"其中有{count}个文件行数是持平的")
    print()
    print(f"代码字符数增加: {total_char_info_increase_count} ({total_char_info_increase_percent:.2%})")
    print(f"代码字符数减少: {total_char_info_decrease_count} ({total_char_info_decrease_percent:.2%})")
    print(f"代码字符数不变: {total_char_info_no_change_count} ({total_char_info_no_change_percent:.2%})")
    all_total_char_info = sorted(all_total_char_info.items(), key=lambda x: x[1], reverse=True)
    for char_change, count in all_total_char_info:
        old_char, new_char = char_change.split("_")
        change = int(new_char) - int(old_char)
        if change > 0:
            print(f"其中有{count}个文件 之前平均每行{old_char}个字符 现在平均每行{new_char}个字符 增加了{change}个字符")
        elif change < 0:
            print(f"其中有{count}个文件 之前平均每行{old_char}个字符 现在平均每行{new_char}个字符 减少了{-change}个字符")
        else:
            print(f"其中有{count}个文件 之前平均每行{old_char}个字符 现在平均每行{new_char}个字符 没有变化")

    print(f"\n文件层面行数统计 \n")
    print(f"总代码行数增加: {total_file_rows_info_increase_count} ({total_file_rows_info_increase_percent:.2%})")
    print(f"总代码行数减少: {total_file_rows_info_decrease_count} ({total_file_rows_info_decrease_percent:.2%})")
    print(f"总代码行数不变: {total_file_rows_info_no_change_count} ({total_file_rows_info_no_change_percent:.2%})")
    all_file_rows_info = sorted(all_file_rows_info.items(), key=lambda x: x[1], reverse=True)
    for rows, count in all_file_rows_info:
        old_rows, new_rows = rows.split("_")
        print(f"文件行数变化: {old_rows} -> {new_rows} 数量: {count}")


def threshold(
    repository, language: str = "all", start_time: str = None, end_time: str = None,
    params: int = None, circle: int = None, lines: int = None, chars: int = None, method_rows: int = None,
    file_rows: int = None):
    """
    :param repository: 仓库名称
    :param language: 语言
    :param start_time: 开始时间 2021-01-01
    :param end_time: 结束时间 2022-01-01
    :param params: 参数变化阈值
    :param circle: 圈复杂度变化阈值
    :param lines: 修改代码行数变化阈值
    :param chars: 修改代码字符数变化阈值
    :param method_rows: 函数行数变化阈值
    :param file_rows: 文件行数变化阈值
    """
    # 校验参数格式
    if start_time:
        assert re.match(r"\d{4}-\d{2}-\d{2}", start_time) is not None, "start_time格式错误"
    if end_time:
        assert re.match(r"\d{4}-\d{2}-\d{2}", end_time) is not None, "end_time格式错误"
    # 校验参数大小
    if start_time and end_time:
        assert start_time <= end_time, "start_time不能大于end_time"
    # 查询数据
    query = {"repository": repository, "analysis": {"$exists": True}}
    if start_time and not end_time:
        query["release_time"] = {"$gte": start_time}
    if end_time and not start_time:
        query["release_time"] = {"$lte": end_time}
    if start_time and end_time:
        query["$and"] = [
            {"release_time": {"$gte": start_time}},
            {"release_time": {"$lte": end_time}}
        ]
    # 统计数据
    all_params_info = {}
    all_circle_info = {}
    all_total_lines_info = []
    all_total_char_info = {}
    all_method_rows_info = {}
    all_file_rows_info = {}
    # commits = commit_collection.find(query)
    # for commit in commits:
    #     print(commit)
    commits = commit_collection.find(query, {"params_info": 1, "circle_info": 1, "total_lines_info": 1, "total_char_info": 1, "method_rows_info": 1, "file_rows_info": 1})
    for commit in commits:
        params_info = commit.get("params_info", {}).get(language, {})
        circle_info = commit.get("circle_info", {}).get(language, {})
        total_lines_info = commit.get("total_lines_info", {}).get(language, [])
        total_char_info = commit.get("total_char_info", {}).get(language, {})
        method_rows_info = commit.get("method_rows_info", {}).get(language, {})
        file_rows_info = commit.get("file_rows_info", {}).get(language, {})
        for key in params_info:
            all_params_info.setdefault(key, 0)
            all_params_info[key] += params_info[key]
        for key in circle_info:
            all_circle_info.setdefault(key, 0)
            all_circle_info[key] += circle_info[key]
        all_total_lines_info.extend(total_lines_info)
        for key in total_char_info:
            all_total_char_info.setdefault(key, 0)
            all_total_char_info[key] += total_char_info[key]
        for key in method_rows_info:
            all_method_rows_info.setdefault(key, 0)
            all_method_rows_info[key] += method_rows_info[key]
        for key in file_rows_info:
            all_file_rows_info.setdefault(key, 0)
            all_file_rows_info[key] += file_rows_info[key]
    # 输出数据
    total_lines_info_counter = Counter(all_total_lines_info)
    total_lines_info_counter = sorted(total_lines_info_counter.items(), key=lambda x: x[0])
    # print("all_params_info", all_params_info)
    # print("all_circle_info", all_circle_info)
    # print("all_total_char_info", all_total_char_info)
    # print("total_lines_info_counter", total_lines_info_counter)
    # print("all_method_rows_info", all_method_rows_info)
    # print("all_file_rows_info", all_file_rows_info)
    # 处理参数变化
    if params:
        params_nn = 0
        params_yn = 0
        params_ny = 0
        params_yy = 0
        params_info = sorted(all_params_info.items(), key=lambda x: x[1], reverse=True)
        for key, count in params_info:
            old_params, new_params = key.split("_")
            old_params = int(old_params)
            new_params = int(new_params)
            if old_params > params:
                if new_params > params:
                    print(f"参数修改前后数量都不符合规范: {old_params} -> {new_params} 数量: {count}")
                    params_nn += count
                else:
                    print(f"参数修改前数量符合规范，修改后不符合规范: {old_params} -> {new_params} 数量: {count}")
                    params_yn += count
            else:
                if new_params > params:
                    print(f"参数修改前数量不符合规范，修改后符合规范: {old_params} -> {new_params} 数量: {count}")
                    params_ny += count
                else:
                    print(f"参数修改前后数量都符合规范: {old_params} -> {new_params} 数量: {count}")
                    params_yy += count
        print(f"参数修改前后数量都不符合规范: {params_nn}")
        print(f"参数修改前数量符合规范，修改后不符合规范: {params_yn}")
        print(f"参数修改前数量不符合规范，修改后符合规范: {params_ny}")
        print(f"参数修改前后数量都符合规范: {params_yy}")
    if circle:
        circle_nn = 0
        circle_yn = 0
        circle_ny = 0
        circle_yy = 0
        circle_info = sorted(all_circle_info.items(), key=lambda x: x[1], reverse=True)
        for key, count in circle_info:
            old_circle, new_circle = key.split("_")
            old_circle = int(old_circle)
            new_circle = int(new_circle)
            if old_circle > circle:
                if new_circle > circle:
                    print(f"函数圈复杂度修改前后都不符合规范: {old_circle} -> {new_circle} 数量: {count}")
                    circle_nn += count
                else:
                    print(f"函数圈复杂度修改前符合规范，修改后不符合规范: {old_circle} -> {new_circle} 数量: {count}")
                    circle_yn += count
            else:
                if new_circle > circle:
                    print(f"函数圈复杂度修改前不符合规范，修改后符合规范: {old_circle} -> {new_circle} 数量: {count}")
                    circle_ny += count
                else:
                    print(f"函数圈复杂度修改前后都符合规范: {old_circle} -> {new_circle} 数量: {count}")
                    circle_yy += count
        print(f"函数圈复杂度修改前后都不符合规范: {circle_nn}")
        print(f"函数圈复杂度修改前符合规范，修改后不符合规范: {circle_yn}")
        print(f"函数圈复杂度修改前不符合规范，修改后符合规范: {circle_ny}")
        print(f"函数圈复杂度修改前后都符合规范: {circle_yy}")
    if lines:
        lines_no = 0
        lines_yes = 0
        lines_info = sorted(total_lines_info_counter, key=lambda x: x[1], reverse=True)
        for key, count in lines_info:
            if key > lines:
                print(f"代码行数不符合规范: {key} 数量: {count}")
                lines_no += count
            else:
                print(f"代码行数符合规范: {key} 数量: {count}")
                lines_yes += count
        print(f"代码行数不符合规范: {lines_no}")
        print(f"代码行数符合规范: {lines_yes}")
    if chars:
        chars_nn = 0
        chars_yn = 0
        chars_ny = 0
        chars_yy = 0
        char_info = sorted(all_total_char_info.items(), key=lambda x: x[1], reverse=True)
        for key, count in char_info:
            old_char, new_char = key.split("_")
            old_char = int(old_char)
            new_char = int(new_char)
            if old_char > chars:
                if new_char > chars:
                    print(f"代码字符数修改前后都不符合规范: {old_char} -> {new_char} 数量: {count}")
                    chars_nn += count
                else:
                    print(f"代码字符数修改前符合规范，修改后不符合规范: {old_char} -> {new_char} 数量: {count}")
                    chars_yn += count
            else:
                if new_char > chars:
                    print(f"代码字符数修改前不符合规范，修改后符合规范: {old_char} -> {new_char} 数量: {count}")
                    chars_ny += count
                else:
                    print(f"代码字符数修改前后都符合规范: {old_char} -> {new_char} 数量: {count}")
                    chars_yy += count
        print(f"代码字符数修改前后都不符合规范: {chars_nn}")
        print(f"代码字符数修改前符合规范，修改后不符合规范: {chars_yn}")
        print(f"代码字符数修改前不符合规范，修改后符合规范: {chars_ny}")
        print(f"代码字符数修改前后都符合规范: {chars_yy}")
    if method_rows:
        method_rows_nn = 0
        method_rows_yn = 0
        method_rows_ny = 0
        method_rows_yy = 0
        method_rows_info = sorted(all_method_rows_info.items(), key=lambda x: x[1], reverse=True)
        for key, count in method_rows_info:
            old_method_rows, new_method_rows = key.split("_")
            old_method_rows = int(old_method_rows)
            new_method_rows = int(new_method_rows)
            if old_method_rows > method_rows:
                if new_method_rows > method_rows:
                    print(f"函数行数修改前后都不符合规范: {old_method_rows} -> {new_method_rows} 数量: {count}")
                    method_rows_nn += count
                else:
                    print(f"函数行数修改前符合规范，修改后不符合规范: {old_method_rows} -> {new_method_rows} 数量: {count}")
                    method_rows_yn += count
            else:
                if new_method_rows > method_rows:
                    print(f"函数行数修改前不符合规范，修改后符合规范: {old_method_rows} -> {new_method_rows} 数量: {count}")
                    method_rows_ny += count
                else:
                    print(f"函数行数修改前后都符合规范: {old_method_rows} -> {new_method_rows} 数量: {count}")
                    method_rows_yy += count
        print(f"函数行数修改前后都不符合规范: {method_rows_nn}")
        print(f"函数行数修改前符合规范，修改后不符合规范: {method_rows_yn}")
        print(f"函数行数修改前不符合规范，修改后符合规范: {method_rows_ny}")
        print(f"函数行数修改前后都符合规范: {method_rows_yy}")
    if file_rows:
        file_rows_nn = 0
        file_rows_yn = 0
        file_rows_ny = 0
        file_rows_yy = 0
        file_rows_info = sorted(all_file_rows_info.items(), key=lambda x: x[1], reverse=True)
        for key, count in file_rows_info:
            old_file_rows, new_file_rows = key.split("_")
            old_file_rows = int(old_file_rows)
            new_file_rows = int(new_file_rows)
            if old_file_rows > file_rows:
                if new_file_rows > file_rows:
                    print(f"文件行数修改前后都不符合规范: {old_file_rows} -> {new_file_rows} 数量: {count}")
                    file_rows_nn += count
                else:
                    print(f"文件行数修改前符合规范，修改后不符合规范: {old_file_rows} -> {new_file_rows} 数量: {count}")
                    file_rows_yn += count
            else:
                if new_file_rows > file_rows:
                    print(f"文件行数修改前不符合规范，修改后符合规范: {old_file_rows} -> {new_file_rows} 数量: {count}")
                    file_rows_ny += count
                else:
                    print(f"文件行数修改前后都符合规范: {old_file_rows} -> {new_file_rows} 数量: {count}")
                    file_rows_yy += count
        print(f"文件行数修改前后都不符合规范: {file_rows_nn}")
        print(f"文件行数修改前符合规范，修改后不符合规范: {file_rows_yn}")
        print(f"文件行数修改前不符合规范，修改后符合规范: {file_rows_ny}")
        print(f"文件行数修改前后都符合规范: {file_rows_yy}")


def threshold_detail(
    repository, language: str = "all", start_time: str = None, end_time: str = None,
    params: int = None, circle: int = None, lines: int = None, chars: int = None, method_rows: int = None,
    file_rows: int = None):
    """
    :param repository: 仓库名称
    :param language: 语言
    :param start_time: 开始时间 2021-01-01
    :param end_time: 结束时间 2022-01-01
    :param params: 参数变化阈值
    :param circle: 圈复杂度变化阈值
    :param lines: 修改代码行数变化阈值
    :param chars: 修改代码字符数变化阈值
    :param method_rows: 函数行数变化阈值
    :param file_rows: 文件行数变化阈值
    """
    # 校验参数格式
    if start_time:
        assert re.match(r"\d{4}-\d{2}-\d{2}", start_time) is not None, "start_time格式错误"
    if end_time:
        assert re.match(r"\d{4}-\d{2}-\d{2}", end_time) is not None, "end_time格式错误"
    # 校验参数大小
    if start_time and end_time:
        assert start_time <= end_time, "start_time不能大于end_time"
    # 查询数据
    query = {"repository": repository, "analysis": {"$exists": True}}
    if start_time and not end_time:
        query["release_time"] = {"$gte": start_time}
    if end_time and not start_time:
        query["release_time"] = {"$lte": end_time}
    if start_time and end_time:
        query["$and"] = [
            {"release_time": {"$gte": start_time}},
            {"release_time": {"$lte": end_time}}
        ]
    commits = commit_collection.find(query)
    total_write_lines = []
    total_json_right_data = []
    total_json_wrong_data = []
    for commit in commits:
        info_lines = []
        commit_write_lines = []
        mongoId = commit["_id"]
        commit_sha = commit["commit_sha"]
        info_lines.append(">" * 100 + "\n")
        info_lines.append(f"{repository} {commit_sha} {mongoId}\n")
        print(f"{repository} {commit_sha} {mongoId}")
        datas = commit["datas"]
        # print(len(datas))
        for data in datas:
            mainFlag = 0
            write_lines = []
            fileName = data["fileName"]
            fileType = fileName.split(".")[-1]
            patch = data.get("patch", "")
            newFileContent = data["newFileContent"]
            oldFileContent = data["oldFileContent"]
            if fileType not in suffix_list:
                continue
            if language != "all" and fileType != language:
                continue
            total_lines_count, total_lines_char_avg, file_row_change = parse_patch(patch, oldFileContent, newFileContent)
            if lines:
                if total_lines_count > lines:
                    write_lines.append(f"代码行数不符合规范: {total_lines_count}\n")
                    mainFlag = -1
            if chars:
                old_char, new_char = total_lines_char_avg.split("_")
                old_char = int(old_char)
                new_char = int(new_char)
                if old_char <= chars < new_char:
                    write_lines.append(f"字符数量修改前符合规范，修改后不符合规范: {old_char} -> {new_char} \n")
                    mainFlag = -1
                if old_char > chars >= new_char:
                    write_lines.append(f"字符数量修改前不符合规范，修改后符合规范: {old_char} -> {new_char} \n")
                    mainFlag = 1
            if file_rows:
                old_file_rows, new_file_rows = file_row_change.split("_")
                print(old_file_rows, new_file_rows)
                old_file_rows = int(old_file_rows)
                new_file_rows = int(new_file_rows)
                if old_file_rows <= file_rows < new_file_rows:
                    write_lines.append(f"文件行数修改前符合规范，修改后不符合规范: {old_file_rows} -> {new_file_rows} \n")
                    mainFlag = -1
                if old_file_rows > file_rows >= new_file_rows:
                    write_lines.append(f"文件行数修改前不符合规范，修改后符合规范: {old_file_rows} -> {new_file_rows} \n")
                    mainFlag = 1
            if fileType == "py":
                newResult = parse_python(newFileContent)
                oldResult = parse_python(oldFileContent)
            elif fileType == "java":
                newResult = parse_java(newFileContent)
                oldResult = parse_java(oldFileContent)
            elif fileType == "c":
                newResult = parse_c(newFileContent)
                oldResult = parse_c(oldFileContent)
            elif fileType == "cpp":
                newResult = parse_cpp(newFileContent)
                oldResult = parse_cpp(oldFileContent)
            elif fileType == "js":
                newResult = parse_js(newFileContent)
                oldResult = parse_js(oldFileContent)
            else:
                newResult = {}
                oldResult = {}
            for method in oldResult:
                flag = False
                if method not in newResult:
                    continue
                oldCircle = oldResult[method].get("circle", 1)
                oldCircleStatement = oldResult[method].get("circle_statements", [])
                oldParams = oldResult[method].get("params", [])
                oldMethodRows = oldResult[method].get("rows", 0)
                oldParamsCount = len(oldParams)
                oldMethodStart = oldResult[method].get("start", 0)

                newCircle = newResult[method].get("circle", 1)
                newCircleStatement = newResult[method].get("circle_statements", [])
                newParams = newResult[method].get("params", [])
                newMethodRows = newResult[method].get("rows", 0)
                newParamsCount = len(newParams)
                newMethodStart = newResult[method].get("start", 0)
                prefix = f"函数：{method}\n"
                if params:
                    if oldParamsCount <= params < newParamsCount:
                        write_lines.append(f"{prefix}参数数量修改前符合规范，修改后不符合规范: {oldParamsCount} -> {newParamsCount}\n")
                    if oldParamsCount > params >= newParamsCount:
                        write_lines.append(f"{prefix}参数数量修改前不符合规范，修改后符合规范: {oldParamsCount} -> {newParamsCount}\n")
                        flag = True
                if circle:
                    if oldCircle <= circle < newCircle:
                        write_lines.append(f"{prefix}圈复杂度修改前符合规范，修改后不符合规范: {oldCircle} -> {newCircle}\n")
                    if oldCircle > circle >= newCircle:
                        write_lines.append(f"{prefix}圈复杂度修改前不符合规范，修改后符合规范: {oldCircle} -> {newCircle}\n")
                        flag = True
                if method_rows:
                    if oldMethodRows <= method_rows < newMethodRows:
                        write_lines.append(f"{prefix}函数行数修改前符合规范，修改后不符合规范: {oldMethodRows} -> {newMethodRows}\n")
                    if oldMethodRows > method_rows >= newMethodRows:
                        write_lines.append(f"{prefix}函数行数修改前不符合规范，修改后符合规范: {oldMethodRows} -> {newMethodRows}\n")
                        flag = True
                if write_lines:
                    json_data = {
                        "repository"        : repository,
                        "commit_sha"        : commit_sha,
                        "mongoId"           : str(mongoId),
                        "fileName"          : fileName,
                        "oldFileContent"    : oldFileContent,
                        "newFileContent"    : newFileContent,
                        "patch"             : patch,
                        "method"            : method,
                        "oldCircle"         : oldCircle,
                        "newCircle"         : newCircle,
                        "oldCircleStatement": oldCircleStatement,
                        "newCircleStatement": newCircleStatement,
                        "oldParams"         : oldParams,
                        "newParams"         : newParams,
                        "oldMethodRows"     : oldMethodRows,
                        "newMethodRows"     : newMethodRows,
                        "oldMethodStart"    : oldMethodStart,
                        "newMethodStart"    : newMethodStart,
                        "description"       : "".join(write_lines)
                    }
                    if flag:
                        total_json_right_data.append(json_data)
                    else:
                        total_json_wrong_data.append(json_data)
            if write_lines:
                commit_write_lines.append(f"文件名: {fileName}\n")
                commit_write_lines.extend(write_lines)
                commit_write_lines.append("patch:\n")
                commit_write_lines.append(patch)
                commit_write_lines.append("\n")
                json_data = {
                    "repository"    : repository,
                    "commit_sha"    : commit_sha,
                    "mongoId"       : str(mongoId),
                    "fileName"      : fileName,
                    "oldFileContent": oldFileContent,
                    "newFileContent": newFileContent,
                    "patch"         : patch,
                    "description"   : "".join(write_lines)
                }
                if mainFlag == 1:
                    total_json_right_data.append(json_data)
                elif mainFlag == -1:
                    total_json_wrong_data.append(json_data)
        if commit_write_lines:
            info_lines.extend(commit_write_lines)
            info_lines.append("<" * 100 + "\n")
            total_write_lines.extend(info_lines)
    with open("result.txt", "w", encoding="utf-8") as f:
        f.writelines(total_write_lines)
    with open("result_right_json.json", "w", encoding="utf-8") as f:
        json.dump(total_json_right_data, f)
    with open("result_wrong_json.json", "w", encoding="utf-8") as f:
        json.dump(total_json_wrong_data, f)


def threshold_detail_with_message(
    repository, language: str = "all", start_time: str = None, end_time: str = None,
    params: int = None, circle: int = None, lines: int = None, chars: int = None, method_rows: int = None,
    file_rows: int = None):
    """
    :param repository: 仓库名称
    :param language: 语言
    :param start_time: 开始时间 2021-01-01
    :param end_time: 结束时间 2022-01-01
    :param params: 参数变化阈值
    :param circle: 圈复杂度变化阈值
    :param lines: 修改代码行数变化阈值
    :param chars: 修改代码字符数变化阈值
    :param method_rows: 函数行数变化阈值
    :param file_rows: 文件行数变化阈值
    """
    # 校验参数格式
    if start_time:
        assert re.match(r"\d{4}-\d{2}-\d{2}", start_time) is not None, "start_time格式错误"
    if end_time:
        assert re.match(r"\d{4}-\d{2}-\d{2}", end_time) is not None, "end_time格式错误"
    # 校验参数大小
    if start_time and end_time:
        assert start_time <= end_time, "start_time不能大于end_time"
    # 查询数据
    query = {"repository": repository}
    if start_time and not end_time:
        query["release_time"] = {"$gte": start_time}
    if end_time and not start_time:
        query["release_time"] = {"$lte": end_time}
    if start_time and end_time:
        query["$and"] = [
            {"release_time": {"$gte": start_time}},
            {"release_time": {"$lte": end_time}}
        ]
    commits = commit_collection.find(query)
    total_right_lines = []
    total_wrong_lines = []
    pref = ">" * 20
    prex = "<" * 20
    for commit in commits:
        info_lines = []
        info_right_lines = []
        info_wrong_lines = []
        commit_right_lines = []
        commit_wrong_lines = []
        mongoId = commit["_id"]
        commit_sha = commit["commit_sha"]
        print(f"正在处理{repository} {commit_sha} {mongoId}")
        message = commit.get("message", "")
        # info_lines.append(prefix + "\n")
        info_lines.append(f"{pref} {repository} {commit_sha} {mongoId}\n")
        datas = commit.get("datas", [])
        for data in datas:
            if data == None:
                continue
            right_lines = []
            wrong_lines = []
            fileName = data["fileName"]
            fileType = fileName.split(".")[-1]
            patch = data.get("patch", "")
            newFileContent = data["newFileContent"]
            oldFileContent = data["oldFileContent"]
            if fileType not in suffix_list:
                continue
            if language != "all" and fileType != language:
                continue
            total_lines_count, total_lines_char_avg, file_row_change = parse_patch(patch, oldFileContent, newFileContent)
            if lines:
                if total_lines_count > lines:

                    wrong_lines.append(f"代码行数不符合规范: {total_lines_count}\n")
            if chars:
                old_char, new_char = total_lines_char_avg.split("_")
                old_char = int(old_char)
                new_char = int(new_char)
                if old_char <= chars < new_char:
                    wrong_lines.append(f"字符数量修改前符合规范，修改后不符合规范: {old_char} -> {new_char} \n")
                if old_char > chars >= new_char:
                    right_lines.append(f"字符数量修改前不符合规范，修改后符合规范: {old_char} -> {new_char} \n")
            if file_rows:
                old_file_rows, new_file_rows = file_row_change.split("_")
                old_file_rows = int(old_file_rows)
                new_file_rows = int(new_file_rows)
                if old_file_rows <= file_rows < new_file_rows:
                    wrong_lines.append(f"文件行数修改前符合规范，修改后不符合规范: {old_file_rows} -> {new_file_rows} \n")
                if old_file_rows > file_rows >= new_file_rows:
                    right_lines.append(f"文件行数修改前不符合规范，修改后符合规范: {old_file_rows} -> {new_file_rows} \n")

            # if fileType == "py":
            #     newResult = parse_python(newFileContent)
            #     oldResult = parse_python(oldFileContent)
            if fileType == "java":
                newResult = parse_java(newFileContent)
                oldResult = parse_java(oldFileContent)
            # elif fileType == "c":
            #     newResult = parse_c(newFileContent)
            #     oldResult = parse_c(oldFileContent)
            # elif fileType == "cpp":
            #     newResult = parse_cpp(newFileContent)
            #     oldResult = parse_cpp(oldFileContent)
            # elif fileType == "js":
            #     newResult = parse_js(newFileContent)
            #     oldResult = parse_js(oldFileContent)
            else:
                newResult = {}
                oldResult = {}
            for method in oldResult:
                oldCircle = oldResult[method].get("circle", 1)
                oldParams = oldResult[method].get("params", [])
                oldMethodRows = oldResult[method].get("rows", 0)
                oldParamsCount = len(oldParams)
                if method not in newResult:
                    continue
                newCircle = newResult[method].get("circle", 1)
                newParams = newResult[method].get("params", [])
                newMethodRows = newResult[method].get("rows", 0)
                newParamsCount = len(newParams)
                prefix = f"函数：{method}\n"
                if params:
                    if oldParamsCount <= params < newParamsCount:
                        wrong_lines.append(f"{prefix}参数修改前数量符合规范，修改后不符合规范: {oldParamsCount} -> {newParamsCount}\n")
                    if oldParamsCount > params >= newParamsCount:
                        right_lines.append(f"{prefix}参数修改前数量不符合规范，修改后符合规范: {oldParamsCount} -> {newParamsCount}\n")
                if circle:
                    if oldCircle <= circle < newCircle:
                        wrong_lines.append(f"{prefix}圈复杂度修改前符合规范，修改后不符合规范: {oldCircle} -> {newCircle}\n")
                    if oldCircle > circle >= newCircle:
                        right_lines.append(f"{prefix}圈复杂度修改前不符合规范，修改后符合规范: {oldCircle} -> {newCircle}\n")
                if method_rows:
                    if oldMethodRows <= method_rows < newMethodRows:
                        wrong_lines.append(f"{prefix}函数行数修改前符合规范，修改后不符合规范: {oldMethodRows} -> {newMethodRows}\n")
                    if oldMethodRows > method_rows >= newMethodRows:
                        right_lines.append(f"{prefix}函数行数修改前不符合规范，修改后符合规范: {oldMethodRows} -> {newMethodRows}\n")
            if right_lines:
                commit_right_lines.append(f"{pref} 文件名: {fileName}\n")
                commit_right_lines.append(f"{message}\n")
                # commit_right_lines.extend(right_lines)
                # commit_right_lines.append("patch:\n")
                # commit_right_lines.append(patch)
                # commit_right_lines.append("\n")
            if wrong_lines:
                commit_wrong_lines.append(f"{pref} 文件名: {fileName}\n")
                commit_wrong_lines.append(f"{message}\n")
                # commit_wrong_lines.extend(wrong_lines)
                # commit_wrong_lines.append("patch:\n")
                # commit_wrong_lines.append(patch)
                # commit_wrong_lines.append("\n")
        if commit_right_lines:
            info_right_lines.extend(info_lines)
            info_right_lines.extend(commit_right_lines)
            info_right_lines.append(prex + "\n")
            total_right_lines.extend(info_right_lines)
        if commit_wrong_lines:
            info_wrong_lines.extend(info_lines)
            info_wrong_lines.extend(commit_wrong_lines)
            info_wrong_lines.append(prex + "\n")
            total_wrong_lines.extend(info_wrong_lines)
    if total_right_lines:
        with open("right.txt", "w", encoding="utf-8") as f:
            f.writelines(total_right_lines)
    if total_wrong_lines:
        with open("wrong.txt", "w", encoding="utf-8") as f:
            f.writelines(total_wrong_lines)


def search(repository, start_time=None, end_time=None):
    """
    :param repository: 仓库名称
    :param start_time: 开始时间 2021-01-01
    :param end_time: 结束时间 2022-01-01
    """
    # 校验参数格式

    if start_time:
        assert re.match(r"\d{4}-\d{2}-\d{2}", start_time) is not None, "start_time格式错误"
    if end_time:
        assert re.match(r"\d{4}-\d{2}-\d{2}", end_time) is not None, "end_time格式错误"
    # 校验参数大小
    if start_time and end_time:
        assert start_time <= end_time, "start_time不能大于end_time"
    # 获取最新的commit的sha
    latest_sha = get_first_commit(repository)
    if not latest_sha:
        return

    # 获取commit
    get_commits(repository, latest_sha, start_time, end_time)

def analysis_contributor(repository, start_time, end_time, flag):
    ### get data ###
    """
    :param repository: 仓库名称
    :param start_time: 开始时间 2021-01-01
    :param end_time: 结束时间 2022-01-01
    """
    # 校验参数格式
    if flag:
        if start_time:
            assert re.match(r"\d{4}-\d{2}-\d{2}", start_time) is not None, "start_time格式错误"
        if end_time:
            assert re.match(r"\d{4}-\d{2}-\d{2}", end_time) is not None, "end_time格式错误"
        # 校验参数大小
        if start_time and end_time:
            assert start_time <= end_time, "start_time不能大于end_time"
        # 获取最新的commit的sha
        latest_sha = get_first_commit(repository)
        if not latest_sha:
            return
        get_contributor(repository, latest_sha, start_time, end_time)
    else: 
        # analysis ###        
        project_real_contributor = {}

        # 获取满足查询条件的文档数量
        results = commit_collection.find({"repository": repository})

        for result in results:
            if start_time:
                if result['release_time'] < start_time:
                    continue
            if end_time:
                if result['release_time'] > end_time:
                    continue
            # if int(result['release_time'][:4]) >= 2022:
                # if result['committer'].lower() == 'github':
                #     continue
            if result['committer'].lower() not in project_real_contributor:
                project_real_contributor[result['committer'].lower()] = 1
            else:
                project_real_contributor[result['committer'].lower()] += 1
        project_real_contributor = sorted(project_real_contributor.items(), key=lambda x: x[1], reverse=True)    
        print(project_real_contributor)    

def update_contributor(repository, latest_sha, start_time, end_time):
    results = commit_collection.find({"repository": repository})
    for result in results:
        if start_time:
            if result['release_time'] < start_time:
                continue
        if end_time:
            if result['release_time'] > end_time:
                continue
        if 'committer' not in result and result['commit_sha'] == "499b7dbe844558b95567f8467c01c0ac3fccc873":
            # commit_sha = result.get("sha", "")
            # url = f"https://api.github.com/repos/{repository}/commits"
            # params = {
            #     "per_page": 100,
            #     "sha"     : commit_sha
            # }
            # response = get_response(url, params)
            # results = response.json()
            # if not results:
            #     return
            # for result in results:
            #     sha = result.get("sha", "")
            #     if commit_sha == sha:
            #         committer = result.get("commit", {}).get("committer", {}).get("name", {})
            commit_collection.update_one({"commit_sha": "499b7dbe844558b95567f8467c01c0ac3fccc873"}, {"$set": {"committer":  "zhangjidi2016"}})
                
        #     committer = result.get("commit", {}).get("committer", {}).get("name", {})
        #     # release_time = result.get("commit", {}).get("committer", {}).get("date", "")[:10]
        #     # commit_collection.update_one({"_id": mongo_id}, {"$set": {"download": time.strftime("%Y-%m-%d %H:%M:%S"), "message": message, "datas": datas}})
        # commit_collection.update_one({"commit_sha": commit_sha}, {"$set": {"committer":  committer}})
        
        
def get_contributor(repository, latest_sha, start_time, end_time):
    url = f"https://api.github.com/repos/{repository}/commits"
    params = {
        "per_page": 100,
        "sha"     : latest_sha
    }
    response = get_response(url, params)
    results = response.json()
    # pprint(results)
    if not results:
        return
    for result in results:
        commit_sha = result.get("sha", "")
        committer = result.get("commit", {}).get("committer", {}).get("name", {})
        release_time = result.get("commit", {}).get("committer", {}).get("date", "")[:10]
        if start_time:
            if release_time < start_time:
                return
        if end_time:
            if release_time > end_time:
                continue
        # release_time = result.get("commit", {}).get("committer", {}).get("date", "")[:10]
        # commit_collection.update_one({"_id": mongo_id}, {"$set": {"download": time.strftime("%Y-%m-%d %H:%M:%S"), "message": message, "datas": datas}})
        commit_collection.update_one({"commit_sha": commit_sha}, {"$set": {"committer":  committer}})
    last_sha = results[-1]["sha"]
    last_parents_sha = results[-1]["parents"]
    if last_parents_sha:
        get_contributor(repository, last_sha, start_time, end_time)

def analysis_age(repository):
    results = commit_collection.find({"repository": repository})
    yearSet = set()
    for result in results:
        release_time = result['release_time']
        # if start_time:
        #     if release_time < start_time:
        #         return
        # if end_time:
        #     if release_time > end_time:
        #         continue
        yearSet.add(int(release_time[:4]))
    print(yearSet)
        # commit_sha = result.get("sha", "")
        # url = f"https://api.github.com/repos/{repository}/commits"
        # params = {
        #     "per_page": 100,
        #     "sha"     : commit_sha
        # }
        # response = get_response(url, params)
        # results = response.json()
        # if not results:
        #     return

def analysis_variable(repository, start_time, end_time):
    """
    分析代码变量
    """
    # commits = commit_collection.find({"repository": repository, "download": {"$exists": True}, "analysis": {"$exists": False}})
    commits = commit_collection.find({"repository": repository, "download": {"$exists": True}})
    for commit in commits:
        datas = commit.get("datas", [])
        for data in datas:
            # fileName = data["fileName"]
            newFileContent = data["newFileContent"]
            oldFileContent = data["oldFileContent"]
            # print(newFileContent, oldFileContent)
            # 连接到运行中的 Java Gateway 服务
            gateway = JavaGateway()  # 默认连接本地的Gateway

            # 获取 Java 类
            java_parser_example = gateway.jvm.com.example.JavaParserExample()
            
            # 调用 Java 方法提取变量名
            variable_names = java_parser_example.extractVariableNames(newFileContent)

            print(variable_names)

def analysis_method(repository):
    """
    分析代码
    """
    commits = commit_collection.find({"repository": repository, "download": {"$exists": True}})
    # commits = commit_collection.find({"repository": repository, "download": {"$exists": True}})
    set_method = set()
    total_files = 0
    for commit in commits:
        mongo_id = commit["_id"]
        params_info = {}  # 参数信息
        circle_info = {}  # 圈复杂度信息
        total_lines_info = {}  # 行数变化信息
        total_char_info = {}  # 字符变化信息
        method_rows_info = {}  # 函数行数信息
        file_rows_info = {}  # 文件行数信息
        for keyword in keyword_list:
            params_info[keyword] = {}
            circle_info[keyword] = {}
            total_lines_info[keyword] = []
            total_char_info[keyword] = {}
            method_rows_info[keyword] = {}
            file_rows_info[keyword] = {}
        datas = commit.get("datas", [])
        for data in datas:
            if data == None:
                continue
            fileName = data["fileName"]
            fileType = fileName.split(".")[-1]
            patch = data.get("patch", "")
            newFileContent = data["newFileContent"]
            oldFileContent = data["oldFileContent"]
            # print(fileName)
            if fileType not in suffix_list:
                continue
            total_lines_count, total_lines_char_avg, file_row_change = parse_patch(patch, oldFileContent, newFileContent)
            # if fileType not in total_lines_info:
            #     total_lines_info[fileType] = []
            # if "all" not in total_lines_info:
            #     total_lines_info["all"] = []
            # 单commit中，所有文件修改的行数
            total_lines_info[fileType].append(total_lines_count)
            total_lines_info["all"].append(total_lines_count)
            # if fileType not in total_char_info:
            #     total_char_info[fileType] = {}
            # if "all" not in total_char_info:
            #     total_char_info["all"] = {}

            # 单commit中，所有文件的字符变化
            total_char_info[fileType].setdefault(total_lines_char_avg, 0)
            total_char_info[fileType][total_lines_char_avg] += 1
            total_char_info["all"].setdefault(total_lines_char_avg, 0)
            total_char_info["all"][total_lines_char_avg] += 1
            # 单commit中，所有文件的行数变化
            file_rows_info[fileType].setdefault(file_row_change, 0)
            file_rows_info[fileType][file_row_change] += 1
            file_rows_info["all"].setdefault(file_row_change, 0)
            file_rows_info["all"][file_row_change] += 1

            # if fileType == "py":
            #     newResult = parse_python(newFileContent)
            #     oldResult = parse_python(oldFileContent)
            if fileType == "java":
                newResult = parse_java(newFileContent)
                oldResult = parse_java(oldFileContent)
            else:
                continue
            total_files += 1
            # pprint(newResult)
            # pprint(oldResult)
            for method in oldResult:
                # total_files += 1
                set_method.add(method)                   
    print(len(set_method))
    
def passQuarterly(company, start_time, end_time):
    projectList = {"apache":["apache/dubbo",
                            "apache/kafka",
                            "apache/flink",
                            "apache/skywalking",
                            "apache/rocketmq",
                            "apache/shardingsphere",
                            "apache/hadoop",
                            "apache/pulsar",
                            "apache/druid",
                            "apache/zookeeper"],
                   "google":["google/guava",
                            "google/gson", 
                            "google/ExoPlayer", 
                            "google/dagger", 
                            "google/guice", 
                            "google/auto", 
                            "google/tsunami-security-scanner",
                            "google/error-prone", 
                            "google/closure-compiler", 
                            "google/nomulus"],
                   "spring-projects":["spring-projects/spring-boot",
                            "spring-projects/spring-framework",
                            "spring-projects/spring-security",
                            "spring-projects/spring-authorization-server",
                            "spring-projects/spring-ai",
                            "spring-projects/spring-data-jpa",
                            "spring-projects/spring-kafka",
                            "spring-projects/spring-batch",
                            "spring-projects/spring-session",
                            "spring-projects/spring-data-mongodb"]}
    total_failure = defaultdict(lambda: defaultdict(int))
    def process_commit(commit, companypProject):
        """
        处理单个 commit，检查 check-runs 状态
        """
        commitSha = commit["commit_sha"]
        url = f"https://api.github.com/repos/{companypProject}/commits/{commitSha}/check-runs"
        
        try:
            response = get_response(url)
            result = response.json()
            check_runs = result.get("check_runs", [])
            
            # 判断是否有失败的 check
            failureFlag = any(check.get("conclusion") == "failure" for check in check_runs)
            
            # 如果没有失败的 check，增加计数
            if not failureFlag:
                release_time = commit['release_time']
                total_failure[companypProject][release_time] += 1
        except Exception as e:
            print(f"Error processing commit {commitSha}: {e}")     
    for companypProject in projectList[company]:
        # 查询 commits，增加 release_time 的过滤条件
        commits = commit_collection.find({
        "repository": companypProject,
        "download": {"$exists": True},
        "release_time": {
            "$gte": start_time,  # release_time >= start_time
            "$lte": end_time     # release_time <= end_time
            }
        })
        """
        使用线程池并发处理 commits
        """
        with ThreadPoolExecutor(max_workers=24) as executor:
            futures = [executor.submit(process_commit, commit, companypProject) for commit in commits]
            for future in as_completed(futures):
                try:
                    future.result()  # 获取线程执行结果，捕获异常
                except Exception as e:
                    print(f"Thread raised an exception: {e}")  
    #     # commits = commit_collection.find({"repository": repository, "download": {"$exists": True}})
    #     for commit in commits:
    #         commitSha = commit["commit_sha"]
    #         url = f"https://api.github.com/repos/{companypProject}/commits/{commitSha}/check-runs"
    #         response = get_response(url)
    #         result = response.json() 
    #         # print(result)   
    #         check_runs = result.get("check_runs", [])
    #         failureFlag = False 
    #         for check in check_runs:
    #             if check.get("conclusion") == "failure" :  # 检查是否未通过
    #                 failureFlag = True
    #                 break
    #         if failureFlag == False:
    #             total_failure[companypProject][commit['release_time']] += 1
    # print(total_failure)     
                    
    with open(f"{company}.json", "w") as file:
        json.dump(total_failure, file)     
               
if __name__ == "__main__":

    
    parser = argparse.ArgumentParser(description="Download repository data with specified time range.")
    
    # 添加命令行参数
    # 仓库名，可以选择多个Apache项目
    parser.add_argument('-r', '--repository', type=str, default='apache/dubbo',
                        help="""Specify the repository to download. 
                        Example:
                        - apache/dubbo: 多版本名
                        - apache/kafka: 多版本
                        - apache/incubator-seata: 多版本
                        - apache/flink: 有主分支
                        - apache/skywalking: 多版本，有主分支
                        - apache/rocketmq: 多版本，main、master、feature都有
                        - apache/shardingsphere: 只有主分支
                        - apache/hadoop: 多版本
                        - apache/pulsar: 多版本，主分支
                        - apache/druid: 多版本
                        - apache/zookeeper: 多版本，主分支
                        (default: apache/rocketmq).""")
    
    # 开始时间，可以选择时间范围
    parser.add_argument('-s', '--start_time', type=str, default='2022-01-01',
                        help="Specify the start time for the download (default: 2022-01-01).")
    
    # 结束时间，可以选择时间范围
    parser.add_argument('-e', '--end_time', type=str, default='2024-12-15',
                        help="Specify the end time for the download (default: 2024-12-15).")
    
    parser.add_argument('-sf', '--search_flag', type=int, default=0,
                    help="Search function.")
    
    parser.add_argument('-df', '--download_flag', type=int, default=0,
                    help="Download function.")
   
    parser.add_argument('-af', '--analysis_flag', type=int, default=0,
                    help="Analysis function.")   

    parser.add_argument('-suf', '--summary_flag', type=int, default=0,
                    help="Summary function.")   
    
    parser.add_argument('-tf', '--threshold_flag', type=int, default=0,
                help="Summary function.")  
    
    parser.add_argument('-com', '--company', type=str, default="apache",
                help="company.")

    parser.add_argument('-pf', '--pass_flag', type=int, default=0,
                help="company.")
    
    # 解析命令行参数
    args = parser.parse_args()
    if args.search_flag:
       rate_limit_thread = threading.Thread(target=check_rate_limit)
       rate_limit_thread.start()  # Start the rate limit checking thread
       search(args.repository, args.start_time, args.end_time)
    if args.download_flag:
       rate_limit_thread = threading.Thread(target=check_rate_limit)
       rate_limit_thread.start()  # Start the rate limit checking thread
       download(args.repository)
    if args.analysis_flag:
       analysis(args.repository)    
    if args.summary_flag:
       summary(args.repository)
    if args.threshold_flag:
       threshold(args.repository, method_rows=30)
    if args.pass_flag:
       passQuarterly(args.company, args.start_time, args.end_time)
    
    # threshold(args.repository, circle=10)
    # if args.analysis_flag:
    #    analysis(args.repository)    
    # # 输出接收到的参数信息
    # print(f"Repository: {args.repository}")
    # print(f"Start Time: {args.start_time}")
    # print(f"End Time: {args.end_time}")

    # 使用流程
    # 1. 设定仓库名称
    # 2. 设定开始时间 可以不设定
    # 3. 设定结束时间 可以不设定
    # 4. 运行函数 search()    获取commit
    # 5. 运行函数 download()  下载commit的文件
    # 6. 运行函数 analysis()  解析文件内容 获取函数参数变化、函数圈复杂度变化、代码行数变化、代码字符变化
    # 7. 运行函数 summary()   统计函数参数变化、函数圈复杂度变化、代码行数变化、代码字符变化
    # 8. 运行函数 threshold() 校验函数参数变化、函数圈复杂度变化、代码行数变化、代码字符变化是否符合规范

    # repository = "tree-sitter/tree-sitter-python"
    # repository = "google/guava"
    # repository = "google/gson"
    # repository = "google/ExoPlayer"
    # # repository = "google/dagger"
    # # repository = "google/tink"



    # 各个库的分支名不同，合并分支
    # repository = "apache/dubbo" # 多版本名
    # repository = "apache/kafka" # 多版本
    # repository = "apache/incubator-seata" # 多版本
    # repository = "apache/flink" # 有主分支 
    # repository = "apache/skywalking" # 多版本，有主分支
    # repository = "apache/rocketmq" # 多版本，main，master，feature都有
    # repository = "apache/shardingsphere" # 只有主分支
    # repository = "apache/hadoop" # 多版本 
    # repository = "apache/pulsar" # 多版本，主分支
    # repository = "apache/druid" #  多版本
    # repository = "apache/zookeeper" # 多版本，主分支
    # start_time = "2022-01-01"
    # end_time = "2024-12-15"
    # analysis(args.repository)
    # threshold_detail_with_message(repository, file_rows=300)
    # threshold_detail(repository, method_rows=50)
    # threshold_detail(repository, file_rows=300, start_time=start_time, end_time=end_time)
    # threshold_detail(repository, method_rows=50, start_time=start_time, end_time=end_time)
    # threshold_detail_with_message(repository,method_rows=30,start_time=start_time,end_time=end_time)
    # threshold_detail(repository, method_rows=30, start_time=start_time, end_time=end_time)
    # threshold(repository, params=1, circle=1, lines=1, chars=1, method_rows=50, file_rows=1)
    # threshold(repository, chars=100)
    # threshold(repository, circle=5)
    # threshold(repository, method_rows=30)
    # threshold(repository, file_rows=300)
    # search(repository, start_time, end_time)
    # summary(repository, language="py")
    # summary(repository, language="js")
    # summary(repository, language="c")
    # summary(repository, language="cpp")
    # summary(args.repository, language="java")
    # commit_collection.delete_many({})
    
    
    # analysis_contributor(repository, start_time, end_time, flag = 0)
    # analysis_contributor(repository, start_time, end_time, flag = 1)
    # update_contributor(repository, None, start_time, end_time)
    # analysis_age(args.repository)
    # analysis_variable(repository, start_time=start_time, end_time=end_time)
    # analysis_method(args.repository)
    # https://github.com/spring-projects/spring-framework/commit/50b1fb0b15d944e9f426b770308828ca28dc25c6