import asyncio
import nio

nio.RoomMember.get_friendly_name = lambda self: self.display_name

class MatrixRoom():

    def __init__(self, client, nio_room):
        self.client = client
        self.nio_room = nio_room


    async def send_html(self, formatted_txt, txt=""):
        #print(formatted_txt)
        #print(txt)
        response = await self.client.room_send(
                room_id=self.nio_room.room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "format": "org.matrix.custom.html",
                    "formatted_body" : formatted_txt,
                    "body": txt,
                },
                ignore_unverified_devices=True)
        print(response)

    async def send_text(self, txt):
        response = await self.client.room_send(
                room_id=self.nio_room.room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": txt,
                },
                ignore_unverified_devices=True)
        print(response)

    async def get_joined_members(self):
       k = await self.client.joined_members(self.nio_room.room_id)
       return k.members
