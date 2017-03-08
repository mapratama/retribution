from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import login, logout

from rumahtotok.api.response import ErrorResponse
from rumahtotok.api.views import RumahtotokAPIView, SessionAPIView
from rumahtotok.apps.orders.models import Order
from rumahtotok.core.serializers import (serialize_order, serialize_user)

from rumahtotok.core.utils import force_login
from rest_framework.views import APIView

from .forms import RegisterForm, LoginForm, GetConfirmationCodeForm, ResetPasswordForm


class Login(APIView):

    def post(self, request):
        response = {
            "user": {
                "id": 1,
                "email": "test@gmail.com",
                "name": "test",
                "phone": "087829976921",
                "city": "Jakarta",
                "address": "Jalan ampasit 6 no 12",
                "image_url": "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQ9M2S-BNaiMXe8Yyl9gtBkOWW95TIEVvyzm-Dq-0zO8lQYgAny",
                "balance": 65000,
            },
            "faqs": [
                {
                    "id": 1,
                    "question": "Bagaimana cara topup?",
                    "answer": "Dengan menklik tombol dan ..."
                },
                {
                    "id": 2,
                    "question": "Bagaimana cara beli voucher?",
                    "answer": "Dengan menklik tombol dan ..."
                }
            ],
            "banners": [
                {
                    "id": 1,
                    "banner_url": "https://media.stamps.co.id/thumb/header_photos/banner-960x384_size_960x384.jpg",
                    "link": "http://anomalicoffee.com/",
                    "id_voucher": 1,
                },
                {
                    "id": 2,
                    "banner_url": "https://media.stamps.co.id/thumb/header_photos/cab1bab0-198a-4576-95d3-127accf3906a_size_960x384.jpg",
                    "link": "http://prodia.com",
                    "id_voucher": 2,
                }
            ],
            "banks": [
                {
                    "id": 1,
                    "nama": "BCA",
                    "nomor_rekening": "1234567EFGH",
                    "nama_rekening": "promosee account",
                    "logo_url": "http://2.bp.blogspot.com/-qcuWjD9yNOU/VhrB1mFQh2I/AAAAAAAAA9s/MdgX4itheE8/s1600/klikbca%2Bkurs%252CSitus%2BBank%2BBCA%252CSitus%2BBank%2BBRI%252Ctentang%2Bbca%252Cwww.bank%2Bbca.com%252Cwww.bca.co.id%252C.jpg",
                },
                {
                    "id": 2,
                    "nama": "BNI",
                    "nomor_rekening": "456789KLMNOP",
                    "nama_rekening": "promosee account",
                    "logo_url": "http://2.bp.blogspot.com/-GH45sfgfuJo/VhrTDrv8tLI/AAAAAAAABAs/YdYqPomeO1E/s1600/Bank%2BBNI%2BInternet%2BBanking%252C%2Bbank%2Bbri%252C%2Bbank%2Bmandiri%252C%2BBank%2BMandiri%2BInternet%2BBanking%252C%2Bbni%2Binternet%2Bbanking%252C.jpg",
                }
            ],
            "news_events": [
                {
                    "id": 1,
                    "title": "Birthday Promotion",
                    "subject": "Anomali Coffee",
                    "image_url": "https://media.stamps.co.id/thumb/voucher_templates/2015/12/16/f5rcdj5y6nrqwrxqvckh3t_size_440.png",
                    "description": "Celebrate your birthday at Anomali and get free pastry/cake with any purchase.",
                    "id_voucher": 1,
                },
                {
                    "id": 2,
                    "title": "Signin Promotion",
                    "subject": "Zap Laundry",
                    "image_url": "https://media.stamps.co.id/thumb/voucher_templates/2014/7/6/fae166e7-c019-4431-a1ef-94934394e7fc_size_440.jpg",
                    "description": "Register your email on stamps.co.id/register and present your email to our staff to take advantage of this discount.",
                    "id_voucher": 2,
                }
            ],
            "categories": [
                {
                    "id": 1,
                    "name": "Food & Beverages",
                    "image_url": "https://media.stamps.co.id/thumb/rewards_photo/2015/3/31/c6rm3rsihge83pbjovyyzm_size_440.jpg",
                    "order_id": 1,
                    "tenants": [
                        {
                            "id": 1,
                            "code": "ANOMALI808",
                            "name": "Anomali Coffee",
                            "type": "offline",
                            "phone": "+62 21 3106370",
                            "address": "Jl Teuku Cik Ditiro no 52 Menteng, Jakarta Pusat",
                            "email": "anomali@mail.com",
                            "website_url": "http://anomalicoffee.com/",
                            "order_id": 1,
                            "logo_url": "https://media.stamps.co.id/thumb/merchant_logos/2014/4/2/logo_size_188.png",
                            "banner_url": "https://media.stamps.co.id/thumb/header_photos/banner-960x384_size_960x384.jpg",
                            "locations": [
                                {
                                    "id": 1,
                                    "name": "Kelapa Gading",
                                    "address": "Jalan Kelapa Gading Selatan No 2",
                                    "latitude": -6.167372,
                                    "longitude": 106.813419,
                                },
                                {
                                    "id": 2,
                                    "name": "Blok M",
                                    "address": "Jalan Blok M Selatan No 2",
                                    "latitude": -6.167159,
                                    "longitude": 106.798656,
                                }
                            ]
                        },
                    ]

                },
                {
                    "id": 2,
                    "name": "Home Services",
                    "image_url": "https://media.stamps.co.id/thumb/rewards_photo/2014/7/6/3606f0ab-8721-4e07-b349-75984d5b5ddb_size_440.jpg",
                    "order_id": 2,
                    "tenants": [
                        {
                            "id": 2,
                            "code": "ZAP989",
                            "name": "Zap Laundry",
                            "type": "online",
                            "phone": "021456789",
                            "address": "Royal Mediterania Garden Residences Tower Royal Marigold Lt B1 Unit SH10",
                            "email": "zap@mail.com",
                            "website_url": "http://www.zaplaundry.com/",
                            "order_id": 2,
                            "logo_url": "https://media.stamps.co.id/thumb/merchant_logos/2014/6/25/9206d1f2-7c10-45e6-8d01-896a673e89f7_size_188.jpg",
                            "banner_url": "https://media.stamps.co.id/thumb/header_photos/cab1bab0-198a-4576-95d3-127accf3906a_size_960x384.jpg",
                            "locations": [
                                {
                                    "id": 3,
                                    "name": "Kebon Jeruk",
                                    "address": "Jalan Kebon Jeruk Selatan No 2",
                                    "latitude": -6.181234,
                                    "longitude": 106.813562,
                                },
                                {
                                    "id": 4,
                                    "name": "Menteng",
                                    "address": "Jalan Menteng Selatan No 2",
                                    "latitude": -6.582911,
                                    "longitude": 106.787769,
                                }
                            ]
                        },
                    ]

                }
            ],
            "vouchers": [
                {
                    "id": 1,
                    "name": "Free Pastry or Cake",
                    "subject": "Free Pastry or Cake",
                    "description": "Celebrate your birthday get free pastry/cake.",
                    "price": 1000,
                    "id_tenant": 1,
                    "start_date": "2017-02-02",
                    "end_date": "2017-04-04",
                    "voucher_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2015/3/31/zcipyp6flavopadxupnuux_size_440.jpg",
                    "slide_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2015/3/31/zcipyp6flavopadxupnuux_size_440.jpg",
                    "big_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2015/3/31/zcipyp6flavopadxupnuux_size_440.jpg",
                    "min_payment": 500,
                    "redeem_code": "PASTRY456",
                },
                {
                    "id": 2,
                    "name": "Buy 1 Get 1",
                    "subject": "Buy 1 Get 1",
                    "description": "Become an Anomali Coffee member and enjoy Buy 1 Get 1, drinks only!",
                    "price": 1500,
                    "id_tenant": 1,
                    "start_date": "2017-03-02",
                    "end_date": "2017-04-11",
                    "voucher_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2016/8/2/7zxqpzwkttx8vryynkuukr_size_440.jpg",
                    "slide_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2016/8/2/7zxqpzwkttx8vryynkuukr_size_440.jpg",
                    "big_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2016/8/2/7zxqpzwkttx8vryynkuukr_size_440.jpg",
                    "min_payment": 800,
                    "redeem_code": "BUY1GET1",
                },
                {
                    "id": 3,
                    "name": "Chicken Fried Rice",
                    "subject": "Chicken Fried Rice",
                    "description": "Get Chicken Fried Rice for your lunch today",
                    "price": 2300,
                    "id_tenant": 1,
                    "start_date": "2017-01-02",
                    "end_date": "2017-03-20",
                    "voucher_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2016/8/2/ssnjsz2cu3bhug4xa6zfnl_size_440.jpg",
                    "slide_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2016/8/2/ssnjsz2cu3bhug4xa6zfnl_size_440.jpg",
                    "big_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2016/8/2/ssnjsz2cu3bhug4xa6zfnl_size_440.jpg",
                    "min_payment": 600,
                    "redeem_code": "CHICKEN456",
                },
                {
                    "id": 4,
                    "name": "Black Coffee / Tea",
                    "subject": "Black Coffee / Tea",
                    "description": "Minimum purchase 20000 get free Black Coffee / Tea",
                    "price": 2500,
                    "id_tenant": 1,
                    "start_date": "2017-01-02",
                    "end_date": "2017-05-08",
                    "voucher_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2015/3/31/ydn5c3aeuplswefsnheud3_size_440.jpg",
                    "slide_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2015/3/31/ydn5c3aeuplswefsnheud3_size_440.jpg",
                    "big_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2015/3/31/ydn5c3aeuplswefsnheud3_size_440.jpg",
                    "min_payment": 500,
                    "redeem_code": "BLACK444",
                },
                {
                    "id": 5,
                    "name": "Free Wash and Dry",
                    "subject": "Free Wash and Dry",
                    "description": "Get a FREE Self Service Wash & Dry",
                    "price": 4000,
                    "id_tenant": 2,
                    "start_date": "2017-02-02",
                    "end_date": "2017-03-20",
                    "voucher_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2014/7/5/0712ac88-f18d-414d-8afe-628a00702081_size_440.jpg",
                    "slide_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2014/7/5/0712ac88-f18d-414d-8afe-628a00702081_size_440.jpg",
                    "big_image_url": "https://media.stamps.co.id/thumb/rewards_photo/2014/7/5/0712ac88-f18d-414d-8afe-628a00702081_size_440.jpg",
                    "min_payment": 900,
                    "redeem_code": "WASHANDDRY03",
                }
            ],
        }
        return Response(response, status=status.HTTP_200_OK)


class Register(APIView):

    def post(self, request):
        print request.data


class Logout(SessionAPIView):

    def post(self, request):
        user = request.user
        user.gcm_key = ""
        user.save()

        logout(request)

        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class GetConfirmationCode(RumahtotokAPIView):

    def post(self, request):
        form = GetConfirmationCodeForm(data=request.data)
        if form.is_valid():
            form.send_confirmation_code()
            response = {
                'mobile_number': form.cleaned_data['mobile_number']
            }
            return Response(response, status=status.HTTP_200_OK)

        return ErrorResponse(form=form)


class ResetPassword(RumahtotokAPIView):

    def post(self, request):
        form = ResetPasswordForm(data=request.data)
        if form.is_valid():
            form.save()
            return Response({'status': 'oke'}, status=status.HTTP_200_OK)

        return ErrorResponse(form=form)
