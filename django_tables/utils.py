def get_order_by(query_dict, order_by_param, secondary=None):
    '''
    ``query_dict`` is either the get or post data
    ``order_by_param`` is the variable name with which to sort on
    ``default`` which column to order on in a default case
    '''
    order_by = query_dict.get(order_by_param)
    if order_by and not order_by.lstrip('-') == secondary:
        order_by = [order_by, secondary]
    return order_by
