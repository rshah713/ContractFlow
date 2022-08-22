# ContractFlow Known Issues

A collection of Known Issues identified by the ContractFlow developer team. CF developer team has assigned each issue a priority level and are investigating possible solutions. 

------------------------

## File an Issue / Password Reset


Don't see your issue? File it [Here](https://forms.gle/hqFUxiabb4gcEFU37).
Still don't see your issue? Our developer team is working on documenting and fixing your issue :)

Password Reset: Request a PW Reset [Here](https://forms.gle/hqFUxiabb4gcEFU37)

_Disclaimer: Requests are currently human-verified to ensure security and therefore may be denied or take an extended amount of time._


------------------------

### User Data Complete Reset on DB Fail
**Priority Level: High**

_Description_: In the event of an authentication fail (e.g. no internet available, invalid username when logging in, etc) ContractFlow mistakes account for a "new user" executes the "new user protocol" which wipes all user data. **_There is currently NO way to retrieve missing data._**

_Dev Description_: If a `HTTPError`, `client.InvalidURL`, or external error is thrown in any low-level Firebase function while performing a `READ` on the Realtime Database, all RTDB nodes are automatically reset to `locations/DefaultLocation` and `meetings/lastAppt`. This `PATCH` operation removes all other locations & appointments under that  `user`'s node

_Steps to Recreate_:

    1. We have put preventative measures to prevent triggering of auth fail
    2. No intentional way to recreate yet could still be triggered
    
    
------------------------

### Duplicate entries have errors in deletion
**Priority Level: Mid**

_Description_: Create two appointments with exact same attributes (date, starttime, endtime, location) and attempt to delete both of them. This will result in a mismatch of deletion and ContractFlow will delete both yet believe one still numerically exists. 

_Dev Description_: By creating two attribute-identical events, you can trick `delete_entry` which matches attributes of requested delete to the first available node that holds matching children values. This leads to `meetings/lastAppt` not being triggered at necessary times and being off by one count. This also misleads Dashboard into believing there is one more event than actually exists. 

_Steps to Recreate_:

    1. Menu --> Add Meeting --> Create Meeting
    2. Menu --> Add Meeting --> Create Meeting
    3. Menu --> Edit Meeting --> Scroll to Duplicate --> Delete
    4. Menu --> Edit Meeting --> Scroll to Duplicate --> Delete
    5. Dashboard --> Possible Error in Top Label & Layout
    
------------------------

### Location Count Reports as Total Locations Available
**Priority Level: Low**

_Description_: Location Count Label on Dashboard is meant to show the number of unique locations you have in your appointments. However, the label shows the _total_ number of unique locations you have set up in your account as opposed to locations tied to appointments. This means an account with 0 appointments that has set up 10 locations will show 10 in label as opposed to 0. 

_Dev Description_: `num_unique_locs` simply reads the length of `user/locations` which holds locations _registered_ as opposed to used. `user/meetings/appt#/location` will have the name and can be used to generate that label number. _Possible Solution: We can probably use `get_location_used` to get actively used locations from `.values()` and set the label from there_

_Steps to Recreate_:

    1. Add any number of locations in Menu --> Manage Locations
    2. Ensure your appointments do NOT use all of the locations
        - ex. 5 locations set up, 3 being used
    3. Dashboard label will incorrectly report number of locations set up
        - ex. Dashboard reports 5 as opposed to 3 being actively used
        
- [x] Fixed by [`e8613c4`](https://github.com/rshah713/ContractFlow/commit/e8613c43638de40ce38867b6b567fd60da27d793)
------------------------

### Editing Meeting & Cancelling will Delete Meeting
**Priority Level: Mid**

_Description_: If editing an existing meeting and cancelling the edit before saving a new copy, the meeting will automatically be deleted.  

_Dev Description_: Edit button auto-runs `remove_entry` to Firebase while screen switches to add meeting. Nature of back button is to simply return to previous screen and does not verify the meeting has been replaced via `add_meeting` and therefore it is possible to run `remove_entry` and not `patch_data`


_Steps to Recreate_:

    1. Menu --> Edit Meeting --> Edit
    2. BACK arrow --> Home
        
------------------------

### Signing into new account without refresh leads to content leak
**Priority Level: High**

_Description_: By signing into a new account without closing the app, the dashboard will show the previous meetings of the old account instead of the new signed in account. **Temporary fix: Either fully close the app OR add/edit a meeting in the new account to manually refresh the dashboard** 

_Dev Description_: `kivy.graphics.instructions.Canvas` draws the layout to the Dashboard screen, and while `gen_layout()` is called it does not automatically refresh and therefore holds previously drawn content. Possible solution is to `remove_widget(Dashboard())` off of `kivy.uix.screenmanager` when logging in.


_Steps to Recreate_:

    1. Menu --> Settings --> Sign Out
    2. Sign in with new account
        

------------------------

### Forgot Password?

_Dev Solution_: `debug:` it, then delete account and have them signup for new one with same email, therefore `Firebase()` will route to same directories and data will still live. (Also can use Firebase-gen email but will be auto-marked as spam)
