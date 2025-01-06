#!/usr/bin/python3

import sys
import git
from datetime import datetime, timezone

COMMIT_MESSAGE = "minor changes"

if len(sys.argv) < 3:
	print("Usage: commit.py add/remove <mm/dd/yy>")
	sys.exit(0)

# Commit to Git
def commit(file_to_edit, author_date, message=COMMIT_MESSAGE):
	try:
		repo = git.Repo()
		index = repo.index
		index.add([file_to_edit])
		author_date = author_date.replace(tzinfo=timezone.utc)
		index.commit(message, author_date=author_date)
		print(f"Committed changes to '{file_to_edit}' ('{message}') with timestamp: {author_date}")
	except Exception as e:
		print(f"Error while commiting: {e}")

# Undo a commit to Git
def uncommit(author_date):
	try:
		# Adjust author_date to be in our timezone
		author_date = author_date.replace(tzinfo=timezone.utc)
		
		# Now iterate through commits
		repo = git.Repo()
		commits_to_delete = []
		for commit in repo.iter_commits("main"):
			commit_date = datetime.fromtimestamp(commit.authored_date, timezone.utc).date()

			# print(f"{commit.hexsha}\t{commit_date.strftime('%m/%d/%Y')}")
			if commit_date == author_date.date():
				print(f"Commit {commit.hexsha} will be deleted")
				commits_to_delete.append(commit)
		# Found everything, checkout to most recent head
		repo.git.checkout("HEAD")

		# Start rebasing
		for commit in commits_to_delete:
			# Get the parent commit hash
			if len(commit.parents) > 0:
				parent_commit = commit.parents[0]
				print(f"Rebasing around {commit.hexsha} using parent {parent_commit.hexsha}")
				repo.git.rebase("--onto", parent_commit.hexsha, f"{commit.hexsha}^")
			else:
				print(f"Commit {commit.hexsha} has no parents")
	except Exception as e:
		print(f"Error while uncommiting: {e}")

# Get the date
date_str = sys.argv[2]
commit_date = datetime.strptime(date_str, "%m/%d/%Y").date()
commit_date = datetime.combine(commit_date, datetime.min.time())


addrm = sys.argv[1]
if addrm == "add":
	commit("file.txt", commit_date)
elif addrm == "remove":
	uncommit(commit_date)
else:
	print("Usage: commit.py add/remove <mm/dd/yy>")
	sys.exit(0)
