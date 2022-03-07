import json



class Client_Class:
    def __init__(self, nickname, deafened, muted):  # self "represents" the individual object instance of a class
        self.nickname = nickname
        self.deafened = deafened
        self.muted = muted
        self.priority_speaker = False


client_test = Client_Class("za", False, False)
#print(client_test.deafened)
jsoned = json.dumps(client_test.__dict__) #this is a problem
#print(jsoned)

config = json.dump('server_config.json')
print(config)
#Rather then working with python objects, I'm going to use a JSON structure, so serialisation / complex conversion doesn't have to occur
