from django.shortcuts import render

# Create your views here.


from .serializers import DocumentSerializer, DocumentListSerializer, ShareDocumentSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Document
from django.http import FileResponse

import jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema



def authenticateUser(token):
    if not token:
        return Response("Loggin first")
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except ExpiredSignatureError:
        raise AuthenticationFailed({"error":'You session has expired!'})
    except DecodeError:
        raise AuthenticationFailed({"error":'Log in failed!'})
    return payload


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'description': openapi.Schema(type=openapi.TYPE_STRING),
            'format': openapi.Schema(type=openapi.TYPE_STRING),
            'file': openapi.Schema(type=openapi.TYPE_FILE),
        },
        required=['title', 'format', 'file']
    ),
    responses={
        200: openapi.Response('Success: Document successfully uploaded', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        400: openapi.Response('Bad Request', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        401: openapi.Response('Unauthorized', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        403: openapi.Response('Forbidden', schema=openapi.Schema(type=openapi.TYPE_STRING)),
    }
)
@api_view(['POST'])
def documentUpload(request):

    token=request.COOKIES.get("logintoken")
    payload=authenticateUser(token)
    
    user=User.objects.get(pk=payload['id'])
    request.data['owner']=user.pk
    serializer=DocumentSerializer(data=request.data)
    if serializer.is_valid():
        #serializer.save()
        print("valid")
        return Response({"success":"successfully upload your document"})
    else:
        return Response(serializer.errors)
    


@api_view(['GET'])
def documentDownload(request,document_id):
    
    token=request.COOKIES.get("logintoken")
    payload=authenticateUser(token)
    
    doc=Document.objects.get(id=document_id)
    if not doc:
        return Response({"message":"Document not found"})
    
    user=User.objects.get(pk=payload['id'])
    if doc.owner!=user and user.is_superuser==False:
        return Response({"message":"You do not have permission to download"})
    
    file_path = doc.file.path
    response = FileResponse(open(file_path, 'rb'))
    return response


@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'description': openapi.Schema(type=openapi.TYPE_STRING),
            'format': openapi.Schema(type=openapi.TYPE_STRING),
            'file': openapi.Schema(type=openapi.TYPE_FILE),
        },
        required=[]
    ),
    responses={
        200: openapi.Response('Success: Document metadata updated successfully.', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        400: openapi.Response('Bad Request', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        401: openapi.Response('Unauthorized', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        403: openapi.Response('Forbidden', schema=openapi.Schema(type=openapi.TYPE_STRING)),
    }
)
@api_view(['PUT'])
def documentUpdate(request, document_id):

    token=request.COOKIES.get("logintoken")
    payload=authenticateUser(token)
    
    doc=Document.objects.get(id=document_id)
    if not doc:
        return Response({"message":"Document not found"})
    
    user=User.objects.get(pk=payload['id'])
    if doc.owner!=user and user.is_superuser==False:
        return Response({"message":"You do not have permission to download"})


    serializer = DocumentSerializer(doc, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"success":'Document metadata updated successfully.'})
    else:
        return Response(serializer.errors)



@api_view(['DELETE']) 
def documentDelete(request,document_id):
    token=request.COOKIES.get("logintoken")
    payload=authenticateUser(token)
    
    doc=Document.objects.get(id=document_id)
    if not doc:
        return Response({"message":"Document not found"})
    
    user=User.objects.get(pk=payload['id'])
    if doc.owner!=user and user.is_superuser==False:
        return Response({"message":"You do not have permission to download"})
          
    doc.delete()
    return Response({"success":'Document deleted successfully.'})



from django.db.models import Q

@api_view(['GET'])  
def documentList(request):
    token=request.COOKIES.get("logintoken")
    payload=authenticateUser(token)
    
    user=User.objects.get(id=payload['id'])
    if user.is_superuser==True:
        documents=Document.objects.all()
    else:
        documents=Document.objects.filter(Q(owner=payload['id'])|Q(sharedocument__sharedwith=user))
    serializers=DocumentListSerializer(documents,many=True)
    return Response(serializers.data)
    


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'gmails': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                description='List of email addresses to share the document with'
            ),
        },
        required=['gmails']
    ),
    responses={
        200: openapi.Response('Success: Document successfully shared.', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        400: openapi.Response('Bad Request', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        401: openapi.Response('Unauthorized', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        403: openapi.Response('Forbidden', schema=openapi.Schema(type=openapi.TYPE_STRING)),
    }
)
@api_view(['POST'])
def documentShare(request,document_id):
    token=request.COOKIES.get("logintoken")
    payload=authenticateUser(token)
    
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
                Response({"success":"Successfully your Document has shared"})
            else:
                Response(serializer.errors)




@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'description': openapi.Schema(type=openapi.TYPE_STRING),
            'format': openapi.Schema(type=openapi.TYPE_STRING),
            'upload_date': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=[]
    ),
    responses={
        200: openapi.Response('Success: Document search successful.', schema=openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT))),
        400: openapi.Response('Bad Request', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        401: openapi.Response('Unauthorized', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        403: openapi.Response('Forbidden', schema=openapi.Schema(type=openapi.TYPE_STRING)),
    }
)
@api_view(['POST'])
def searchDocument(request):
    token=request.COOKIES.get("logintoken")
    payload=authenticateUser(token)

    data = request.data
    method = list(data.keys())[0]
    value = data[method]

    if method == 'title':
        documents = Document.objects.filter(Q(owner=payload['id']) & Q(title=value))
    elif method == 'description':
        documents = Document.objects.filter(Q(owner=payload['id']) & Q(description=value))
    elif method == 'format':
        documents = Document.objects.filter(Q(owner=payload['id']) & Q(format=value))
    elif method == 'upload_date':
        documents = Document.objects.filter(Q(owner=payload['id']) & Q(upload_date=value))
    else:
        return Response({'error': 'Invalid search method.'})

    serializers=DocumentListSerializer(documents,many=True)
    return Response(serializers.data)






