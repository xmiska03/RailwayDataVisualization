## @file data_tab_callbacks.py
# @author Zuzana Miškaňová
# @brief Contains definitions of Dash callbacks used in the "data" tab.

from dash import Output, Input, State, Patch, ctx, no_update
import base64
import numpy as np
from pypcd4 import PointCloud
import time
import os
import tomllib

from general_functions import calculate_train_profile_transformation_matrix, load_rotation, \
                              rotation_to_euler, rotation_to_matrix, rotation_to_inv_matrix, \
                              calculate_projection_matrix
from loading_functions import load_pcl_timestamps_file, load_pcl_timestamps, \
                              load_csv_file_into_nparray, load_csv_into_nparray, \
                              load_timestamps_file_into_nparray, load_timestamps_into_nparray, \
                              load_profile_translations, load_profile_rotations, \
                              load_space_separated_into_nparray


## @brief Registers all callbacks for the "data" tab.
# @param app The Dash app instance.
def get_callbacks(app):

    # copy the transformations data from a store to the window object
    app.clientside_callback(
        """
        function(profile_transf_data, translations_data, rotations_data, rotations_inv_data, rot_euler_data) {
            // make the data accessible for the visualization.js script
            window.vis.profile_transf = profile_transf_data;
            window.vis.translations = translations_data;
            window.vis.rotations = rotations_data;
            window.vis.rotations_inv = rotations_inv_data;
            window.vis.rotations_euler = rot_euler_data;
            // update the visualization if it is already created
            if (window.vis.deck_initialized) {
                window.vis.updateDeck();  // call function defined in the JavaScript file
            }
            return dash_clientside.no_update;
        }
        """,
        Output('translations-data', 'id'),  # dummy output needed so that the initial call occurs
        Input('profile-transf-data', 'data'),
        Input('translations-data', 'data'),
        Input('rotations-data', 'data'),
        State('rotations-inv-data', 'data'),
        State('rotations-euler-data', 'data')
    )
    
    # calculate new train profile transformations when new guage translations or rotations are uploaded
    @app.callback(
        Output('profile-transf-data', 'data'),
        Input('profile-trans-data', 'data'),
        Input('profile-rot-data', 'data')
    )
    def create_train_profile_transformations(trans_data, rot_data):
        transf_matrices = [[] for _ in range(4)]
        
        # calculate transformations for distances 25m, 50m, 75m, 100m
        for i in range(4):
            trans_nparray = np.array(trans_data[i])  # convert from lists to numpy arrays
            rot_nparray = np.array(rot_data[i])
            for j in range(min(trans_nparray.shape[0], rot_nparray.shape[0])):
                transf_matrix = calculate_train_profile_transformation_matrix(trans_nparray[j],
                                                                              rot_nparray[j])
                transf_matrices[i].append(transf_matrix)
        return transf_matrices
    

    # upload/delete project file
    @app.callback(
        Output('project-file-upload-div', 'style'),
        Output('project-file-uploaded-file-div', 'style'),
        Output('project-file-filename-div', 'children'),
        
        Output('united-pcd-path-store', 'data'),
        Output('divided-pcd-paths-store', 'data'),
        Output('pc-timestamps-path-store', 'data'),

        Output('video-path-store', 'data'),

        Output('vector-data-path-store', 'data'),

        Output('translations-path-store', 'data'),
        Output('rotations-path-store', 'data'),
        Output('timestamps-path-store', 'data'),

        Output('profile-trans-paths-store', 'data'),
        Output('profile-rot-paths-store', 'data'),

        Output('calibration-matrix-textarea', 'value'),
        Output('far-plane-input', 'value'),
        Output('distortion-params-textarea', 'value'),
        
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
            united_pcd_path = os.path.join(data['project_path'], data['postprocess_pcd_path'])
            divided_pcd_paths = {
                "dir_path": os.path.join(data['project_path'], data['realtime_pcd_path']),
                "filename_prefix": data['realtime_pcd_filename_prefix'],
                "files_cnt": data['realtime_pcd_files_cnt']
            }
            pc_timestamps_path = os.path.join(data['project_path'], data['realtime_pcd_timestamps_path'])
            video_path = os.path.join(data['project_path'], data['video_path'])
            vector_data_path = os.path.join(data['project_path'], data['vector_data_path'])
            translations_path = os.path.join(data['project_path'], data['translations_path'])
            rotations_path = os.path.join(data['project_path'], data['rotations_path'])
            timestamps_path = os.path.join(data['project_path'], data['timestamps_path'])
            profile_trans_paths = {
                "dir_path": os.path.join(data['project_path'], data['profile_translations_path']),
                "filename_prefix": data['profile_translations_filename_prefix']
            }
            profile_rot_paths = {
                "dir_path": os.path.join(data['project_path'], data['profile_rotations_path']),
                "filename_prefix": data['profile_rotations_filename_prefix']
            }

            calibm = data['calibration_matrix']
            calib_matrix_str = f"{calibm[0]}, {calibm[1]}, {calibm[2]},\n" \
                             + f"{calibm[3]}, {calibm[4]}, {calibm[5]},\n" \
                             + f"{calibm[6]}, {calibm[7]}, {calibm[8]}"
            far_plane = data['far_plane']
            distp = data['distortion_parameters']
            dist_params_str = f"{distp[0]}, {distp[1]}, {distp[2]}, {distp[3]}, {distp[4]}"

            return {"display": "none"}, {"display": "block"}, filename, \
                united_pcd_path, divided_pcd_paths, pc_timestamps_path, \
                video_path, vector_data_path, \
                translations_path, rotations_path, timestamps_path, \
                profile_trans_paths, profile_rot_paths, \
                calib_matrix_str, far_plane, dist_params_str
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, "", \
                no_update, "", "", no_update, "", no_update, no_update, no_update, "", "", \
                no_update, no_update, no_update


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
            # write the point cloud to a temporary file
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
        Output('divided-pc-upload-div', 'style'),
        Output('divided-pc-uploaded-file-div', 'style'),
        Output('divided-pc-filename-div', 'children'),
        Output('visualization-data', 'data'),
        Input('divided-pcd-paths-store', 'data'),
        Input('divided-pc-upload', 'contents'),
        State('divided-pc-upload', 'filename'),
        prevent_initial_call = True
    )
    def upload_divided_pc(pcd_paths, file_content, filenames):
        if ctx.triggered_id == 'divided-pcd-paths-store' and pcd_paths != "":
            # the file path was set by the project file
            # create quasi-filename
            dirname = os.path.basename(pcd_paths['dir_path'])
            quasi_filename = os.path.join(dirname, pcd_paths['filename_prefix']) + "_*.pcd"
            # read the files one by one
            data = []
            for i in range(pcd_paths['files_cnt']):
                file_path = os.path.join(pcd_paths['dir_path'], f"{pcd_paths['filename_prefix']}_{i}.pcd")
                pc = PointCloud.from_path(file_path)
                data.append(pc.numpy(("x", "y", "z", "intensity")))
            # create a patch for the visualization data store
            patched_data = Patch()
            patched_data["layers"][0]["data"] = data
            return {"display": "none"}, {"display": "block"}, quasi_filename, patched_data
        elif file_content is not None:
            # new files uploaded
            # create quasi-filename
            quasi_filename = filenames[0]
            if len(filenames) > 1: quasi_filename += ", ..."   # suggest that there are more files
            # read the files one by one
            data = [[] for i in range(len(filenames))]
            for i in range(len(filenames)):
                # decide which file is it - name must always be "pcd_*.pcd"
                index = int(filenames[i][4:-4])
                # read the file
                content_type, content_string = file_content[i].split(',')
                decoded = base64.b64decode(content_string)
                # write the point cloud to a temporary file
                server_filename = f"assets/temp/uploaded_pcd_{int(time.time())}.pcd" # filename with a timestamp
                with open(server_filename, "wb") as f:
                    f.write(decoded)
                # read the temporary file
                pc = PointCloud.from_path(server_filename)
                data[index] = pc.numpy(("x", "y", "z", "intensity"))
                # delete the temporary file
                os.remove(server_filename)
            # create a patch for the visualization data store
            patched_data = Patch()
            patched_data["layers"][0]["data"] = data
            return {"display": "none"}, {"display": "block"}, quasi_filename, patched_data
        else:
            # it is the initial call
            return {"display": "block"}, {"display": "none"}, "", no_update


    # upload/delete file with divided point cloud timestamps
    @app.callback(
        Output('pc-timestamps-upload-div', 'style'),
        Output('pc-timestamps-uploaded-file-div', 'style'),
        Output('pc-timestamps-filename-div', 'children'),
        Output('pcl-timestamps-data', 'data'),
        Input('pc-timestamps-path-store', 'data'),
        Input('pc-timestamps-upload', 'contents'),
        State('pc-timestamps-upload', 'filename'),
        prevent_initial_call = True
    )
    def upload_pc_timestamps(pc_timestamps_path, file_content, filename):
        if ctx.triggered_id == 'pc-timestamps-path-store' and pc_timestamps_path != "":
            # the file path was set by the project file
            # get filename
            new_filename = os.path.basename(pc_timestamps_path)
            # read the file
            data = load_pcl_timestamps_file(pc_timestamps_path)
            return {"display": "none"}, {"display": "block"}, new_filename, data
        elif file_content is not None:
            # new file uploaded
            content_type, content_string = file_content.split(',')
            decoded = base64.b64decode(content_string).decode("utf-8").split('\n')
            # read the file
            data = load_pcl_timestamps(decoded)
            return {"display": "none"}, {"display": "block"}, filename, data
        else:
            # it is the initial call
            return {"display": "block"}, {"display": "none"}, "", no_update


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
        # TODO test if the video is in the right format

        if ctx.triggered_id == 'video-path-store' and video_path != "":
            # the file path was set by the project file
            # get filename
            new_filename = os.path.basename(video_path)
            # the file has to be in the "assets" directory to be loaded into the Dash app
            # so we have to copy it into a temporary file there
            server_filename = f"assets/temp/uploaded_video_{int(time.time())}.mp4" # filename with a timestamp
            with open(video_path, 'rb') as src:
                with open(server_filename, 'wb') as dst:
                    dst.write(src.read())
            return {"display": "none"}, {"display": "block"}, new_filename, server_filename, update_number+1 
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
            return {"display": "block"}, {"display": "none"}, "", no_update, no_update
    

    # upload/delete file with vector data
    @app.callback(
        Output('vector-data-upload-div', 'style'),
        Output('vector-data-uploaded-file-div', 'style'),
        Output('vector-data-filename-div', 'children'),
        Output('vector-data', 'data'),
        Input('vector-data-path-store', 'data'),
        Input('vector-data-upload', 'contents'),
        State('vector-data-upload', 'filename'),
        prevent_initial_call = True
    )
    def upload_vector_data(vector_data_path, file_content, filenames):
        if ctx.triggered_id == 'vector-data-path-store' and vector_data_path != "":
            # the file path was set by the project file
            # create quasi-filename
            dirname = os.path.basename(vector_data_path)
            quasi_filename = os.path.join(dirname, "*.csv")
            # get names of all files in the directory
            files = os.listdir(vector_data_path)
            # read the files one by one
            data = []
            for filename in files:
                file_path = os.path.join(vector_data_path, filename)
                data.append(load_csv_file_into_nparray(file_path))
            return {"display": "none"}, {"display": "block"}, quasi_filename, data
        elif file_content is not None:
            # new files uploaded
            # create quasi-filename
            quasi_filename = filenames[0]
            if len(filenames) > 1: quasi_filename += ", ..."   # suggest that there are more files
            # read the files one by one
            data = []
            for i in range(len(filenames)):
                content_type, content_string = file_content[i].split(',')
                decoded = base64.b64decode(content_string).decode("utf-8").split('\n')
                data.append(load_csv_into_nparray(decoded))
            return {"display": "none"}, {"display": "block"}, quasi_filename, data
        else:
            # it is the initial call
            return {"display": "block"}, {"display": "none"}, "", no_update


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
            trans_nparray = load_csv_file_into_nparray(translations_path)[:, [2, 0, 1]]
            # save the data to the store
            return {"display": "none"}, {"display": "block"}, new_filename, trans_nparray
        elif file_content is not None:
            # new file uploaded
            content_type, content_string = file_content.split(',')
            decoded = base64.b64decode(content_string).decode("utf-8").split('\n')
            data = load_csv_into_nparray(decoded)[:, [2, 0, 1]]
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
            rot_nparray_raw = load_csv_file_into_nparray(rotations_path)
            rot_nparray = []
            rot_inv_nparray = []
            rot_euler_array = []
            for rot_raw in rot_nparray_raw:
                rotation = load_rotation(rot_raw)
                rot_nparray.append(rotation_to_matrix(rotation))
                rot_inv_nparray.append(rotation_to_inv_matrix(rotation))
                rot_euler_array.append(rotation_to_euler(rotation))
            
            # save the data to the store
            return {"display": "none"}, {"display": "block"}, new_filename, rot_euler_array, rot_nparray, rot_inv_nparray
        elif file_content is not None:
            # new file uploaded
            content_type, content_string = file_content.split(',')
            decoded = base64.b64decode(content_string).decode("utf-8").split('\n')
            data = load_csv_into_nparray(decoded)
            rot_nparray = []
            rot_inv_nparray = []
            rot_euler_array = []
            for rot_raw in data:
                rotation = load_rotation(rot_raw)
                rot_nparray.append(rotation_to_matrix(rotation))
                rot_inv_nparray.append(rotation_to_inv_matrix(rotation))
                rot_euler_array.append(rotation_to_euler(rotation))
            
            return {"display": "none"}, {"display": "block"}, filename, rot_euler_array, rot_nparray, rot_inv_nparray
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, "", no_update, no_update, no_update

    # upload/delete file with timestamps
    @app.callback(
        Output('timestamps-upload-div', 'style'),
        Output('timestamps-uploaded-file-div', 'style'),
        Output('timestamps-filename-div', 'children'),
        Output('camera-timestamps-data', 'data'),
        Input('timestamps-upload', 'contents'),
        Input('timestamps-path-store', 'data'),
        State('timestamps-upload', 'filename'),
        prevent_initial_call = True
    )
    def upload_timestamps(file_content, timestamps_path, filename):
        if ctx.triggered_id == 'timestamps-path-store' and timestamps_path != "":
            # the file path was set by the project file
            # get filename
            new_filename = os.path.basename(timestamps_path)
            # read the file
            timestamps_nparray = load_timestamps_file_into_nparray(timestamps_path)
            # save the data to the store
            return {"display": "none"}, {"display": "block"}, new_filename, timestamps_nparray
        elif file_content is not None:
            # new file uploaded
            content_type, content_string = file_content.split(',')
            decoded = base64.b64decode(content_string).decode("utf-8").split('\n')
            timestamps_nparray = load_timestamps_into_nparray(decoded)
            return {"display": "none"}, {"display": "block"}, filename, timestamps_nparray
        else:
            # file deleted (or it is the initial call)
            return {"display": "block"}, {"display": "none"}, "", no_update
    
    # upload/delete file with train profile translations
    @app.callback(
        Output('profile-trans-upload-div', 'style'),
        Output('profile-trans-uploaded-file-div', 'style'),
        Output('profile-trans-filename-div', 'children'),
        Output('profile-trans-data', 'data'),
        Output('profile-line-data', 'data'),
        Input('profile-trans-paths-store', 'data'),
        Input('profile-trans-upload', 'contents'),
        State('profile-trans-upload', 'filename'),
        prevent_initial_call = True
    )
    def upload_profile_translations(profile_trans_paths, file_content, filenames):
        if ctx.triggered_id == 'profile-trans-paths-store' and profile_trans_paths != "":
            # the file path was set by the project file
            # create quasi-filename
            dirname = os.path.basename(profile_trans_paths['dir_path'])
            quasi_filename = os.path.join(dirname, profile_trans_paths['filename_prefix']) + "_*.csv"
            # load data from the files
            profile_translations = load_profile_translations(profile_trans_paths['dir_path'], 
                                                           profile_trans_paths['filename_prefix'])
            profile_line_data = [[profile_translations[0]], [profile_translations[1]], 
                                 [profile_translations[2]], [profile_translations[3]]]
            
            return {"display": "none"}, {"display": "block"}, quasi_filename, profile_translations, \
                   profile_line_data
        elif file_content is not None:
            # new files uploaded
            # create quasi-filename
            quasi_filename = filenames[0]
            if len(filenames) > 1: quasi_filename += ", ..."   # suggest that there are more files
            # load the data from files
            profile_translations = [[] for i in range(4)]
            for i in range(len(filenames)):
                # decide which file is it
                index = 0
                if filenames[i][-6:-4] == "50":
                    index = 1
                elif filenames[i][-6:-4] == "75":
                    index = 2
                elif filenames[i][-7:-4] == "100":
                    index = 3
                # read the file
                content_type, content_string = file_content[i].split(',')
                decoded = base64.b64decode(content_string).decode("utf-8").split('\n')
                profile_translations[index] = load_space_separated_into_nparray(decoded)[:, [2, 0, 1]]
            profile_line_data = [[profile_translations[0]], [profile_translations[1]], 
                                 [profile_translations[2]], [profile_translations[3]]]
            return {"display": "none"}, {"display": "block"}, quasi_filename, profile_translations, \
                   profile_line_data
        else:
            # it is the initial call
            return {"display": "block"}, {"display": "none"}, "", no_update, no_update
        
    # upload/delete file with train profile rotations
    @app.callback(
        Output('profile-rot-upload-div', 'style'),
        Output('profile-rot-uploaded-file-div', 'style'),
        Output('profile-rot-filename-div', 'children'),
        Output('profile-rot-data', 'data'),
        Input('profile-rot-paths-store', 'data'),
        Input('profile-rot-upload', 'contents'),
        State('profile-rot-upload', 'filename'),
        prevent_initial_call = True
    )
    def upload_profile_rotations(profile_rot_paths, file_content, filenames):
        if ctx.triggered_id == 'profile-rot-paths-store' and profile_rot_paths != "":
            # the file path was set by the project file
            # create quasi-filename
            dirname = os.path.basename(profile_rot_paths['dir_path'])
            quasi_filename = os.path.join(dirname, profile_rot_paths['filename_prefix']) + "_*.csv"
            # load data from the files
            data = load_profile_rotations(profile_rot_paths['dir_path'], profile_rot_paths['filename_prefix'])
            return {"display": "none"}, {"display": "block"}, quasi_filename, data
        elif file_content is not None:
            # new files uploaded
            # create quasi-filename
            quasi_filename = filenames[0]
            if len(filenames) > 1: quasi_filename += ", ..."   # suggest that there are more files
            # load the data from files
            profile_rotations = [[] for i in range(4)]
            for i in range(len(filenames)):
                # decide which file is it
                index = 0
                if filenames[i][-6:-4] == "50":
                    index = 1
                elif filenames[i][-6:-4] == "75":
                    index = 2
                elif filenames[i][-7:-4] == "100":
                    index = 3
                # read the file
                content_type, content_string = file_content[i].split(',')
                decoded = base64.b64decode(content_string).decode("utf-8").split('\n')
                rotations_raw = load_space_separated_into_nparray(decoded)
                for rotation_raw in rotations_raw:
                    rotation = load_rotation(rotation_raw)
                    profile_rotations[index].append(rotation_to_inv_matrix(rotation))
            return {"display": "none"}, {"display": "block"}, quasi_filename, profile_rotations
        else:
            # it is the initial call
            return {"display": "block"}, {"display": "none"}, "", no_update
    

    # set a new video to the same time as the old video
    app.clientside_callback(
        """
        function(update_number, camera_pos) {
            const video = document.getElementById('background-video');
            const videoTime = window.vis.camera_timestamps[camera_pos];
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

    # these callback also serve to hide empty boxes at the start of the app:
    
    # delete project file
    @app.callback(
        Output('project-file-upload', 'contents'),
        Input('project-file-delete-button', 'n_clicks')
    )
    def delete_project_file(btn):
        return None
    
    # delete file with united point cloud
    @app.callback(
        Output('united-pc-upload', 'contents'),
        Input('united-pc-delete-button', 'n_clicks')
    )
    def delete_united_pc(btn):
        return None
    
    # delete files with divided point cloud
    @app.callback(
        Output('divided-pc-upload', 'contents'),
        Input('divided-pc-delete-button', 'n_clicks')
    )
    def delete_divided_pc(btn):
        return None

    # delete files with point cloud timestamps
    @app.callback(
        Output('pc-timestamps-upload', 'contents'),
        Input('pc-timestamps-delete-button', 'n_clicks')
    )
    def delete_pc_timestamps(btn):
        return None

    # delete file with video
    @app.callback(
        Output('video-upload', 'contents'),
        Input('video-delete-button', 'n_clicks')
    )
    def delete_video(btn):
        return None
    
    # delete files with vector data
    @app.callback(
        Output('vector-data-upload', 'contents'),
        Input('vector-data-delete-button', 'n_clicks')
    )
    def delete_vector_data(btn):
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
    
    # delete file with timestamps
    @app.callback(
        Output('timestamps-upload', 'contents'),
        Input('timestamps-delete-button', 'n_clicks')
    )
    def delete_timestamps(btn):
        return None
    
    # delete files with train profile translations
    @app.callback(
        Output('profile-trans-upload', 'contents'),
        Input('profile-trans-delete-button', 'n_clicks')
    )
    def delete_profile_trans(btn):
        return None

    # delete files with train profile translations
    @app.callback(
        Output('profile-rot-upload', 'contents'),
        Input('profile-rot-delete-button', 'n_clicks')
    )
    def delete_profile_rot(btn):
        return None

    # update window.vis.frames_cnt, the total time label as well as the range of the slider & input 
    # which control train position when new timestamps data is uploaded
    app.clientside_callback(
        """
        function(camera_timestamps) {
            window.vis.frames_cnt = camera_timestamps.length;
            
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

    # redefines the projection matrix according to the calibration matrix put in by the user
    @app.callback(
        Output('projection-matrix-store', 'data'),
        Input('calibration-matrix-textarea', 'value'),
        Input('far-plane-input', 'value'),
        prevent_initial_call=True
    )
    def redefine_projection_matrix(value, far_plane_raw):
        # parse the far plane value
        if (far_plane_raw == None):
            return no_update
        far_plane = int(far_plane_raw)

        # parse the calibration matrix
        rows = value.strip().split('\n')
        if len(rows) != 3:
            return no_update
        matrix = []
        for row in rows:
            if row[len(row) - 1] == ',':   # strip ',' at the ends of rows
                row = row[:-1]
            parsed_row_str = row.strip().split(',')
            if len(parsed_row_str) != 3:
                return no_update
            matrix.append([float(parsed_row_str[0]), float(parsed_row_str[1]), float(parsed_row_str[2])])
        calib_matrix = np.array(matrix)
        proj_matrix = calculate_projection_matrix(
            camera_params_dict={'Camera.width': 2048, 'Camera.height':1536},
            K=calib_matrix,
            far_plane=far_plane
        )
        return proj_matrix 
    
    # apply the new projection matrix
    app.clientside_callback(
        """
        function(proj_matrix) {
            window.vis.setProjectionMatrix(proj_matrix);
        }
        """,
        Input('projection-matrix-store', 'data'),
        prevent_initial_call=True
    )

    # parses the distortion parameters and saves them to a store
    @app.callback(
        Output('distortion-params-store', 'data'),
        Input('distortion-params-textarea', 'value'),
        prevent_initial_call=True
    )
    def parse_distortion_params(value):
        rows = value.strip().split('\n')
        params = []
        for row in rows:
            if row[len(row) - 1] == ',':   # strip ',' at the ends of rows
                row = row[:-1]
            parsed_row_str = row.strip().split(',')
            for param_str in parsed_row_str:
                params.append(float(param_str))
        if len(params) != 5:
            return no_update
        return params

    # pass new data from stores to visualization in deck.gl
    app.clientside_callback(
        """
        function(data_dict) {
            window.vis.data_dict = data_dict;
            window.vis.updateDeck();
        }
        """,
        Input('visualization-data', 'data')
    )
    app.clientside_callback(
        """
        function(united_pc_data) {
            window.vis.united_pc_data = united_pc_data;
            window.vis.updateDeck();
        }
        """,
        Input('united-pc-data', 'data')
    )
    app.clientside_callback(
        """
        function(profile_line_data) {
            window.vis.profile_line_data = profile_line_data;
            window.vis.updateDeck();
        }
        """,
        Input('profile-line-data', 'data')
    )
    app.clientside_callback(
        """
        function(vector_data) {
            window.vis.vector_data = vector_data;
            window.vis.updateDeck();
        }
        """,
        Input('vector-data', 'data')
    )
    app.clientside_callback(
        """
        function(camera_timestamps_data) {
            window.vis.camera_timestamps = camera_timestamps_data;
            window.vis.updateDeck();
        }
        """,
        Input('camera-timestamps-data', 'data')
    )
    app.clientside_callback(
        """
        function(pcl_timestamps_data) {
            window.vis.pcl_timestamps = pcl_timestamps_data;
            window.vis.updateDeck();
        }
        """,
        Input('pcl-timestamps-data', 'data')
    )
