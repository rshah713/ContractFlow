from FirebaseRealtimeDB import sign_up_with_email, login_with_email_password

def read_data():
    """open the file, seperate each entry, and return it"""
    
    # ToDo: handle database reading
    meetings_f = open('meetings.txt', 'r')
    meetings = meetings_f.readlines()
    meetings_f.close()
    return meetings
    
    
def write_entry(entry):
    """
    append an entry containing [start time, end time, date, place name, place address]
    """
    # ToDo: write into db
    
    locations = unique_locations()
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
    
    
def delete_entry(entry):
    entries = read_data()
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
    
    

def content_present():
    """
    return the amount of meetings that day
    """
    return len(read_data())
    
def unique_locations():
    """
    return dict containing {'place' : 'address'}
    """
    entries = read_data()
    places = {}
    for entry in entries:
        info = process_data(entry)
        place = info[3]
        address = info[4].strip()
        places[place] = address #if it exists dict will alr rewrite
    
    return places
    
def num_unique_locations():
    """
    return the number of unique locations to visit that day
    """
    return len(unique_locations())


def signup(email, password):
    """ signup to Firebase via email & password
    :return true/false depending on status
    """
    
    return_payload = sign_up_with_email(email, password)
    
    if return_payload == {}: # it failed
        # reasons for failing: EMAIL_EXISTS, OPERATION_NOT_ALLOWED, or TOO_MANY_ATTEMPTS_TRY_LATER
        return False
    else:
        # ToDo: we may need to return return_payload
        # note: bool({}) == False so maybe return payload flat
        # note: then we can check in main if bool(signup()) == False whatever
        return True

def login(email, password):
    """
    login to Firebase via email/password after signup()
    has been called
    return payload (type dict), {} if unsuccessful
    """
    return_payload = login_with_email_password(email, password)
    
    return return_payload
