import routeros_api

def create_user(phone, duration):
    connection = routeros_api.RouterOsApiPool(
        '192.168.88.1',
        username='Dimba',
        password='Radohgigos2003',
        plaintext_login=True
    )
    api = connection.get_api()

    api.get_resource('/ip/hotspot/user').add(
        name=phone,
        password=phone,
        profile=duration
    )

    connection.disconnect()