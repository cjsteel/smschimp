# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('mysql://root:123456@localhost/sms_chimp',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('gae')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)

crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.settings.extra_fields['auth_user'] = [
    Field('app_id',comment ="app_id and access_token can get from Hoiio"),
    Field('access_token'),
    Field('default_prefix',comment = "This the phone number prefix if no +")]
auth.define_tables(username=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'


## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True


## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
##from gluon.contrib.login_methods.rpx_account import use_janrain
##use_janrain(auth, filename='private/janrain.key')
##from gluon.contrib.login_methods.gae_google_account import GaeGoogleAccount
##auth.settings.login_form=GaeGoogleAccount()

#from gluon.contrib.login_methods.rpx_account import RPXAccount
#auth.settings.actions_disabled=['register','change_password',
#        'request_reset_password']
#auth.settings.login_form = RPXAccount(request,
#              api_key="9efcb933f0f448c65bc3d0554943017ea5e669b0",
#              domain="smschimp",
#              url = "http://localhost:8080/%s/default/user/login" % request.application)
from rpxauth import RPXAuth
rpxAuth = RPXAuth(auth)
rpxAuth.embed = True
rpxAuth.allow_local = True
rpxAuth.api_key = "9efcb933f0f448c65bc3d0554943017ea5e669b0"
rpxAuth.realm = "smschimp"
rpxAuth.token_url = "http://hoiiosmschimp.appspot.com/sms_chimp/default/user/login"
#########################################################################
db.define_table('contact_group',
                 Field('name',length=100),
                 Field('modified_on','datetime',default=request.now),
                 Field('user_uid',db.auth_user,readable=False,writable=False,default=auth.user),format ='%(name)s')

db.define_table('contact',
                Field('name',length = 200),
                Field('phone_number',length = 30),
                Field('dob','date'),
                Field('contact_group_id',db.contact_group),
                Field('group_name',length =100),
                Field('modified_on','datetime',default=request.now),
                Field('user_uid',db.auth_user,readable=False,writable=False,default=auth.user))
db.define_table('campaign', 
                 Field('name',length=200,unique = True),
                 Field('groups',writable=False),
                 Field('msg','text',writable=False),
                 Field('total_reciver',writable=False),
                 Field('create_on','datetime',default=request.now,writable=False,readable=False),
                 Field('user_uid',db.auth_user,readable=False,writable=False,default=auth.user))
db.define_table('sending_result',
                 Field('campagin_id',db.campaign),
                 Field('phone_number',length = 30),
                 Field('status'),
                 Field('modified_on','datetime',default=request.now,writable=False,readable=False))
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
