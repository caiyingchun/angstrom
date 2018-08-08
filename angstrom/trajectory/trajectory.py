"""
--- Ångström ---
Read, manipulate and analyze molecular trajectory files.
"""
from .read import read_xyz_traj
from .write import write_xyz_traj
from .tools import non_periodic_coordinates
from angstrom.geometry import get_molecule_center
import numpy as np


class Trajectory:
    """
    Reading and analyzing trajectories in xyz format.

    """
    def __init__(self, atoms=None, coordinates=None, read=None):
        """
        Create a trajectory object.

        Parameters
        ----------
        atoms : list or None
            List of elements of the molecule for each frame.
        coordinates : list or None
            List of atomic positions of the molecule for each frame.
        read : str or None
            File name to read molecule file (formats: xyz).

        """
        if atoms is not None and coordinates is not None:
            self.atoms = atoms
            self.coordinates = coordinates
        elif read is not None:
            self.read(read)
        else:
            self.atoms = []
            self.coordinates = []

    def __repr__(self):
        """
        Returns basic trajectory info.

        """
        return "<Trajectory frames: %i | atoms: %i | dimensions: %i>" % tuple(np.shape(self.coordinates))

    def __len__(self):
        """
        Returns number of frames.

        """
        return len(self.atoms)

    def __add__(self, traj):
        """
        Trajectory addition for joining the coordinates and elements into a new Trajectory object.

        Parameters
        ----------
        traj : Trajectory
            Trajectory object to be added

        Returns
        -------
        Trajectory
            Joined Trajectory object.

        """
        new_traj = Trajectory(atoms=np.append(self.atoms, traj.atoms, axis=0),
                              coordinates=np.append(self.coordinates, traj.coordinates, axis=0))
        return new_traj

    def read(self, filename):
        """
        Read xyz formatted trajectory file.

        Parameters
        ----------
        filename : str
            Trajectory file name.

        Returns
        -------
        None
            Assigns 'coordinates', 'atoms', and 'headers' attributes.

        """
        traj = read_xyz_traj(filename)
        self.atoms, self.coordinates, self.headers = traj['atoms'], traj['coordinates'], traj['headers']

    def write(self, filename):
        """
        Write xyz formatted trajectory file.

        Parameters
        ----------
        filename : str
            Trajectory file name (formats: xyz).

        Returns
        -------
        None
            Writes molecule information to given file name.

        """
        with open(filename, 'w') as traj_file:
            if hasattr(self, 'headers'):
                write_xyz_traj(traj_file, self.atoms, self.coordinates, headers=self.headers)
            else:
                write_xyz_traj(traj_file, self.atoms, self.coordinates)

    def get_center(self, mass=True):
        """
        Get coordinates of molecule center at each frame.

        Parameters
        ----------
        mass : bool
            Calculate center of mass (True) or geometric center (False).

        Returns
        -------
        ndarray
            Molecule center coordinates for each frame.

        """
        centers = np.empty((len(self.atoms), 3))
        for f, (frame_atoms, frame_coors) in enumerate(zip(self.atoms, self.coordinates)):
            centers[f] = get_molecule_center(frame_atoms, frame_coors, mass=mass)
        return centers

    def get_msd(self, coordinates, reference=0):
        """
        Calculate mean squared displacement (MSD) for given 1D coordinates.

        Parameters
        ----------
        coordinates : ndarray
            List of 1D coordinates.
        reference : int
            Index for reference frame (default: 0).

        Returns
        -------
        float: Mean squared displacement

        Example (calculate MSD for the first atom in x direction for each frame):
            >>> traj.get_msd(traj.coordinates[:, 0, 0])
        """
        ref_coor = coordinates[reference]
        return np.average(np.power((coordinates - ref_coor), 2))
