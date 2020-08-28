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
                 src_branch = None,
                 dest_branch = None,
                 position = None,
                 tag_suffix = None,
                 tag_latest = None,
                 tag_latest_nosuffix=None,
                 tag_meta = None,
                 tag_next = None):
        self.repo_name = repo_name
        self.src_branch = src_branch
        self.dest_branch = dest_branch
        self.position = position
        self.tag_suffix = tag_suffix
        self.tag_latest = tag_latest
        self.tag_latest_nosuffix = tag_latest_nosuffix
        self.tag_meta = {"development":
                             {"tag_suffix": "-dev"},
                         "master":
                             {"tag_suffix": ""} }
        self.tag_next = tag_next


class MhConfigModel(object):

    def __init__(self, github_api_token=None):
        self.github_api_token = github_api_token


def connect_github(api_token):
    return Github(base_url="https://api.github.com", login_or_token=api_token)


def get_github_tags(repo_name=None, gh_api=None):
    print("Get tags from GitHub")

    # Get tags from GitHub as a list
    repo = gh_api.get_user().get_repo(repo_name)
    git_tags = repo.get_tags()
    return [tag.name for tag in git_tags]


def get_semver_position():
    # Determine which semantic position to bump
    if semver.dest_branch == 'development':
        position = 'MINOR'
        print("Position: {0}".format(position))

        return position


def get_latest_tag(git_tags, dest_branch, tag_suffix):
    for tag in git_tags:
        if re.search(r'{0}$'.format(tag_suffix), tag):
            print('Latest tag ({0}): {1}'.format(dest_branch, tag))

            return tag


def semver_bump(tag_latest, tag_suffix):
    print("Generate New Version")

    # Remove tag suffix
    if tag_suffix != '':
        semver.tag_latest_nosuffix = tag_latest.split("-")[0]
        tag = semver.tag_latest_nosuffix
    else:
        tag = tag_latest

    # Convert semantic version (without suffix) to integers
    MAJOR = int(tag.split(".")[0])
    MINOR = int(tag.split(".")[1])
    PATCH = int(tag.split(".")[2])

    if semver.position == 'MAJOR':
        MAJOR = MAJOR + 1
    elif semver.position == 'MINOR':
        MINOR = MINOR + 1
        PATCH = 0   # Reset Patch
    elif semver.position == 'PATCH':
        PATCH = PATCH + 1

    # Assemble full semantic version, reattaching suffix if applicable
    if tag_suffix != '':
        tag_next = "{0}.{1}.{2}{3}".format(MAJOR, MINOR, PATCH, semver.tag_suffix)
    else:
        tag_next = "{0}.{1}.{2}".format(MAJOR, MINOR, PATCH)

    print("New Version: {0}".format(tag_next))

    return tag_next


def mh_config(mode='live'):
    mh_config_model = MhConfigModel()

    if mode == 'local':
        # Read configs from file
        path = '{0}/.meethook/config.txt'.format(os.environ["HOME"])
        print("Loading config from path: {0}".format(path))

        file = open(path, 'r')
        for line in file:
            key = line.split('=')[0].rstrip("\n")
            value = line.split('=')[1].rstrip("\n")
            if key == 'github_api_token':
                mh_config_model.github_api_token = value
        file.close()

    if mode == 'live':
        print("Loading config from Github Secrets")
        mh_config_model.github_api_token = os.environ["INPUT_REPO-TOKEN"]


    return mh_config_model


def push_github_tag(repo_name, dest_branch, tag_next, gh_api):
    # https://stackoverflow.com/questions/11801983/how-to-create-a-commit-and-push-into-repo-with-github-api-v3

    # Instantiate a Github object
    repo = gh_api.get_user().get_repo(repo_name)

    # Get latest commit from destination branch (post MERGE)
    git_branch = repo.get_branch(branch=dest_branch)

    # Push next tag to repository
    repo.create_git_tag_and_release(tag=tag_next,
                                    tag_message='Test Message',
                                    release_name='Test Release Name',
                                    release_message='Test Release Message',
                                    object=git_branch.commit.sha,
                                    type='commit',
                                    prerelease=True)

    print('New tag: {0}\nSHA: {1}\nOn Branch: {2}'.format(tag_next,
                                                          git_branch.commit.sha,
                                                          dest_branch))

# ---- INPUTS ----
# src_branch = os.environ["GITHUB_REF"].split('/')[2]     # Ex: feat_branch
src_branch = "feature_branch"     # Ex: feat_branch
dest_branch = 'development'

# Set mode: Local (local config) or Live (GitHub Secrets)
mh_config = mh_config(mode='live')

# Instantiate GitHub connection object
gh_api = connect_github(api_token=mh_config.github_api_token)

# Instantiate data model
semver = SemVerModel(repo_name="branching-test",
                     src_branch=src_branch,
                     dest_branch=dest_branch)

# Get tags from Github
tags = get_github_tags(repo_name=semver.repo_name,
                       gh_api=gh_api)

# Output latest tag ending associated branch suffix
semver.tag_suffix = semver.tag_meta[dest_branch]['tag_suffix']

# Get latest tag from branch
semver.tag_latest = get_latest_tag(git_tags=tags,
                                   dest_branch=semver.dest_branch,
                                   tag_suffix=semver.tag_suffix)

# Figure out which semantic position to bump
semver.position = get_semver_position()

# Generate new tag
semver.tag_next = semver_bump(tag_latest=semver.tag_latest,
                              tag_suffix=semver.tag_suffix)
print("::set-output name=tag_new::{0}".format(semver.tag_next))

# push_github_tag(repo_name=semver.repo_name,
#                 dest_branch=semver.dest_branch,
#                 tag_next=semver.tag_next,
#                 gh_api=gh_api)


'''
TODO:
- Master, hotfix branches
- PR checkbox to bump MAJOR, MINOR
'''
