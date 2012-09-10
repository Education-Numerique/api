import datetime
from wtforms import Form, BooleanField, TextField, validators, DateTimeField

from lib import router, output
from lib.app import Controller, Error
from lib.storage import Db
from lib.admin import AdminRequest, AdminError
from lib.flush import FlushRequest
from lib.mailer import AsyncMailer, AsyncUserRegister

from model.users import User, UserFactory, Duplicate


class Account(router.Root):

    def create(self, environ, params):
        try:
            datas = Controller().getRequest().POST
            form = AccountCreateValidation(datas)

            if not form.validate():
                output.error(form.errors)

            try:
                beta = BetaInvite.check(form.beta.data)
            except AlreadyValidatedCode:
                output.error('already validated beta code', 403)
            except UnknownValidationCode:
                output.error('invalid beta code', 400)

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
                resp = AdminRequest().request('/1.0/user', {
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
            profile['gender'] = int(form.gender.data)
            profile['birthdate'] = form.birthdate.data

            #XXX should be done by the model
            Db().get('profile').update({'uid': user.uid}, {
                'datas': profile,
                'uid': user.uid,
                'updated': datetime.datetime.utcnow()
            }, True)

            #validate beta code
            BetaInvite.validate(form.beta.data, user)

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
                    'subject': 'Validate your e-mail at Roxee',
                    'from_email': 'no-reply@roxee.tv',
                    'from_name': 'Roxee Project',
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
                    'google_analytics_domains': ['beta.roxee.tv'],
                    'google_analytics_campaign': ['internal_email_validation'],
                    'auto_text': True,
                    'track_opens': True,
                    'track_clicks': True
                }
            ).start()

            bday = ''
            if (profile['birthdate'].month, profile['birthdate'].day):
                bday = profile['birthdate']

            #register user in mailchimp internal user list
            AsyncUserRegister(
                email_address=beta.email,
                #use the invitation email and update it
                double_optin=False,
                update_existing=True,
                merge_vars={
                    'EMAIL': user.email,
                    'UID': user.uid,
                    'USERNAME': user.username,
                    'FNAME': user.firstname,
                    'LNAME': user.lastname,
                    'GENDER': 'Male' if profile['gender'] == 1 else 'Female',
                    'STATUS': 'Pending activation',
                    'ACTCODE': user.activation_code,
                    'CREATIONDT': "%s" % datetime.datetime.utcnow(),
                    'BIRTHDAY': "%s/%s",
                    'SOURCE': 'Roxee'
                }
            ).start()

            #Let's flush a few stuff
            FlushRequest(
            ).request('users.Beta.[requests]', {'uid': beta.godfather})

            try:
                #XXX should not refetch from MONGO
                UserSync.update(UserFactory().get(user.uid))
            except:
                print('////####\\\\\\\\ user index error')

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
            AsyncMailer(
                template_name='registered',
                template_content=[],
                global_merge_vars=[],
                message={
                    'subject': 'Welcome to Roxee Private Beta !',
                    'from_email': 'no-reply@roxee.tv',
                    'from_name': 'Roxee Project',
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
    gender = TextField('gender', [validators.Length(min=1, max=2)])
    birthdate = DateTimeField('birthdate', format='%Y-%m-%d')
    beta = TextField('beta', [validators.Length(min=20, max=20)])
