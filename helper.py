import json
import datetime

def get_basic_info(github_client, owner, repo_name):

    try:
        repo = github_client.get_repo(f"{owner}/{repo_name}")
        
        return {
            "title": repo.name,
            "description": repo.description or "",
            "url": repo.html_url,
            "date": {
                "created": repo.created_at.isoformat(),
                "lastModified": repo.updated_at.isoformat(),
                "metaDataLastUpdated": datetime.datetime.now().isoformat()
            }
        }
    except Exception as e:
        print(f"Failed to get basic info: {e}")
        raise

def get_programming_languages(github_client, owner, repo_name):
    try:
        repo = github_client.get_repo(f"{owner}/{repo_name}")
        languages = list(repo.get_languages().keys())
        return languages
    except Exception as e:
        print(f"Failed to get languages: {e}")
        raise

def calculate_metadata(github_client, owner, repo_name):
    try:
        basic_info = get_basic_info(github_client, owner, repo_name)
        languages = get_programming_languages(github_client, owner, repo_name)
        # labor_hours = get_labor_hours()
        
        return {
            "name": basic_info["title"],
            "description": basic_info["description"],
            "repositoryURL": basic_info["url"],
            "laborHours": 0, # labor_hours  
            "languages": languages,
            "date": {
                "created": basic_info["date"]["created"],
                "lastModified": basic_info["date"]["lastModified"],
                "metaDataLastUpdated": basic_info["date"]["metaDataLastUpdated"]
            }
        }
    except Exception as e:
        print(f"Failed to calculate metadata: {e}")
        raise

# def get_labor_hours():
#     try:
#         HOURS_PER_MONTH = 730.001 
        
#         result = subprocess.run(['scc', '.', '--format', 'json2'], 
#                                capture_output=True, text=True, check=True)
#         scc_data = json.loads(result.stdout)
        
#         labor_hours = math.ceil(scc_data["estimatedScheduleMonths"] * HOURS_PER_MONTH)
#         return labor_hours
#     except Exception as e:
#         print(f"Failed to get labor hours: {e}")
#         raise

def check_codejson_exists(github_client, owner, repo_name):
    try:
        repo = github_client.get_repo(f"{owner}/{repo_name}")
        
        try:
            contents = repo.get_contents("code.json")
            file_content = contents.decoded_content.decode("utf-8")
            return json.loads(file_content)
        except Exception as e:
            print(f"No code.json content found!")
            return None
            
    except Exception as e:
        print(f"Failed to get repository: {e}")
        raise 

def body_of_pr():
    return """
        ## Welcome to the Federal Open Source Community!

        Hello, and thank you for your contributions to the Federal Open Source Community. 🙏

        This pull request adding [code.json repository metadata](https://github.com/DSACMS/gov-codejson/blob/main/docs/metadata.md) is being sent on behalf of the CMS Source Code Stewardship Taskforce, in compliance with [The Federal Source Code Inventory Policy](https://code.gov/agency-compliance/compliance/inventory-code), [M-16-21](https://obamawhitehouse.archives.gov/sites/default/files/omb/memoranda/2016/m_16_21.pdf), and in preparation for the [SHARE IT Act of 2024](https://www.congress.gov/bill/118th-congress/house-bill/9566). If you have questions, please file an issue [here](https://github.com/DSACMS/automated-codejson-generator/issues) or join our #cms-ospo slack channel [here](https://cmsgov.enterprise.slack.com/archives/C07HM92S9QQ).

        ## Next Steps
        ### Add Missing Information to code.json
        - We have automatically calculated some fields but many require manual input
        - Please enter the missing fields by directly editing code.json in Files Changed tab on your pull-request
        - We also have a [form](https://dsacms.github.io/codejson-generator/) where you can create your code.json via a website, and then download directly to your local machine, and then you can copy and paste into here.

        If you would like additional information about the code.json metadata requirements, please visit the repository [here](https://github.com/DSACMS/gov-codejson).
    """

def create_pr(github_client, owner, repo_name, updated_code_json, branch=None):
    try:
        repo = github_client.get_repo(f"{owner}/{repo_name}")
        branch = repo.default_branch

        formatted_content = json.dumps(updated_code_json, indent=2)
        
        new_branch = f"code-json-{int(datetime.datetime.now().timestamp())}"
        
        default_ref = repo.get_git_ref(f"heads/{branch}")

        repo.create_git_ref(ref=f"refs/heads/{new_branch}", sha=default_ref.object.sha)

        file_exists = False
        try:
            contents = repo.get_contents("code.json", ref=new_branch)
            file_exists = True
            
            print("Updating code.json!")
        except:
            print("Creating a new code.json!")

        if file_exists:
            repo.update_file(
                path="code.json",
                message="Update code.json metadata",
                content=formatted_content,
                sha=contents.sha,
                branch=new_branch
            )
        else:
            repo.create_file(
                path="code.json",
                message="Add code.json metadata",
                content=formatted_content,
                branch=new_branch
            )
        
        pr = repo.create_pull(
            title="Update code.json",
            body=body_of_pr(),
            head=new_branch,
            base=branch
        )

        pr.add_to_labels("codejson-initialized")
        return pr
    except Exception as e:
        print(f"Failed to create PR: {e}")
        raise