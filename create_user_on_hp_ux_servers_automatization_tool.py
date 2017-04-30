#!/usr/bin/python3
#generate password --  openssl passwd -crypt
import os
import subprocess
import sys

os.chdir(os.path.dirname(os.path.realpath(__file__)))

if sys.platform=="linux":
    ssh="ssh "
    scp="scp "
elif sys.platform=="win32":
    my_password=input("Please, enter the root password\n")
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

def check_logins_and_names(login_from_hp_user_name, login_from_names):
    '''Function for check that hp_user_name.txt and names.txt contain same logins'''
    logins_set=set(list(login_from_hp_user_name.keys()))
    names_set=set(list(login_from_names))
    difference_set=set.symmetric_difference(logins_set, names_set)
    if  len(difference_set) !=0:
        print("Files name.txt and hp_user_name.txt is not same! Fix it.")
        exit()

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

def create_accounts(hp_ux_version):
    """Function for create account"""
    #check len of the login (HP UX soes not support login longer 8 symbol)
    hp_users = get_login_and_password()
    for current_user in hp_users.keys():
        if len(current_user) > 8:
            print("The login " + current_user + " is too long. The maximum length is 8 symbols. Fix it!")
            exit()
    #loop for read usernames
    for counter_1, current_user in enumerate(hp_users.keys()):
        print("Creating the account for the user "+current_user)
        hp_server_list.seek(0)
        #loop for read server name
        for counter_2, curren_hp_server in enumerate(hp_server_list):
            try:
                settings['comment']=settings['comment'].replace(' ', '_')
                if hp_ux_version=="new":
                    command = "{ssh}{server} 'useradd -g {group} -s {shell} -c {comment} -k /etc/skel -m -p '{pass_hash}' {user}'".format(
                        ssh=ssh,
                        server=curren_hp_server.rstrip(),
                        group=settings['group'],
                        shell=settings['shell'],
                        comment=settings['comment'],
                        pass_hash=hp_users[current_user],
                        user=current_user)
                elif hp_ux_version=="old":
                    command = "{ssh}{server} 'useradd -g {group} -s {shell} -c {comment} -k /etc/skel -m {user}'".format(
                        ssh=ssh,
                        server=curren_hp_server.rstrip(),
                        group=settings['group'],
                        shell=settings['shell'],
                        comment=settings['comment'],
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
                print("ALARM! Check the server " + curren_hp_server.rstrip() + " immediately!")

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
            print("ALARM! Check the server " + curren_hp_server.rstrip() + " immediately!")

def edit_profile():
    '''Function for modify .profile'''
    hp_users = get_login_and_password()
    #if need create personal welcome, check that list is correct
    if settings['say_hello']=='True':
        names=get_names_of_tje_login()
        check_logins_and_names(hp_users, names)
    profile_file=open("profile.txt", 'r')
    for counter_1, current_user in enumerate(hp_users.keys()):
        print("editing .profile of the user "+current_user)
        hp_server_list.seek(0)
        for counter_2, current_hp_server in enumerate(hp_server_list):
            current_hp_server=current_hp_server.rstrip()
            print("On the server " + current_hp_server)
            profile_file.seek(0)
            #copy our .profile to the server and modify .profile on the server
            command='{scp} ./profile.txt root@{server}:/tmp/profile.txt'.format(
            scp=scp,
            server=current_hp_server)
            command_2 = '{ssh}{server} "cat /tmp/profile.txt>>/home/{user}/.profile"'.format(
                ssh=ssh,
                user=current_user,
                server=current_hp_server)
            try:
                if counter_1==0 and counter_2==0:
                    answer = input("Is construction correct?(y,n)\n" + command + "\n")
                    question(answer)
                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
                proc.wait(timeout=300)
                proc = subprocess.Popen(command_2, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
                proc.wait(timeout=300)
            except:
                print("ALARM! Check the server" + current_hp_server.rstrip() + " immediately!")
            #create personal welcome
            if settings['say_hello'] == 'True':
                with open("hello_user.txt", "w") as hello_file:
                    hello_file.write("echo Hello, {user}! It is HP-UX, not Linux. Be careful!\n".format(user=names[current_user]))
                command = '{scp} ./hello_user.txt root@{server}:/tmp/hello_user.txt'.format(
                    scp=scp,
                    server=current_hp_server)
                command_2 = '{ssh}{server} "cat /tmp/hello_user.txt>>/home/{user}/.profile"'.format(
                    ssh=ssh,
                    user=current_user,
                    server=current_hp_server)
                try:
                    if counter_2==0:
                        answer = input("Is name and home folder correct?(y,n)\nhome: {login}; name: {real_name}\n".format(
                            real_name=names[current_user],
                            login=current_user))
                        question(answer)
                    command_3="{ssh}{server} 'rm -f /tmp/hello_user.txt /tmp/hello_user.txt'".format(
                    ssh=ssh,
                    server=current_hp_server)
                    for com in command, command_2, command_3:
                        proc = subprocess.Popen(com, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
                        proc.wait(timeout=300)
                except:
                    print("ALARM! Check the server " + current_hp_server.rstrip() + " immediately!")

def run_custom_command():
    """Function for run custom programm"""
    command_i=input("Please, enter the command which will be run on servers:\n")
    for counter, curren_hp_server in enumerate(hp_server_list):
        command="{ssh}{server} '{command_r}'".format(
            ssh=ssh,
            server=curren_hp_server.rstrip(),
            command_r=command_i)
        if counter==0:
            answer=input("Is construction correct?(y,n)\n"+ command + "\n")
            question(answer)
        try:
            print(curren_hp_server.rstrip())
            proc = subprocess.Popen(command, shell=True, universal_newlines=True)
            proc.wait(timeout=300)
        except:
            print("ALARM! Check the server " + curren_hp_server.rstrip() + " immediately!")

def copy_file():
    """Function for copy file via scp"""
    source=input("Please, enter the file which should be copy to the server\n")
    destination=input("Please, enter the destination of the file (full path)\n")
    for counter, curren_hp_server in enumerate(hp_server_list):
        command="{scp}'{source} root@{server}:{destination}'".format(
            scp=scp,
            source=source,
            server=curren_hp_server.rstrip(),
            destination=destination)
        if counter==0:
            answer=input("Is construction correct?(y,n)\n"+ command + "\n")
            question(answer)
        try:
            print(curren_hp_server.rstrip())
            proc = subprocess.Popen(command, shell=True, universal_newlines=True)
            proc.wait(timeout=300)
        except:
            print("ALARM! Check the server " + curren_hp_server.rstrip() + " immediately!")

def change_password():
    """Function for change passwords"""
    hp_users = get_login_and_password()
    for current_user in hp_users.keys():
        if len(current_user) > 8:
            print("The login " + current_user + " is too long. The maximum length is 8 symbols. Fix it!")
            exit()
    #loop for read usernames
    for counter_1, current_user in enumerate(hp_users.keys()):
        print("Changint the password of the user "+current_user)
        hp_server_list.seek(0)
        #loop for read server name
        for counter_2, curren_hp_server in enumerate(hp_server_list):
            try:
                settings['comment']=settings['comment'].replace(' ', '_')
                command = "{ssh}{server} '/usr/sam/lbin/usermod.sam -p '{pass_hash}' {user}'".format(
                    ssh=ssh,
                    server=curren_hp_server.rstrip(),
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
                print("ALARM! Check the server " + curren_hp_server.rstrip() + " immediately!")

def menu_choose():
    """Function for display menu for variables"""
    choose=input("Hello.\nPress 1 to create accounts with password (HP-UX 11.31+)\nPress 2 to create accounts without password (HP-UX 11.23+)  \nPress 3 to create group \nPress 4 to edit '.profile'"
                 "\nPress 5 for change the password of the users\nPress 6 for copy file to remote server \nPress 7 to run custom command \nPress 0 for exit\n")
    if choose=='0':
        exit()
    elif choose=='1':
        create_accounts("new")
    elif choose=='2':
        create_accounts("old")
    elif choose=='3':
        create_group()
    elif choose=='4':
        edit_profile()
    elif choose=='5':
        change_password()
    elif choose=='6':
        copy_file()
    elif choose=='7':
        run_custom_command()
    else:
        print("Are you OK? What are you doing? Try again.")

def start():
    """Main function"""
    menu_choose()

settings=get_settings()
hp_server_list=open('hp_server_list.txt', 'r')
start()
