from users.models import User




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




    # user_data = request.user.owning.all
    return {'user_data': user_data_dictionary}

