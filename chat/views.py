# 필요한 라이브러리와 모듈을 임포트합니다.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

# 채팅 관련 폼과 모델을 임포트합니다.
from chat.forms import RoomForm
from chat.models import Room

# 채팅의 초기 페이지를 보여주는 뷰 함수입니다.
def index(request):
    # 모든 채팅방 정보를 가져옵니다.
    room_qs = Room.objects.all()
    # 가져온 채팅방 정보를 템플릿으로 전달하여 렌더링합니다.
    return render(request, "chat/index.html", {
        "room_list": room_qs,
    })

# 로그인 사용자만 채팅방을 생성할 수 있습니다.
@login_required
def room_new(request):
    # POST 요청 시 채팅방 생성 작업을 수행합니다.
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            created_room = form.save(commit=False)
            created_room.owner = request.user
            created_room.save()
            return redirect("chat:room_chat", created_room.pk)
    else: # GET 요청 시 폼을 보여줍니다.
        form = RoomForm()

    return render(request, "chat/room_form.html", {
        "form": form,
    })

# 로그인 사용자만 채팅방에 입장할 수 있습니다.
@login_required
def room_chat(request, room_pk):
    # 주어진 PK로 채팅방 정보를 가져옵니다.
    room = get_object_or_404(Room, pk=room_pk)
    # 채팅방 정보를 템플릿으로 전달하여 렌더링합니다.
    return render(request, "chat/room_chat.html", {
        "room": room,
    })

# 로그인 사용자만 채팅방을 삭제할 수 있습니다.
@login_required
def room_delete(request, room_pk):
    # 주어진 PK로 채팅방 정보를 가져옵니다.
    room = get_object_or_404(Room, pk=room_pk)

    # 요청자가 채팅방의 소유자가 아닌 경우 오류 메시지를 보냅니다.
    if room.owner != request.user:
        messages.error(request, "채팅방 소유자가 아닙니다.")
        return redirect("chat:index")

    # POST 요청 시 채팅방을 삭제합니다.
    if request.method == "POST":
        room.delete()
        messages.success(request, "채팅방을 삭제했습니다.")
        return redirect("chat:index")

    return render(request, "chat/room_confirm_delete.html", {
        "room": room,
    })

# 채팅방에 접속한 사용자 목록을 반환합니다.
@login_required
def room_users(request, room_pk):
    room = get_object_or_404(Room, pk=room_pk)

    # 요청하는 사용자가 채팅방에 참여하지 않았으면 401 오류를 반환합니다.
    if not room.is_joined_user(request.user):
        return HttpResponse("Unauthorized user", status=401)

    # 채팅방에 접속 중인 사용자 이름을 가져옵니다.
    username_list = room.get_online_usernames()

    return JsonResponse({
        "username_list": username_list,
    })
