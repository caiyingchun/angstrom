"""
--- Ångström ---
Blender visualization adapter and configuration.
Molecular visualization models for Blender.
"""
import os
import yaml
import pickle
import subprocess
from pprint import pprint


IMG_SCRIPT = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'blender_image.py')
SEQ_SCRIPT = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'blender_sequencer.py')

default_model = {'use_center': True,               # Position object to origin
                 'use_camera': False,              # Add camera
                 'use_lamp': False,                # Add lamp
                 'ball': '0',                      # Type of ball -> 0: NURBS | 1: Mesh | 2: Meta
                 'mesh_azimuth': 32,               # Number of sectors (azimuth)
                 'mesh_zenith': 32,                # Number of sectors (zenith)
                 'scale_ballradius': 0.5,          # Scale factor for all atom radii
                 'scale_distances': 1,             # Scale factor for all distances
                 'atomradius': '2',                # Type of radius -> 0: Pre-defined | 1: Atomic radius | 2: van der Waals
                 'use_sticks': True,               # Use bonds as cylinders
                 'use_sticks_type': '0',           # Sticks type -> 0: Dupliverts | 1: Skin | 2: Normal
                 'sticks_subdiv_view': 2,          # Number of subdivisions (view)
                 'sticks_subdiv_render': 2,        # Number of subdivisions (render)
                 'sticks_sectors': 20,             # Number of sectors of a stick
                 'sticks_radius': 0.25,            # Radius of a stick
                 'sticks_unit_length': 0.05,       # Length of the unit of a stick in Angstrom
                 'use_sticks_color': True,         # The sticks appear in the color of the atoms
                 'use_sticks_smooth': True,        # The sticks are round (sectors are not visible)
                 'use_sticks_bonds': False,        # Show double and tripple bonds.
                 'sticks_dist': 1.1,               # Distance between sticks measured in stick diameter (min:1 / max:3)
                 'use_sticks_one_object': True,    # All sticks are one object
                 'use_sticks_one_object_nr': 200   # Number of sticks to be grouped at once
                 }

ball_and_stick_model = {'scale_ballradius': 0.5,
                        'sticks_radius': 0.2
                        }

space_filling_model = {'scale_ballradius': 1,
                       'atomradius': '2',
                       'use_sticks': False
                       }

stick_model = {'scale_ballradius': 0.0,
               'sticks_radius': 0.2,
               'use_sticks_type': '0'
               }

surface_model = {'ball': '2',
                 'use_sticks': False
                 }

MODELS = {'default': default_model,
          'ball_and_stick': ball_and_stick_model,
          'space_filling': space_filling_model,
          'stick': stick_model,
          'surface': surface_model
          }

COLORS = {'Carbon': (0.05, 0.05, 0.05),
          'Hydrogen': (1.00, 1.00, 1.00),
          'Nitrogen': (0.18, 0.34, 0.95),
          'Oxygen': (0.70, 0.00, 0.00)
          }

SCRIPTS = {'img': IMG_SCRIPT, 'seq': SEQ_SCRIPT}

PI = 3.14159265359


