import boto3
import configparser
import json
import datetime
import os

def create_client(accessKey, secretKey, sessionToken, region):
    if (sessionToken != ''):
        print("a")
        client = boto3.client(
            's3',
            aws_access_key_id=accessKey,
            aws_secret_access_key=secretKey,
            aws_session_token=sessionToken,
            region_name=region
        )
        return client
    else:
        print("b")
        client = boto3.client(
            's3',
            aws_access_key_id=accessKey,
            aws_secret_access_key=secretKey,
            region_name=region
        )
        return client

def get_directory_array(string):
    array = string.split('/')
    if ('' in array):
        array.remove('')
    
    
    return array

def is_bucket(bucketList, string):
    for bucket in bucketList:
        if (bucket['Name'] == string):
            return True
    return False

def get_bucket_list(client):
    response = client.list_buckets()
    if ('Buckets' in response):
        return response['Buckets']
    else:
        return False

def get_object_list(client, bucket):
    response = client.list_objects(Bucket=bucket)
    if ('Contents' in response):   
        return response['Contents']
    else:
        return False

def is_object(objects, path):
    for obj in objects:
        if (obj['Key'].startswith(path)):
            return True
    return False

def is_object_num(objects, path):
    i = 0
    for obj in objects:
        if (obj['Key'].startswith(path)):
            i += 1
    return i

def check_path(newPath, pathArray, client):   
    bucket_list = get_bucket_list(client)
    if (len(pathArray) == 0):
        return False
    bucket_exists = is_bucket(bucket_list, pathArray[0])

    if (bucket_exists == False):
        return False
    
    temp_path = newPath.replace('/' + pathArray[0] + '/', '')

    if (len(pathArray) != 1):
        object_list = get_object_list(client, pathArray[0])
        if (object_list == False):
            return False
        object_exists = is_object(object_list, temp_path)

        if (object_exists == True):
            return True
        else:
            return False
    else:
        return True
    
def get_object_info(bucket, client, key, name):
    response = client.get_object(Bucket=bucket, Key=key)
    
    temp_arr = []
    temp_arr.append(response['ContentType'])
    temp_arr.append(response['ContentLength'])
    temp_arr.append(response['LastModified'])
    temp_arr.append(name)

    return temp_arr

def get_folder_info(bucket, client, key, name):
    object_list = get_object_list(client, bucket)
    
    if (object_list == False):
        return []
    else:
        date_arr = []
        for obj in object_list:
            
            if (key in obj['Key']):
                date_arr.append(obj['LastModified'])

        date_arr.sort()

        temp_arr = []
        temp_arr.append('application/x-directory')
        temp_arr.append(0)
        temp_arr.append(date_arr[-1])
        temp_arr.append(name)

        return temp_arr

def create_dir(bucket, client, path, dirName):
    new_obj_path = path.replace('/' + bucket + '/', '')
    new_obj_path += dirName

    client.put_object(Bucket=bucket, Key=new_obj_path)

def delete_dir(bucket, client, path):
    client.delete_object(Bucket=bucket, Key=path)

def valid_absolute_path_from(absolutePath, client):
    if (absolutePath.startswith('s3:')):
        absolutePath = absolutePath.replace('s3:', '')
    
    temp_arr = get_directory_array(absolutePath)
    temp_path = absolutePath.replace('/' + temp_arr[0] + '/', '')

    try:
        response = client.get_object(Bucket=temp_arr[0], Key=temp_path)
        return True
    except:
        return False

    
def valid_absolute_folder(absolutePath, client, flag):
    if (absolutePath.startswith("s3:")):
        absolutePath = absolutePath.replace('s3:', '')

    temp_arr = get_directory_array(absolutePath)
    
    check_2 = check_path(absolutePath, temp_arr, client)

    if (flag == 1 and len(temp_arr) == 1):
        check_1 = check_path(absolutePath, temp_arr, client)
    else:
        temp_path = absolutePath.replace('/' + temp_arr[-1], '')
        path_arr = get_directory_array(temp_path)

        check_1 = check_path(temp_path, path_arr, client)

    
    if (check_1 == True and check_2 == True):
        return [True, 0]
    elif (check_1 == True and check_2 == False):
        return [True, 1]
    elif (check_1 == False):
        return [False, 0]
    

