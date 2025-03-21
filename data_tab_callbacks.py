# This file contains definitions of dash callbacks used in the "data" tab of the app.

from dash import Output, Input, State, Patch
import base64
import numpy as np
import pandas as pd
from pypcd4 import PointCloud
import time
import os
from scipy.spatial.transform import Rotation

from general_functions import calculate_transformation_matrix, calculate_loading_gauge_transformation_matrix


def get_callbacks(app):

    # copy the transformations data from a store to the window object
    app.clientside_callback(
        """
        function(transf_data, transf_inv_data, translations_data, rotations_data, rotations_inv_data) {
            window.transf = transf_data;  // make the data accessible for the visualization.js script
            window.transf_inv = transf_inv_data;
            window.translations = translations_data;
            window.rotations = rotations_data;
            window.rotations_inv = rotations_inv_data;
            // update the visualization if it is already created
            if (window.deck_initialized) {
                window.updateDeck();  // call function defined in the JavaScript file
            }
            return dash_clientside.no_update;
        }
        """,
        Output('transformations-data', 'id'),  # dummy output needed so that the initial call occurs
        Input('transformations-data', 'data'),
        State('transformations-inv-data', 'data'),
        State('translations-data', 'data'),
        State('rotations-data', 'data'),
        State('rotations-inv-data', 'data')
    )
    
    # calculate new transformations when new translations or rotations are uploaded
    @app.callback(
        Output('transformations-data', 'data'),
        Output('transformations-inv-data', 'data'),
        Input('translations-data', 'data'),
        Input('rotations-data', 'data'),
        State('rotations-inv-data', 'data')
    )
    def create_transformations(trans_data, rot_data, inv_rot_data):
        trans_nparray = np.array(trans_data)  # convert from lists to numpy arrays
        rot_nparray = np.array(rot_data)
        inv_rot_nparray = np.array(inv_rot_data)

        transf_matrices = []
        inv_transf_matrices = []
        for i in range(min(trans_nparray.shape[0], rot_nparray.shape[0])):
            transf_matrix = calculate_transformation_matrix(trans_nparray[i], rot_nparray[i])
            transf_matrices.append(transf_matrix)
            inv_transf_matrix = calculate_loading_gauge_transformation_matrix(trans_nparray[i],
                                                                              inv_rot_nparray[i])
            inv_transf_matrices.append(inv_transf_matrix)
        return transf_matrices, inv_transf_matrices

    # upload/delete file with point cloud
    @app.callback(
        Output('point-cloud-upload-div', 'style'),
        Output('point-cloud-uploaded-file-div', 'style'),
        Output('point-cloud-filename-div', 'children'),
        Output('visualization-data', 'data'),
        Output('update-pcd-store', 'data'),
        Input('point-cloud-upload', 'contents'),
        State('point-cloud-upload', 'filename'),
        State('update-pcd-store', 'data'),
        prevent_initial_call = True
    )
    def upload_point_cloud(file_content, filename, update_number):
        if file_content is not None:
            # new file uploaded
            content_type, content_string = file_content.split(',')
            decoded = base64.b64decode(content_string)
            # write the video to a temporary file
            server_filename = f"assets/temp/uploaded_pcd_{int(time.time())}.pcd" # filename with a timestamp
            with open(server_filename, "wb") as f:
                f.write(decoded)
            # read the temporary file
            pc = PointCloud.from_path(server_filename)
            pc_nparray = pc.numpy(("x", "y", "z", "intensity"))
            pc_df = pd.DataFrame(pc_nparray, columns=["x", "y", "z", "intensity"])
            # create a patch for the visualization data store
            patched_data = Patch()
            patched_data["layers"][0]["data"] = pc_df.to_dict(orient="records")
            # delete the temporary file
            os.remove(server_filename)
            return {"display": "none"}, {"display": "block"}, filename, patched_data, update_number+1
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, "", Patch(), update_number+1

    # upload/delete file with translations
    @app.callback(
        Output('translations-upload-div', 'style'),
        Output('translations-uploaded-file-div', 'style'),
        Output('translations-filename-div', 'children'),
        Output('translations-data', 'data'),
        Input('translations-upload', 'contents'),
        State('translations-upload', 'filename'),
        prevent_initial_call = True
    )
    def upload_translations(file_content, filename):
        if file_content is not None:
            # new file uploaded
            content_type, content_string = file_content.split(',')
            decoded_lines = base64.b64decode(content_string).decode("utf-8").split('\n')
            data = []
            for line in decoded_lines:         # parse the csv
                split_line = line.split(',')
                if len(split_line) >= 3:
                    data.append([float(split_line[0]), float(split_line[1]), float(split_line[2])])
            return {"display": "none"}, {"display": "block"}, filename, data
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, "", Patch()

    # react to uploaded/deleted file with rotations
    @app.callback(
        Output('rotations-upload-div', 'style'),
        Output('rotations-uploaded-file-div', 'style'),
        Output('rotations-filename-div', 'children'),
        Output('rotations-data', 'data'),
        Output('rotations-inv-data', 'data'),
        Input('rotations-upload', 'contents'),
        State('rotations-upload', 'filename'),
        prevent_initial_call = True
    )
    def upload_rotations(file_content, filename):
        if file_content is not None:
            # new file uploaded
            content_type, content_string = file_content.split(',')
            decoded_lines = base64.b64decode(content_string).decode("utf-8").split('\n')
            data = []
            inv_data = []
            for line in decoded_lines:         # parse the csv
                split_line = line.split(',')
                if len(split_line) >= 3:
                    rot_array = [float(split_line[0]), float(split_line[1]), float(split_line[2])]
                    rotation = Rotation.from_euler("zyx", rot_array, degrees=True)
                    rot_mat_3x3 = rotation.as_matrix()
                    data.append(rot_mat_3x3)
                    inv_data.append(rot_mat_3x3)
            return {"display": "none"}, {"display": "block"}, filename, data, inv_data
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, "", Patch(), Patch()

    # upload/delete file with video
    @app.callback(
        Output('video-upload-div', 'style'),
        Output('video-uploaded-file-div', 'style'),
        Output('video-filename-div', 'children'),
        Output('background-video', 'src'),
        Output('update-video-store', 'data'),  # to set the same position in the new video
        Input('video-upload', 'contents'),
        State('video-upload', 'filename'),
        State('update-video-store', 'data'),
        prevent_initial_call = True
    )
    def upload_video(file_content, filename, update_number):
        if file_content is not None:
            # new file uploaded
            content_type, content_string = file_content.split(',')
            decoded = base64.b64decode(content_string)
            # write the video to a temporary file
            server_filename = f"assets/temp/uploaded_video_{int(time.time())}.mp4" # filename with a timestamp
            with open(server_filename, "wb") as f:
                f.write(decoded)
            return {"display": "none"}, {"display": "block"}, filename, server_filename, update_number+1
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, "", Patch(), update_number+1
    
    # set a new video to the same time as the old video
    app.clientside_callback(
        """
        function(update_number, camera_pos) {
            const video = document.getElementById('background-video');
            const videoTime = parseInt(camera_pos) / 25;
            video.currentTime = videoTime;
        }
        """,
        Input('update-video-store', 'data'),
        State('camera-position-input', 'value'),
        prevent_initial_call=True
    )

    # delete old temporary video files
    @app.callback(
        Input('delete-temp-video-interval', 'n_intervals')
    )
    def delete_temp_video_files(n):
        now = int(time.time())  # current time in seconds
        for filename in os.listdir("assets/temp"):    # find all temporary video files
            file_path = f"assets/temp/{filename}"
            if os.path.isfile(file_path):
                if now - int(filename[15:-4]) > 120:  # determine if the file is at least 2 minutes old
                    os.remove(file_path)

    # delete file with point cloud
    @app.callback(
        Output('point-cloud-upload', 'contents'),
        Input('point-cloud-delete-button', 'n_clicks')
    )
    def delete_point_cloud(btn):
        return None

    # delete file with translations
    @app.callback(
        Output('translations-upload', 'contents'),
        Input('translations-delete-button', 'n_clicks')
    )
    def delete_translations(btn):
        return None

    # delete file with rotations
    @app.callback(
        Output('rotations-upload', 'contents'),
        Input('rotations-delete-button', 'n_clicks')
    )
    def delete_rotations(btn):
        return None

    # delete file with video
    @app.callback(
        Output('video-upload', 'contents'),
        Input('video-delete-button', 'n_clicks')
    )
    def delete_video(btn):
        return None

