import logging
import threading
import socket
file_semaphore = threading.BoundedSemaphore()
def file_operation(listname, operation, ip): #Handles the required file IO for the whitelist and blacklist.

    if operation == "check": #check if there is an occurance of a given IP in whitelist or blacklist and give feedback of this.
        file_semaphore.acquire()
        input_file = open(f'{listname}.txt', 'r')
        parsed_file = (input_file.read().splitlines())
        if ip in parsed_file:
            input_file.close()
            file_semaphore.release()
            return True
        else:
            input_file.close()
            file_semaphore.release()
            return False

    elif operation == "append": #append a given IP to the whitelist or blacklist
        if file_operation(listname, "check", ip) is False:
            file_semaphore.acquire()
            input_file = open(f'{listname}.txt', 'a')
            input_file.write('\n')
            input_file.write(f'{ip}')
            input_file.close()
            file_semaphore.release()
            logging.debug(f'Successfully added {ip} to {listname}.')
        else: logging.error(f'attempted to add an allready present IP, {ip} to {listname}.')

    elif operation == "remove": #Remove a given IP from the whitelist or blacklist by checking
        if file_operation(listname, "check", ip) is True:
            file_semaphore.acquire()
            input_file = open(f'{listname}.txt', 'r')
            parsed_file = input_file.read().splitlines()
            input_file.close()
            parsed_file.remove(ip)
            output_file = open(f'{listname}.txt', 'w+')
            for lines in parsed_file:
                output_file.write(lines)
            output_file.close()
            file_semaphore.release()
            logging.debug(f'Successfully removed {ip} from {listname}.')
        else: logging.error(f'Attempted to remove a non present IP, {ip} from {listname}.')
    else: logging.error(f'Invalid use of file_operation function, with params: {listname} {operation} {ip}')

for item in range(0, 9):

