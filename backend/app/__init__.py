import traceback
from flask import Flask, Response, request, make_response, send_from_directory 

from werkzeug.utils import secure_filename

from .storage import _Storage

import pathlib
import os
# from secrets import token_hex

app = Flask(__name__)

Storage = _Storage()

app.config['DATA_FOLDER'] = os.path.join(
    pathlib.Path(__file__).parent.parent, 'data')


@app.route('/maps/uploadImage/<map_id>/<map_name>', methods=['POST'])
async def maps_upload(map_id: str, map_name: str):
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

    await Storage.create_map(map_id, map_name.replace('__', ' '), filename)

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
        await Storage.create_point(point_id, map_id, request.args['name'], float(request.args['pos_x']), float(request.args['pos_y']), request.args['color'], filenames)
    except Exception as exc:
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        return make_response({'ok': False, 'error': 'Cannot create point from provided data'}, 400)

    return make_response({'ok': True}, 200)


@app.route('/maps/getMaps', methods=['GET'])
async def maps_get():

    maps = await Storage.get_maps()

    data = {
        'ok': True,
        'maps': {m.id: m.name for m in maps}
    }

    return make_response(data, 200)


@app.route('/maps/getMap', methods=['POST'])
async def map_get():
    map_id = request.json.get('map_id') if request.is_json else None

    if not map_id:
        return make_response({'ok': False, 'error': 'Not map_id provided'}, 400)

    map = await Storage.get_map(map_id)

    if not map:
        return make_response({'ok': False, 'error': 'Map not found'}, 404)

    points = await Storage.get_points(map_id)

    data = {
        'ok': True,
        'urls': {
            'map': '/files/map/'+map.id,
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


@app.route('/files/map/<map_id>', methods=['GET', 'POST'])
async def map_file_get(map_id: str):
    map = await Storage.get_map(map_id)
    return send_from_directory(directory=os.path.join(app.config['DATA_FOLDER'], map_id, '__map'), path=map.filename, as_attachment=False)
