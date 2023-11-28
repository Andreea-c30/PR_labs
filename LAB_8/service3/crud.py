# Importing all needed modules.

import requests



class CRUDUser:
    def __init__(self, leader : bool, followers : dict =None):
        '''
            The constructor of the CrudUser.
        :param leader: bool
            The parameter deciding if the service is a leader or not.
        :param followers: dict, default = None
            The dictionary containing the credentials of the services.
        '''
        self.leader = leader
        if self.leader:
            self.followers = followers



    def post_electro_scooter(self, user_dict: dict):
        if self.leader:
            for follower in self.followers:
                requests.post(f"http://{follower['host']}:{follower['port']}/api/electro-scooters",
                              json=user_dict,
                              headers={"Token": "leader"})

    def update_electro_scooter(self, index: str, user_dict: dict):
        if self.leader:
            for follower in self.followers:
                requests.put(f"http://{follower['host']}:{follower['port']}/api/electro-scooters/{index}",
                             json=user_dict,
                             headers={"Token": "leader"})

    def delete_electro_scooter(self, index: str):
        if self.leader:
            for follower in self.followers:
                requests.delete(f"http://{follower['host']}:{follower['port']}/api/electro-scooters/{index}",
                                headers={"Token": "leader", "X-Delete-Password": "your_secret_password"})