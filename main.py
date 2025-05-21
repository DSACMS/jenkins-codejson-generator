import os
import sys
from github import Github
from helper import calculate_metadata, check_codejson_exists, create_pr

def main():
    github_token = os.environ.get('GITHUB_TOKEN')
    org_name = os.environ.get("ORGANIZATION")
    repo_name = os.environ.get("REPOSITORY") 

    if not github_token:
        print("Error: GITHUB_TOKEN environment variable is required")
        sys.exit(1)
    if not org_name:
        print("Error: ORGANIZATION environment variable is required")
        sys.exit(1)
    if not repo_name:
        print("Error: REPOSITORY environment variable is required")
        sys.exit(1)

    baseline_code_json = {
    "name": "",
    "description": "",
    "longDescription": "",
    "status": "",
    "permissions": {
        "license": [
            {
                "name": "",
                "URL": "",
            },
        ],
        "usageType": "",
        "exemptionText": "",
    },
    "organization": "",
    "repositoryURL": "",
    "projectURL": "",
    "repositoryHost": "github",
    "repositoryVisibility": "",
    "vcs": "git",
    "laborHours": 0,
    "reuseFrequency": {
        "forks": 0,
        "clones": 0,
    },
    "platforms": [],
    "categories": [],
    "softwareType": "",
    "languages": [],
    "maintenance": "",
    "contractNumber": "",
    "date": {
        "created": "",
        "lastModified": "",
        "metaDataLastUpdated": "",
    },
    "tags": [],
    "contact": {
        "email": "",
        "name": "",
    },
    "feedbackMechanisms": [],
    "localisation": False,
    "repositoryType": "",
    "userInput": False,
    "fismaLevel": "",
    "group": "",
    "projects": [],
    "systems": [],
    "upstream": "",
    "subsetInHealthcare": [],
    "userType": [],
    "maturityModelTier": 0,
}

    # Enterprise Client
    # github_client = Github(base_url = "https://github.cms.gov/api/v3", login_or_token = github_token)

    # Public Client
    github_client = Github(login_or_token = github_token)
    metadata = calculate_metadata(github_client, org_name, repo_name)
    current_code_json = check_codejson_exists(github_client, org_name, repo_name)
    
    if current_code_json:
        final_code_json = {**baseline_code_json, **current_code_json, **metadata}
    else:
        final_code_json = {**baseline_code_json, **metadata}
    
    create_pr(github_client, org_name, repo_name, final_code_json)

if __name__ == "__main__":
    main()