"""
This module is responsible for the following major tasks:
"""

import PySimpleGUI as sg

sg.theme('Dark')    # Keep things interesting for your users



layout = [[sg.Text('Client Nickname'),sg.Input(key='-IN-')],
          [sg.Text('Inital Client IP'),sg.Input(key='-IN-')],
          [sg.Text('Password'),sg.Input(key='-IN-')],
          [sg.Frame('Options', [[sg.Checkbox('Onion', key='Onion Sauce'),
                                            sg.Checkbox('Paprika', key='Paprika'),
                                            sg.Checkbox('Schezwan', key='Schezwan'),
                                            sg.Checkbox('Tandoori', key='Tandoori')]])],
          [sg.Button('Connect'), sg.Button('Exit'),]]



window = sg.Window('Unamed Voip Application v0.0.1', layout)

while True:                             # The Event Loop
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

window.close()