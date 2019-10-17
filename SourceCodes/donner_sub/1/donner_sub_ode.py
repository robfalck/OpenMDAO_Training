import openmdao.api as om

from ship_radius_comp import ShipRadiusComp
from ship_eom_comp import ShipEOMComp

class DonnerSubODE(om.Group):

    def initialize(self):
        self.options.declare('num_nodes', types=int)

    def setup(self):
        nn = self.options['num_nodes']

        self.add_subsystem('eom_comp', ShipEOMComp(num_nodes=nn))
        self.add_subsystem('nav_comp', ShipRadiusComp(num_nodes=nn))
        self.add_subsystem('threat_comp', om.ExecComp('sub_range = r_ship - time',
                                                      sub_range={'shape': (nn,)},
                                                      r_ship={'shape': (nn,)},
                                                      time={'shape': (nn,)}))

        self.connect('nav_comp.r_ship', 'threat_comp.r_ship')


