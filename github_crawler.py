import pycurl
import json
from StringIO import StringIO
import subprocess
import os
import gzip
import tempfile
import urllib
from random import random
from time import sleep
import shutil

#main_url = "http://localhost:8888/"
api_url = "https://api.github.com"
site_url = "https://github.com"
url_code = getattr(pycurl, "URL")


def get_url(path):
    buffer = StringIO()
    handle = pycurl.Curl()
    handle.setopt(pycurl.URL, api_url + path)
    handle.setopt(pycurl.WRITEDATA, buffer)
    handle.perform()
    if handle.getinfo(handle.RESPONSE_CODE) != 200:
        sleep(120)
        return get_url(path)
    return buffer.getvalue()

def get_followers(user):
    body = get_url("/users/" + user + "/followers")
    return [user['login'] for user in json.loads(body)]

def get_user_repos(user):
    repos = get_url("/users/" + user + "/repos")
    return [(repo['name'], repo['fork']) for repo in json.loads(repos)]

def get_org_repos(org):
    repos = get_url("/orgs/" + org + "/repos")
    return [(repo['name'], repo['fork']) for repo in json.loads(repos)]

def get_parent_repo(owner, repo_name):
    body = get_url("/repos/" + owner + "/" + repo_name)
    parent = json.loads(body)['parent']
    return parent['owner']['login'], parent['name']

def get_parent_repos(owner, func):
    repos = func(owner)
    parent_repos = []
    for repo, fork in repos:
        if fork:
            parent_repos += [get_parent_repo(owner, repo)]
        else:
            parent_repos += [(owner, repo)]
    return parent_repos

def get_user_parent_repos(user):
    return get_parent_repos(user, get_user_repos)

def get_org_parent_repos(user):
    return get_parent_repos(user, get_org_repos)

def clone_repo(owner, repo):
    clone_repo = site_url + "/" + owner + "/" + repo
    directory = tempfile.mkdtemp() + "/" + repo
    subprocess.check_output(["git", "clone", clone_repo, directory], stderr=subprocess.STDOUT)
    return directory

def get_gzip_size(fullfilename):
    with open(fullfilename, "rb") as fin:
        outname = tempfile.NamedTemporaryFile(dir="/tmp", prefix="gzipped_").name
        with gzip.open(outname, "wb") as fout:
            fout.writelines(fin)
    size = os.path.getsize(outname)
    os.remove(outname)
    return size

def analyze_file(root, filename):
    if '.git' in root:
        return
    if '.' in filename:
        extension = filename.split('.')[-1]
        original_size = os.path.getsize(root + "/" + filename)
        if original_size == 0:
            return
        gzip_size = get_gzip_size(root + "/" + filename)
        return (extension, gzip_size / float(original_size))

def analyze_repo(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            info = analyze_file(root, filename)
            if info:
                yield info
    shutil.rmtree(directory)
    os.rmdir(os.path.dirname(directory))

def get_users_with_n_followers(n):
    url = '/search/users?' + urllib.urlencode({'q':'followers:' + str(n)})
    body = get_url(url)
    return [user['login'] for user in json.loads(body)['items']]

def get_random_users():
    rand = int(random() * 40)
    return get_users_with_n_followers(100 + rand)

if __name__ == "__main__":
    #print get_followers("pooya")
    #print get_user_repos("pooya")
    #print get_org_repos("discoproject")
    #print get_parent_repo("pooya", "disco")
    #print get_user_parent_repos("pooya")
    #print get_user_parent_repos("discoproject")
    #directory = clone_repo("2600hz", "kazoo")
    directory = clone_repo("talko", "plists")
    #analyze_repo(directory)
    #print get_random_users()
    pass

