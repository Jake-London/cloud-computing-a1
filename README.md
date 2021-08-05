Python Modules
 - configparser (pip)
 - boto3 (pip)
 - os
 - csv
 - json
 - datetime
 - sys

Part 1: awsS3Shell.py Program

Basic Commands and Flags NOT Handled

NONE

Extra Commands or Flags

NONE

Error Conditions
 - Most error conditions are handled such that nothing happens or a message is given and a new prompt is given,
   but does not terminate the prompt
   (example: using commands before logging in does nothing and returns a new prompt)
 - If 'config.ini' is not present, program will terminate

Comments/Instructions for the Marker
 - First time using python so code is messy as I learnt as I went
 - IMPORTANT - When using commands that specify an s3 path (either total or relative),
   please avoid adding a '/' to the end of a specified path as certain commands will not work properly
   (example: s3:/bucket/folder <---- GOOD BAD ----> s3:/bucket/folder/)
 - IMPORTANT - Do not use quotes when entering a file path
 - Upload and download can take any s3 path, but will only upload/download to/from the folder the script is run in

-------------------------------------------------------------------

Part 2: DynamoDB

loadTable.py Program
 - Primary Key:
	Partition Key named 'PartitionKey' in table is combination of Commodity + Variable in the form 'commoditycode-variable'
	(example: WT-IM for Wheat Import
	Sort Key is 'Year'
 - Field/Attribute Names:
	- PartitionKey
	- Year
	- Commodity
	- Mfactor
	- Units
	- Value
	- Variable
 - encodings.csv loaded by loadTable.py: no
 - if no: program that does and how it is run
	- queryOECD.py - script reads it to local storage each time program runs (not put in DynamoDB)

queryOECD.py Program
 - Running this program:
 - encodings table read in by this program: encodings.csv is read from folder script is in

Error Conditions:
 - If encodings.csv is missing, message is printed and program ends
 - similarily if tablename or filename is invalid, message prints and program ends

Comments/Instructions for the Marker:



