from enum import Enum



######### Enum List #########

class RequestType(Enum):
    
    CHAT_MSG = "channel.chat.message"
    POINTS_REDEMPTION_ADD = "channel.channel_points_custom_reward_redemption.add"
    POINTS_REWARD_ADD = "channel.channel_points_custom_reward.add"
    POINTS_REWARD_REMOVE = "channel.channel_points_custom_reward.remove"
    CHEER = "channel.cheer"
    CHARITY_DONATION = "channel.charity_campaign.donate"




######### Public Functions #########

class Subscription_Data():
    def __init__(self, session_id:"str", broadcast_user_id:"str") -> None:
        self.bodyBase = {
            'version': '1',
            'transport': {
                'method': 'websocket',
                'session_id': session_id
            }
        }

        self.broadcast_user_id = broadcast_user_id


        ######### Data Payloads #########

        self.requestParams = {
            RequestType.CHAT_MSG: {
                'type': RequestType.CHAT_MSG.value,
                'condition': {
                    'broadcaster_user_id': self.broadcast_user_id,  # Broadcaster user ID is used to identify the channel being observed.
                    'user_id': self.broadcast_user_id  # User ID is used to identify who is observing the messages.
                }   
            },
            RequestType.POINTS_REDEMPTION_ADD: {
                'type': RequestType.POINTS_REDEMPTION_ADD.value,
                'condition': {
                    'broadcaster_user_id': self.broadcast_user_id, # Broadcaster user ID is used to identify the channel being observed.
                }
            },
            RequestType.POINTS_REWARD_ADD: {
                'type': RequestType.POINTS_REWARD_ADD.value,
                'condition': {
                    'broadcaster_user_id': self.broadcast_user_id, # Broadcaster user ID is used to identify the channel being observed.
                }
            },
            RequestType.POINTS_REWARD_REMOVE: {
                'type': RequestType.POINTS_REWARD_REMOVE.value,
                'condition': {
                    'broadcaster_user_id': self.broadcast_user_id, # Broadcaster user ID is used to identify the channel being observed.
                }
            },
            RequestType.CHEER: {
                'type': RequestType.CHEER.value,
                'condition': {
                    'broadcaster_user_id': self.broadcast_user_id, # Broadcaster user ID is used to identify the channel being observed.
                }
            },
            RequestType.CHARITY_DONATION: {
                'type': RequestType.CHARITY_DONATION.value,
                'condition': {
                    'broadcaster_user_id': self.broadcast_user_id, # Broadcaster user ID is used to identify the channel being observed.
                }
            }
        }


    def get_subscription_data(self, requestType:"str") -> dict:
        return {
            'type': self.requestParams[requestType]['type'],
            'version': self.bodyBase['version'],
            'condition': self.requestParams[requestType]['condition'],
            'transport': self.bodyBase['transport']
        }


    