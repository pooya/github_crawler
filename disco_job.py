from disco.core import Job, result_iterator

def map(line, params):
    import github_crawler
    n = int(line)
    users = github_crawler.get_users_with_n_followers(n)
    print str(len(users)) + " users"
    for user in users:
        repos = github_crawler.get_user_parent_repos(user)
        print str(len(repos)) + " repos"
        for owner, repo in repos:
            print owner + "/" + repo
            directory = github_crawler.clone_repo(owner, repo)
            for item in github_crawler.analyze_repo(directory):
                yield item

def reduce(iter, params):
    from disco.util import kvgroup
    for extension, ratios in kvgroup(sorted(iter)):
        l_ratios = [r for r in ratios]
        yield extension, sum(l_ratios) / len(l_ratios)

if __name__ == "__main__":
    input = ["raw://" + str(i) for i in range(0, 1000, 10)]
    job = Job().run(input=input, map=map, reduce=reduce, required_files=["github_crawler.py"])
    for extension, avg in result_iterator(job.wait(show=True)):
        print extension, ": ", avg
