from .resources import restaurantApi
def initialize_routes(api):
    api.add_resource(restaurantApi, '/api/res')