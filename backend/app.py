from flask import Flask, Response, Request

from werkzeug.utils import secure_filename

from core.storage import Storage

import pathlib
import os
# from secrets import token_hex

app = Flask(__file__)

app.config['DATA_FOLDER'] = os.path.join(pathlib.Path(__file__).parent.parent, 'data')


@app.route('/maps/uploadImage/<str:map_id>', methods=['POST'])
async def maps_upload(map_id):
    request = Request()

    image = request.files.get('image')

    if not image or image.filename == '':
        return Response(status=400, response={'ok': False, 'error': 'Not image provided'})

    filename = os.path.join(app.config['DATA_FOLDER'], '__map', secure_filename(image.filename))

    image.save(filename)

    await Storage.create_map(map_id, filename)

    return Response(status=200, response={'ok': True})


# @app.route('/maps/getImage/<str:map_id>', methods=['GET'])
# async def maps_get(map_id):
#     request = Request()

#     # if not map_id:
#     #     return Response(status=400, response={'ok': False, 'error': 'Not map_id provided'})

#     map = await Storage.get_map(map_id)

#     if not map:
#         return Response(status=404, response={'ok': False, 'error': 'Map not found'})

#     return send_file(path_or_file=os.path.join(app.config['DATA_FOLDER'], map_id, '__map', map.filename), attachment_filename=map.filename)


@app.route('/points/uploadImages/<str:map_id>/<str:point_id>', methods=['POST'])
async def points_upload(map_id, point_id):
    request = Request()

    images = request.files.to_dict()

    if not images:
        return Response(status=400, response={'ok': False, 'error': 'Not images provided'})

    filenames = []

    for name, image in images.items():
        filename = os.path.join(app.config['DATA_FOLDER'], map_id, point_id, secure_filename(image.filename))
        filenames.append(filename)
        image.save(filename)
    
    try:
        await Storage.create_point(point_id, request.args['name'], float(request.args['pos_x']), float(request.args['pos_y']), request.args['color'], filenames)
    except Exception as exc:

        return Response(status=400, response={'ok': False, 'error': 'Cannot create point from provided data'})

    return Response(status=200, response={'ok': True})


# @app.route('/points/getImages', methods=['POST'])
# async def points_get():
#     request = Request()

#     map_id = request.json().get('map_id')

#     if not map_id:
#         return Response(status=400, response={'ok': False, 'error': 'Not map_id provided'})

#     map = await Storage.get_map(map_id)

#     if not map:
#         return Response(status=404, response={'ok': False, 'error': 'Map not found'})

#     return send_file(path_or_file=os.path.join(app.config['DATA_FOLDER'], map.filename), attachment_filename=map.filename)


@app.route('/maps/getMap/<str:map_id>', methods=['POST'])
async def maps_get():
    request = Request()

    map_id = request.json.get('map_id')

    if not map_id:
        return Response(status=400, response={'ok': False, 'error': 'Not map_id provided'})

    map = await Storage.get_map(map_id)

    if not map:
        return Response(status=404, response={'ok': False, 'error': 'Map not found'})
    
    points = await Storage.get_points(map_id)
    
    data = {
        'ok': True,
        'urls': {
            'map': map.filename,
            'points': [
                {
                    'filenames': p.filenames,
                    'pos_x': p.pos_x,
                    'pos_y': p.pos_y,
                    'name': p.name
                } for p in points
            ]
        }
    }

    return Response(status=200, response=data)


app.run('0.0.0.0', 80, debug=False)