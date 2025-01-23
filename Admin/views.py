from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from event.models import *
from users.models import *
from django.http import HttpResponse
import csv
from datetime import timedelta
from Accommodation.models import Accommodation, Variable
from Merchandise.models import Order
from .scripts import imgproc
from passes.models import *
# from Tryst.utils import *
import json
from users.views import generateUserId

# Create your views here.

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}

@api_view(['GET'])
def dump(request):
    if not request.user.is_staff:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    p = Profile.objects.all()
    e = Event.objects.all().values()
    r = Registration.objects.all().values()
    w = Wize.objects.all().values()
    out = []
    for profile in p:
        college = College.objects.get(collegeId=profile.collegeId)
        orders = profile.orders.all().values()
        events = profile.registeredEvents.all().values()
        photo = profile.photo.url if profile.photo else None
        if profile.accommodation:
            accommodationBooker = profile.accommodationBooker
            acc = Accommodation.objects.filter(bookedBy=accommodationBooker).values('id', 'bookedBy', 'checkInDate', 'checkOutDate', 'men', 'women', 'memberDetails')[0]
        else: acc = None
        out.append({'userId': profile.userId, 'name': profile.name, 'email': profile.emailId, 'phone': profile.phoneNumber, 'photo': photo, 'collegeName': college.name, 'collegeState': college.state, 'collegeCity': college.city, 'accommodation': profile.accommodation, 'accomodationDetails': acc, 'orders': orders, 'registeredEvents': events, 'isStaff': request.user.is_staff})
    return Response({'profiles': p.values(), 'events': e, 'registration': r, 'wize': w, 'out': out}, status=status.HTTP_200_OK)

