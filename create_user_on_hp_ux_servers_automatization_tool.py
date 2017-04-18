#!/usr/bin/python3
#generate password --  openssl passwd -crypt
import os
import subprocess
import sys

os.chdir(os.path.dirname(os.path.realpath(__file__)))

if sys.platform=="linux":
    ssh="ssh "
elif sys.platform=="win32":
    my_password=input("Please, enter the root password")
    ssh="\"C:\Program Files (x86)\PuTTY\plink.exe\" -pw " + my_password + " root@"

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

def get_names_of_tje_login():
    '''Function for return login and password hash as dictionary'''
    names={}
    exec(open('names.txt', 'r').read(), None, names)
    return names

def question(answer):
    '''Function for processing answer (y\n) before continue'''
    if answer == 'y':
        pass
    elif answer == 'n':
        print("Fix the error and try again...")
        os._exit(1)
    else:
        print("Are you OK? Try again..")
        os._exit(1)

def create_accounts():
    """Function for create account"""
    #check len of the login (HP UX soes not support login longer 8 symbol)
    hp_users = get_login_and_password()
    for current_user in hp_users.keys():
        if len(current_user) > 8:
            print("The login " + current_user + " is too long. The maximum length is 8 symbols. Fix it!")
            exit()
    #loop for read usernames
    for counter_1, current_user in enumerate(hp_users.keys()):
        print("Create the account for the user "+current_user)
        hp_server_list.seek(0)
        #loop for read server name
        for counter_2, curren_hp_server in enumerate(hp_server_list):
            try:
                settings['comment']=settings['comment'].replace(' ', '_')
                command = "{ssh}{server} 'useradd -g {group} -s {skel} -c {comment} -k /etc/skel -m -p {pass_hash} {user}'".format(
                    ssh=ssh,
                    server=curren_hp_server.rstrip(),
                    group=settings['group'],
                    skel=settings['shell'],
                    comment=settings['comment'],
                    pass_hash=hp_users[current_user],
                    user=current_user)
                #check command in first iteration
                if counter_1==0 and counter_2==0:
                    answer = input("Is construction correct?(y,n)\n" + command + "\n")
                    question(answer)
                print("Server:", curren_hp_server.rstrip())
                proc=subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, universal_newlines=True)
                proc.wait(timeout=300)
            except:
                exit()
                print("ALARM! Check the server" + curren_hp_server.rstrip() + " immediately!")

def create_group():
    """Function for create group"""
    print("Creating group for  "+settings['group'])
    for counter, curren_hp_server in enumerate(hp_server_list):
        command = "{ssh}{server} 'groupadd {group_name}'".format(
        ssh=ssh,
        group_name=settings['group'],
        server=curren_hp_server.rstrip())
        # check command in first iteration
        if counter==0:
            answer=input("Is construction correct?(y,n)\n"+ command + "\n")
            question(answer)
        try:
            print("Server:", curren_hp_server.rstrip())
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            proc.wait(timeout=300)
        except:
            print("ALARM! Check the server" + curren_hp_server.rstrip() + " immediately!")

def edit_profile():
    hp_users = get_login_and_password()
    names=get_names_of_tje_login()
    profile_file=open("profile.txt", 'r')
    for counter_1, current_user in enumerate(hp_users.keys()):
        print("editing .profile of the user "+current_user)
        hp_server_list.seek(0)
        for counter_2, curren_hp_server in enumerate(hp_server_list):
            print("On the server " + curren_hp_server.rstrip())
            profile_file.seek(0)
            for counter_3, current_line in enumerate(profile_file.readlines()):
                try:
                    command = '{ssh}{server} 'echo '{content}'>>/home/{user}/.profile''.format(
                        ssh=ssh,
                        server=curren_hp_server.rstrip(),
                        user=current_user,
                        content=current_line.rstrip())
                    if counter_1==0 and counter_2==0 and counter_3==0:
                        answer = input("Is construction correct?(y,n) WARNING! Check only first line!\n" + command + "\n")
                        question(answer)
                    print(command)
                    proc=subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, universal_newlines=True)
                    proc.wait(timeout=300)
                except:
                    print("ALARM! Check the server" + curren_hp_server.rstrip() + "immediately!")
            try:
                command = '{ssh}{server} 'echo 'Hello, {content}! It is HP-UX!'>>/home/{user}/.profile''.format(
                    ssh=ssh,
                    server=curren_hp_server.rstrip(),
                    user=current_user,
                    content=names[current_user])
                if counter_2==0:
                    answer = input("Is name and home folder correct?(y,n)\n" + command + "\n")
                    question(answer)
                print(command)
                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
                proc.wait(timeout=300)
            except:
                print("ALARM! Check the server" + curren_hp_server.rstrip() + " immediately!")

def run_custom_command():
    """Function for run custom programm"""
    command_i=input("Please, enter the command which will be run on servers:\n")
    for counter, curren_hp_server in enumerate(hp_server_list):
        command='{ssh}{server} '{command_r}''.format(
            ssh=ssh,
            server=curren_hp_server.rstrip(),
            command_r=command_i)
        if counter==0:
            answer=input("Is construction correct?(y,n)\n"+ command + "\n")
            question(answer)
        try:
            #print(command)
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            proc.wait(timeout=300)
            print(curren_hp_server.rstrip())
            print(proc.stdout.read())
        except:
            print("ALARM! Check the server" + curren_hp_server.rstrip() + " immediately!")

def menu_choose():
    """Function for display menu for variables"""
    choose=input("Hello.\nPress 1 to create accounts \nPress 2 to create group \nPress 3 to edit '.profile'\nPress 4 to run custom command\nPress 0 for exit\n")
    if choose=='0':
        exit()
    if choose=='1':
        create_accounts()
    elif choose=='2':
        create_group()
    elif choose=='3':
        edit_profile()
    elif choose=='4':
        run_custom_command()
    else:
        print("Are you OK? What are you doing? Try again.")

def start():
    """Main function"""
    menu_choose()

settings=get_settings()
hp_server_list=open('hp_server_list.txt', 'r')
start()
