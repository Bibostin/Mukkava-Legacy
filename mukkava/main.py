'''
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE NOTES:
This module sets up logging chains, while this required for sys_logger, it is not for chat logger, however I have adopted the same methodology
simply to make understanding the code easier, rather then switching to the method use to setup a direct logger.

make screen logging optional
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE TEST CODE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DISSERTATION NOTES:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
'''

import PySimpleGUI as sg

sg.theme('Dark')    # Keep things interesting for your users



layout = [[sg.Text('Client Nickname'),sg.Input(key='nick')],
          [sg.Text('Inital Client IP'),sg.Input(key='submitted_ip')],
          [sg.Text('Password'),sg.Input(key='submitted_password')],
          [sg.Frame('Options', [[sg.Checkbox('Chatlog', key='cl'), sg.Checkbox('filelog', key='fl'), sg.Checkbox('stdoutlog', key='stdl')]]), sg.Button('Connect'), sg.Button('Exit')]]



window = sg.Window('Mukkava v0.0.1', icon='icon/icon.ico').Layout(layout)

while True:                             # The Event Loop
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

window.close()