import uuid


def generate_company_uuid():
    id=uuid.uuid1()
    return f'company_{id}'
def generate_uuid():
    return uuid.uuid1()
def generate_member_uuid():
    id=uuid.uuid1()
    return f'member_{id}'
