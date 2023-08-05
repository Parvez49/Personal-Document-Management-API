from django.shortcuts import render

# Create your views here.


from .serializers import DocumentSerializer, DocumentListSerializer, ShareDocumentSerializer
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Document

import jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User



@api_view(['POST'])
def documentUpload(request):

    token=request.COOKIES.get("logintoken")
    if not token:
        return Response("Loggin first")
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated!')
    except DecodeError:
        raise AuthenticationFailed('Unauthenticated!')
    
    user=User.objects.get(pk=payload['id'])
    request.data['owner']=user.pk

    
    serializer=DocumentSerializer(data=request.data)
    if serializer.is_valid():
        #serializer.save()
        print("valid")
        return Response("successfully upload your document")
    else:
        return Response(serializer.errors)
    
from django.http import FileResponse
from django.http import HttpResponse

@api_view(['GET'])
def documentDownload(request,document_id):
    
    token=request.COOKIES.get("logintoken")
    if not token:
        return Response("Loggin first")
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated!')
    except DecodeError:
        raise AuthenticationFailed('Unauthenticated!')
    
    doc=Document.objects.get(id=document_id)
    if not doc:
        return Response("Not found")
    
    user=User.objects.get(pk=payload['id'])
    if doc.owner!=user:
        return Response("You do not have permission to download")
    
    file_path = doc.file.path
    response = FileResponse(open(file_path, 'rb'))
    return response



@api_view(['PUT'])
def documentUpdate(request, document_id):

    token=request.COOKIES.get("logintoken")
    if not token:
        return Response("Loggin first")
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated!')
    except DecodeError:
        raise AuthenticationFailed('Unauthenticated!')
    
    doc=Document.objects.get(id=document_id)
    if not doc:
        return Response("Not found")
    
    user=User.objects.get(pk=payload['id'])
    if doc.owner!=user:
        return Response("You do not have permission to download")

    print(doc)

    serializer = DocumentSerializer(doc, data=request.data, partial=True)
    print(serializer)
    if serializer.is_valid():
        serializer.save()
        return Response('Document metadata updated successfully.')
    else:
        return Response(serializer.errors)

@api_view(['DELETE']) 
def documentDelete(request,document_id):
    token=request.COOKIES.get("logintoken")
    if not token:
        return Response("Loggin first")
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated!')
    except DecodeError:
        raise AuthenticationFailed('Unauthenticated!')
    
    doc=Document.objects.get(id=document_id)
    if not doc:
        return Response("Not found")
    
    user=User.objects.get(pk=payload['id'])
    if doc.owner!=user:
        return Response("You do not have permission to download")
          
    doc.delete()
    return Response('Document deleted successfully.')

@api_view(['GET'])  
def documentList(request):
    token=request.COOKIES.get("logintoken")
    if not token:
        return Response("Loggin first")
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated!')
    except DecodeError:
        raise AuthenticationFailed('Unauthenticated!')
    
    documents=Document.objects.filter(owner=payload['id'])
    serializers=DocumentListSerializer(documents,many=True)
    return Response(serializers.data)
    

@api_view(['POST'])
def documentShare(request,document_id):
    token=request.COOKIES.get("logintoken")
    if not token:
        return Response("Loggin first")
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated!')
    except DecodeError:
        raise AuthenticationFailed('Unauthenticated!')
    
    doc=Document.objects.filter(id=document_id).first()
    user=User.objects.get(id=payload['id'])
    request.data['owner']=user.pk
    request.data['document']=doc.pk
    for gmail in request.data['gmails']:
        sharew=User.objects.filter(email=gmail).first()
        if sharew:
            request.data['sharedwith']=sharew.pk
            serializer=ShareDocumentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)


    return Response("None")




