import requests as req
import sys
import json
import os
import time



#Utility functions
def split_every(string, spacing):  #splits string every spacing
    return [string[loc:loc+spacing] for loc in xrange(0, len(string), spacing)]

def read_file(path):  #returns the contents of a file if it exists
    print "Reading file..."
    try:
        with open(path, 'rb') as f:
            return f.read()
    except:
        critical_error(path + " is not a valid file path")

def check_writable(path):  #checks if a file can be written to
    try:
        open(path, 'wb').close()
    except:
        critical_error(path + " cannot be written to")

def critical_error(text):  #prints an error message and then exits the program
    print "Error: " + text
    exit()

def open_file(path):  #opens the file at the specified path but only on windows
    if sys.platform[:3] == 'win':
        os.startfile(path)


#Request utilities
def do_request(func, url, payload = None):  #performs a request function with the specified url and payload
    for attempt in range(1, 6):  #trys to connect 5 times before giving up
        try:
            response = func(url, payload, timeout = 15)
            if response.status_code == 404:
                critical_error("File shard not found!")
            return response
        except req.ConnectionError:
            print "Connection error, retrying in 2 seconds...(" + str(attempt) + "/5)"
            time.sleep(2)
    critical_error("Can't connect to server")

def upload_piece(payload):  #uploads a piece of a file and returns a link to that piece
    response = do_request(req.post, 'https://hastebin.com/documents', payload)
    try:
        link = json.loads(response.content)['key']
    except:
        critical_error("Expected shard link, got back " + response.content + "instead")
    return link

def download_piece(url):  #downloads a single piece of the file
    response = do_request(req.get, 'https://hastebin.com/raw/' + url)
    return ''.join(chr(int(i)) for i in response.content.split(' '))  #turn data back into bytes



#Main request functions
def upload(data):  #uploads data and returns a file id
    split_data = split_every(data, 100000)
    urls = []
    print "Uploading " + str(len(split_data)) + " shards..."
    for i, payload in enumerate(split_data):
        payload = ' '.join(str(ord(c)) for c in payload)  #hastebin does not accept control characters, so I'll just send every byte as a number seperated by a space
        urls.append(upload_piece(payload))
        print str(i+1) + '/' + str(len(split_data)) + " uploaded"
    print "Getting file ID..."
    print "\nFile ID: " + upload_piece(','.join(urls))

def download(file_id, file_loc):  #downloads the file at file_id to file_loc, opens file
    if len(file_id) == 10:
        print "Finding shards..."
        uri = do_request(req.get, 'https://hastebin.com/raw/' + file_id).content
        urls = uri.split(',')
        data = ''
        print 'Downloading ' + str(len(urls)) + ' file shards...'
        for i, url in enumerate(urls):
            data += download_piece(url)
            print str(i+1) + '/' + str(len(urls)) + " downloaded"
        print "\nDownload complete, Writing to " + file_loc + "..."
        with open(file_loc, 'wb') as f:
            f.write(data)
        print "Done"
        open_file(file_loc)
    else:
        raise critical_error("Not a valid file id (valid file ids are 10 digits long")
    


#Arg parsing
def parse_args(args):
    if len(args) == 1 or args[1].lower() == 'help':  #if theres no args or the first arg is 'help'
        print_help()
    elif len(args) == 2:
        critical_error("Not enough arguments, you must provide a file id when downloading and a file path when uploading")
    else:
        mode = args[1].lower()
        if mode == 'up':
            data = read_file(args[2])
            upload(data)
        elif mode == 'dn':
            file_path = 'delpls.txt'
            file_id = args[2]
            if len(args) == 3:
                print "No download path specificed, downloading to " + file_path + " by default\n"
            else:
                file_path = args[3]
            check_writable(file_path)
            download(file_id, file_path)
        else:
            critical_error(mode + "Is not a valid mode, the only valid modes are 'up' and 'dn'")

def print_help():  #prints instructions then exits
    print '''hbupload is a simple tool to upload and download files.

to upload a file:
    hbupload up file_location
once the file is finished uploading a 10 character file id will be printed. This is the id used to download the file.

to download a file:
    hbupload dn file_id local_file_path
once the file found at file_id is downloaded it is written to local_file_path and the file will be opened with your default program for that file.
if you don't specify a local_file_path the file will be saved to the default file path (delpls.txt)
'''
    exit()

   
parse_args(sys.argv)

