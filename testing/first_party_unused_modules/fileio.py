"""
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
    File checking for specific occurances of statements, e.g. an IP address, a stored public key or the value of a configuration attribute in config.toml
    Appending new values to files if they are found to not be present and the program flow desires to add them
    Removing old values from files if the they are found to be present and the program flow desires to remove them
    setting the value of configuration attributes for persistancy of user choices or input

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE NOTES:

TODO: consider switching string evaluation to regex
TODO: file presence / perm checks, input validation
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE TEST CODE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DISSERTATION NOTES:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
import logging
log = logging.getLogger(__name__)


def check_file(input_file, attribute):
    file = open(input_file,'r')
    parsed_file = (input_file.read().splitlines())
    file.close()
    return True if attribute in parsed_file else False

def append_to_file(input_file, attribute, newline=True):
    if check_file(input_file, attribute) is False:
        try: file = open(input_file,'a')
        except: ValueError("Supplied file not present!")
        if newline is True: file.write('\n')
        file.write(f'{attribute}')
        file.close()
        log.info(f'Successfully added {attribute} to {input_file}.')
    else:
        log.error(f'attempted to add an already present attribute: {attribute} to file: {input_file}.')

def remove_from_file(input_file, attribute):
    if check_file(input_file, attribute) is True:
        try: file = open(input_file,'r')
        except: ValueError("Supplied file not present!")
        parsed_file = input_file.read().splitlines()
        file.close()
        parsed_file.remove(attribute)
        output_file = open(input_file, 'w+')
        for lines in parsed_file:
            output_file.write(lines)
        output_file.close()
        log.info(f'Successfully removed {attribute} from {input_file}.')
    else:
        log.error(f'Attempted to remove a non present attribute: {attribute} from: {input_file}.')

def set_in_file():
    pass

