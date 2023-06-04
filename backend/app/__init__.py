import traceback
from flask import Flask, Response, request, make_response

from werkzeug.utils import secure_filename

from .storage import _Storage

import pathlib
import os
# from secrets import token_hex

app = Flask(__name__)

Storage = _Storage()

app.config['DATA_FOLDER'] = os.path.join(
    pathlib.Path(__file__).parent.parent, 'data')


@app.route('/maps/uploadImage/<map_id>', methods=['POST'])
async def maps_upload(map_id):
    image = request.files.get('image')

    if not image or image.filename == '':
        return make_response({'ok': False, 'error': 'Not image provided'}, 400)

    map = await Storage.get_map(map_id)

    if map:
        return make_response({'ok': False, 'error': 'Map already exists'}, 400)

    filepath = os.path.join(app.config['DATA_FOLDER'], map_id, '__map')

    try:
        os.makedirs(filepath)
    except:
        pass

    filename = os.path.join(filepath, secure_filename(image.filename))

    await Storage.create_map(map_id, filename)

    image.save(filename)

    return make_response({'ok': True}, 200)


@app.route('/points/uploadImages/<map_id>/<point_id>', methods=['POST'])
async def points_upload(map_id, point_id):
    images = request.files.to_dict()

    if not images:
        return make_response({'ok': False, 'error': 'Not images provided'}, 400)
    
    point = await Storage.get_point(map_id, point_id)

    if point:
        return make_response({'ok': False, 'error': 'Point already exists'}, 400)

    filenames = []

    filespath = os.path.join(app.config['DATA_FOLDER'], map_id, point_id)

    try:
        os.makedirs(filespath)
    except:
        pass

    for name, image in images.items():
        filename = os.path.join(filespath, secure_filename(image.filename))
        filenames.append(filename)
        image.save(filename)

    try:
        await Storage.create_point(point_id, request.args['name'], float(request.args['pos_x']), float(request.args['pos_y']), request.args['color'], filenames)
    except Exception as exc:
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        return make_response({'ok': False, 'error': 'Cannot create point from provided data'}, 400)

    return make_response({'ok': True}, 200)


@app.route('/maps/getMap/<map_id>', methods=['POST'])
async def maps_get():
    map_id = request.json.get('map_id')

    if not map_id:
        return make_response({'ok': False, 'error': 'Not map_id provided'}, 400)

    map = await Storage.get_map(map_id)

    if not map:
        return make_response({'ok': False, 'error': 'Map not found'}, 404)

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

    return make_response(data, 200)
