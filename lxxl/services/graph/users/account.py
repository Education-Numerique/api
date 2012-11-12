import datetime
from wtforms import Form, BooleanField, TextField, validators, DateTimeField

from lxxl.lib import router, output
from lxxl.lib.app import Controller, Error
from lxxl.lib.storage import Db
from lxxl.lib.admin import AdminRequest, AdminError
from lxxl.lib.flush import FlushRequest
from lxxl.lib.mailer import AsyncMailer, AsyncUserRegister

from lxxl.model.users import User, UserFactory, Duplicate


class Account(router.Root):

    def create(self, environ, params):
        try:
            datas = Controller().getRequest().POST
            form = AccountCreateValidation(datas)

            if not form.validate():
                output.error(form.errors)

            user = User()
            user.email = form.email.data.lower()
            user.username = form.username.data
            user.date = datetime.datetime.utcnow()

            #UID
            id = Db().get('users').increment()
            user.generateUid(id)

            #activation code
            user.generateActivationCode()

            try:
                user = UserFactory().new(user)

            except Duplicate as e:
                output.error({'duplicate': e.value})

            #Init account on admin service
            try:
                resp = AdminRequest().request('/1.0/user/', {
                    'uid': user.uid,
                    'login': user.email.lower(),
                    'password': form.password.data}
                )
            except AdminError as e:
                output.error('Registration error : %s' % e, 500)

            if resp is None or int(resp.getHeader('status')) != 201:
                Db().get('users').remove(user._id)
                output.error('registration troubles ...', 500)

            profile = {}

            #XXX should be done by the model
            Db().get('profile').update({'uid': user.uid}, {
                'datas': profile,
                'uid': user.uid,
                'updated': datetime.datetime.utcnow()
            }, True)

            if user.email != 'void@webitup.fr':
                #send mail
                AsyncMailer(
                    template_name='email-validation',
                    template_content=[{
                        'name': 'validation_code',
                        'content': user.activation_code
                    }],
                    global_merge_vars=[
                    ],
                    message={
                        'subject': 'Validate your e-mail at Lxxl',
                        'from_email': 'void@webitup.fr',
                        'from_name': 'Education & Numérique',
                        'headers': {},
                        'to': [
                            {
                                'email': user.email,
                                'name': user.username
                            }
                        ],
                        'metadata': {
                            'uid': user.uid,
                            'email_validation_code': user.activation_code
                        },
                        'tags': ['email-validation'],
                        'google_analytics_domains': ['beta.lxxl.com'],
                        'google_analytics_campaign': [
                            'internal_email_validation'
                        ],
                        'auto_text': True,
                        'track_opens': True,
                        'track_clicks': True
                    }
                ).start()


            #register user in mailchimp internal user list
            AsyncUserRegister(
                email_address=user.email,
                #use the invitation email and update it
                double_optin=False,
                update_existing=True,
                merge_vars={
                    'EMAIL': user.email,
                    'UID': user.uid,
                    'USERNAME': user.username,
                    'FNAME': user.firstname,
                    'LNAME': user.lastname,
                    'STATUS': 'Pending activation',
                    'ACTCODE': user.activation_code,
                    'CREATIONDT': "%s" % datetime.datetime.utcnow(),
                    'SOURCE': 'Classic'
                }
            ).start()

            output.success(user.activation_code, 200)

        except Error:
            pass

        return Controller().getResponse(True)

    def validate(self, environ, params):
        try:
            datas = Controller().getRequest().POST

            if not 'email' in datas or not 'code' in datas:
                output.error('invalidate code', 400)

            user = UserFactory().get({'email': datas['email']})

            if user is None:
                output.error('unknown user', 400)

            if user.activate == 1:
                output.error('already activated', 403)

            if user.activation_code != datas['code']:
                output.error('invalidate code', 400)

            #Init account on admin service
            try:
                uri = '/1.0/user/' + user.uid + '/activate'
                resp = AdminRequest().request(uri, {
                    'uid': user.uid,
                    'login': user.email
                })
            except AdminError as e:
                output.error('Registration error : %s' % e, 500)

            if resp is None or int(resp.getHeader('status')) != 200:
                output.error('activation troubles ...', 500)

            user.activation_code = None
            user.activate = 1

            Db().get('users').update({'uid': user.uid}, user)

            #send mail
            if user.email != 'void@webitup.fr':
                AsyncMailer(
                    template_name='registered',
                    template_content=[],
                    global_merge_vars=[],
                    message={
                        'subject': 'Welcome to LxxL !',
                        'from_email': 'void@webitup.fr',
                        'from_name': 'Education & Numérique',
                        'headers': {},
                        'to': [
                            {
                                'email': user.email,
                                'name': user.username
                            }
                        ],
                        'metadata': {
                            'uid': user.uid
                        },
                        'tags': ['welcome'],
                        'google_analytics_domains': ['beta.roxee.tv'],
                        'google_analytics_campaign': ['internal_registered'],
                        'auto_text': True,
                        'track_opens': True,
                        'track_clicks': True
                    }
                ).start()

            output.success('user activated', 200)
        except Error:
            pass

        return Controller().getResponse(True)

    def activate(self, environ, params):
        output.error('activate not yet', 501)
        return Controller().getResponse(True)

    def deactivate(self, environ, params):
        output.error('activate not yet', 501)
        return Controller().getResponse(True)

    def delete(self, environ, params):
        output.error('delete not yet', 501)
        return Controller().getResponse(True)

    #XXX remove me after alpha
    def list(self, environ, params):
        try:
            Controller().checkToken()
            relation = Controller().getRelation()

            #XXX fix privacy
            # if relation != 2 and relation != 1:
            #     output.error('#ApiKeyUnauthorized', 403)

            friends, total = UserFactory().getAllUsers()

            # for u in friends:
            #     try:
            #         UserSync.update(u)
            #     except:
            #         print('////####\\\\\\\\ user index error')

            output.noCache()
            output.varnishCacheManager('1 year')
            output.userList(friends, total)

        except Error:
            pass
        return Controller().getResponse(True)

    def authenticate(self, environ, params):
        try:
            Controller().checkToken()

            output.noCache()

            Controller().getResponse(
            ).headers['X-UID'] = '%s' % Controller().getUid()
            output.success('authenticated', 200)

        except Error:
            pass

        return Controller().getResponse(True)


class AccountCreateValidation(Form):
    username = TextField('username', [validators.Length(min=5, max=25)])
    email = TextField('email', [
        validators.Length(min=6, max=320),
        validators.Email()
    ])
    password = TextField('password', [validators.Length(min=6, max=25)])
