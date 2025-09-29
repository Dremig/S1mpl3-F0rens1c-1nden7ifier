from . import check
from ..logger.logger import Logger as log

def goon():
    result = check.check_upload_and_return_it()
    if result:
        log.info("Checking a useful tool in your computer...")
        check.not_exist_to_ask()
        result = check.string_it(result)
        log.ask("If you want to search flag directly, you can type flag format in the terminal (example:): ")
        check.flag_format(input(), result)

