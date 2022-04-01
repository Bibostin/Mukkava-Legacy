"""
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE NOTES:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE TEST CODE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DISSERTATION NOTES:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

config = toml.load('cfg.toml')# Dictionary pulled from server_config.toml

def list_operation(list_name, operation, ip):  # TODO: file presence / perm checks, input validation
    if operation == "check":  # check for occurrence of an IP in whitelist or blacklist.
        input_file = open(f'{list_name}.txt', 'r')
        parsed_file = (input_file.read().splitlines())
        input_file.close()
        return True if ip in parsed_file else False

    elif operation == "append":  # append a given IP to the whitelist or blacklist
        if file_operation(list_name, "check", ip) is False:
            input_file = open(f'{list_name}.txt', 'a')
            input_file.write('\n')
            input_file.write(f'{ip}')
            input_file.close()
            log_handler.info(f'Successfully added {ip} to {list_name}.')
        else:
            log_handler.error(f'attempted to add an already present IP, {ip} to {list_name}.')

    elif operation == "remove":  # Remove a given IP from the whitelist or blacklist by checking
        if file_operation(list_name, "check", ip) is True:
            input_file = open(f'{list_name}.txt', 'r')
            parsed_file = input_file.read().splitlines()
            input_file.close()
            parsed_file.remove(ip)
            output_file = open(f'{list_name}.txt', 'w+')
            for lines in parsed_file:
                output_file.write(lines)
            output_file.close()
            log_handler.info(f'Successfully removed {ip} from {list_name}.')
        else:
            log_handler.error(f'Attempted to remove a non present IP, {ip} from {list_name}.')

    else:
        log_handler.error(f'Invalid use of file_operation function, with params: {list_name} {operation} {ip}')

def config_operation(operation, data):
    pass

