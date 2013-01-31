# coding: utf8
# try something like
@auth.requires_login()
def index(): 
    response.files.insert(0,URL('static','js/jquery.flot.js'))
    response.files.insert(1,URL('static','js/jquery.flot.pie.js'))
    number_campaigns =  db(db.campaign.user_uid == auth.user.id)
    if number_campaigns:
        summary_btn =  SPAN(_class='icon magnifier icon-signal'),SPAN('Summary',_class='buttontext button')
        return dict(form = SQLFORM.grid(db.campaign.user_uid == auth.user,create=False,maxtextlength=64,
                 links = [lambda row: A(summary_btn,_class='w2p_trap button btn',_onclick="summaryOnClick(%s)"%row.id)]))
def get_summary():
   if request.post_vars.id:
      db_campaign = db(db.campaign.user_uid == auth.user.id)(db.campaign.id == request.post_vars.id).select().first()
      if db_campaign:
          number_of_success = db_campaign.sending_result(db.sending_result.status == 'success').count()
          number_of_fail = db_campaign.sending_result(db.sending_result.status == 'fail').count()
          number_of_ongoing = int(db_campaign.total_reciver) - (number_of_success + number_of_fail)
          result = [("Success",number_of_success),("Fail",number_of_fail),("Ongoing",number_of_ongoing)]
          response.headers['Content-Type'] = 'application/json'
          return response.json(result)


def resend_sms():
    if request.post_vars.id:
        db_campaign = db(db.campaign.user_uid == auth.user.id)(db.campaign.id == request.post_vars.id).select().first()
        if db_campaign:
            fail_result = db_campaign.sending_result(db.sending_result.status == 'fail').select(db.sending_result.phone_number)
            for result in fail_result:
                list_fail_numbers += result,phone_number +','
            sending_list = list_fail_numbers[:-1]
            import urllib
            from google.appengine.api import urlfetch
            params = {'app_id': auth.user.app_id,
                   'access_token': auth.user.access_token,
                   'dest':sending_list,
                   'msg':db_campaign.msg,
                   'tag':db_campaign.id,
                   'notify_url':URL(c='post_back',f='sms_post_back')
                  }
            data = urllib.urlencode(params)
            result = urlfetch.fetch(url="https://secure.hoiio.com/open/sms/bulk_send",
                        payload=data,
                        method=urlfetch.POST,
                        headers={'Content-Type': 'application/x-www-form-urlencoded'})
            response.headers['Content-Type'] = 'application/json'            
            from gluon.contrib import simplejson as json
         
            response = json.loads(result.content) 
            if response['status'] == "success_ok":
                session.flash = "You message's sent successful"
            else :
                session.flash = "Have error (%s) please try again " % response['status']
    redirect(URL('index'))
