from rest_framework.response import Response
from rest_framework.views import APIView

from blog.pagination import postPageNumberPagination
from .models import Post
from .serializer import PostSerializer
from blog import serializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
# 포스팅 목록 및 새 포스팅 작성(CBV)
class PostListAPIView(APIView):
    def get(self, request):
        serializer = PostSerializer(Post.objects.all(), many = True)
        return Response(serializer.data)
    def post(self, request):
        serializer = PostSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        
        return Response(serializer.errors, status = 400)

# 포스트 게시글 가져오기, 수정, 삭제(CBV)
class PostDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Post, pk=pk)
    
    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    def put(self, request, pk):
        post = self.get_object(pk)
        serializer = PostSerializer(post, data = request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# 포스팅 목록 및 새 포스팅 작성(FBV)
@api_view(['GET','POST'])
def post_list(request):
    if request.method == 'GET':
        qs = Post.objects.all()
        serializer = PostSerializer(qs, many = True)
        return Response(serializer.data)
    else:
        serializer = PostSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        
        return Response(serializer.errors, status = 400)

# 포스트 게시글 가져오기, 수정, 삭제(FBV)
@api_view(['GET','PUT',"DELETE"])
def post_detail(request,pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = PostSerializer(post, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.erros, status = status.HTTP_404_NOT_FOUND)
    else:
        post.delete()
        return Response(status.HTTP_204_NO_CONTENT)
    
    
# 포스팅 목록 및 새 포스팅 작성(Mixin 이용)
class PostListMixins(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    def get(self, request, *args,  **kwargs):
        return self.list(request)
    
    def post(self, request, *args, **kwargs):
        return self.create(request)

# 포스트 게시글 가져오기, 수정, 삭제(Mixin 이용)  
class PostDetailMixins(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def pust(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
    
# 포스팅 목록 및 새 포스팅 작성(Generic View이용)
class PostListGenericAPIView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

# 포스트 게시글 가져오기, 수정, 삭제(GenericView 이용)
class PostDetailGenericView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
# 포스팅 목록 및 새 포스팅 작성, 게시글 가져오기, 수정, 삭제 전부가능(ViewSet 이용)
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = postPageNumberPagination
    
    #url post/public_list/
    @action(detail=False)
    def public_list(self, request):
        qs = self.queryset.filter(is_public = True)
        serializer = self.get_serializer(qs, many = True)
        return Response(serializer.data)
    
    #url post/{pk}/set_public/
    @action(detail=True, methods=['patch'])
    def set_public(self, request, pk):
        instance = self.get_object()
        instance.is_public = True
        instance.save()
    

    
    # 필터기능(http://127.0.0.1:8000/post/?search=세영)
    filter_backends = [SearchFilter]
    search_fields = ['title']
    
# as_view 옵션을 통해서 따로 분리하는 것도 가능하다.
post_list = PostViewSet.as_view({
    'get' : 'list',
    'post' : 'create',
})

post_detail = PostViewSet.as_view({
    'get' : 'retrieve',
    'put' : 'update',
    'patch' : 'partial_update',
    'delete' : 'destroy',
})