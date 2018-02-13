# hbupload
A command line utility for hosting files online  
Uploaded files are hosted publicly on hastebin.com  
It's pretty much completely useless tbh  

### to upload a file:  
    python hbupload.py up file_location  
once the file is finished uploading a 10 character file id will be printed. This is the id used to download the file.  

### to download a file:
    python hbupload.py dn file_id local_file_path 
once the file found at file_id is downloaded it's written to local_file_path. 
If your on Windows the file will be opened with your default program for that file.  
if you don't specify a local_file_path the file will be saved to the default file path (delpls.txt)  
