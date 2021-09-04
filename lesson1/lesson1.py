##########################################
#
# Author: Dmitry Gromov
# Date: 2021-08-31
# Homework# 1
#
##########################################


import sys
import json
import requests


def task_one():
    """Сохраняет в файл список репозиториев пользователя.
    """

    gituser = ""
    while(len(gituser) == 0): 
        gituser = input('Enter github user:')

    url = "https://api.github.com/users/" + gituser + "/repos"     
    print("url is:", url)
    response = requests.get(url) 
    if response.status_code == 200:
        git_data = json.loads(response.text)
        
        if len(git_data) == 0:
            print('User does not have any repos')
            sys.exit(0)

        try:
            with open('./repos.json', 'w', encoding='utf8') as f:
                f.write(response.text)
        except OSError as e:
            print(e)
            sys.exit(-1)

        print("File \'repos.json\' has been saved successfully")

#        print("Repo list of user " + "\'" + gituser + "\": ")
#        for item in git_data:
#            repo = item
#            print('Repo name: ' + repo['name'] + '\t' + \
#                'repo full name: ' + repo['full_name'])
#    else:
#        print('Something went wrong. Exit')

    return None


def task_two():
    """ не смог :(
    """
    pass


def main():
    """Домашнее задание №1"""
  
    task_one()
    task_two()


if __name__ == '__main__':
    main()


