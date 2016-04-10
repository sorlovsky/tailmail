from __future__ import print_function
import httplib2
import os
import time

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from apiclient import errors

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def archiveMsg(service, messageId):
  # Gets the message with according messageId
  try:
    meow = service.users().messages().get(userId = 'me', id = messageId, format = 'raw').execute()
    # Removes the label 'Inbox'
    msg_label = {'addLabelsIds' : [], 'removeLabelIds': ['INBOX']}

    # If the message has been 'read' means that it doesn't have an unread label
    # Removes that label from that message and so the message is archived
    if 'UNREAD' not in meow['labelIds']:
      service.users().messages().modify(userId = 'me', id = messageId, body=msg_label).execute()

  except errors.HttpError, error:
    print ('An error occurred: %s' % error)
        


# start_history_id = '1'       
def historyUpdate(service, update_history_id):
  try:
    history = (service.users().history().list(userId = 'me', startHistoryId = update_history_id).execute())
    # All the changes that have happened since 1
    changes = history['history'] if 'history' in history else[]
    removedLabels = []
    
    while 'nextPageToken' in history:
      page_token = history['nextPageToken']
      history = (service.users().history().list(userId = 'me', startHistoryId = update_history_id, pageToken = page_token).execute())
      changes.extend(history['history'])

    for i in range(len(changes)):
      # Just taking the changes where a lable was removed
      if 'labelsRemoved' in (changes[i]):
        removedLabels.append(changes[i]['labelsRemoved'])
        #print (changes[i]['labelsRemoved'])
        #print ("")

    messageId = [] 
    for i  in range(len(removedLabels)):
      
      # If Unread is removed. That means that the message was read
      if 'UNREAD' in removedLabels[i][0]['labelIds']:
        messageId.append(removedLabels[i][0]['message']['id'])

    # This is the list of messages that have had an 'UNREAD' tag removed
    return (messageId)

  except errors.HttpError, error:
    print ('An error occured: %s' % error)


def updateHistoryId(service, update_history_id):
  try:
    history = (service.users().history().list(userId = 'me', startHistoryId = update_history_id).execute())
    changes = history['history'] if 'history' in history else[]

    while 'nextPageToken' in history:
      page_token = history['nextPageToken']
      history = (service.users().history().list(userId = 'me', startHistoryId = update_history_id, pageToken = page_token).execute())
      changes.extend(history['history'])

    if len(changes) == 0:
      return update_history_id 
      
    else:
      return (changes[len(changes)-1]['id'])
  
  except errors.HttpError, error:
    print ('An error occured: %s' % error)  



def main():
  """List all Messages of the user's mailbox matching the query.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

  Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
  """
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('gmail', 'v1', http=http)


  # The program only cleans the things that come in after the program is running
  # If want to clean the entire mailbox, use history_id = 1
  history_id = updateHistoryId(service, 1)
  while True:
    time.sleep(40)
    # Waits again before executing the new list of history
    messageId = historyUpdate(service, history_id)
    for message in messageId:
      print (message)
      archiveMsg(service, message)


    time.sleep(40)
    # After the Inbox is clean, it's gonna wait until the history is updated
    history_id = updateHistoryId(service, history_id)








  


if __name__ == '__main__':
    main()
