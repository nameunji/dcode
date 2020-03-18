import jwt
import json
from django.http       import JsonResponse
from wemakers.settings import SECRET_KEY 
from .models           import Users



def login_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            auth_token = request.headers.get('Authorization')
            payload = jwt.decode(auth_token, SECRET_KEY, algorithm='HS256')
            user = Users.objects.get(id=payload["id"])
            request.user = user
            return func(self, request, *args, **kwargs)
        except Users.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'}, status = 400)
        except TypeError:
            return JsonResponse({'message':'INVALID_VALUE'}, status = 400)
        except KeyError:
            return JsonResponse({'message': 'INVALID'}, status = 400)
        
    return wrapper


