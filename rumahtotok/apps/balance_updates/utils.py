def create_balance_update(user, value, type, created_by, notes, order=None, canceled_by=None):
    balance_update = user.balance_updates.create(
        value=value, order=order, type=type, created_by=created_by, notes=notes, 
        canceled_by=canceled_by)

    user.balance += balance_update.value
    user.save(update_fields=['balance'])

    return balance_update
