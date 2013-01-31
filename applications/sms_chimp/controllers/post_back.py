# coding: utf8
# try something like
def sms_post_back():
    if request.vars.tag :
       campagin_id = int(request.get_vars.tag)
       result_db = db.campaign[campagin_id].sending_result(db.sending_result.phone_number == request.get_vars.dest).select().first()
       if request.get_vars.sms_status == 'delivered':
          status = 'success'
       elif (request.get_vars.sms_status == 'failed') or (request.get_vars.sms_status == "error"):
          status = 'fail'
       else:
          status = 'ongoing'
       if result_db:
           result_db.status = status
           result.update_record()
       else:
           db.sending_result.insert(campagin_id = db.campaign[campagin_id],
                                   phone_number = request.get_vars.dest,
                                   status = status)
