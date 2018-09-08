from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
import redis
import datetime
import ast
import json

app = Flask(__name__, static_url_path="")
api = Api(app, prefix="/api/v1")

# Connect to a local redis server
rdb = redis.Redis(host='localhost', port=6379, db=0)

# A constraint for value formats
value_fields = {
    'key': fields.String,
    'value': fields.String
}


@app.errorhandler(404)
def page_not_found(e):
    """
    Custom 404 json message
    :param e:
    :return:
    """
    return jsonify({'message': 'Url not found'}), 404


class ValuesAPI(Resource):

    def __init__(self):
        """
        Initially making a request parser for post and patch with minimal validation
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('key', type=str, required=True,
                                   help='No task key provided',
                                   location='json')
        self.reqparse.add_argument('value', type=str, default="",
                                   location='json')
        super(ValuesAPI, self).__init__()

    def get(self):
        """
        Implementing the get operation for all values or the values of the given keys
        :return: whole list of values or the values of the provided keys
        """
        # This parser is used for the get url parser, it ignores all parameters except key
        parser = reqparse.RequestParser()
        parser.add_argument('keys', type=str)
        args = parser.parse_args()

        if args['keys'] is None:
            # return [marshal(ast.literal_eval((rdb.get(key))), value_fields) for key in rdb.keys('*')]
            return [marshal(json.loads(rdb.get(key)), value_fields) for key in
                    rdb.keys('*')]  # Deserialize the output
        else:
            list_values = []
            for key in args['keys'].split(','):
                key = key.strip()
                if rdb.get(key):
                    list_values.append(marshal(json.loads((rdb.get(key))), value_fields))
                else:
                    list_values.append({
                        'message': 'No key named {}'.format(key)
                    })
            return list_values

    def post(self):
        """
        Implementing the post operation for storing data in redis
        :return: status, data, message
        """
        args = self.reqparse.parse_args()

        # Two basic validation,
        # i) No empty key
        # ii) Key already exist
        if args['key'] == '':
            return {'message': 'Key cannot be empty'}, 400
        if rdb.get(args['key']):
            return {'message': 'Key already exist'}, 409
        print(args)

        val = {
            'key': args['key'],
            'value': args['value']
        }

        value = json.dumps(val)  # Serialize the input
        rdb.set(args['key'], value)
        rdb.expire(args['key'], 300)  # Expires a kv after 300 sec, ttl of 5 minutes

        return {
                   'status': 'Success',
                   'message': 'Value added',
                   'data': marshal(val, value_fields)
               }, 201

    def patch(self):
        """
        Implementing patch operation
        :return: status, data, message
        """
        args = self.reqparse.parse_args()

        # Two basic validation,
        # i) No empty key
        # ii) Key does not exist
        if args['key'] == '':
            return {'message': 'Key cannot be empty'}, 400
        if not rdb.get(args['key']):
            return {'message': 'Key does not exist'}, 404

        val = {
            'key': args['key'],
            'value': args['value']
        }
        value = json.dumps(val)  # Serialize the input
        rdb.set(args['key'], value)
        rdb.expire(args['key'], 300)  # Expires a kv after 300 sec, ttl of 5 minutes
        return {
                   'status': 'Success',
                   'message': 'Value updated',
                   'data': marshal(val, value_fields)
               }, 200


api.add_resource(ValuesAPI, '/values', endpoint='values')

if __name__ == '__main__':
    app.run(debug=False)
