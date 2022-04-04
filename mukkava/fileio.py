"""
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
    File checking for specific occurances of statements, e.g. an IP address, a stored public key or the value of a configuration attribute in cfg.toml
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

def check_file(input_file, attribute):
    file = open(input_file,'r')
    parsed_file = (input_file.read().splitlines())
    file.close()
    return True if attribute in parsed_file else False

def append_to_file(input_file, attribute):
    if check_file(input_file, attribute) is False:
        file = open(input_file,'a')
        file.write('\n')
        file.write(f'{attribute}')
        file.close()
    #     log_handler.info(f'Successfully added {ip} to {list_name}.')
    # else:
    #     log_handler.error(f'attempted to add an already present IP, {ip} to {list_name}.')

def remove_from_file(self, input_file, attribute):
    if check_file(input_file, attribute) is True:
        file = open(input_file,'r')
        parsed_file = input_file.read().splitlines()
        file.close()
        parsed_file.remove(attribute)
        output_file = open(input_file, 'w+')
        for lines in parsed_file:
            output_file.write(lines)
        output_file.close()
    #     log_handler.info(f'Successfully removed {ip} from {list_name}.')
    # else:
    #     log_handler.error(f'Attempted to remove a non present IP, {ip} from {list_name}.')
    #
    # else:
    #     log_handler.error(f'Invalid use of file_operation function, with params: {list_name} {operation} {ip}')

def set_in_file():
    pass

