
from rumahtotok.apps.orders.models import PaymentConfirmation
from rest_framework import serializers


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentConfirmation
        fields = ("order", 'photo', 'photo_url', 'value', "notes")

    def validate(self, validated_data):
        value = validated_data['value']
        order = validated_data['order']

        if value != order.unique_price:
            raise serializers.ValidationError({'value': 'Please input correct value'})

        if order.payment_confirmations.filter(status=PaymentConfirmation.STATUS.new).exists():
            raise serializers.ValidationError(
                {'payment': 'Please wait, we will confirm your previous request'})

        return validated_data

    def create(self, validated_data):
        payment = PaymentConfirmation.objects.create(**validated_data)
        print payment
        return payment
