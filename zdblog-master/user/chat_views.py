import json
import os
import sqlite3
from datetime import datetime, timedelta

import msgpack
from django.contrib.auth.models import User
from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsSuperAdmin


def _get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, '..', 'chat_robot', 'data', 'asuka_memory.db')


def _get_conn():
    return sqlite3.connect(_get_db_path())


def _decode_checkpoint(blob):
    return msgpack.unpackb(blob)


def _extract_messages(checkpoint):
    """Extract LangChain messages from a checkpoint state."""
    msgs = (
        checkpoint.get('channel_values', {})
        .get('messages', [])
    )
    result = []
    for m in msgs:
        data = m.get('data', m) if isinstance(m, dict) else {}
        content = m.get('content', '') if isinstance(m, dict) else getattr(m, 'content', '')
        msg_type = m.get('type', '') if isinstance(m, dict) else getattr(m, 'type', '')

        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and 'text' in item:
                    text_parts.append(item['text'])
                elif isinstance(item, str):
                    text_parts.append(item)
            content = ''.join(text_parts)

        if isinstance(content, str) and content.strip():
            result.append({
                'role': 'user' if msg_type == 'human' else 'ai',
                'content': content,
            })
    return result


def _get_checkpoints_for_thread(thread_id, since=None):
    """Get all checkpoints for a thread, ordered by time."""
    conn = _get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT checkpoint FROM checkpoints WHERE thread_id = ? ORDER BY rowid ASC',
            (thread_id,)
        )
        rows = cursor.fetchall()
        messages = []
        for row in rows:
            cp = _decode_checkpoint(row[0])
            cp_msgs = _extract_messages(cp)
            if since:
                # Filter messages by timestamp from checkpoint metadata
                pass
            messages.extend(cp_msgs)

        # Deduplicate consecutive identical messages
        deduped = []
        for m in messages:
            if not deduped or m['content'] != deduped[-1]['content'] or m['role'] != deduped[-1]['role']:
                deduped.append(m)
        return deduped
    finally:
        conn.close()


def _get_latest_timestamp_for_thread(thread_id):
    conn = _get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT checkpoint FROM checkpoints WHERE thread_id = ? ORDER BY rowid DESC LIMIT 1',
            (thread_id,)
        )
        row = cursor.fetchone()
        if row:
            cp = _decode_checkpoint(row[0])
            ts = cp.get('ts', '') or cp.get('timestamp', '')
            return ts
        return None
    finally:
        conn.close()


def _delete_checkpoints_for_thread(thread_id):
    conn = _get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM writes WHERE thread_id = ?', (thread_id,))
        cursor.execute('DELETE FROM checkpoints WHERE thread_id = ?', (thread_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def _trim_checkpoints_for_thread(thread_id, keep_days):
    """Delete checkpoints older than keep_days for a thread."""
    conn = _get_conn()
    try:
        cursor = conn.cursor()
        cutoff = (datetime.now() - timedelta(days=keep_days)).isoformat()

        cursor.execute(
            'SELECT checkpoint_id, checkpoint FROM checkpoints WHERE thread_id = ? ORDER BY rowid ASC',
            (thread_id,)
        )
        rows = cursor.fetchall()

        deleted = 0
        for cp_id, blob in rows:
            cp = _decode_checkpoint(blob)
            ts = cp.get('ts', '')
            if ts and ts < cutoff:
                cursor.execute(
                    'DELETE FROM writes WHERE thread_id = ? AND checkpoint_id = ?',
                    (thread_id, cp_id)
                )
                cursor.execute(
                    'DELETE FROM checkpoints WHERE thread_id = ? AND checkpoint_id = ?',
                    (thread_id, cp_id)
                )
                deleted += 1
        conn.commit()
        return deleted
    finally:
        conn.close()


class ChatStreamView(APIView):
    """流式对话接口（仅超管/staff，SSE）"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request):
        message = request.data.get('message', '').strip()
        if not message:
            return Response({'detail': '消息不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        thread_id = str(request.user.id)

        def event_stream():
            from chat_robot.agent import agent
            from chat_robot.utils import stream_chat_with_agent
            try:
                for token in stream_chat_with_agent(agent, message, thread_id):
                    yield f'data: {json.dumps({"token": token})}\n\n'
                yield f'data: {json.dumps({"done": True})}\n\n'
            except Exception as e:
                yield f'data: {json.dumps({"error": str(e)})}\n\n'

        response = StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream',
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response


class ChatHistoryView(APIView):
    """获取当前用户的聊天记录"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        thread_id = str(request.user.id)
        messages = _get_checkpoints_for_thread(thread_id)
        return Response({'messages': messages, 'thread_id': thread_id})


# ---------- S-end chat management (superadmin only) ----------

class ChatUserListView(APIView):
    """列出有聊天记录的所有用户"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        search = request.query_params.get('search', '').strip()
        conn = _get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT thread_id FROM checkpoints')
            thread_ids = [r[0] for r in cursor.fetchall()]
        finally:
            conn.close()

        users = []
        for tid in thread_ids:
            user = User.objects.filter(pk=tid).first()
            if user:
                if search and search.lower() not in user.username.lower():
                    continue
                msg_count = len(_get_checkpoints_for_thread(tid))
                last_ts = _get_latest_timestamp_for_thread(tid)
                users.append({
                    'id': user.id,
                    'username': user.username,
                    'message_count': msg_count,
                    'last_active': last_ts,
                })

        users.sort(key=lambda u: u['last_active'] or '', reverse=True)
        return Response({'users': users})


class ChatUserDetailView(APIView):
    """查看某个用户的聊天记录详情"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request, user_id):
        thread_id = str(user_id)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        messages = _get_checkpoints_for_thread(thread_id)
        return Response({
            'user': {'id': user.id, 'username': user.username},
            'messages': messages,
        })


class ChatClearView(APIView):
    """清空某用户的聊天记录"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request, user_id):
        try:
            User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        thread_id = str(user_id)
        deleted = _delete_checkpoints_for_thread(thread_id)
        return Response({'detail': f'已清空 {deleted} 条记录'})


class ChatTrimView(APIView):
    """只保留某用户最近 N 天的聊天记录"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request, user_id):
        try:
            User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        keep_days = int(request.data.get('days', 30))
        if keep_days < 1:
            return Response({'detail': '天数必须 >= 1'}, status=status.HTTP_400_BAD_REQUEST)

        thread_id = str(user_id)
        deleted = _trim_checkpoints_for_thread(thread_id, keep_days)
        return Response({'detail': f'已清理 {deleted} 条记录，保留最近 {keep_days} 天'})
