# This file contains definitions of dash callbacks used in the "data" tab of the app.

from dash import Output, Input, State, Patch, ctx, no_update
import base64
import numpy as np
from pypcd4 import PointCloud
import time
import os
from scipy.spatial.transform import Rotation
import tomllib

from general_functions import calculate_loading_gauge_transformation_matrix
from loading_functions import load_pcl_timestamps, load_csv_into_nparray


def get_callbacks(app):

    # copy the transformations data from a store to the window object
    app.clientside_callback(
        """
        function(gauge_transf_data, translations_data, rotations_data, rotations_inv_data, rot_euler_data) {
            // make the data accessible for the visualization.js script
            window.gauge_transf = gauge_transf_data;
            window.translations = translations_data;
            window.rotations = rotations_data;
            window.rotations_inv = rotations_inv_data;
            window.rotations_euler = rot_euler_data;
            // update the visualization if it is already created
            if (window.deck_initialized) {
                window.updateDeck();  // call function defined in the JavaScript file
            }
            return dash_clientside.no_update;
        }
        """,
        Output('translations-data', 'id'),  # dummy output needed so that the initial call occurs
        Input('gauge-transf-data', 'data'),
        Input('translations-data', 'data'),
        Input('rotations-data', 'data'),
        State('rotations-inv-data', 'data'),
        State('rotations-euler-data', 'data')
    )
    
    # calculate new loading gauge transformations when new guage translations or rotations are uploaded
    @app.callback(
        Output('gauge-transf-data', 'data'),
        Input('gauge-trans-data', 'data'),
        State('gauge-rot-inv-data', 'data')
    )
    def create_loading_gauge_transformations(trans_data, inv_rot_data):
        inv_transf_matrices = [[] for _ in range(4)]
        
        # calculate transformations for distances 25m, 50m, 75m, 100m
        for i in range(4):
            trans_nparray = np.array(trans_data[i])  # convert from lists to numpy arrays
            inv_rot_nparray = np.array(inv_rot_data[i])
            for j in range(min(trans_nparray.shape[0], inv_rot_nparray.shape[0])):
                inv_transf_matrix = calculate_loading_gauge_transformation_matrix(trans_nparray[j],
                                                                                inv_rot_nparray[j])
                inv_transf_matrices[i].append(inv_transf_matrix)
        return inv_transf_matrices
    
    # switch between displaying united and not united point cloud data
    @app.callback(
        Output('display-united-store', 'data'),
        Input('display-united-checkbox', 'value'),
        prevent_initial_call = True
    )
    def change_pc_mode(checkbox_values):
        if 'united' in checkbox_values:
            return True
        else:
            return False

    app.clientside_callback(
        """
        function(display_united) {
            window.changePCMode(display_united);
        }
        """,
        Input('display-united-store', 'data')
    )


    # upload/delete project file
    @app.callback(
        Output('project-file-upload-div', 'style'),
        Output('project-file-uploaded-file-div', 'style'),
        Output('project-file-filename-div', 'children'),
        
        Output('display-united-checkbox', 'value'),
        Output('united-pcd-path-store', 'data'),
        Output('divided-pcd-paths-store', 'data'),
        Output('pc-timestamps-path-store', 'data'),

        Output('translations-path-store', 'data'),
        Output('rotations-path-store', 'data'),
        Output('video-path-store', 'data'),
        
        Input('project-file-upload', 'contents'),
        State('project-file-upload', 'filename'),
        prevent_initial_call = True
    )
    def upload_project_file(file_content, filename):
        if file_content is not None:
            # new file uploaded
            content_type, content_string = file_content.split(',')
            decoded = base64.b64decode(content_string)
            data = tomllib.loads(decoded.decode("utf-8"))

            # load data from toml file and use them as needed
            display_united_checkbox_val = ['united'] if data['show_united_pcd'] else []
            united_pcd_path = os.path.join(data['project_path'], data['united_pcd_path'])
            divided_pcd_paths = {
                "dir_path": os.path.join(data['project_path'], data['divided_pcd_path']),
                "filename_prefix": data['divided_pcd_filename_prefix'],
                "files_cnt": data['divided_pcd_files_cnt']
            }
            pc_timestamps_path = os.path.join(data['project_path'], data['divided_pcd_timestamps_path'])
            translations_path = os.path.join(data['project_path'], data['translations_path'])
            rotations_path = os.path.join(data['project_path'], data['rotations_path'])
            timestamps_path = os.path.join(data['project_path'], data['timestamps_path'])
            video_path = os.path.join(data['project_path'], data['video_path'])

            return {"display": "none"}, {"display": "block"}, filename, \
                display_united_checkbox_val, united_pcd_path, divided_pcd_paths, pc_timestamps_path, \
                translations_path, rotations_path, video_path
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, "", \
                no_update, no_update, "", "", no_update, no_update, no_update


    # upload/delete file with united point cloud
    @app.callback(
        Output('united-pc-upload-div', 'style'),
        Output('united-pc-uploaded-file-div', 'style'),
        Output('united-pc-filename-div', 'children'),
        Output('united-pc-data', 'data'),
        Output('update-pcd-store', 'data'),
        Input('united-pc-upload', 'contents'),
        Input('united-pcd-path-store', 'data'),
        State('united-pc-upload', 'filename'),
        State('update-pcd-store', 'data'),
        prevent_initial_call = True
    )
    def upload_united_pc(file_content, pcd_path, filename, update_number):
        if ctx.triggered_id == 'united-pcd-path-store' and pcd_path != "":
            # the file path was set by the project file
            # get filename
            new_filename = os.path.basename(pcd_path)
            # read the file
            pc = PointCloud.from_path(pcd_path)
            pc_nparray = pc.numpy(("x", "y", "z", "intensity"))
            # save the data to the store
            return {"display": "none"}, {"display": "block"}, new_filename, pc_nparray, update_number+1
        elif file_content is not None:
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
            # delete the temporary file
            os.remove(server_filename)
            # save the data to the store
            return {"display": "none"}, {"display": "block"}, filename, pc_nparray, update_number+1
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, "", no_update, update_number+1

    
    # upload/delete files with divided point cloud
    @app.callback(
        Output('divided-pc-uploaded-file-div', 'style'),
        Output('divided-pc-filename-div', 'children'),
        Output('visualization-data', 'data'),
        Input('divided-pcd-paths-store', 'data'),
        prevent_initial_call = True
    )
    def upload_divided_pc(pcd_paths):
        if ctx.triggered_id == 'divided-pcd-paths-store' and pcd_paths != "":
            # the file path was set by the project file
            # get directory name (in this case displayed instead of filename)
            dirname = os.path.basename(pcd_paths['dir_path'])
            # read the files one by one
            data = []
            for i in range(pcd_paths['files_cnt']):
                file_path = os.path.join(pcd_paths['dir_path'], f"{pcd_paths['filename_prefix']}_{i}.pcd")
                pc = PointCloud.from_path(file_path)
                data.append(pc.numpy(("x", "y", "z", "intensity")))
            # create a patch for the visualization data store
            patched_data = Patch()
            patched_data["layers"][0]["data"] = data
            return {"display": "block"}, dirname, patched_data
        else:
            # it is the initial call
            return {"display": "none"}, "", no_update


    # upload/delete file with divided point cloud timestamps
    @app.callback(
        Output('pc-timestamps-uploaded-file-div', 'style'),
        Output('pc-timestamps-filename-div', 'children'),
        Output('pcl-timestamps-data', 'data'),
        Input('pc-timestamps-path-store', 'data'),
        prevent_initial_call = True
    )
    def upload_pc_timestamps(pc_timestamps_path):
        if ctx.triggered_id == 'pc-timestamps-path-store' and pc_timestamps_path != "":
            # the file path was set by the project file
            # get filename
            new_filename = os.path.basename(pc_timestamps_path)
            # read the file
            data = load_pcl_timestamps(pc_timestamps_path)
            return {"display": "block"}, new_filename, data
        else:
            # it is the initial call
            return {"display": "none"}, "", no_update


    # upload/delete file with translations
    @app.callback(
        Output('translations-upload-div', 'style'),
        Output('translations-uploaded-file-div', 'style'),
        Output('translations-filename-div', 'children'),
        Output('translations-data', 'data'),
        Input('translations-upload', 'contents'),
        Input('translations-path-store', 'data'),
        State('translations-upload', 'filename'),
        prevent_initial_call = True
    )
    def upload_translations(file_content, translations_path, filename):
        if ctx.triggered_id == 'translations-path-store' and translations_path != "":
            # the file path was set by the project file
            # get filename
            new_filename = os.path.basename(translations_path)
            # read the file
            trans_nparray = load_csv_into_nparray(translations_path)[:, [2, 0, 1]]
            # save the data to the store
            return {"display": "none"}, {"display": "block"}, new_filename, trans_nparray
        elif file_content is not None:
            # new file uploaded
            content_type, content_string = file_content.split(',')
            decoded_lines = base64.b64decode(content_string).decode("utf-8").split('\n')
            data = []
            for line in decoded_lines:         # parse the csv
                split_line = line.split(',')
                if len(split_line) >= 3:
                    # fix the order of columns
                    data.append([float(split_line[2]), float(split_line[0]), float(split_line[1])])
            return {"display": "none"}, {"display": "block"}, filename, data
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, "", no_update


    # upload/delete file with rotations
    @app.callback(
        Output('rotations-upload-div', 'style'),
        Output('rotations-uploaded-file-div', 'style'),
        Output('rotations-filename-div', 'children'),
        Output('rotations-euler-data', 'data'),
        Output('rotations-data', 'data'),
        Output('rotations-inv-data', 'data'),
        Input('rotations-upload', 'contents'),
        Input('rotations-path-store', 'data'),
        State('rotations-upload', 'filename'),
        prevent_initial_call = True
    )
    def upload_rotations(file_content, rotations_path, filename):
        if ctx.triggered_id == 'rotations-path-store' and rotations_path != "":
            # the file path was set by the project file
            # get filename
            new_filename = os.path.basename(rotations_path)
            # read the file
            rot_nparray = load_csv_into_nparray(rotations_path)[:, [2, 0, 1]]
            
            # TODO
            
            rotations_euler = []
            rotations = []
            inv_rotations = []
            # save the data to the store
            return {"display": "none"}, {"display": "block"}, new_filename, no_update, no_update, no_update
        elif file_content is not None:
            # new file uploaded
            content_type, content_string = file_content.split(',')
            decoded_lines = base64.b64decode(content_string).decode("utf-8").split('\n')
            rotations = []
            inv_rotations = []
            rotations_euler = []
            for line in decoded_lines:         # parse the csv
                split_line = line.split(',')
                if len(split_line) >= 3:
                    rot_array = [float(split_line[0]), float(split_line[1]), float(split_line[2])]
                    rotation = Rotation.from_euler("xzy", rot_array, degrees=True)
                    rotation_zyx = rotation.inv().as_euler("zyx", degrees=True)
                    rotations_euler.append([-rotation_zyx[0], rotation_zyx[1], rotation_zyx[2]])
                    rotations.append(rotation.as_matrix())
                    inv_rotations.append(rotation.inv().as_matrix())
            
            return {"display": "none"}, {"display": "block"}, filename, rotations_euler, rotations, inv_rotations
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, "", no_update, no_update, no_update


    # upload/delete file with video
    @app.callback(
        Output('video-upload-div', 'style'),
        Output('video-uploaded-file-div', 'style'),
        Output('video-filename-div', 'children'),
        Output('background-video', 'src'),
        Output('update-video-store', 'data'),  # to set the same position in the new video
        Input('video-upload', 'contents'),
        Input('video-path-store', 'data'),
        State('video-upload', 'filename'),
        State('update-video-store', 'data'),
        prevent_initial_call = True
    )
    def upload_video(file_content, video_path, filename, update_number):
        if ctx.triggered_id == 'video-path-store' and video_path != "":
            # the file path was set by the project file
            # get filename
            new_filename = os.path.basename(video_path)
            # read the file

            # TODO
            
            # save the data to the store
            return {"display": "none"}, {"display": "block"}, new_filename, no_update, update_number+1 
        elif file_content is not None:
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
            return {"display": "block"}, {"display": "none"}, "", no_update, update_number+1
    

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

    # delete project file
    @app.callback(
        Output('project-file-upload', 'contents'),
        Input('project-file-delete-button', 'n_clicks')
    )
    def delete_project_file(btn):
        return None
    
    # delete file with point cloud
    @app.callback(
        Output('united-pc-upload', 'contents'),
        Input('united-pc-delete-button', 'n_clicks')
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

    # hide empty boxes at the start of the app


    # update window.frames_cnt, the total time label as well as the range of the slider & input 
    # which control train position when new timestamps data is uploaded
    app.clientside_callback(
        """
        function(camera_timestamps) {
            window.frames_cnt = camera_timestamps.length;
            
            // we get the total time by reading the last timestamp
            const time_sec = Math.floor(camera_timestamps[camera_timestamps.length - 1]); 
            const minutes = Math.floor(time_sec / 60);
            const seconds = time_sec % 60;
            const label = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
            dash_clientside.set_props("total-time-div", {children: label});

            // update the range of the slider and number input
            dash_clientside.set_props("camera-position-slider-input", {max: camera_timestamps.length - 1});
            dash_clientside.set_props("camera-position-input", {max: camera_timestamps.length - 1});
            
            return dash_clientside.no_update;
        }
        """,
        Output('camera-timestamps-data', 'id'),  # dummy output needed so that the initial call occurs
        Input('camera-timestamps-data', 'data')
    )
