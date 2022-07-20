from FirebaseRealtimeDB import sign_up_with_email, login_with_email_password

def read_data(db):
    """open the file, seperate each entry, and return it
        return original entry list split into
    [start time, end time, date, place name, place address]"""
    
    final = []
    meets = db.read_path('meetings')
    del meets['lastAppt']
    for i in meets:
        curr = meets[i]
        final.append([
           curr['start_time'], curr['end_time'], curr['date'], curr['location'],
           get_loc_address(db, curr['location']) ]
           )
           
    return final
    
    
def write_entry(db, entry):
    """
    append an entry containing [start time, end time, date, place name, place address]
    """
    # ToDo: write into db
    
    locations = unique_locations(db)
    # we dont need to check if it exists
    # bc the only way user can select is from addMeeting
    # which only lets them pick prexisting places
    address = locations[entry[3]]
    entry.append(address)
    e = entry.copy()
    for ind, elem in enumerate(e):
        entry[ind] = elem.strip()
    meetings_f = open('meetings.txt', 'a')
    meetings_f.write('\n')
    meetings_f.write(', '.join(entry))
    meetings_f.close()
    
    

def process_data(entry):
    """
    return original entry list split into
    [start time, end time, date, place name, place address]
    """
    split = entry.split(',')[:4]
    # if we run split off comma, it also seperates address which naturally has commas
    # for this reason we split everything then join the address at the end back into a string, then append to split variable
    address = ''.join(entry.split(',')[4:])[1:]
    split.append(address)
    return split
    
    
def delete_entry(db, entry):
    entries = read_data(db)
    entries = [process_data(entry) for entry in entries]
    entries.remove(entry)
    e = entries.copy()
    entries = []
    for entry in e:
        c = []
        for item in entry:
            c.append(item.strip())
        entries.append(c)
    meetings_f = open('meetings.txt', 'w')
    
    for ind in range(len(entries)-1): # everything except the last we write \n
        meetings_f.write(', '.join(entries[ind]))
        meetings_f.write('\n')
        
    meetings_f.write(', '.join(entries[-1]))
    meetings_f.close()
    
    #ToDo: reload editmeeting screen from menu when we click


def content_present(db):
    """
    return the amount of meetings that day
    """
    apptNum = db.read_path('meetings')
    apptNum = apptNum['lastAppt']
    apptNum = int(apptNum[len('appt'):])
    return apptNum
    
def unique_locations(db):
    """
    return dict containing {'place' : 'address'}
    """
    locs = db.read_path('locations')
    places = {}
    
    for location_name in locs:
        places[location_name] = locs[location_name]['address']
        
    return places
    
def num_unique_locations(db, data=None):
    """
    return the number of unique locations to visit that day
    
    :data optional dict of today's meetings, from which unique_locs will be extracted. if none provided, general unique locs provided
    """
    
    if data is None:
        return len(unique_locations(db))
    
    # ToDo: implement once we figure out read_data()
    return len(unique_locations(db))
    
def get_loc_address(db, loc_name):
    locs = unique_locations(db)
    return locs.get(loc_name)

def signup(email, password):
    """ signup to Firebase via email & password
    :return {} if failed or credential dict if success
    """
    
    return_payload = sign_up_with_email(email, password)
    
    if return_payload == {}: # it failed
        # reasons for failing: EMAIL_EXISTS, OPERATION_NOT_ALLOWED, or TOO_MANY_ATTEMPTS_TRY_LATER
        return False
    else:
        # NoLongerToDo: we may need to return return_payload
        # note: bool({}) == False so maybe return payload flat
        # note: then we can check in main if bool(signup()) == False whatever
        
        # Updated comment: Since we make user sign in after signup(),
        # login() is called which returns payload
        # which is passed to Firebase()
        # so this implementation can stay same
        # without breaking changes
        return True

def login(email, password):
    """
    login to Firebase via email/password after signup()
    has been called
    return payload (type dict), {} if unsuccessful
    """
    return_payload = login_with_email_password(email, password)
    
    return return_payload

def create_new_user(db):
    """
    Create basic directories for a new user
    :db Firebase instance
    """
    
    db.patch_path('locations/Default Location',
            {"address": "Add another location to remove this",
            "wage": 0})
    db.patch_path('meetings', {'lastAppt': 'appt0'})

