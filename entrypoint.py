import os
import re
import subprocess
import json
from github import Github

# my_input = os.environ["INPUT_MYINPUT"]
# print("::set-output name=myOutput::{0}".format(my_input))

# status = "IT WORKS"
# print("::set-output name=status::{0}".format(status))

class SemVerModel(object):

    def __init__(self, repo_name,
                 dest_branch = None,
                 tag_latest = None,
                 tag_latest_nosuffix=None,
                 tag_next=None,
                 tag_meta = None):

        self.repo_name = repo_name
        self.dest_branch = dest_branch
        self.tag_latest = tag_latest
        self.tag_latest_nosuffix = tag_latest_nosuffix
        self.tag_next = tag_next
        self.tag_meta = {"development":
                             [
                                 {"tag_latest": None,
                                 "tag_latest_nosuffix": None,
                                 "tag_suffix": "-dev",
                                 "prerelease": True
                                 }
                             ],
                         "master":
                             [
                                 {"tag_latest": None,
                                 "tag_latest_nosuffix": None,
                                 "tag_suffix": "",
                                 "prerelease": False
                                 }
                             ]
                         }


class MhConfigModel(object):

    def __init__(self,
                 mode='live',
                 src_branch=None,
                 dest_branch=None,
                 github_api_token=None):

        self.mode = mode
        self.dest_branch = dest_branch
        self.github_api_token = github_api_token


def connect_github(api_token):
    return Github(base_url="https://api.github.com", login_or_token=api_token)


def get_github_tags(repo_name=None):
    print("Get tags from GitHub")

    # Get tags from GitHub as a list
    repo = gh_api.get_user().get_repo(repo_name)
    git_tags = repo.get_tags()
    return [tag.name for tag in git_tags]


def get_latest_tag(git_tags):
    # Get latest tag for each branch and set values in semver.tag_meta
    print("Find latest tags")

    return git_tags[0]
    #
    # for branch in semver.tag_meta:
    #     # Set tag suffix for given branch
    #     tag_suffix = semver.tag_meta[branch][0]['tag_suffix']
    #
    #     for tag in git_tags:
    #         regex = re.search(r'(\d+\.\d+\.\d+){0}$'.format(tag_suffix), tag)
    #         if regex:
    #             # Set latest tag values with and without tag suffix
    #             semver.tag_meta[branch][0]['tag_latest'] = tag
    #             semver.tag_meta[branch][0]['tag_latest_nosuffix'] = regex.group(1)
    #             print('({0}): {1}'.format(branch, tag))
    #
    #             break


def semver_bump(tag_latest, dest_branch):
    print("Generate New Version")
    print("Dest Branch:", dest_branch)

    # if dest_branch == 'development':
    #     # Commit feature to development branch, MINOR bump
    #     # Bump Minor position - Example: development @1.2.0-dev --> @1.3.0-dev
    #
    #     tag_latest = semver.tag_meta['development'][0]['tag_latest']
    #     tag_latest_nosuffix = semver.tag_meta['development'][0]['tag_latest_nosuffix']
    #     tag_suffix = semver.tag_meta['development'][0]['tag_suffix']
    #
    #     # Convert semantic version (without suffix) to integers
    #     MAJOR = int(tag_latest_nosuffix.split(".")[0])
    #     MINOR = int(tag_latest_nosuffix.split(".")[1])
    #     PATCH = int(tag_latest_nosuffix.split(".")[2])
    #
    #     # Bump version
    #     MINOR = MINOR + 1
    #     PATCH = 0  # Reset Patch
    #
    #     tag_next = "{0}.{1}.{2}{3}".format(MAJOR, MINOR, PATCH, tag_suffix)
    #
    # elif dest_branch == 'master':
    #     # Retain version, drop suffix. No version bump
    #     # Example: development @1.2.0-dev --> master @1.2.0
    #
    #     tag_latest_nosuffix = semver.tag_meta['development'][0]['tag_latest_nosuffix']
    #     tag_next = tag_latest_nosuffix

    # Convert semantic version (without suffix) to integers
    MAJOR = int(tag_latest.split(".")[0])
    MINOR = int(tag_latest.split(".")[1])
    PATCH = int(tag_latest.split(".")[2])

    # Bump version
    MINOR = MINOR + 1
    PATCH = 0  # Reset Patch

    return "{0}.{1}.{2}".format(MAJOR, MINOR, PATCH)


