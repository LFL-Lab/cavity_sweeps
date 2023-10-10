"""
========================================================================================================================
SimulationConfig
========================================================================================================================
"""

from qiskit_metal.analyses.quantization import EPRanalysis
from utils import *

class SimulationConfig:
    def __init__(self, design_name="CavitySweep", renderer_type="hfss", sim_type="eigenmode",
                 setup_name="Setup", max_passes=50, max_delta_f=0.05, min_converged_passes=2, Lj=0, Cj=0):
        self.design_name = design_name
        self.renderer_type = renderer_type
        self.sim_type = sim_type
        self.setup_name = setup_name
        self.max_passes = max_passes
        self.max_delta_f = max_delta_f
        self.min_converged_passes = min_converged_passes
        self.Lj = Lj
        self.Cj = Cj


def start_simulation(design, config):
    """
    Starts the simulation with the specified design and configuration.

    :param design: The design to be simulated.
    :param config: The configuration settings for the simulation.
    :return: A tuple containing the EPR analysis object and the HFSS object.
    """
    epra = EPRanalysis(design, config.renderer_type)
    hfss = epra.sim.renderer
    print("Starting the Simulation")
    hfss.start()
    hfss.new_ansys_design(config.design_name, config.sim_type)
    return epra, hfss


def set_simulation_hyperparameters(epra, config):
    """
    Sets the simulation hyperparameters based on the provided configuration.

    :param epra: The EPR analysis object.
    :param config: The configuration settings for the simulation.
    :return: The setup object with the updated settings.
    """
    setup = epra.sim.setup
    setup.name = config.setup_name
    setup.max_passes = config.max_passes
    setup.max_delta_f = config.max_delta_f
    setup.min_converged_passes = config.min_converged_passes
    setup.n_modes = 1
    setup.vars = {'Lj': f'{config.Lj}nH', 'Cj': f'{config.Cj}fF'}
    return setup


def render_simulation_with_ports(epra, ansys_design_name, setup_vars, coupler):
    """
    Renders the simulation into HFSS.

    :param epra: The EPR analysis object.
    :param ansys_design_name: The name of the Ansys design.
    :param setup_vars: The setup variables for the rendering.
    :param coupler: The coupler object.
    """
    epra.sim._render(name=ansys_design_name,
                     solution_type='eigenmode',
                     vars_to_initialize=setup_vars,
                     open_pins=[(coupler.name, "prime_start"), (coupler.name, "prime_end")],
                     port_list=[(coupler.name, 'prime_start', 50), (coupler.name, "prime_end", 50)],
                     box_plus_buffer=False)
    print("Sim rendered into HFSS!")

def render_simulation_no_ports(epra, components, open_pins, ansys_design_name, setup_vars):
    """
    Renders the simulation into HFSS.

    :param epra: The EPR analysis object.
    :param ansys_design_name: The name of the Ansys design.
    :param setup_vars: The setup variables for the rendering.
    :param components: List of QComponent object.
    """
    epra.sim._render(name=ansys_design_name,
                     selection=[qcomp.name for qcomp in components],
                     open_pins=open_pins,
                     solution_type='eigenmode',
                     vars_to_initialize=setup_vars,
                     box_plus_buffer=False)
    print("Sim rendered into HFSS!")


if __name__ == "__main__":
    # Usage
    config = SimulationConfig()
    bbox = generate_bbox(coupler)
    epra, hfss = start_simulation(design, config)
    setup = set_simulation_hyperparameters(epra, config)
    render_simulation(epra, config.design_name, setup.vars, coupler)
    modeler = hfss.pinfo.design.modeler
