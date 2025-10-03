import shutil
from ..logger.logger import Logger as log
import subprocess
import re
import os
from pyzbar.pyzbar import decode
from PIL import Image, ImageDraw
import numpy as np

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
    '''
    ensure that there is only one file in upload folder, and return its path
    '''
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


def is_valid_flag_format(format):
    '''
    check if format is valid
    '''
    if "{" not in format or format.endswith("}\n"):
        log.error("format must be in the form of ...{...}, for example: flag{...}")
        return False
    else:
        parts = format.split("{", 1)
        if len(parts) < 2:
            log.error("format must be in the form of ...{...}, for example: flag{...}")
            return False
        
        return True


def is_valid_flag(format, flag):
    '''
    check if flag suits the format
    '''
    parts = format.split('{', 1)
    former, later = parts
    flag.replace("\n", "")
    if flag.startwith(former) and flag.endwith("}"):
        return True
    else:
        return False


    


def search_for_flag_directly(format, result):
    '''
    search for flag that is shown "directly" in text
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



def bitstream_to_qr_image(bitstream, module_size=10, quiet_zone=4):
    """
    generate a qrcode image from a bitstream
    """
    length = len(bitstream)
    side_length = int(length ** 0.5)
    
    if side_length * side_length != length:
        raise ValueError(f"the bit length {length} is not a perfect square, cannot form a valid QR code.")
    
    img_size = (side_length + 2 * quiet_zone) * module_size
    img = Image.new('RGB', (img_size, img_size), 'white')
    draw = ImageDraw.Draw(img)
    
    for i, bit in enumerate(bitstream):
        if bit == '1':  
            row = i // side_length
            col = i % side_length
            x0 = (col + quiet_zone) * module_size
            y0 = (row + quiet_zone) * module_size
            x1 = x0 + module_size
            y1 = y0 + module_size
            draw.rectangle([x0, y0, x1, y1], fill='black')
    
    return img

def decode_bitstream_via_image(bitstream):
    try:
        qr_image = bitstream_to_qr_image(bitstream)
        
        decoded_objects = decode(Image.open(qr_image))
        
        if decoded_objects:
            result = decoded_objects[0]
            log.success(f"Decoded QR code content: {result.data.decode('utf-8')}")
        else:
            pass
    except Exception as e:
        pass





def find_continuous_binary(result, format):
    """
    search for information that stored in binary 
    """
    pattern = r'[01]+'
    matches = re.findall(pattern, result)
    for match in matches:
        can_use = True
        decode_already = False
        if len(match) < 20:
            continue
        if len(match) % 7 == 0:
            result_str = ""
            for i in range(0, len(match), 7):
                # result_str += chr(int(match[i:i+7], 2))
                int_char = int(match[i:i+7], 2)
                if int_char > 128 or int_char < 32:
                    can_use = False
                    break
                else:
                    result_str += chr(int_char)


            if can_use:
                decode_already = True


        if len(match) % 8 == 0:
            result_str = ""
            for i in range(0, len(match), 8):
                # result_str += chr(int(match[i:i+8], 2))
                int_char = int(match[i:i+8], 2)
                if int_char > 128 or int_char < 32:
                    can_use = False
                    break
                else:
                    result_str += chr(int_char)

            if can_use:
                decode_already = True

        

        if can_use and decode_already:
            log.success(f"Found continuous binary, and can be encoded as ascii in str : {result_str}")


        decode_bitstream_via_image(match)




    



