from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from users.models import *
from Merchandise.models import *
import json
import datetime
import razorpay
from django.views.decorators.csrf import csrf_exempt
from utils_accomodation.mailer import send_accomodation_email


@api_view(['POST'])
def accommodation(request):
    if request.user.is_authenticated:
        user = Profile.objects.get(user_ID=request.user.username)
        data = request.data
        if 'checkin' not in data or 'checkout' not in data or 'men' not in data or 'women' not in data or 'memberDetails' not in data:
            return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if len(data['memberDetails']) > 20:
            return Response({'error': 'Maximum 20 bookings can be made at a time!'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        men = int(Variable.objects.get(name="men").value)
        women = int(Variable.objects.get(name="women").value)
        data['men'] = int(data['men'])
        data['women'] = int(data['women'])
        if data['men'] > men or data['women'] > women:
            return Response({'error': 'Not enough seats available!'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        var = False
        for member in data['memberDetails']:
            if 'trystUID' not in member or 'name' not in member or 'aadhar' not in member:
                return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not Profile.objects.filter(user_ID=member['trystUID']):
                return Response({'error': f'No member with trystUID {member["trystUID"]} found'}, status=status.HTTP_404_NOT_FOUND)
            profile = Profile.objects.get(user_ID=member['trystUID'])
            if profile.accomodation:
                return Response({'error': f'User {member["trystUID"]} is already booked'}, status=status.HTTP_409_CONFLICT)
            if profile.user_ID == request.user.username:
                var = True
        if not var:
            return Response({'error': 'You must be a member of the booking'}, status=status.HTTP_401_UNAUTHORIZED)
        acc_members = []
        for member in data['memberDetails']:
            profile = Profile.objects.get(user_ID=member['trystUID'])
            acc_members.append(profile.user_ID)
        acc = Accommodation.objects.create(bookedBy=user.user_ID, checkInDate=data['checkin'], checkOutDate=data['checkout'], men=data[
                                           'men'], women=data['women'], memberDetails=data['memberDetails'])
        d1 = datetime.datetime.strptime(data['checkin'], '%Y-%m-%d')
        d2 = datetime.datetime.strptime(data['checkout'], '%Y-%m-%d')
        days = max((d2-d1).days, 1)
        people = len(data['memberDetails'])
        amount = 750 * days * people
        client = razorpay.Client(
            auth=('rzp_live_xWt5saWhXdyfTL', 'GDaAi7w6dUBDo5euSo8yf8DZ'))
        order = client.order.create(
            {'amount': amount*100, 'currency': 'INR', 'payment_capture': '1'})
        acc.orderId = order['id']
        acc.amount = amount
        acc.save()
        return Response({
            'message': 'Accommodation created',
            'accommodation_id': acc.orderId,
            'options': {
                "key": 'rzp_live_xWt5saWhXdyfTL',
                "amount": amount,
                "currency": "INR",
                "name": "Tryst IIT Delhi",
                "description": "Tryst Accommodation for " + user.user_ID,
                "image": "https://www.tryst-iitd.org/assets/tryst-favicon-Bjmus4BO.png",
                "order_id": order['id'],
                "notes": {
                    "Tryst_ID": user.user_ID,
                    "Name": user.name,
                    "email": user.email_ID,
                    "accommodation_id": acc.orderId
                },
                "theme": {"color": "#041429"},
            },
            'members': acc_members,
        }, status=status.HTTP_201_CREATED)
    return Response({'error': 'User not logged in'}, status=status.HTTP_401_UNAUTHORIZED)


@csrf_exempt
@api_view(['POST'])
def verify_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        razorpay_order_id = data['razorpay_order_id']
        razorpay_payment_id = data['razorpay_payment_id']
        razorpay_signature = data['razorpay_signature']
        members = data['members']
        try:
            client = razorpay.Client(
                auth=('rzp_live_xWt5saWhXdyfTL', 'GDaAi7w6dUBDo5euSo8yf8DZ')).utility.verify_payment_signature({
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature
                })
            if client:
                acc = Accommodation.objects.get(orderId=razorpay_order_id)
                acc.paymentReceived = True
                acc.paymentId = razorpay_payment_id
                acc.save()
                for member in members:
                    profile = Profile.objects.get(user_ID=member)
                    profile.accomodation = True
                    profile.save()
                profile = Profile.objects.get(user_ID=acc.bookedBy)
                send_accomodation_email(profile.email_ID, profile.name, acc.amount, acc.orderId,
                                        acc.paymentId, acc.checkInDate, acc.checkOutDate, acc.men, acc.women)
                men_variable = Variable.objects.get(name="men")
                men_variable.value = int(men_variable.value) - acc.men
                men_variable.save()

                women_variable = Variable.objects.get(name="women")
                women_variable.value = int(women_variable.value) - acc.women
                women_variable.save()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except razorpay.errors.SignatureVerificationError as e:
            return Response({'status': 'failure', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def cancel_order(request):
    if request.user.is_authenticated:
        user = Profile.objects.get(user_ID=request.user.username)
        Accommodation.objects.filter(bookedBy=user.user_ID).delete()
        return Response({'message': 'Order cancelled'}, status=status.HTTP_200_OK)
    return Response({'error': 'User not logged in'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def get_accommodation(request):
    if request.user.is_authenticated:
        user = Profile.objects.get(user_ID=request.user.username)
        if not user.accomodation:
            return Response({'error': 'User has not booked accommodation'}, status=status.HTTP_404_NOT_FOUND)
        for acc in Accommodation.objects.all():
            for member in acc.memberDetails:
                if member['trystUID'] == user.user_ID:
                    print('done')
