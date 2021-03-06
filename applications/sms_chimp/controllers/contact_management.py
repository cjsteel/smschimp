# coding: utf8
# try something like
import cStringIO
import csv
@auth.requires_login()
def index(): 
    export_csv_link = A('export csv',_href=URL('contact_management','export_contact_to_csv'),_class='btn')
    formcsv = FORM("Default Prefix : ", 
                       INPUT(_type='text',_name ='default_prefix',_value=auth.user.default_prefix,_style ="max-width:50px"),
                       BR(),
                       str(T('Import from csv file')) + " ",
                       INPUT(_type='file', _name='csvfile'),
                       INPUT(_type='submit', _value=T('import')))
    if formcsv.process().accepted:
        try:
            import_contact_from_csv(request.vars.default_prefix,request.vars.csvfile.file)
            response.flash = 'Import data successful'
        except Exception, e:
            response.flash = DIV(T('unable to parse csv file'), PRE(str(e)))
    
    remove_empty_groups()  
    groups = db(db.contact_group.user_uid == auth.user.id).select(db.contact_group.id,db.contact_group.name)
    return dict(import_csv = formcsv,export_csv = export_csv_link,groups=groups)

def remove_empty_groups():
    groups = db(db.contact_group.user_uid == auth.user.id).select(db.contact_group.id,db.contact_group.name)
    for group in groups :
        if (db(db.contact.contact_group_id == group.id).count() < 1) :
               db(db.contact_group.id == group.id).delete()
            
def export_contact_to_csv():
    
    s = cStringIO.StringIO()
    data =  db(db.contact.user_uid == auth.user.id).select(db.contact.name,db.contact.phone_number,db.contact.dob,db.contact.group_name);
    data.export_to_csv_file(s)
    response.headers['Content-Type'] = 'text/csv'
    return s.getvalue()
    
   
def import_contact_from_csv(prefix,file):
        csv_data = csv.reader(file)
        for row in csv_data:                               
            group_id = db(db.contact_group.user_uid == auth.user.id)(db.contact_group.name == row[3]).select().first()
            if not group_id :
               group_id = db.contact_group.insert(name=row[3])
            phone_number = (row[1][0] =='+' and row[1]) or  prefix + row[1]
            current_contact = db(db.contact.user_uid == auth.user.id)(db.contact.phone_number == phone_number).select().first()
            if current_contact:
               current_contact.name = row[0]
               current_contact.dob = row[2]
               current_contact.group_name = row[3]
               current_contact.contact_group_id = group_id
               current_contact.update_record()
            else :
               
               db.contact.insert(name = row[0],phone_number = phone_number or row[0],dob = row[2],group_name = row[3],contact_group_id = group_id)


def get_contacts_of_group():
     group_contact = db(db.contact_group.user_uid == auth.user.id)(db.contact_group.name == request.args(0)).select().first().contact.select()
     return response.json(group_contact)

def update_contact():
    contact = db.contact(request.post_vars.id)
    if contact and (contact.user_uid == auth.user.id):
       contact.name = request.post_vars.name
       contact.phone_number = request.post_vars.phone_number
       contact.dob = request.post_vars.dob
       contact.group_name = request.post_vars.group_name
       group_id = db(db.contact_group.user_uid == auth.user.id)(db.contact_group.name == contact.group_name).select(db.contact_group.id).first()
       if group_id :
          contact.contact_group_id = group_id 
       else :
          contact.contact_group_id = db.contact_group.insert(name=contact.group_name)
       contact.update_record()
       session.flash = "Update contact successful"
    else :
       session.flash = "Invaild data"
    
def search_group_name():
    query =  request.vars.query
    groups = db(db.contact_group.user_uid == auth.user.id).select(db.contact_group.name).find(lambda row:row.name.startswith(query))  
    return_groups = [group.name for group in groups]
    response.headers['Content-Type'] = 'application/json'
    return response.json(return_groups)
       
def delete_contact():
    contact = db.contact(request.vars.id)
    try:
        if contact and (contact.user_uid == auth.user.id):
            contact.delete_record()
            session.flash = "Delete contact successful"
        else :
            session.flash = "Invaild data"
    except Exception, e:
           session.flash = DIV(T('Cannot delete this contact'), PRE(str(e)))
    redirect(URL('contact_management','index'))
