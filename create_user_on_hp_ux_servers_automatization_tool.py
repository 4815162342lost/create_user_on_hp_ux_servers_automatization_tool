#!/usr bin/python3
#generate password --  openssl passwd -crypt
import os
import subprocess

os.chdir(os.path.dirname(os.path.realpath(__file__)))

#question=input("Did you edit settings.txt, hp_user_name.txt and hp_server_list.txt file? \n Continue? [y/n]")

# if question=='y':
#     print("script is starting now...")
#     pass
# elif question=='n':
#     print("fix files and try again")
#     exit()
# else:
#     print("Are you OK?")
#     exit()

def get_login_and_password():
    '''Function for return login and password hash as dictionary'''
    hp_users={}
    exec(open('hp_user_name.txt', 'r').read(), None, hp_users)
    return  hp_users

def get_settings():
    '''Function for get group and comment. You can add new options, if you want'''
    settings={}
    exec(open('settings.txt', 'r').read(), None, settings)
    return settings

def upload_skel_to_servers():
    """Function for upload skeland extract files from arch"""
    global hp_server_list
    for current_server in hp_server_list:
        try:
            subprocess.Popen("ssh " + current_server.rstrip() +  " '" +  'mkdir /tmp/skell_fj' + "'", shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            subprocess.Popen("scp "+ settings['skel'] + " root@" + current_server.rstrip() + ":" + "/tmp/skell_fj" + "'", shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            subprocess.Popen("ssh " + current_server.rstrip() +  " '" + 'tar -xvf /tmp/skell_fj/skel.tar' + "'", shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            exit()
        except:
            print("There are error in the server " + current_server.rstrip() + ". Please, check.")

hp_users=get_login_and_password()
for current_user in hp_users.keys():
    if len(current_user) >8:
        print("The login " + current_user + " is too long. The maximum length is 8 symbols. Fix it!")
        exit(0)

settings=get_settings()
hp_server_list=open('hp_server_list.txt', 'r')
upload_skel_to_servers()

for current_user in hp_users.keys():
    print("Create the account for the user "+current_user)
    hp_server_list.seek(0)
    for curren_hp_server in hp_server_list:
        print(curren_hp_server)
        try:
            proc=subprocess.Popen("ssh " + curren_hp_server.rstrip() + " useradd -g " + settings['group'] + ' -s ' + settings['shell']  + " "  +  "-d /home/" + current_user + " -c " + "'" + settings['comment'] + "' " + "-k /tmp/skell_fj" + ' -m ' + '-p ' +  hp_users[current_user] + " " + current_user, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            proc.wait(timeout=300)
        except:
            print("ALARM! Check the server" + curren_hp_server + "immediately!")
