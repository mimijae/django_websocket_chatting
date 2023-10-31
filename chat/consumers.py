# 필요한 함수와 클래스를 가져옵니다.
from asgiref.sync import async_to_sync  # 비동기 함수를 동기식으로 호출하기 위해 사용됩니다.
from channels.generic.websocket import JsonWebsocketConsumer  # WebSocket에 대한 기본 컨슈머 클래스입니다.

from chat.models import Room  # chat 앱에서 Room 모델을 가져옵니다.

# ChatConsumer 정의. JsonWebsocketConsumer의 하위 클래스입니다.
class ChatConsumer(JsonWebsocketConsumer):

    # ChatConsumer의 생성자 함수입니다.
    def __init__(self, *args, **kwargs):
        # 상위 클래스의 생성자를 호출합니다.
        super().__init__(*args, **kwargs)
        self.group_name = ""  # group_name을 빈 문자열로 초기화합니다.
        self.room = None  # room 객체를 None으로 초기화합니다.

    # WebSocket이 연결 과정 중일 때 호출됩니다.
    def connect(self):
        user = self.scope["user"]  # scope에서 사용자를 가져옵니다.

        # 사용자가 인증되지 않았다면 WebSocket 연결을 종료합니다.
        if not user.is_authenticated:
            self.close()
        else:
            # url 경로에서 방의 기본 키를 가져옵니다.
            room_pk = self.scope["url_route"]["kwargs"]["room_pk"]

            try:
                # 기본 키를 통해 Room 객체를 가져옵니다.
                self.room = Room.objects.get(pk=room_pk)
            except Room.DoesNotExist:
                # 방이 존재하지 않으면 WebSocket 연결을 종료합니다.
                self.close()
            else:
                # room 객체에서 그룹 이름을 가져옵니다.
                self.group_name = self.room.chat_group_name

                # 사용자를 방에 추가하고 새로운 참가자인지 확인합니다.
                is_new_join = self.room.user_join(self.channel_name, user)
                if is_new_join:
                    # 새로운 사용자라면 그룹에 참가 알림을 보냅니다.
                    async_to_sync(self.channel_layer.group_send)(
                        self.group_name,
                        {
                            "type": "chat.user.join",
                            "username": user.username,
                        }
                    )

                # 현재 채널을 그룹에 추가합니다.
                async_to_sync(self.channel_layer.group_add)(
                    self.group_name,
                    self.channel_name,
                )

                # WebSocket 연결을 수락합니다.
                self.accept()

    # WebSocket이 닫힐 때 호출됩니다.
    def disconnect(self, code):
        # group_name이 있으면 현재 채널을 그룹에서 제거합니다.
        if self.group_name:
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name,
                self.channel_name,
            )

        user = self.scope["user"]

        # room 객체가 있으면 사용자가 마지막으로 나가는지 확인합니다.
        if self.room is not None:
            is_last_leave = self.room.user_leave(self.channel_name, user)
            if is_last_leave:
                # 사용자가 마지막이라면 그룹에 나가기 알림을 보냅니다.
                async_to_sync(self.channel_layer.group_send)(
                    self.group_name,
                    {
                        "type": "chat.user.leave",
                        "username": user.username,
                    }
                )

    # 서버가 WebSocket으로부터 메시지를 받을 때 호출됩니다.
    def receive_json(self, content, **kwargs):
        user = self.scope["user"]

        _type = content["type"]

        # 메시지 유형이 채팅 메시지인 경우.
        if _type == "chat.message":
            sender = user.username
            message = content["message"]
            # 그룹에 채팅 메시지를 전송합니다.
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                    "type": "chat.message",
                    "message": message,
                    "sender": sender,
                }
            )
        else:
            print(f"잘못된 메시지 유형 : ${_type}")

    # 사용자가 채팅에 참가할 때의 처리입니다.
    def chat_user_join(self, message_dict):
        self.send_json({
            "type": "chat.user.join",
            "username": message_dict["username"],
        })

    # 사용자가 채팅에서 나갈 때의 처리입니다.
    def chat_user_leave(self, message_dict):
        self.send_json({
            "type": "chat.user.leave",
            "username": message_dict["username"],
        })

    # 전송된 채팅 메시지를 처리하는 함수입니다.
    def chat_message(self, message_dict):
        self.send_json({
            "type": "chat.message",
            "message": message_dict["message"],
            "sender": message_dict["sender"],
        })

    # 채팅방이 삭제될 때의 처리입니다.
    def chat_room_deleted(self, message_dict):
        custom_code = 4000  # 방 삭제에 대한 사용자 정의 코드입니다.
        self.close(code=custom_code)  # 사용자 정의 코드로 WebSocket을 닫습니다.
