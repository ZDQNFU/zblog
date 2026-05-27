from django.contrib.auth.models import User
from django.db.models import Count
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from article.models import Article, Category, Tag, Comment
from .captcha import generate_captcha, verify_captcha
from .permissions import IsSuperAdmin
from .email_verification import generate_verification_code
from .serializers import (
    LoginSerializer, UserInfoSerializer, UserAdminSerializer, UserCreateSerializer,
    EmailVerificationSerializer, RegisterSerializer,
)
from .throttling import LoginRateThrottle

throttle = LoginRateThrottle()


class CaptchaView(APIView):
    """获取验证码"""

    def get(self, request):
        expr, captcha_key = generate_captcha()
        return Response({'captcha_key': captcha_key, 'expression': expr})


class LoginView(APIView):
    """登录接口（JWT + 验证码 + 频率限制）"""

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            username = request.data.get('username', '')
            if username:
                throttle.record_failure(username)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        captcha_key = request.data.get('captcha_key', '')
        captcha_answer = request.data.get('captcha_answer', '')

        # 检查是否被锁定
        locked, remaining = throttle.is_locked(username)
        if locked:
            return Response(
                {'detail': f'登录失败次数过多，请 {remaining} 秒后再试'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # 验证码校验
        if not verify_captcha(captcha_key, captcha_answer):
            throttle.record_failure(username)
            return Response(
                {'captcha_answer': ['验证码错误']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 验证成功，清除失败记录
        throttle.reset(username)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserInfoSerializer(user).data,
        })


class UserInfoView(APIView):
    """获取当前用户信息"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserInfoSerializer(request.user).data)


class LogoutView(APIView):
    """登出"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({'detail': '已登出'})


class StatsView(APIView):
    """管理端统计数据"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_articles = Article.objects.count()
        published_articles = Article.objects.filter(status='published').count()
        draft_articles = Article.objects.filter(status='draft').count()
        private_articles = Article.objects.filter(status='private').count()
        total_tags = Tag.objects.count()
        total_categories = Category.objects.count()
        total_comments = Comment.objects.count()
        total_views = Article.objects.aggregate(s=Count('view_count'))['s'] or 0
        total_likes = Article.objects.aggregate(s=Count('like_count'))['s'] or 0

        # 分类下的文章数
        category_stats = list(
            Category.objects.annotate(article_count=Count('article')).values('name', 'article_count')
        )

        # 标签下的文章数（Top 10）
        tag_stats = list(
            Tag.objects.annotate(article_count=Count('article'))
            .order_by('-article_count')[:10]
            .values('name', 'article_count', 'color')
        )

        # 近6个月发布趋势
        from django.db.models.functions import TruncMonth
        monthly_trend = list(
            Article.objects
            .filter(published_at__isnull=False)
            .annotate(month=TruncMonth('published_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('-month')[:6]
        )

        return Response({
            'totals': {
                'articles': total_articles,
                'published': published_articles,
                'draft': draft_articles,
                'private': private_articles,
                'tags': total_tags,
                'categories': total_categories,
                'comments': total_comments,
                'views': total_views,
                'likes': total_likes,
            },
            'category_stats': category_stats,
            'tag_stats': tag_stats,
            'monthly_trend': list(reversed(monthly_trend)),
        })


# ---------- User Management (superadmin only) ----------

class UserListView(generics.ListCreateAPIView):
    """用户列表 & 创建"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    search_fields = ['username', 'email']
    queryset = User.objects.order_by('-date_joined')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserAdminSerializer
        return UserCreateSerializer

    def get_queryset(self):
        qs = User.objects.order_by('-date_joined')
        # 布尔字段过滤
        is_superuser = self.request.query_params.get('is_superuser')
        if is_superuser is not None:
            qs = qs.filter(is_superuser=is_superuser.lower() == 'true')
        is_staff = self.request.query_params.get('is_staff')
        if is_staff is not None:
            qs = qs.filter(is_staff=is_staff.lower() == 'true')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        return qs


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """用户详情 & 更新 & 删除"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer


# ---------- Registration ----------

class SendVerificationCodeView(APIView):
    """发送邮箱验证码"""

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data['email']
        generate_verification_code(email)
        return Response({'detail': '验证码已发送'})


class RegisterView(APIView):
    """用户注册"""

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.create_user()
        refresh = RefreshToken.for_user(user)

        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserInfoSerializer(user).data,
        })