@api_view(['GET'])
def details(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            user = request.user
            return Response({'name': f'{user.first_name} {user.last_name}', 'email': user.email}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User is not a staff member'}, status=status.HTTP_403_FORBIDDEN)
    else:
        return Response({'message': 'Not logged in'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'POST'])
def login(request):
    if request.user.is_authenticated:
        return Response({'error': 'Already logged in'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    data = request.data
    if 'email' not in data or 'password' not in data:
        return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if not User.objects.filter(email=data['email']).exists():
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    user = User.objects.get(email=data['email'])
    if not user.is_staff and not user.username == 'tshirt':
        return Response({'error': 'User is not a staff member'}, status=status.HTTP_403_FORBIDDEN)
    if not user.check_password(data['password']):
        return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'message': 'Logged in', 'tokens': get_tokens_for_user(user)}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def events(request):
    if request.method == 'GET':
        if request.user.is_staff:
            category = request.GET.get('category')
            events = Event.objects.filter(category=category).values()
            return Response(events, status=status.HTTP_200_OK)
        return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'POST':
        if request.user.is_staff:
            data = request.data
            if 'category' not in data or 'poster' not in data or 'name' not in data or 'info' not in data or 'rules' not in data or 'start' not in data or 'location' not in data or 'formLink' not in data:
                return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if 'club' not in data and data['category'] == "Competitions":
                return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if 'end' in data: end = data['end']
            else: end = None
            if 'contact' in data: contact = data['contact']
            else: contact = None
            imgproc.compress(data['poster'])
            Event.objects.create(category=data['category'], name=data['name'], poster=data['poster'], info=data['info'], rules=data['rules'], start=data['start'], end=end, location=data['location'], contact=contact, formLink=data['formLink'], club=data['club'])
            return Response({'message': 'Event created'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'PUT':
        if request.user.is_staff:
            data = request.data
            if 'id' not in data or 'category' not in data or 'name' not in data or 'info' not in data or 'rules' not in data or 'start' not in data or 'location' not in data or 'formLink' not in data:
                return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not Event.objects.filter(id=data['id']).exists():
                return Response({'error': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)
            if 'club' not in data and data['category'] == "Competitions":
                return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if 'end' in data: end = data['end']
            else: end = None
            if 'contact' in data: contact = data['contact']
            else: contact = None
            event = Event.objects.get(id=data['id'])
            # if 'poster' in data:
            #     event.poster = data['poster']
            event.category = data['category']
            event.name = data['name']
            event.info = data['info']
            event.rules = data['rules']
            event.start = data['start']
            event.end = end
            event.location = data['location']
            event.contact = contact
            event.formLink = data['formLink']
            event.club = data['club']
            event.save()
            return Response({'message': 'Event updated'}, status=status.HTTP_200_OK)
        return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'DELETE':
        if request.user.is_staff:
            data = request.data
            if 'id' not in data:
                return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not Event.objects.filter(id=data['id']).exists():
                return Response({'error': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)
            Event.objects.get(id=data['id']).delete()
            return Response({'message': 'Event deleted'}, status=status.HTTP_200_OK)
        return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)
    
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def speaker(request):
    if request.method == 'GET':
        if request.user.is_staff:
            speakers = Speaker.objects.all().values()
            return Response(speakers, status=status.HTTP_200_OK)
        return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'POST':
        if request.user.is_staff:
            data = request.data
            if 'name' not in data or 'image' not in data or 'designation' not in data or 'about' not in data:
                return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            Speaker.objects.create(name=data['name'], image=data['image'], designation=data['designation'], about=data['about'])
            return Response({'message': 'Speaker created'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'PUT':
        if request.user.is_staff:
            data = request.data
            if 'id' not in data or 'name' not in data or 'designation' not in data or 'about' not in data:
                return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not Speaker.objects.filter(id=data['id']).exists():
                return Response({'error': 'Speaker does not exist'}, status=status.HTTP_404_NOT_FOUND)
            speaker = Speaker.objects.get(id=data['id'])
            # if 'image' in data:
            #     speaker.image = data['image']
            speaker.name = data['name']
            speaker.designation = data['designation']
            speaker.about = data['about']
            speaker.save()
            return Response({'message': 'Speaker updated'}, status=status.HTTP_200_OK)
        return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'DELETE':
        if request.user.is_staff:
            data = request.data
            if 'id' not in data:
                return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not Speaker.objects.filter(id=data['id']).exists():
                return Response({'error': 'Speaker does not exist'}, status=status.HTTP_404_NOT_FOUND)
            speaker = Speaker.objects.get(id=data['id'])
            speaker.delete()
            return Response({'message': 'Speaker deleted'}, status=status.HTTP_200_OK)
        return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['PUT'])
def updatePoster(request):
    if request.user.is_staff:
        if 'poster' not in request.data or 'id' not in request.data:
            return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not Event.objects.filter(id=request.data['id']).exists():
            return Response({'error': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)
        event = Event.objects.get(id=request.data['id'])
        event.poster = request.data['poster']
        event.save()
        return Response({'message': 'Poster updated'}, status=status.HTTP_200_OK)
    return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['PUT'])
def updateImage(request):
    if request.user.is_staff:
        if 'image' not in request.data or 'id' not in request.data:
            return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not Speaker.objects.filter(id=request.data['id']).exists():
            return Response({'error': 'Speaker does not exist'}, status=status.HTTP_404_NOT_FOUND)
        speaker = Speaker.objects.get(id=request.data['id'])
        speaker.image = request.data['image']
        speaker.save()
        return Response({'message': 'Image updated'}, status=status.HTTP_200_OK)
    return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def download(request):
    if request.user.is_staff:
        eventId = request.GET.get('id')
        if not Event.objects.filter(id=eventId).exists():
            return Response({'error': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)
        event = Event.objects.get(id=eventId)
        registrations = Registration.objects.filter(eventId=eventId).order_by('id')
        response = HttpResponse(content_type='text/csv', headers={'Content-Disposition': 'attachment; filename=f"{event.name} Registrations.csv"'})
        writer = csv.writer(response)
        i = 1
        writer.writerow([
            'Team ID', 'Tryst ID', 'Name', 'Email', 'Phone', 
            'College', 'State', 'City',
            'Date and Time of Registration', 
        ])
        colleges = College.objects.all()
        cid = {}
        for c in colleges: cid[c.collegeId] = [c.name, c.state, c.city]
        profiles = Profile.objects.filter(emailVerified=True)
        pfiles = {}
        for p in profiles: pfiles[p.userId] = [p.name, p.emailId, p.phoneNumber, p.collegeId]
        for registration in registrations:
            team = registration.team ; team = team.split(',')
            for member in team:
                try: profile = pfiles[member]
                except: continue
                c = cid[profile[3]]
                writer.writerow([
                    i, member, profile[0], profile[1], profile[2], 
                    c[0], c[1], c[2],
                    str(registration.timestamp+timedelta(hours=5, minutes=30)).split('+')[0],
                ])
            i += 1
        return response
    return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def accDownload(request):
    if request.user.is_staff:
        acc = Accommodation.objects.filter(paymentReceived=True)
        response = HttpResponse(content_type='text/csv', headers={'Content-Disposition': 'attachment; filename=f"Accommodation Bookings.csv"'})
        writer = csv.writer(response)
        writer.writerow([
            'Tryst ID', 'Name', 'Name (as on aadhar)', 'Aadhar', 'Email', 'Phone', 
            'College', 'State', 'City',
            'Check In Date', 'Check Out Date', 'Booked By'
        ])
        colleges = College.objects.all()
        cid = {}
        for c in colleges: cid[c.collegeId] = [c.name, c.state, c.city]
        profiles = Profile.objects.filter(accommodation=True)
        pfiles = {}
        for p in profiles: pfiles[p.userId] = [p.name, p.emailId, p.phoneNumber, p.collegeId]
        accommodations = Accommodation.objects.filter(paymentReceived=True)
        for acc in accommodations:
            for member in acc.memberDetails.values():
                profile = pfiles[member['userId']]
                c = cid[profile[3]]
                writer.writerow([
                    member['userId'], profile[0], member['name'], member['aadhar'], profile[1], profile[2], 
                    c[0], c[1], c[2],
                    acc.checkInDate, acc.checkOutDate, f"{pfiles[acc.bookedBy][0]} ({acc.bookedBy})"
                ])
        return response
    return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def merchDownload(request):
    if request.user.is_staff or request.user.username == 'tshirt':
        response = HttpResponse(content_type='text/csv', headers={'Content-Disposition': 'attachment; filename=f"Accommodation Bookings.csv"'})
        writer = csv.writer(response)
        writer.writerow([
            'Lot', 'Tryst ID', 'Name', 'Size', 'Name on T-Shirt', 'Phone'
        ])
        profiles = Profile.objects.filter()
        pfiles = {}
        for p in profiles: pfiles[p.userId] = [p.name, p.phoneNumber]
        orders = Order.objects.filter(paymentReceived=True).order_by('lot')
        for order in orders:
            i = 0
            profile = pfiles[order.userId]
            if type(order.details) == str:
                order.details = json.loads(order.details)
            for k,tshirt in order.details.items():
                writer.writerow([
                    order.lot + i, order.userId, profile[0], tshirt['size'], tshirt['name'], profile[1]
                ])
                i += 1
        return response
    return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def merchDownloadInternal(request):
    if request.user.is_staff:
        response = HttpResponse(content_type='text/csv', headers={'Content-Disposition': 'attachment; filename=f"Accommodation Bookings.csv"'})
        writer = csv.writer(response)
        writer.writerow([
            'Tryst ID', 'Name', 'Size', 'Name on T-Shirt', 'Phone', 'Screenshot Link'
        ])
        profiles = Profile.objects.filter()
        pfiles = {}
        for p in profiles: pfiles[p.userId] = [p.name, p.phoneNumber]
        orders = Order.objects.filter()
        for order in orders:
            i = 0
            profile = pfiles[order.userId]
            if type(order.details) == str:
                order.details = json.loads(order.details)
            for k,tshirt in order.details.items():
                writer.writerow([
                    order.userId, profile[0], tshirt['size'], tshirt['name'], profile[1], f"https://tryst-bucket.s3.ap-south-1.amazonaws.com/{order.paymentProof}"
                ])
                i += 1
        return response
    return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def accConfirm(request):
    if request.user.is_staff:
        data = request.data
        if 'status' not in data or 'accommodationId' not in data:
            return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not Accommodation.objects.filter(id=data['accommodationId']):
            return Response({'error': 'No accommodation found'}, status=status.HTTP_404_NOT_FOUND)
        acc = Accommodation.objects.get(id=data['accommodationId'])
        if data['status'] == 'confirm':
            acc.paymentReceived = True ; acc.save()
            men = Variable.objects.get(name="men") ; women = Variable.objects.get(name="women")
            men.value = int(men.value) - int(acc.men) ; women.value = int(women.value) - int(acc.women)
            men.save() ; women.save()
            booker = Profile.objects.get(userId=acc.bookedBy)
            emails = []
            for key,member in acc.memberDetails.items():
                profile = Profile.objects.get(userId=member['userId'])
                profile.accommodationBooker = acc.bookedBy
                profile.accommodation = True ; profile.save()
                Accommodation.objects.filter(bookedBy=member['userId'], paymentReceived=False).delete()
                emails.append(profile.emailId)
            send_accommodation(booker.name, 769 * (acc.men + acc.women), acc.id, acc.paymentId, acc.checkInDate, acc.checkOutDate, acc.men, acc.women, emails)
            return Response({'message': 'Accommodation confirmed'}, status=status.HTTP_200_OK)
        else:
            acc.delete()
            return Response({'message': 'Accommodation cancelled'}, status=status.HTTP_200_OK)
    return Response({'error': 'Not a staff member'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def accommodation(request):
    if request.user.is_staff:
        accommodations = Accommodation.objects.all().values('id', 'bookedBy', 'checkInDate', 'checkOutDate', 'men', 'women', 'memberDetails', 'paymentReceived', 'paymentProof').order_by('paymentReceived', '-id')
        profiles = Profile.objects.all()
        pfiles = {}
        for p in profiles: pfiles[p.userId] = [p.userId, p.name, p.emailId, p.phoneNumber]
        for acc in accommodations:
            acc['bookedBy'] = pfiles[acc['bookedBy']]
            acc['memberDetails'] = [pfiles[member['userId']] for key,member in acc['memberDetails'].items()]
        return Response(accommodations)
    return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def merchConfirm(request):
    if request.user.username == 'tshirt':
        data = request.data
        if 'status' not in data or 'orderId' not in data:
            return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not Order.objects.filter(id=data['orderId']):
            return Response({'error': 'No order found'}, status=status.HTTP_404_NOT_FOUND)
        order = Order.objects.get(id=data['orderId'])
        if data['status'] == 'confirm':
            confOrders = Order.objects.filter(paymentReceived=True).order_by('-id')
            if not confOrders:
                order.lot = 1
            else:
                lastOrder = confOrders[0]
                order.lot = lastOrder.lot + lastOrder.quantity
            order.paymentReceived = True ; order.save()
            profile = Profile.objects.get(userId=order.userId)
            profile.orders.add(order) ; profile.save()
            send_tshirt(order.orderDate, profile.userId, order.quantity, order.lot, order.paymentId, 349 * order.quantity, profile.emailId)
            return Response({'message': 'Order confirmed'}, status=status.HTTP_200_OK)
        else:
            order.delete()
            return Response({'message': 'Order cancelled'}, status=status.HTTP_200_OK)
    return Response({'error': 'Not a staff member'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def merchandise(request):
    if request.user.username == 'tshirt':
        merchandise = Order.objects.all().values('id', 'userId', 'quantity', 'details', 'paymentReceived', 'paymentProof').order_by('paymentReceived', '-id')
        profiles = Profile.objects.all()
        pfiles = {}
        for p in profiles: pfiles[p.userId] = [p.userId, p.name, p.emailId, p.phoneNumber]
        for merch in merchandise:
            merch['user'] = pfiles[merch['userId']]
            del merch['userId']
        return Response(merchandise)
    return Response({'error': 'Not a staff member'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def passes(request):
    if request.user.is_staff:
        data = request.data
        if 'code' not in data:
            return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not Pass.objects.filter(code=data['code']):
            return Response({'error': 'No pass found'}, status=status.HTTP_404_NOT_FOUND)
        pass_ = Pass.objects.filter(code=data['code']).values()
        return Response(pass_[0], status=status.HTTP_200_OK)
    return Response({'error': 'Not a staff member'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def enterPasses(request):
    if request.user.is_staff:
        data = request.data
        if 'code' not in data:
            return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not Pass.objects.filter(code=data['code']):
            return Response({'error': 'No pass found'}, status=status.HTTP_404_NOT_FOUND)
        pass_ = Pass.objects.get(code=data['code'])
        if pass_.entry:
            return Response({'error': 'Pass already used', 'time': pass_.entryTime}, status=status.HTTP_400_BAD_REQUEST)
        pass_.entry = True ; pass_.save()
        return Response({'message': 'Entry successful'}, status=status.HTTP_200_OK)
    return Response({'error': 'Not a staff member'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def internalPass(request):
    if request.user.username == 'T23H000002':
        data = request.data
        if 'userId' not in data:
            if 'name' not in data or 'email' not in data:
                return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            userId = generateUserId(data['name'])
            Profile.objects.create(userId=userId, name=data['name'], emailId=data['email'], collegeId=4570, phoneNumber="9999999999", emailVerified=True)
            User.objects.create(username=userId)
            p = Pass.objects.create(userId=userId, slotId=23)
            slot = Slot.objects.get(id=23)
            slot.capacity -= 1 ; slot.save()
            return Response({'message': 'Pass created', 'code': p.code}, status=status.HTTP_200_OK)
        if not Profile.objects.filter(userId=data['userId']):
            return Response({'error': 'No user found'}, status=status.HTTP_404_NOT_FOUND)
        profile = Profile.objects.get(userId=data['userId'])
        p = Pass.objects.create(userId=profile.userId, slotId=23)
        slot = Slot.objects.get(id=23)
        slot.capacity -= 1 ; slot.save()
        return Response({'message': 'Pass created', 'code': p.code}, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_404_NOT_FOUND)

# @api_view(['POST'])
# def internalPassSend(request):
#     if request.user.username == 'T23H000002':
#         data = request.data
#         if 'code' not in data or 'pass' not in data:
#             return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
#         if not Pass.objects.filter(code=data['code']):
#             return Response({'error': 'No pass found'}, status=status.HTTP_404_NOT_FOUND)
#         pass_ = Pass.objects.get(code=data['code'])
#         profile = Profile.objects.get(userId=pass_.userId)
#         pass_ = data['pass'].read()
#         # send_pass(pass_, profile.name, profile.emailId)
#         return Response({'message': 'Pass sent'}, status=status.HTTP_200_OK)
#     return Response(status=status.HTTP_404_NOT_FOUND)

# @api_view(['GET'])
# def downloadPassData(request):
#         passes = Pass.objects.all().values()
#         if not passes: return Response({'error': 'No passes found'}, status=status.HTTP_404_NOT_FOUND)
#         response = HttpResponse(content_type='text/csv', headers={'Content-Disposition': 'attachment; filename=f"Pronites.csv"'})
#         writer = csv.writer(response)
#         writer.writerow(['Name', 'Email'])
#         profiles = Profile.objects.all()
#         pfiles = {}
#         for p in profiles: pfiles[p.userId] = [p.name, p.emailId]
#         i = 0
#         for pass_ in passes:
#             try: writer.writerow(pfiles[pass_['userId']][:2])
#             except: print(pass_['userId']) ; continue
#         return response
#     # return Response({'error': 'User not staff'}, status=status.HTTP_401_UNAUTHORIZED)