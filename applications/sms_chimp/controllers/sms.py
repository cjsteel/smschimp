# coding: utf8
# try something like
@auth.requires_login()
def index(): 
    return dict()

def send_sms():
    if auth.user.access_token and auth.user.app_id:
         numbers = ""
         groups=""
         total_reciver=0
         for group in request.post_vars.groups.split(','):
              db_group = db(db.contact_group.user_uid == auth.user.id)(db.contact_group.name == group).select().first()
              if db_group:
                  phone_numbers = db_group.contact.select(db.contact.phone_number)
                  numbers += ','.join([phone.phone_number for phone in phone_numbers])
                  groups += db_group.name +',' 
                  total_reciver +=1
         if request.post_vars.campaign_name and groups:
                groups = groups[:-1]
                campaign_id = db.campaign.insert(name=request.post_vars.campaign_name,
                                   groups=groups,
                                   msg = request.post_vars.message,
                                   total_reciver = total_reciver or 0)
         import urllib
         from google.appengine.api import urlfetch
         params = {'app_id': auth.user.app_id,
                   'access_token': auth.user.access_token,
                   'dest':numbers,
                   'msg':request.post_vars.message,
                   'tag':campaign_id or '',
                   'notify_url':"http://hoiiosmschimp.appspot.com/sms_chimp/post_back/sms_post_back"
                  }
         data = urllib.urlencode(params)
         result = urlfetch.fetch(url="https://secure.hoiio.com/open/sms/bulk_send",
                        payload=data,
                        method=urlfetch.POST,
                        headers={'Content-Type': 'application/x-www-form-urlencoded'})
                        
         from gluon.contrib import simplejson as json
         
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
    groups = db(db.contact_group.user_uid == auth.user.id).select(db.contact_group.name).find(lambda row:row.name.startswith(query))   
    
    return DIV(*[DIV(groups.name,
                       _onclick="add_new_group('%s')" % groups.name,
                       _class="group_selector") for groups in groups])
