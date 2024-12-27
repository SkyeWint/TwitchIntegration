import json
from types import SimpleNamespace



######### Public Methods #########


def parse_message(msg):

    # Message type is changed from text data frame to standard json to make accessing fields easier.
    msg_json = json.loads(msg)
    metadata = msg_json['metadata']
    payload = msg_json['payload']
    msg_type = metadata["message_type"]
    if msg_type == 'notification' or msg_type == 'revocation':
        return SubscriptionMessage(metadata, payload)
    else:
        return Message(metadata, payload)
    


######### Private Classes #########

class Message(object):
    def __init__(self, metadata, payload):
        self._metadata = metadata
        self._payload = payload
        self._type = self.message_type()

        payloadLayer1 = {}
        for k, v in self._payload.items():
            payloadLayer1[k] = SimpleNamespace(**v)
            
        self._payload = SimpleNamespace(**payloadLayer1)


    def message_id(self):
        return self._metadata["message_id"]
    
    def message_type(self):
        return self._metadata["message_type"]
    
    def message_timestamp(self):
        return self._metadata["message_timestamp"]


class SubscriptionMessage(Message):
    def __init__(self, metadata, payload):
        super().__init__(metadata, payload)

    def subscription_type(self):
        return self._metadata["subscription_type"]

    def subscription_version(self):
        return self._metadata["subscription_version"]
    
    def subscription_type(self):
        return self._payload.subscription.type
        
    def subscription_status(self):
        return self._payload.subscription.status
    
    def event_data(self):
        return self._payload.event
    