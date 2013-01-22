from mailsnake import MailSnake
from .config import Config
import threading

mandrill = MailSnake(Config().get('mailer')['mandrill'], api='mandrill')
mailchimp = MailSnake(Config().get('mailer')['mailchimp'])

#XXX Thread queue
#http://stackoverflow.com/questions/9770133/cpu-load-of-a-python-threadpool


class AsyncMailer(threading.Thread):

    def __init__(self, **params):
        self.params = params
        threading.Thread.__init__(self)
        #self.daemon = True

    def run(self):
        print('****sending', self.params)
        m = mandrill.messages.send_template(**self.params)

        return

# merge_vars = {
#     'UID' : user.uid,
#     'USERNAME' : user.username,
#     'FNAME' : user.firstname,
#     'LNAME' : user.lastname,
#     'AVATAR' : '',
#     'STATUS' : 'Pending activation', #Invited/Pending activation/Registered
#     'ACTCODE' : '', #activation code
#     'INVITEDT' : '', #invitation date
#     'CREATIONDT' : '', #creation date
#     'BIRTHDAY' : '', #MM/DD
#     'PREMIUM' : 0, #premier user ?
#     'BETAUSER' : 1, #is a beta user ?,
#     'SOURCE' : '' #Facebook or Roxee
# }


class AsyncUserRegister(threading.Thread):

    def __init__(self, **params):
        self.params = params
        self.params['id'] = Config().get('mailer')['list_id']
        threading.Thread.__init__(self)
        #self.daemon = True

    def run(self):
        m = mailchimp.listSubscribe(**self.params)

        return
