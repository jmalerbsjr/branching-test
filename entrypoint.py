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

def get_github_tags(repo_name=None):
    print("Get tags from GitHub")
    # Instantiate a Github object
    g = Github(base_url="https://api.github.com", login_or_token=mh_config.github_api_token)

    # Get tags from GitHub as a list
    repo = g.get_user().get_repo(repo_name)
    git_tags = repo.get_tags()
    return [tag.name for tag in git_tags]

def set_semver_position():
    # Determine which semantic position to bump
    if semver.dest_branch == 'development':
        semver.position = 'MINOR'
        print("Position: {0}".format(semver.position))


def get_latest_tag(git_tags, dest_branch):
    # Output latest tag ending associated branch suffix
    semver.tag_suffix = semver.tag_meta[dest_branch]['tag_suffix']

    for tag in git_tags:
        if re.search(r'{0}$'.format(semver.tag_suffix), tag):
            print('Latest tag ({0}): {1}'.format(dest_branch, tag))
            semver.tag_latest = tag

            return


def semver_bump(semver):
    print("Bump Version")

    # Remove tag suffix
    if semver.tag_suffix != '':
        semver.tag_latest_nosuffix = semver.tag_latest.split("-")[0]
        tag = semver.tag_latest_nosuffix
    else:
        tag = semver.tag_latest

    # Convert semantic version (without suffix) to integers
    MAJOR = int(tag.split(".")[0])
    MINOR = int(tag.split(".")[1])
    PATCH = int(tag.split(".")[2])

    if semver.position == 'MAJOR':
        MAJOR = MAJOR + 1
    elif semver.position == 'MINOR':
        MINOR = MINOR + 1
    elif semver.position == 'PATCH':
        PATCH = PATCH + 1

    # Assemble full semantic version, reattaching suffix if applicable
    if semver.tag_suffix != '':
        semver.tag_next = "{0}.{1}.{2}{3}".format(MAJOR, MINOR, PATCH, semver.tag_suffix)
    else:
        semver.tag_next = "{0}.{1}.{2}".format(MAJOR, MINOR, PATCH)

    print("New Version: {0}".format(semver.tag_next))


# ---- INPUTS ----

def mh_config(mode='live'):
    mh_config_model = MhConfigModel()

    if mode == 'test':
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


# ---- INPUTS ----
# src_branch = os.environ["GITHUB_REF"].split('/')[2]     # Ex: feat_branch
src_branch = "feature_branch"     # Ex: feat_branch
dest_branch = 'development'

# Load local config for testing instead of GitHub Secrets
mode = 'live'
mh_config = mh_config(mode=mode)

# Instantiate data model
semver = SemVerModel(repo_name="branching-test",
                     src_branch=src_branch,
                     dest_branch=dest_branch)

# Get tags from Github TODO: Limit results to 500
tags = get_github_tags(repo_name=semver.repo_name)

# Get latest tag from branch
get_latest_tag(git_tags=tags, dest_branch=semver.dest_branch)

# Figure out which semantic position to bump
set_semver_position()

# Generate new tag
semver_bump(semver=semver)
print("::set-output name=tag_new::{0}".format(semver.tag_next))

# Push new tag
print("Get tags from GitHub")
# Instantiate a Github object
g = Github(base_url="https://api.github.com", login_or_token=mh_config.github_api_token)

# Get tags from GitHub as a list
print("----")
# https://stackoverflow.com/questions/11801983/how-to-create-a-commit-and-push-into-repo-with-github-api-v3
print('Pushing new tag: {0}'.format(semver.tag_next))
repo = g.get_user().get_repo(semver.repo_name)
# repo.create_git_ref(ref='refs/heads/feat_test', sha='445f095c664c16e674054ed6db2d13678593ac1c')

# Get latest commit from destination branch (post MERGE)
git_branch = repo.get_branch(branch=semver.dest_branch)

# Push next tag
print('SHA:', git_branch.commit.sha)
# repo.create_git_tag_and_release(tag=semver.tag_next,
#                                 tag_message='Test Message',
#                                 release_name='Test Release Name',
#                                 release_message='Test Release Message',
#                                 object=git_branch.commit.sha,
#                                 type='commit',
#                                 prerelease=True)


#
#
# print('Latest tag: {0}'.format(semver.tag_latest))
exit(0)


'''
TODO:
- Master, hotfix branches
- PR checkbox to bump MAJOR, MINOR
- Bump tag on MERGE only
'''