class Blender:
    """
    Blender visualization adapter and configuration.
    """
    def __init__(self, read=None):
        """
        Initializes Blender visualization adapter with default configuration.
        """
        self.models = MODELS
        self.colors = COLORS
        if read is not None:
            self.read_config(read)
        else:
            self.config = self.configure()

    def configure(self, mol_file='', img_file='', img_format='PNG',
                  images=[], vid_file='', vid_format='AVI_JPEG', fps=10,
                  script='img', render=True, save='',
                  model='default', colors=COLORS, background_color=None,
                  resolution=(1920, 1080), brightness=1.0, lamp=2.0,
                  camera_zoom=20, camera_distance=10, camera_view='xy', camera_type='ORTHO',
                  verbose=False, pickle='temp-config.pkl', executable='blender'):
        """
        Get Blender image rendering settings.

        Parameters
        ----------
        mol_file : str
            Molecule file name to read.
        img_file : str
            Image file name to save ('png' file format is recommended).
        img_format : str
            Image file format ([PNG] | JPEG | TIFF | BMP and more)
        images : list
            List of image paths for sequencer.
        vid_file : str
            Video file name (sequencer only).
        vid_format : str
            Video file format ([AVI_JPEG] | AVI_RAW | FFMPEG | H264 | XVID)
        fps : int
            Frame per second for the video.
        script : str
            Python script to run ([img] | seq).
                - img: Renders image of a molecule using pdb reader.
                - seq: Sequence images to create a video.
        render : bool
            Render image switch.
        save : str
            Saves .blend file to given filename.
        model : str
            Molecule model (default | ball-and-stick | space_filling).
        colors : dict
            Atom colors in RGB (0 - 1) | ex: {'Carbon': (0.1, 0.1, 0.1), 'Oxygen': (0.7, 0.0, 0.0)}.
        background_color : tuple or None
            Background color in RGB (0 - 1) | ex: (1.0, 1.0, 1.0) for white. None for transparent.
        resolution : tuple
            Image resolution (default: 1920 x 1080).
        brightness : float
            Brightness [environment lightning] (default: 1.0).
        lamp : float
            Lamp strength (default: 2).
        camera_zoom : float
            Camera zoom / focal length (default: 20).
        camera_distance : float
            Distance between the camera and the molecule (default: 10).
        camera_view : str
            Camera view plane (xy | xz | yx | yz | zx | zy).
        camera_type : str
            Camera type (ORTHO | PERSP).
        verbose : bool
            Blender subprocess verbosity.
        pickle : str
            Pickle file for communicating settings with Blender.
        executable : str
            Path to blender executable (depends on OS).

        Returns
        -------
        dict
            Blender render settings.

        """
        d = camera_distance
        VIEW = {'xy': dict(location=[0, 0, d], rotation=[0, 0, 0]),
                'xz': dict(location=[0, -d, 0], rotation=[PI / 2, 0, 0]),
                'yx': dict(location=[0, 0, -d], rotation=[0, PI, -PI / 2]),
                'yz': dict(location=[d, 0, 0], rotation=[PI / 2, 0, PI / 2]),
                'zx': dict(location=[0, d, 0], rotation=[PI / 2, -PI / 2, PI]),
                'zy': dict(location=[-d, 0, 0], rotation=[PI / 2, -PI / 2, -PI / 2])}

        config = {'pdb': {**{'filepath': mol_file}, **self.models[model]},
                  'img_file': img_file, 'img_format': img_format,
                  'vid_file': vid_file, 'vid_format': vid_format, 'images': images, 'fps': fps,
                  'camera': dict(location=VIEW[camera_view]['location'],
                                 rotation=VIEW[camera_view]['rotation'],
                                 type=camera_type, zoom=camera_zoom),
                  'brightness': brightness, 'lamp': lamp, 'resolution': resolution,
                  'colors': colors, 'background_color': background_color,
                  'verbose': verbose, 'render': render, 'save': save,
                  'executable': executable, 'script': SCRIPTS[script], 'pickle': pickle}
        self.config = config
        return config

    def write_config(self, config_file):
        """
        Write config pickle file to send config information to Blender.

        Parameters
        ----------
        config_file : str
            Pickle file name.

        Returns
        -------
        None
            Writes pickle config file.
        """
        with open(config_file, 'wb') as handle:
            pickle.dump(self.config, handle, protocol=pickle.HIGHEST_PROTOCOL)


    def read_config(self, config_file):
        """
        Read config yaml file.

        Parameters
        ----------
        config_file : str
            Yaml file name.

        Returns
        -------
        None
            Configures Blender object.

        Notes
        -----
        The 'script' variable in the config file is changed to the path of the actual script after
        reading the config. This is to make sure correct path is selected. In the config file
        user can simply write 'img' or 'vid' to select image or video rendering.
        """
        with open(config_file, 'r') as f:
            self.config = yaml.load(f)
        self.config['script'] = SCRIPTS[self.config['script']]

    def print_config(self):
        """
        Print Blender render configuration.

        Parameters
        ----------
        None

        Returns
        -------
        None
            Prints configuration.
        """
        pprint(self.config)

    def run(self):
        """
        Run Blender in the background using subprocess and following command:
            >>> blender --background --python blender_image.py -- temp-config.pkl

        Parameters
        ----------
        None

        Returns
        -------
        None
            Runs Blender Python script.
        """
        self.write_config(self.config['pickle'])
        command = [self.config['executable'], '--background', '--python', self.config['script'], '--', self.config['pickle']]
        with open(os.devnull, 'w') as null:
            blend = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = blend.stdout.decode(), blend.stderr.decode()
            if self.config['verbose']:
                print("Stdout:\n\n%s\nStderr:\n%s" % (stdout, stderr))
        if os.path.exists(self.config['pickle']):
            os.remove(self.config['pickle'])