def mh_config(mode='live', dest_branch=None):
    mh_config_model = MhConfigModel()

    if mode == 'live':
        print("{0} MODE: Loading config from Github Secrets and ENV Variables".format(mode.upper()))
        mh_config_model.dest_branch = os.environ["GITHUB_REF"].split('/')[2]
        mh_config_model.github_api_token = os.environ["INPUT_REPO-TOKEN"]

        print("Destination Branch:", mh_config_model.dest_branch, "API Repo Token: From Github Secrets")

    elif mode == 'local':
        # Read configs from file and function input parameters
        path = '{0}/.meethook/config.txt'.format(os.environ["HOME"])
        print("{0} MODE: Loading values from path: {1}".format(mode.upper(), path))

        file = open(path, 'r')
        for line in file:
            key = line.split('=')[0].rstrip("\n")
            value = line.split('=')[1].rstrip("\n")
            if key == 'github_api_token':
                mh_config_model.github_api_token = value
        file.close()

        # Set source and destination TEST branches
        mh_config_model.dest_branch = dest_branch

        print("Destination Branch:", mh_config_model.dest_branch,
              "API Repo Token: From Github Secrets")

    return mh_config_model


def push_github_tag(repo_name, dest_branch, tag_next):
    # https://stackoverflow.com/questions/11801983/how-to-create-a-commit-and-push-into-repo-with-github-api-v3

    # Instantiate a Github object
    repo = gh_api.get_user().get_repo(repo_name)

    # Get latest commit from destination branch (post MERGE)
    git_branch = repo.get_branch(branch=dest_branch)

    # Push next tag to repository
    prerelease = semver.tag_meta[dest_branch][0]['prerelease']
    print('New tag: {0}\nSHA: {1}\nOn Branch: {2}\nPrerelease: {3}'.format(tag_next,
                                                                           git_branch.commit.sha,
                                                                           dest_branch,
                                                                           prerelease))

    repo.create_git_tag_and_release(tag=tag_next,
                                    tag_message='Test Message',
                                    release_name='Test Release Name',
                                    release_message='Test Release Message',
                                    object=git_branch.commit.sha,
                                    type='commit',
                                    prerelease=prerelease)




# ---- Local Testing INPUTS ----
# Set mode: Local (local config) or Live (GitHub Secrets)
# mh_config = mh_config(mode='local', dest_branch='master')
mh_config = mh_config(mode='live')
# ------------------------------
semver = SemVerModel(repo_name="branching-test",
                     dest_branch=mh_config.dest_branch)

# Instantiate GitHub connection object
gh_api = connect_github(api_token=mh_config.github_api_token)

# Get tags from Github
tags = get_github_tags(repo_name=semver.repo_name)

# Get latest tag from branch
semver.tag_latest = get_latest_tag(git_tags=tags)

# Generate new tag
semver.tag_next = semver_bump(tag_latest=semver.tag_latest,
                              dest_branch=semver.dest_branch)

push_github_tag(repo_name=semver.repo_name,
                dest_branch=semver.dest_branch,
                tag_next=semver.tag_next)

# print("::set-output name=tag_new::{0}".format(semver.tag_next))

'''
TODO:
- Update release body message
- Flag for local testing
- PR checkbox to bump MAJOR, MINOR
- Hotfix branches

IMPLEMENTATION STEPS
- Create repo secret REPO-TOKEN

Gitworkflow
https://hackernoon.com/how-the-creators-of-git-do-branches-e6fcc57270fb
https://github.com/rocketraman/gitworkflow/blob/master/docs/task-oriented-primer.adoc#visualization-4
'''
