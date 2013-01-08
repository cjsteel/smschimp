# coding: utf8
# try something like
@auth.requires_login()
def index(): 
    return dict()

def send_sms():
    if auth.user.access_token and auth.user.app_id:
         numbers = ""
         for group in request.post_vars.groups.split(','):
              db_group = db(db.contact_group.user_uid == auth.user.id)(db.contact_group.name == group).select().first()
              if db_group:
                  phone_numbers = db_group.contact.select(db.contact.phone_number)
                  numbers += ','.join([phone.phone_number for phone in phone_numbers])
         
         import urllib
         from google.appengine.api import urlfetch
         params = {'app_id': auth.user.app_id, 'access_token': auth.user.access_token,'dest':numbers,'msg':request.post_vars.message}
         data = urllib.urlencode(params)
         result = urlfetch.fetch(url="https://secure.hoiio.com/open/sms/bulk_send",
                        payload=data,
                        method=urlfetch.POST,
                        headers={'Content-Type': 'application/x-www-form-urlencoded'})
                        
         from django.utils import simplejson as json
         
         response = json.loads(result.content) 
         if response['status'] == "success_ok":
            session.flash = "You message's sent successful"
         else :
            session.flash = "Have error (%s) please try again " % response['status']
    else:
        session.flash = "You have to configuration app id and access token before sending sms"
    redirect(URL('index'))


def group_selector():
    if not request.vars.query: 
        return ''
    query = request.vars.query
    groups = db(db.contact_group.user_uid == auth.user.id)(db.contact_group.name.like(query +'%')).select(db.contact_group.name)   
    
    return DIV(*[DIV(groups.name,
                       _onclick="add_new_group('%s')" % groups.name,
                       _class="group_selector") for groups in groups])
