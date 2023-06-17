from users.models import User, MessageToUser
from django.db.models import Q



# owning data for cabinet sidebar
def get_owning_data(request):
    user_list_data = list(User.objects.filter(id=request.user.id)\
                            .prefetch_related('owning')\
                            .values('owning__id', 'owning__house__title', 'owning__number'))

    user_data_dictionary = {'appartments':[]}

    for user_dictionary in user_list_data:
        house_in_owning = user_dictionary.pop('owning__house__title')
        number_in_owning = user_dictionary.pop('owning__number')
        user_dictionary['address'] = f'ЖК { house_in_owning }, кв.{ number_in_owning }'
        user_data_dictionary['appartments'].append(user_dictionary)


    new_users_data = list(User.objects.filter(status='new').values('id', 'email', 'full_name'))
    length_new_users_data = len(new_users_data)

    Q_list = []
    Q_list.append(Q(to_users = request.user))
    unreaded_messages = MessageToUser.objects.filter(to_users = request.user).exclude(read_by_user = request.user)
    unreaded_messages_len = len(unreaded_messages)

    context = {'user_data': user_data_dictionary,
            'unreaded_messages': unreaded_messages,
            'unreaded_messages_len': unreaded_messages_len,
            'new_users_data': new_users_data,
            'length_new_users_data': length_new_users_data}
    return context

