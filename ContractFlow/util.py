from FirebaseRealtimeDB import sign_up_with_email, login_with_email_password
from datetime import datetime, date

def read_data(db):
    """
    ALL meetings in the DB, formatted as below
    
    open the file, seperate each entry, and return it
        return original entry list split into
    [start time, end time, date, place name, place address]
    
    :note: mainly used by edit_meeting which needs all of them
    :note: dashboard uses read_data_for_today()
    """
    
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
    
def read_data_for_today(db):
    """
    return the meetings by today's DATE
    only used by Dashboard()
    
    :note: edit_meeting will ask for entire meetings list from read_data
    """
    all_meetings = read_data(db)
    today_meetings = []
    for meeting in all_meetings:
        # loop thru all meetings
        # if it's today we keep otherwise skip
            # - convert 'July 13' --> datetime object
            # compare against datetime.now() datetime obj
        meeting_date = meeting[2]
        meeting_datetime_obj = datetime.strptime(meeting_date, "%B %d")
        meeting_datetime_obj = meeting_datetime_obj.date()
        
        """
        when we convert from "%B %d" (%month %date),
        it defaults year to 1900,
        so we manually replace the year to current year
        which is what datetime.now() has
        so then we r only comparing "%B %d" (%month %date)
        """
        meeting_datetime_obj = meeting_datetime_obj.replace(year=date.today().year)
        today_datetime_obj = datetime.now().date()
        if meeting_datetime_obj ==  today_datetime_obj:
            today_meetings.append(meeting)
        # ToDo: if we ever do datesorting this is probably the place
    return today_meetings
    
def create_location(db, loc_name, details):
    """
    loc_name: name of location (will overwrite if already exists)
    details: dict {'address': '321 ehfs...', 'wage': 50.5}
    """
    db.patch_path(f'locations/{loc_name}', details)
    

def create_meeting(db, entry):
    """
    ::note.. entry does not have address yet, we add it here
    append an entry containing [start time, end time, date, place name, place, address]
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
        
    lastAppt = db.read_path('meetings/lastAppt')
    apptNum = int(lastAppt[len('appt'):])
    nextAppt = 'appt' + str(apptNum+1)
    
    # first patch lastAppt to nextAppt
    db.patch_path('meetings', {'lastAppt': nextAppt})
    
    # now patch the actual meeting w/ apptNum
    
    data = {
        'start_time': entry[0],
        'end_time': entry[1],
        'date': entry[2],
        'location': entry[3]
    }
    db.patch_path(f'meetings/{nextAppt}', data)
    

    
def delete_meeting(db, *args):
    """ when we actually know apptNum to delete
    as opposed to delete_entry when we gotta attribute match
    - invoked from manage_locations
    """
    for apptNum in args:
        db.delete_path(f'meetings/{apptNum}')
        
    
def delete_entry(db, entry):
        ### to delete node from JSON
    ### we need appt# foldername
    ### we can't just check time == time bc "06:00" != "6:00"
    
    # Convert to datetime.datetime() --> check equality --> backtrace and store appt#
    # delete appt# and re-patch data to branch
    meetings = db.read_path('meetings')
    
    e = []
    for i in entry:
        e.append(i.strip())
        
    entry_date = datetime.strptime(e[2], '%B %d')
    entry_starttime = datetime.strptime(e[0], "%I:%M %p")
    entry_endtime = datetime.strptime(e[1], "%I:%M %p")
    entry_loc = entry[3]
    
    CHOSEN_APPTNUM = ''
    
    for apptNum in meetings:
        curr = meetings[apptNum]
        curr_date = datetime.strptime(curr['date'], '%B %d')
        curr_starttime = datetime.strptime(curr['start_time'], "%I:%M %p")
        curr_endtime = datetime.strptime(curr['end_time'], "%I:%M %p")
        if curr_date == entry_date:
            if curr_starttime == entry_starttime:
                if curr_endtime == entry_endtime:
                    CHOSEN_APPTNUM = apptNum
                    break
    
    db.delete_path('meetings/' + CHOSEN_APPTNUM)
    
    
    # Currently if we delete a node (ex. appt3) out of max (appt6)
    # it will read appt1, appt2, appt4, appt5, appt6, lastAppt: appt6
    # Right now: we check if deleted appt6 to shift the lastAppt down
    # But this overtime will create gaps in appt# that should be filled
    # ToDo: Possible solution: always shift keys down 1 when deleting node
    
    # check if we deleted last node
    lastAppt = db.read_path('meetings/lastAppt')
    if lastAppt == CHOSEN_APPTNUM:
            apptNum = int(lastAppt[len('appt'):])
            prevAppt = 'appt' + str(apptNum-1)
            db.patch_path('meetings', {'lastAppt': prevAppt})
        
        
def delete_location(db, location):
    db.delete_path(f'locations/{location}')
    
def content_present(db):
    """
    return the amount of meetings that day
    """
    return len(read_data_for_today(db))
    
def unique_locations(db):
    """
    return dict containing {'place' : 'address'}
    """
    locs = db.read_path('locations')
    places = {}
    
    for location_name in locs:
        places[location_name] = locs[location_name]['address']
        
    return places
    
def all_location_info(db):
    """
    return COMPLETE info about each location including wage
    """
    locs = db.read_path('locations')
    return locs
    
def num_unique_locations(db, data=None):
    """
    return the number of unique locations to visit that day
    
    :data optional dict of today's meetings, from which unique_locs will be extracted. if none provided, general unique locs provided
    """
    
    return len(unique_locations(db))
    
def get_location_used(db):
    """ return a dict {appt#: location}
    for every appointment & it's corresponding location
    aka giving the actively used locations & how many times
    """
    meetings = db.read_path('meetings')
    
    del meetings['lastAppt']
    
    locs_used = {}
    for apptNum in meetings:
        locs_used[apptNum] = meetings[apptNum]['location']
        
    return locs_used
    
    
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

def delete_account(db):
    return db.delete_account()
