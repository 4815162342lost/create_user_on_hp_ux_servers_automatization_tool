#!/usr/bin/python3
#generate password --  openssl passwd -crypt
import os
import subprocess
#import sys
#import getopt

os.chdir(os.path.dirname(os.path.realpath(__file__)))

def get_login_and_password():
    '''Function for return login and password hash as dictionary'''
    hp_users={}
    exec(open('hp_user_name.txt', 'r').read(), None, hp_users)
    return hp_users

def get_settings():
    '''Function for get group and comment. You can add new options, if you want'''
    settings={}
    exec(open('settings.txt', 'r').read(), None, settings)
    return settings

def question(answer):
    '''Function for processing answer (y\n) before continue'''
    if answer == 'y':
        pass
    elif answer == 'n':
        print("Fix the error and try again...")
        exit()
    else:
        print("Are you OK? Try again..")
        exit()

def create_accounts():
    """Function for create account"""
    #check len ght of the login
    hp_users = get_login_and_password()
    for current_user in hp_users.keys():
        if len(current_user) > 8:
            print("The login " + current_user + " is too long. The maximum length is 8 symbols. Fix it!")
            exit(0)

    for counter_1, current_user in enumerate(hp_users.keys()):
        print("Create the account for the user "+current_user)
        hp_server_list.seek(0)
        for counter_2, curren_hp_server in enumerate(hp_server_list):
            try:
                settings['comment']=settings['comment'].replace(' ', '_')
                command = "ssh {server} 'useradd -g {group} -s {skel} -c {comment} -k /etc/skel -m -p {pass_hash} {user}'".format(
                    server=curren_hp_server.rstrip(),
                    group=settings['group'],
                    skel=settings['shell'],
                    comment=settings['comment'],
                    pass_hash=hp_users[current_user],
                    user=current_user)
                if counter_1==0 and counter_2==0:
                    answer = input("Is construction correct?(y,n)\n" + command + "\n")
                    question(answer)
                proc=subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, universal_newlines=True)
                proc.wait(timeout=300)
            except:
                exit()
                print("ALARM! Check the server" + curren_hp_server.rstrip() + "immediately!")

def create_group():
    """Function for create group"""
    for counter, curren_hp_server in enumerate(hp_server_list):
        command = "ssh {server} 'groupadd {group_name}'".format(
        group_name=settings['group'],
        server=curren_hp_server.rstrip())
        if counter==0:
            answer=input("Is construction correct?(y,n)\n"+ command + "\n")
            question(answer)
        try:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            proc.wait(timeout=300)
        except:
            print("ALARM! Check the server" + curren_hp_server.rstrip() + "immediately!")

def edit_profile():
    hp_users = get_login_and_password()
    for counter_1, current_user in enumerate(hp_users.keys()):
        print("editing .profile of the user "+current_user)
        hp_server_list.seek(0)
        for counter_2, curren_hp_server in enumerate(hp_server_list):
            try:
                command = "ssh {server} 'echo {content}>>/home/{user}/.profile'".format(
                    server=curren_hp_server.rstrip(),
                    user=current_user,
                    content="aaaaaaaaaa")
                if counter_1==0 and counter_2==0:
                    answer = input("Is construction correct?(y,n)\n" + command + "\n")
                    question(answer)
                proc=subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, universal_newlines=True)
                proc.wait(timeout=300)
            except:
                exit()
                print("ALARM! Check the server" + curren_hp_server.rstrip() + "immediately!")

def run_custom_command():
    """Function for run custom programm"""
    command=input("Please, enter the command which will be run on servers:\n")
    for counter, curren_hp_server in enumerate(hp_server_list):
        command="ssh {server} '{command}'".format(
            server=curren_hp_server.rstrip(),
            command=command)
        if counter==0:
            answer=input("Is construction correct?(y,n)\n"+ command + "\n")
            question(answer)
        try:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            proc.wait(timeout=300)
        except:
            print("ALARM! Check the server" + curren_hp_server.rstrip() + "immediately!")

def menu_choose():
    """Function for display meny vir variables"""
    chose=input("Hello.\nPress 1 to create accounts \nPress 2 to create group \nPress 3 to edit '.profile'\nPress 4 to run custom command\n")
    if chose=='1':
        create_accounts()
    elif chose=='2':
        create_group()
    elif chose=='3':
        edit_profile()
    elif chose=='4':
        run_custom_command()

    else:
        print("Are you OK? Ehat are you doing? Try again.")

def start():
    """Main function"""
    menu_choose()

settings=get_settings()
hp_server_list=open('hp_server_list.txt', 'r')
start()
