"""Contains general use utility functions."""

import re
from itertools import permutations, product

from scipy import linalg
import numpy as np


def trace_matrix_squared(matrix: np.ndarray) -> float:

    """
    Returns the trace of the square of an input matrix.

    Parameters
    ----------
    matrix : array of array of complex
        The input square matrix whose square trace will be
        evaluated.

    Returns
    -------
    complex
        The trace of the square of the input matrix.
    """

    assert matrix.shape[0] == matrix.shape[1], 'Input matrix must be square.'

    return np.real(np.trace(np.matmul(matrix, matrix)))

def trace_distance(A: np.ndarray, B: np.ndarray) -> float:

    """
    Returns the trace distance between 2 quantum states (matrices)
    defined in H.-P. BREUER, E.-M. LAINE, AND J. PIILO, Measure
    for the Degree of Non-Markovian Behavior of Quantum Processes
    in Open Systems, Phys. Rev. Lett., 103 (2009), p. 210401,
    given by:

    .. math::
        D = 0.5 tr(|A - B|)

    where $|A| = (A^\\dagger A)^{frac{1}{2}}$ and $\\A$ is
    the density matrix at time t, and $\\B$ is a reference density
    matrix i.e. the equilibrium state.

    Parameters
    ----------
    A : np.ndarray
        The first array to use in calculation of the trace distance
    B : np.ndarray
        The second or reference array to use in calculation of the
        trace distance.

    Returns
    ------
    float
        The trace distance of the density matrix relative to the
        reference state.
    """

    diag = np.diag(np.absolute(eigv(A - B)))
    return 0.5 * np.trace(diag)

def renormalise_matrix(matrix: np.ndarray) -> np.ndarray:

    """
    Takes a matrix adnd renormalises it to trace=1 by dividing
    all elements by its trace.

    Parameters
    ----------
    matrix : np.ndarray
        The input matrix to renormalise

    Returns
    -------
    np.ndarray
        The renormalised matrix, with trace=1.
    """

    assert isinstance(matrix, np.ndarray), 'Must pass as numpy ndarray'
    assert np.trace(matrix) != 0., 'Input matrix cannot have trace zero.'

    return matrix / np.trace(matrix)

def commutator(A: np.ndarray, B: np.ndarray, anti: bool = False) -> complex:

    """
    Returns either the commutator:

    .. math::
        [A, B] = AB - BA

    or the anti-commutator:

    .. math::
        {A, B} = AB + BA

    of 2 square matrices A and B.

    Parameters
    ----------
    A, B : array of array of complex
        Input square matrices for which the (anti) commutator will be
        calculated.
    anti : bool
        If True calculates the anti-commutator of A and B, otherwise
        calculates just the commutator. Default value is False.

    Returns
    -------
    array of array of complex
        The (anti) commutator of A and B.
    """

    assert (A.shape[0] == A.shape[1]
            and B.shape[0] == B.shape[1]), 'Input matrices must be square.'

    if anti:
        return np.matmul(A, B) + np.matmul(B, A)

    return np.matmul(A, B) - np.matmul(B, A)

def eigv(A: np.ndarray) -> np.ndarray:

    """
    Returns the eigenvalues of an input matrix.

    Parameters
    ----------
    A : np.ndarray of complex
        A square 2D array.

    Returns
    -------
    np.ndarray
        An array of the eigenvalues of A.
    """

    return linalg.eig(A)[0]

def eigs(A: np.ndarray) -> np.ndarray:

    """
    Returns the eigenstates of an input matrix.

    Parameters
    ----------
    A : np.ndarray of complex
        A square 2D array.

    Returns
    -------
    np.ndarray
        An array of the eigenstates of A, where the columns
        give the eigenstate for each eigenvalue.
    """

    return linalg.eig(A)[1]

