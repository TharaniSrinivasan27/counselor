from flask import request
from app.service.counselor_service import create_counselor, get_all_counselors, get_counselor_by_id, update_counselor, delete_counselor

def counselor_init_routes(app):
    @app.route('/create_counselor', methods=['POST'])
    def create_counselor_route():
        data = request.form 
        files = request.files
        current_user = 'thara'
        return create_counselor(data,files,current_user)

    @app.route('/get_counselors', methods=['GET'])
    def get_counselors_route():
        return get_all_counselors()

    @app.route('/get_counselor/<counselor_id>', methods=['GET'])
    def get_counselor_route(counselor_id):
        return get_counselor_by_id(counselor_id)

    @app.route('/update_counselor/<counselor_id>', methods=['PUT'])
    def update_counselor_route(counselor_id):
        data = request.form
        files = request.files  
        return update_counselor(counselor_id, data,files)

    @app.route('/delete_counselor/<counselor_id>', methods=['DELETE'])
    def delete_counselor_route(counselor_id):
        return delete_counselor(counselor_id)
