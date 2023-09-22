from player import Player
import xml.etree.ElementTree as ET
import player_pb2
class PlayerFactory:


    def to_json(self, players):

        '''
            This function should transform a list of Player objects into a list with dictionaries.
        '''

        player_dicts = []
        for player in players:
             player_dict = {
                        'nickname': player.nickname,
                        'email': player.email,
                        'date_of_birth': player.date_of_birth.strftime("%Y-%m-%d"),
                        'xp':player.xp,
                        'class':player.cls
                    }
             player_dicts.append(player_dict)
        return player_dicts


    def from_json(self, list_of_dict):
        '''
            This function should transform a list of dictionaries into a list with Player objects.
        '''

        pl_lst=[]
        for i in list_of_dict:
            player=Player(i["nickname"],i["email"],i["date_of_birth"],i["xp"],i["class"])
            pl_lst.append(player)

        return pl_lst

    def from_xml(self, xml_string):
        '''
            This function should transform a XML string into a list with Player objects.
        '''
        players = []
        root = ET.fromstring(xml_string)

        for player_element in root.findall('player'):
            name = player_element.find('nickname').text
            email = player_element.find('email').text
            dt = player_element.find('date_of_birth').text
            xp = int(player_element.find('xp').text)
            cl = player_element.find('class').text
            player = Player(name, email,dt,xp,cl)
            players.append(player)

        return players

    import xml.etree.ElementTree as ET

    def to_xml(self, list_of_players):
        '''
            This function should transform a list with Player objects into a XML string.
        '''

        root = ET.Element("data")

        for player in list_of_players:
            i = ET.SubElement(root, "player")

            name = ET.SubElement(i, "nickname")
            name.text = player.nickname

            email_ = ET.SubElement(i, "email")
            email_.text = str(player.email)

            pl = ET.SubElement(i, "date_of_birth")
            pl.text = player.date_of_birth.strftime("%Y-%m-%d")

            pl = ET.SubElement(i, "xp")
            pl.text = str(player.xp)

            pl = ET.SubElement(i, "class")
            pl.text = player.cls

        xml_string = ET.tostring(root, encoding='utf-8', method='xml')

        return xml_string.decode('utf-8')


#Homework

    def from_protobuf(self, binary):
        list = player_pb2.PlayersList()

        list.ParseFromString(binary)

        newlist = []
        for i in list.player:
            pl = Player(
                nickname=i.nickname,
                email=i.email,
                date_of_birth=i.date_of_birth,
                xp=i.xp,
                cls=player_pb2.Class.Name(i.cls)
            )
            newlist.append(pl)

        return newlist


    def to_protobuf(self, list_of_players):
        list = player_pb2.PlayersList()
        for i in list_of_players:
            pl = list.player.add()

            pl.nickname = i.nickname
            pl.email = i.email
            pl.date_of_birth = i.date_of_birth.strftime("%Y-%m-%d")
            pl.xp = i.xp
            pl.cls = i.cls

        return list.SerializeToString()