def basis_change(matrix: np.ndarray, states: np.ndarray,
                 liouville: bool = False) -> np.ndarray:

    """
    Transforms a matrix expressed in Liouville space into the basis
    expressed by the states matrix.

    Parameters
    ----------
    matrix : np.ndarray
        The matrix to be transformed. If in Liouville space, must
        set 'liouville=True' and 'matrix' must have dimensions
        N^2 x N^2. Otherwise, pass in N x N dimensions.
    states : np.ndarray
        The Hilbert space of states in the basis into which
        'matrix' will be transformed, of dimensions N x N. 'states'
        must be orthogonal (i.e. that states^{dagger} states = I),
        and each column must correspond to an eigenstate.
    liouville : bool
        Whether or not the input matrix 'matrix' is given in
        Liouville space. If True, 'matrix' must be given in
        dimensions N^2 x N^2 and 'states' as N x N. If False
        (default), both 'matrix' and 'states' must be N x N.

    Returns
    -------
    np.ndarray
        The input matrix transformed. Has dimensions N^2 x N^2 if
        'matrix' passed in Liouville space, or N x N otherwise.
    """

    # Check 'matrix' and 'states' are square
    assert (matrix.shape[0] == matrix.shape[1]
            and states.shape[0] == states.shape[1]), (
                'Input matrices must be square.')
    assert isinstance(liouville, bool), 'Must pass liouville as a bool.'

    # Perform transformation
    if liouville:
        assert matrix.shape[0] == states.shape[0]**2, (
            'If providing an input matrix in Liouville space it must have'
            ' dimensions N^2 x N^2, where the eigenstates matrix has dimensions'
            ' N x N.')
        states = np.kron(states, states.conjugate())
    # Check for orthogonality
    # assert np.allclose(np.matmul(states, states.conjugate().T),
    #                    np.eye(matrix.shape[0]))
    return np.matmul(states, np.matmul(matrix, states.conjugate().T))

def lowest_non_zero_eigv(eigvals: np.ndarray) -> float:

    """
    Takes an array of eigenvalues, in units of rad ps^-1, and
    returns the lowest non-zero eigenvalue in units of fs.

    Parameters
    ----------
    eigvals : np.ndarray
        An array of eigenvalues, in rad ps^-1

    Returns
    -------
    float
        The lowest non-zero eigenvalue, in units of fs.
    """

    eigvals = np.round(np.absolute(eigvals), decimals=15)
    mask = (eigvals > 0)
    min_eigv = min(eigvals[mask])  # Take lowest non-zero eigenvalue
    min_eigv *= 1e-3  # Convert rad ps^-1 --> rad fs^-1
    lifetime = np.absolute(min_eigv)**-1  # Inverse; frequency ---> time

    return lifetime

def elements_from_str(sites: int, elements: str) -> list:

    """
    Generates a list of elements of the density matrix from a
    string representation. For instance, if elements='all' and
    sites=3, this function will return ['11', '12', '13', '21',
    '22', '23', '31', '32', '33'], if elements='diagonals' will
    return ['11', '22', '33'], and if elements='off-diagonals'
    will return ['12', '13', '21', '23', '31', '32'].

    Parameters
    ----------
    sites : int
        The number of sites in the Open Quantum System.
    elements : str
        The numerical string representations of the elements of
        the square density matrix to return. Either 'all',
        'diagonals', or 'off-diagonals'.

    Returns
    -------
    list
        A list of numerical string representations of density
        matrix elements.

    Raises
    ------
    ValueError
        If an invalid input for the elements is passed.
    """

    # Check elements input
    if elements is None:
        return None
    if isinstance(elements, list):
        assert len(elements) <= sites ** 2, (
            'The number of elements plotted must be a positive integer less'
            ' than or equal to the number of elements in the density matrix.')
        for element in elements:
            try:
                int(element)
            except ValueError:
                raise ValueError('Invalid format of string representation of'
                                 ' density matrix element.')
        return elements
    if isinstance(elements, str):
        assert elements in ['all', 'diagonals', 'off-diagonals'], (
            'Must choose from "all", "diagonals", or "off-diagonals".')
        if elements == 'all':
            return [str(i) + str(j)
                    for i, j in product(range(1, sites + 1), repeat=2)]
        if elements == 'diagonals':
            return [str(i) + str(i) for i in range(1, sites + 1)]
        # Off-diagonals
        return [str(i) + str(j)
                for i, j in permutations(range(1, sites + 1), 2)]
    raise ValueError('elements argument passed as invalid value.')

def types_of_elements(elements):

    """
    Characterises whether all the elements passed in the input list
    are 'diagonals' (i.e. if elements=['11', '22', '33']),
    'off-diagonals' (i.e. if elements=['12', '21', '42']), or 'both'
    (i.e. if elements=['11', '22', '21', '12']). String descriptions
    of 'diagonals', 'off-diagonals', or 'all' may also be passed.

    Parameters
    ----------
    elements : list of str
        A list of string represntations of the elements of a
        matrix, numbered with indexing starting at 1; i.e ['11',
        '12', '21', '22']. Alternatively, the string description
        can also be passed, in accordance with the specification
        for the elements argument to the
        figures.complex_space_time() method.

    Returns
    -------
    str
        The characterisation of the list of elements as a whole,
        returning either 'diagonals', 'off-diagonals', or 'both'.
    None
        If the value of elements is passed as None.
    """
    # If elements is passed as None
    if elements is None:
        return None

    # If elements pass as 'all', 'off_diagonals', or 'diagonals'
    if isinstance(elements, str):
        assert elements in ['all', 'off-diagonals', 'diagonals']
        if elements == 'all':
            return 'both'
        return elements

    # If elements are passed in list form i.e. ['11', '21', ...]
    if isinstance(elements, list):
        if all([int(element[0]) == int(element[1]) for element in elements]):
            return 'diagonals'
        if all([int(element[0]) != int(element[1]) for element in elements]):
            return 'off-diagonals'
        return 'both'

    raise ValueError('Incorrect format for elements')

