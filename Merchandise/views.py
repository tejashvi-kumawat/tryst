from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from users.models import Profile
from Accommodation.models import Accommodation
import os, razorpay
# from Tryst.utils import *

# Create your views here.

@api_view(['POST'])
def merchandise(request):
    if request.user.is_authenticated:
        data = request.data
        if 'details' not in data or 'quantity' not in data or 'paymentProof' not in data:
            return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if int(data['quantity']) > 10:
            return Response({'error': 'Maximum 10 tshirts can be ordered at a time!'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        profile = Profile.objects.get(userId=request.user.username)
        if Order.objects.filter(userId=request.user.username, paymentReceived=False):
            return Response({'error': 'Please wait till your previous order is confirmed'}, status=status.HTTP_409_CONFLICT)
        order = Order.objects.create(userId=request.user.username, details=data['details'], quantity=int(data['quantity']), paymentProof=data['paymentProof'])
        return Response({'message': 'Order Created', 'orderId': order.id}, status=status.HTTP_201_CREATED)
        # client = razorpay.Client(auth=(os.environ['RAZORPAY_KEY'], os.environ['RAZORPAY_KEY_SECRET']))
        # user = Profile.objects.get(userId=request.user.username)
        # amount = 349 * data['quantity']
        # payOrder = client.order.create({'amount': amount*100, 'currency': 'INR', 'payment_capture': '1'})
        # order.orderId = payOrder['id'] ; order.save()
        # # profile = Profile.objects.get(userId=request.user.username)
        # # profile.orders.add(order) ; profile.save()
        # return Response({
        #     'message': 'Order Created', 
        #     'orderId': order.id, 
        #     'options' : {
        #         "key": os.environ['RAZORPAY_KEY'], 
        #         "amount": amount,
        #         "currency": "INR",
        #         "name": "Tryst IIT Delhi",
        #         "description": "Tryst Tshirt for " + user.userId,
        #         "image": "https://www.tryst-iitd.org/static/media/logo.2c01264983bd36cf8463.webp",
        #         "order_id": payOrder['id'],
        #         "notes": {
        #             "Tryst_ID": user.userId,
        #             "email" : user.emailId,
        #             "orderId" : order.id,
        #         },
        #         "theme": { "color": "#041429" },
        #     },
        # }, status=status.HTTP_201_CREATED)
    return Response({'error': 'User not logged in'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def confirmMerchandise(request):
    if request.user.is_authenticated:
        data = request.data
        if 'status' not in data or 'orderId' not in data:
            return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not Order.objects.filter(id=data['orderId']):
            return Response({'error': 'No order found'}, status=status.HTTP_404_NOT_FOUND)
        order = Order.objects.get(id=data['orderId'])
        if data['status'] == 'confirm':
            if not 'paymentId' in data:
                return Response({'error': 'Invalid fields'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if Order.objects.filter(paymentId=data['paymentId']) or Accommodation.objects.filter(paymentId=data['paymentId']):
                return Response({'error': 'Payment already done'}, status=status.HTTP_409_CONFLICT)
            client = razorpay.Client(auth=(os.environ['RAZORPAY_KEY'], os.environ['RAZORPAY_KEY_SECRET']))
            try: paymentData = client.payment.fetch(data['paymentId'])
            except: return Response({'error': 'Payment not captured'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if paymentData['status'] != 'captured' or paymentData['order_id'] != order.orderId:
                return Response({'error': 'Payment not captured'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            order.paymentId = data['paymentId']
            confOrders = Order.objects.filter(paymentReceived=True).order_by('-id')
            if not confOrders:
                order.lot = 1
            else:
                lastOrder = confOrders[0]
                order.lot = lastOrder.lot + lastOrder.quantity
            order.paymentReceived = True ; order.save()
            profile = Profile.objects.get(userId=request.user.username)
            profile.orders.add(order) ; profile.save()
            send_tshirt(order.orderDate, profile.userId, order.quantity, order.lot, order.paymentId, 349 * order.quantity, profile.emailId)
            return Response({'message': 'Order confirmed'}, status=status.HTTP_200_OK)
        else:
            order.delete()
            return Response({'message': 'Order cancelled'}, status=status.HTTP_200_OK)
    return Response({'error': 'User not logged in'}, status=status.HTTP_401_UNAUTHORIZED)