def main():
    current_user = ''
    current_path = ''
    prompt_msg = '> '
    is_logged_in = False
    global client

    # Main shell loop
    while True:
        command = input(prompt_msg)
        command_arr = command.split()
        command_len = len(command_arr)

        config = configparser.ConfigParser()
        config.sections()
        config.read('config.ini')

        # No command given, continue to next loop
        if (command_len == 0):
            continue

        # If no arguments specified (command_len == 1), default user used
        if (command_arr[0] == 'login' and command_len <= 2):
            # Login the specified user if they exist in config
            if (command_len == 2 and command_arr[1] in config):
                print("Retrieving keys for user: " + command_arr[1])
                accessKey = ''
                secretKey = ''
                sessionToken = ''
                region = ''

                accessKey = config[command_arr[1]]['accesskey']
                secretKey = config[command_arr[1]]['secretkey']
                region = config[command_arr[1]]['region']

                # If user has a session token, use it to login
                if ('sessiontoken' in config[command_arr[1]]):
                    sessionToken = config[command_arr[1]]['sessiontoken']
                
                # Login/instantiate client
                client = create_client(accessKey, secretKey, sessionToken, region)

                current_user = command_arr[1]
                current_path = '/'
                is_logged_in = True
                
            # Login the default user
            else:
                if (command_len == 1):
                    print("Retrieving default keys")

                    accessKey = ''
                    secretKey = ''
                    sessionToken = ''
                    region = ''

                    accessKey = config['DEFAULT']['accesskey']
                    secretKey = config['DEFAULT']['secretkey']
                    region = config['DEFAULT']['region']

                    if ('sessiontoken' in config['DEFAULT']):
                        sessionToken = config['DEFAULT']['sessiontoken']

                    print(accessKey)
                    print(secretKey)
                    print(sessionToken)
                    print(region)

                    
                    client = create_client(accessKey, secretKey, sessionToken, region)

                    current_user = 'root'
                    current_path = '/'

                    is_logged_in = True

                else:
                    print("User not found. Check you username or use the default login")

        # Change directories command
        if (command_arr[0] == 'cd' and is_logged_in == True):
            if (command_len > 2 or command_len == 1):
                print("Invalid number of arguments for command: cd")
                continue

            # If only arg is root, go to root
            if (command_arr[1] == '~' or command_arr[1] == '/'):
                current_path = '/'

            else:
                # Remove s3: from input if it exists
                if ('s3:' in command_arr[1]):
                    command_arr[1] = command_arr[1].replace('s3:', '')

                # add input to current_path (current dir)
                # split new path into array (split on '/' char)
                temp_path = current_path + command_arr[1]
                temp_arr = get_directory_array(temp_path)
                temp_path = '/'
                temp_len = len(temp_arr)

                # go through array and check if first arg is a bucket
                # if not, check if it is .. meaning we want to go up
                for idx, item in enumerate(temp_arr):
                    if (idx == 0):
                        if (item == '..'):
                            temp_arr[idx] = ''

                        bucket_list = get_bucket_list(client)
                        bucket_exists = is_bucket(bucket_list, item)
                        
                        if (bucket_exists == True):
                            temp_path += item
                    else:
                        if (item == '..'):
                            # takes the last instance of .. if it exists
                            # and replaces itself and the closes non '..' word in the array with empty string
                            for idx2, i in reversed(list(enumerate(temp_arr))):
                                if (i != '..' and i != ''):
                                    if (idx2 < idx):
                                        temp_arr[idx2] = ''
                                        temp_arr[idx] = ''
                                        break
                                    else:
                                        temp_arr[idx] = ''
                            
                # Remove any empty strings (or .. in the case we already went up as much as possible)
                while ('' in temp_arr):
                    temp_arr.remove('')

                while ('..' in temp_arr):
                    temp_arr.remove('..')

                # Build the new path by adding the items in the array
                new_path = '/'
                for idx, item in enumerate(temp_arr):
                    new_path += item + '/'

                # If the array is empty, we are at the root
                if (len(temp_arr) == 0):
                    current_path = '/'
                    continue
                
                # Check if our new path is actually a directory
                result = check_path(new_path, temp_arr, client)

                # If so, set the new current_path (current dir)
                if (result == True):
                    current_path = new_path
                else:
                    print("No such file or directory")

        if (command_arr[0] == 'pwd' and is_logged_in == True):
            if (command_len > 1):
                print("Too many arguments. Command 'pwd' has no arguments")
            else:
                print('s3:' + current_path)

        if (command_arr[0] == 'mkbucket' and is_logged_in == True):
            if (command_len != 2):
                print("Invalid number of arguments for command: mkbucket")

            response = client.list_buckets()

            bucket_list = response['Buckets']
            name_exists = False

            for bucket in bucket_list:
                if (bucket['Name'] == command_arr[1]):
                    name_exists = True
                    break

            if (name_exists == False):
                try:
                    response = client.create_bucket(Bucket=command_arr[1])
                except:
                    print("Error creating bucket. Name may be invalid or the bucket already exists.")
            else:
                print("A bucket with this name already exists. Please choose another name.")

        if (command_arr[0] == 'ls' and command_len <= 2 and is_logged_in == True):
            if (command_len == 2):
                if (command_arr[1] != '-l'):
                    continue
            elif (command_len > 2):
                continue

            if (current_path == '/'):
                bucket_list = get_bucket_list(client)

                if (bucket_list == False):
                    continue

                # When using ls -l at bucket level, size is always 0, we know its a 'directory' so can hardcode those values
                if (command_len == 2):
                    for bucket in bucket_list:
                        print('application/x-directory        0              ' , bucket['CreationDate'] , '       ' ,bucket['Name'])
                else:
                    for bucket in bucket_list:
                        print('-dir- ', bucket['Name'])

            else:
                # If we are not at the root/bucket level, then we need to get our current full path,
                # split it into an array of words,
                # Remove the bucket from the path (temp_arr[0]),
                # then we can build the key to use list_objects in get_object_list to get info about objects in the dir
                temp_arr = get_directory_array(current_path)
                
                current_bucket = temp_arr[0]
                temp_path = current_path.replace('/' + current_bucket + '/', '')
                temp_arr.remove(current_bucket)
                temp_len = len(temp_arr)

                object_list = get_object_list(client, current_bucket)
                if (object_list == False):
                    continue
                else:
                    #If there are objects in the current directory, we need to know if they are dir or file
                    temp_list = []
                    for obj in object_list:
                        if (temp_path in obj['Key']):
                            # For each of our objects, we want to only want to look at things in the current dir
                            # so we remove and higher level folders by replacing them with empty string
                            relative_path = obj['Key'].replace(temp_path, '')
                            temp_list.append(relative_path)
                    
                    while ('' in temp_list):
                        temp_list.remove('')
                    
                    # mark where the '/' is to indicate a directory
                    for idx, item in enumerate(temp_list):
                        if ('/' in item):
                            temp_list[idx] = item.replace('/', '#/')

                    # each item is a path of an object in the bucket
                    # we put them all in a list
                    dir_list = []
                    for item in temp_list:
                        # Removes our '/' which is why we marked with '#'
                        arr = get_directory_array(item)
                        dir_list.append(arr[0])

                    # Remove any duplicates using set()
                    dir_list = list(set(dir_list))

                    # Using our marker for directories we re add '/'
                    for idx, item in enumerate(dir_list):
                        if ('#' in item):
                            dir_list[idx] = item.replace('#', '/')

                # if not using -l simple print
                if (command_len == 1):
                    for item in dir_list:
                        if ('/' in item):
                            print("-dir- ", item)
                        else:
                            print("      ", item)
                # if we are using -l fancy print
                else:
                    temp_arr = get_directory_array(current_path)
                    current_bucket = temp_arr[0]
                    temp_path = current_path.replace('/' + current_bucket + '/', '')

                    final_arr = []

                    for item in dir_list:
                        if ('/' not in item):
                            new_path = temp_path + item
                            final_arr.append(get_object_info(current_bucket, client, new_path, item))
                        else:
                            new_path = temp_path + item
                            final_arr.append(get_folder_info(current_bucket, client, new_path, item))
                    
                    for item in final_arr:
                        print('{:<30s} {:<15d} {}      {:<10s}'.format(item[0], item[1], item[2], item[3]))

        if (command_arr[0] == 'mkdir' and is_logged_in == True):
            if (command_len > 2):
                print("Invalid number of arguments for command: mkdir")
                continue

            if (current_path == '/'):
                print("mkdir is not allowed at the root level. Try mkbucket instead.")
            else:
                if ('s3:' in command_arr[1]):
                    command_arr[1] = command_arr[1].replace('s3:', '')
                dir_name = command_arr[1] + '/'
                temp_arr = get_directory_array(current_path)
                current_bucket = temp_arr[0]

                object_list = get_object_list(client, current_bucket)
                object_exists = is_object(object_list, dir_name)

                if (object_exists == True):
                    print("Cannot create directory '" + command_arr[1] + "': Already exists")
                else:
                    create_dir(current_bucket, client, current_path, dir_name)
        
        if (command_arr[0] == 'rmdir' and is_logged_in == True):
            if (command_len != 2):
                print("Invalid number of arguments for command: rmdir")
                continue
            
            if (current_path == '/'):
                print("rmdir is not allowed at the root level")
            else:
                dir_name = command_arr[1] + '/'
                temp_arr = get_directory_array(current_path)
                current_bucket = temp_arr[0]
                relative_path = current_path.replace('/' + current_bucket + '/', '')
                relative_path += dir_name

                object_list = get_object_list(client, current_bucket)
                object_num = is_object_num(object_list, relative_path)

                if (object_num == 0):
                    print("Unable to remove directory '" + dir_name + "'. Directory does not exist")
                else:
                    if (object_num > 1):
                        print("Unable to remove directory '" + dir_name + "'. Directory is not empty")
                    else:
                        delete_dir(current_bucket, client, relative_path)
        
        # mv objects between directories
        if (command_arr[0] == 'mv' and is_logged_in == True):
            if (command_len != 3):
                print("Invalid number of arguments for command: mv")
                continue
            
            # argument 1 - from
            path_from = command_arr[1]
            
            # argument 2 - to
            path_to = command_arr[2]   
            absolute_from = ''
            absolute_to = ''

            if (path_from == path_to):
                continue

            # if s3:/ or / was at the start of input, then absolute_from is same as input
            # remove s3: for easier parsing
            if (path_from.startswith("s3:/") or path_from.startswith("/")):
                absolute_from = path_from
                valid_from = valid_absolute_path_from(path_from, client)
            # if s3:/ or / is not at start of input, add input to the current path as it must be in the current directory,
            # or one of its children
            else:
                absolute_from = current_path + path_from
                valid_from = valid_absolute_path_from(absolute_from, client)   

            # similar idea but with the path we want to move to
            if (path_to.startswith("s3:/") or path_to.startswith('/')):
                absolute_to = path_to
                valid_to = valid_absolute_folder(path_to, client, 1)
            else:
                absolute_to = current_path + path_to
                valid_to = valid_absolute_folder(absolute_to, client, 0)

            # Print if invalid paths
            if (valid_from == False):
                print("Invalid src path. File not found")
                continue
            if (valid_to[0] == False):
                print("Invalid dest path. Folder(s) in path may not exist.")
                continue

            if (absolute_to.startswith('s3:')):
                absolute_to = absolute_to.replace('s3:', '')

            if (absolute_from.startswith('s3:')):
                absolute_from = absolute_from.replace('s3:', '')
            
            # get filename as last word in our array we got from splitting our path
            # get our bucket we are moving from and the key
            temp_arr = get_directory_array(absolute_from)
            from_bucket = temp_arr[0]
            filename = temp_arr[-1]
            from_key = absolute_from.replace('/' + temp_arr[0] + '/', '')

            # if the end word in the path to move to is a folder as determined in valid_absolute_folder,
            # then that means no filename was given, so we add the filename from the from path
            temp_arr_2 = get_directory_array(absolute_to)
            to_bucket = temp_arr_2[0]
            if (valid_to[1] == 0):
                absolute_to += '/' + filename
            if (len(temp_arr_2) == 1):
                to_key = filename
            else:
                to_key = absolute_to.replace('/' + temp_arr_2[0] + '/', '')

            copy_source = {
                'Bucket': from_bucket,
                'Key': from_key
            }

            client.copy(copy_source, to_bucket, to_key)
            client.delete_object(Bucket=from_bucket, Key=from_key)

        # Very similar to mv but we don't delete the original file after moving
        if (command_arr[0] == 'cp' and is_logged_in == True):
            if (command_len != 3):
                print("Invalid number of arguments for command: mv")
                continue
            
            path_from = command_arr[1]
            
            path_to = command_arr[2]   
            absolute_from = ''
            absolute_to = ''

            if (path_from.startswith("s3:/") or path_from.startswith("/")):
                absolute_from = path_from
                valid_from = valid_absolute_path_from(path_from, client)
            else:
                absolute_from = current_path + path_from
                valid_from = valid_absolute_path_from(absolute_from, client)   

            if (path_to.startswith("s3:/") or path_to.startswith('/')):
                absolute_to = path_to
                valid_to = valid_absolute_folder(path_to, client)
            else:
                absolute_to = current_path + path_to
                valid_to = valid_absolute_folder(absolute_to, client)

            
            if (valid_from == False):
                print("Invalid src path. File not found")
                continue
            if (valid_to[0] == False):
                print("Invalid dest path. Folder(s) in path may not exist.")
                continue

            if (absolute_to.startswith('s3:')):
                absolute_to = absolute_to.replace('s3:', '')

            if (absolute_from.startswith('s3:')):
                absolute_from = absolute_from.replace('s3:', '')
            
            temp_arr = get_directory_array(absolute_from)
            from_bucket = temp_arr[0]
            filename = temp_arr[-1]
            from_key = absolute_from.replace('/' + temp_arr[0] + '/', '')

            temp_arr_2 = get_directory_array(absolute_to)
            to_bucket = temp_arr_2[0]
            if (valid_to[1] == 0):
                absolute_to += '/' + filename
            if (len(temp_arr_2) == 1):
                to_key = filename
            else:
                to_key = absolute_to.replace('/' + temp_arr_2[0] + '/', '')

            if (from_bucket == to_bucket and from_key == to_key):
                temp_arr = get_directory_array(to_key)
                temp_string = temp_arr[-1]
                temp_arr[-1] = 'copy-' + temp_string
                to_key = to_key.replace(temp_string, temp_arr[-1])

            copy_source = {
                'Bucket': from_bucket,
                'Key': from_key
            }

            client.copy(copy_source, to_bucket, to_key)

        # similar to mv and cp, but one argument is from the users,
        # so we use os.path.basename to get the file the user wants to upload
        if (command_arr[0] == 'upload' and is_logged_in == True):
            if (command_len != 3):
                print("Invalid number of arguments for command: upload")
                continue
            
            path_to = command_arr[2]
            local_filename = command_arr[1] 
            absolute_to = ''

            if (path_to.startswith("s3:/") or path_to.startswith('/')):
                absolute_to = path_to
                valid_to = valid_absolute_folder(path_to, client, 1)
            else:
                absolute_to = current_path + path_to
                valid_to = valid_absolute_folder(absolute_to, client, 0)

            if (valid_to[0] == False):
                print("Invalid dest path. Folder(s) in path may not exist.")
                continue

            if (absolute_to.startswith('s3:')):
                absolute_to = absolute_to.replace('s3:', '')

            filename = os.path.basename(local_filename)

            temp_arr_2 = get_directory_array(absolute_to)
            to_bucket = temp_arr_2[0]
            if (valid_to[1] == 0):
                absolute_to += '/' + filename
            if (len(temp_arr_2) == 1):
                to_key = filename
            else:
                to_key = absolute_to.replace('/' + temp_arr_2[0] + '/', '')

            client.upload_file(local_filename, to_bucket, to_key)

        # basically a reverse of upload
        if (command_arr[0] == 'download' and is_logged_in == True):
            if (command_len != 3):
                print("Invalid number of arguments for command: download")
                continue

            path_from = command_arr[1]
            local_dir = command_arr[2]

            absolute_from = ''

            if (path_from.startswith("s3:/") or path_from.startswith('/')):
                absolute_from = path_from
                valid_from = valid_absolute_path_from(path_from, client)
            else:
                absolute_from = current_path + path_from
                valid_from = valid_absolute_path_from(absolute_from, client)

            if (valid_from == False):
                print("Invalid object location. Object not found")
                continue

            if (absolute_from.startswith("s3:")):
                absolute_from = absolute_from.replace('s3:', '')

            temp_arr = get_directory_array(absolute_from)
            from_bucket = temp_arr[0]
            filename = temp_arr[-1]
            from_key = absolute_from.replace('/' + temp_arr[0] + '/', '')

            filename = os.path.basename(local_dir)

            client.download_file(from_bucket, from_key, filename)

        if (command_arr[0] == 'rm' and is_logged_in == True):
            if (command_len != 2):
                print("Invalid number of arguments for command: rm")
                continue

            path_from = command_arr[1]

            absolute_from = ''

            if (path_from.startswith("s3:/") or path_from.startswith('/')):
                absolute_from = path_from
                valid_from = valid_absolute_path_from(path_from, client)
            else:
                absolute_from = current_path + path_from
                valid_from = valid_absolute_path_from(absolute_from, client)

            if (valid_from == False):
                print("Invalid object location. Object not found")
                continue
            
            temp_arr = get_directory_array(absolute_from)
            bucket = temp_arr[0]
            key = absolute_from.replace('/' + temp_arr[0] + '/', '')

            client.delete_object(Bucket=bucket, Key=key)


        if (command == 'logout' or command == 'exit' or command == 'quit'):
            break


main()