def convert_args_to_latex(file: str) -> list:

    """
    Takes the file created when plotting figures with 'save=True'
    with quantum_HEOM and converts the arguments into strings
    that render correctly in LaTeX, printing them to console.
    The 2 lines corrspond to the 2 sets of arguments for 1)
    initialising the QuantumSystem object and 2) calling its
    plot_time_evolution() method.

    Parameters
    ----------
    file : str
        The absolute path of the input file.
    """

    args = []
    with open(file, 'r') as f:
        for line in f:
            if line.startswith('args') or line.startswith('plot_args'):
                line = line.replace('\'', '\"').replace(', "', ', \\newline "')
                line = line.replace('{', '\{').replace('}', '\}')
                line = line.replace('_', '\_')
                args.append(line)
    return args

def write_args_to_file(systems, plot_args: dict, filename: str):

    """
    Writes a file of name 'filename' that contains the arguments
    used to define a QuantumSystem object and plot its dynamics.

    Parameters
    ----------
    systems : list of QuantumSystem
        The QuantumSystem objects whose dynamics have been plotted.
    plot_args : dict
        The arguments passed to the plot_dynamics() method,
        used to plot the dynamics of the systems.
    filename : str
        The absolute path of the file to be created.
    """

    # Define names of all systems plotted and args used to be written to file
    sys_names, arg_names = [], []
    for i in range(1, len(systems) + 1):
        sys_names.append('q' + str(i))
        arg_names.append('args' + str(i))
    # Write file header
    with open(filename, 'w+') as f:
        f.write('-------------------------------------------------------\n')
        f.write('Arguments for reproducing figure in file of name:\n')
        f.write(filename.replace('.txt', '.pdf') + '\n')
        f.write('-------------------------------------------------------\n')
        f.write('\n')
    # Write args to file as Python copyable text
    with open(filename, 'a+') as f:
        f.write('-------------------------------------------------------\n')
        f.write('ARGS IN PYTHON-FUNCTIONAL CODE:\n')
        f.write('-------------------------------------------------------\n')
        for idx, sys in enumerate(systems):
            args = re.sub(' +', ' ', str(sys.__dict__).replace("\'_", "\'"))
            args = args.replace('\n', '')
            f.write('# Args for initialising QuantumSystem '
                    + str(idx + 1) + '\n')
            f.write(arg_names[idx] + ' = ' + args + '\n')
        plot_args = re.sub(' +', ' ', str(plot_args))
        plot_args = plot_args.replace('\n', '')
        if 'dynamics' in filename:
            f.write('# Arguments for plotting dynamics\n')
        elif 'spectral_density' in filename:
            f.write('# Arguments for plotting spectral density\n')
        else:
            raise ValueError('Incorrectly named files')
        f.write('plot_args = ' + plot_args + '\n')
        f.write('\n\n')
        f.write('# Use the arguments in the following way:\n')
        f.write('from quantum_heom.quantum_system import QuantumSystem\n')
        f.write('from quantum_heom import figures as figs\n\n')
        for sys, arg in zip(sys_names, arg_names):
            f.write(sys + ' = QuantumSystem(**' + arg + ')\n')
        if 'dynamics' in filename:
            f.write('figs.plot_dynamics([' + sys_names[0])
        elif 'spectral_density' in filename:
            f.write('figs.plot_spectral_density([' + sys_names[0])
        else:
            raise ValueError('Incorrectly named files')
        for idx in range(1, len(sys_names)):
            f.write(', ' + sys_names[idx])
        f.write('], **plot_args)\n')
        f.write('-------------------------------------------------------\n')
        f.write('\n')
    # Write args to file as LaTeX-renderable text
    with open(filename, 'a+') as f:
        args = convert_args_to_latex(filename)
        f.write('-------------------------------------------------------\n')
        f.write('ARGS IN LATEX-RENDERABLE FORMAT:\n')
        f.write('-------------------------------------------------------\n')
        for arg in args:
            f.write(arg + '\n')
        f.write('-------------------------------------------------------\n')
