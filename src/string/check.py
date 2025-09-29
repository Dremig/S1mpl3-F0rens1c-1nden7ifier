import shutil
from ..logger.logger import Logger as log
import subprocess
import re
import os

TEMP_STRING_FILE = "temp"
UPLOAD_PATH = "upload"

def is_string_tool_exist():
    '''
    check if strings tool exist
    '''
    return shutil.which('strings') is not None

def not_exist_to_ask():
    '''
    choose if want to continue or not.
    can use the logic "if char can be in ascii, then it is a string that we can see", but slower and may cause error
    '''
    if not is_string_tool_exist():
        log.warning('strings tool not exist, please install it')
        log.ask('If you do not want to install it, you can use the project as well but maybe in a slower speed and have a higher error rate.\nDo you want to continue (if so, you can type "yes" or "y" to continue)?')
        if input() == 'y' or input() == 'yes':
            return True
        else:
            return False
    else:
        pass

def check_upload_and_return_it():
    count = len(os.listdir(UPLOAD_PATH))
    if not count:
        log.error("No file uploaded, please upload a file first")
        return False
    elif count == 1:
        # log.info("Only one file uploaded, using i")
        return UPLOAD_PATH + "/" + os.listdir(UPLOAD_PATH)[0]
    else:
        log.error("Too many file to analyze")
        return False

    

def maybe_fake_flag(flag):
    '''
    check if flag is fake
    '''
    maybe_fake_list = ['fake', 'f4k3', 'f4ke']
    
    flag_lower = flag.lower()
    
    for fake_str in maybe_fake_list:
        if fake_str in flag_lower:
            return True 
    
    return False 

def string_it(filepath):
    result = subprocess.run(['strings', filepath ], capture_output=True, text=True, check=True)
    with open("temp/strings", "w") as f:
        f.write(result.stdout)
    return result.stdout


    

def flag_format(format, result):
    '''
    search for flag that may fit flag format
    '''
    flags = []
    
    if "{" not in format or format.endswith("}\n"):
        log.error("format must be in the form of ...{...}, for example: flag{...}")
        return False
    else:
        parts = format.split("{", 1)
        if len(parts) < 2:
            log.error("invalid format")
            return False
            
        former, latter = parts
        flag_former = former + "{"
        escaped_former = re.escape(flag_former)
        escaped_latter = re.escape(latter) if latter else ""
        if latter:
            pattern = escaped_former + r"(.*?)" + escaped_latter
        else:
            pattern = escaped_former + r"(.*?)}"
        matches = re.findall(pattern, result)
        
        for match in matches:
            if latter:
                flag = flag_former + match + latter
            else:
                flag = flag_former + match + "}"
            flags.append(flag)

        for flag in flags:
            if maybe_fake_flag(flag):
                # flags.remove(flag)
                log.warning(f"Found suspected fake flag: {flag}")
                # print("test")
            else:
                log.success(f"Found suspected flag: {flag}")
        
        if not flags:
            log.info("No flag found. Maybe you can search for some encoding string like base64.")
        
        return True