from rest_framework import viewsets, permissions
from .models import Message
from .serializers import MessageSerializer
from django.db.models import Q, Max
from rest_framework.decorators import action
from rest_framework.response import Response

class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        target_id = self.request.query_params.get('target_id')
        user = self.request.user
        
        if not target_id:
            return Message.objects.none()


        ids = sorted([user.id, int(target_id)])
        room_name = f"{ids[0]}_{ids[1]}"
        
        return Message.objects.filter(room_name=room_name).order_by('timestamp')
   
    @action(detail=False, methods=['get'])
    def list_recent_contacts(self, request):
        user = request.user
        
        # 1. 找到所有与我相关的消息，按房间名和ID排序
        # 注意：PostgreSQL 的 distinct 必须配合对应的 order_by
        queryset = Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).order_by('room_name', '-id').distinct('room_name')

        # 2. 将结果按时间倒序排列
        recent_messages = sorted(queryset, key=lambda x: x.timestamp, reverse=True)
        
        # 3. 统计未读总数
        unread_count = Message.objects.filter(receiver=user, is_read=False).count()
        
        serializer = MessageSerializer(recent_messages, many=True)
        
        # 打印日志
        # print(f"DEBUG: 为用户 {user.username} 查到 {len(recent_messages)} 个联系人")
        
        return Response({
            'results': serializer.data,
            'unread_total': unread_count
        })

    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """将某个房间的消息设为已读"""
        target_id = request.data.get('target_id')
        ids = sorted([request.user.id, int(target_id)])
        room_name = f"{ids[0]}_{ids[1]}"
        Message.objects.filter(room_name=room_name, receiver=request.user).update(is_read=True)
        return Response({'status': 'ok'})