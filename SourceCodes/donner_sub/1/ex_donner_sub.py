import openmdao.api as om
import dymos as dm

from donner_sub_ode import DonnerSubODE


p = om.Problem(model=om.Group())

traj = dm.Trajectory()

phase = dm.Phase(ode_class=DonnerSubODE, transcription=dm.GaussLobatto(num_segments=30, order=3, compressed=False))

phase.set_time_options(units=None, targets=['threat_comp.time'], fix_initial=True, duration_bounds=(0.1, 100))
phase.add_state('x', rate_source='eom_comp.dx_dt', targets=['nav_comp.x'], fix_initial=True, fix_final=True)
phase.add_state('y', rate_source='eom_comp.dy_dt', targets=['nav_comp.y'], fix_initial=True, fix_final=True)

phase.add_design_parameter('v', targets=['eom_comp.v'], opt=True, upper=5, lower=0.1)
phase.add_control('phi', targets=['eom_comp.phi'], units='rad')

phase.add_path_constraint('threat_comp.sub_range', lower=0)

phase.add_timeseries_output('nav_comp.r_ship', shape=(1,))
# phase.add_timeseries_output('threat_comp.sub_range', shape=(1,))

phase.add_objective(name='v', loc='initial')

traj.add_phase('phase0', phase=phase)
p.model.add_subsystem('traj', traj)

p.driver = om.pyOptSparseDriver()
p.driver.options['optimizer'] = 'SNOPT'
p.driver.opt_settings['iSumm'] = 6
# p.driver.declare_coloring()

p.setup(force_alloc_complex=True)

p.set_val('traj.phase0.t_initial', value=0)
p.set_val('traj.phase0.t_duration', value=1.0)
p.set_val('traj.phase0.states:y', value=phase.interpolate(ys=[0, 0], nodes='state_input'))
p.set_val('traj.phase0.states:x', value=phase.interpolate(ys=[-1, 1], nodes='state_input'))
p.set_val('traj.phase0.controls:phi', value=phase.interpolate(ys=[90, 90], nodes='control_input'), units='deg')
p.set_val('traj.phase0.design_parameters:v', value=2.0)

p.run_driver()

exp_out = traj.simulate()

import matplotlib.pyplot as plt

speed = p.get_val('traj.phase0.timeseries.design_parameters:v')

lat = p.get_val('traj.phase0.timeseries.states:y')
lon = p.get_val('traj.phase0.timeseries.states:x')

lat_x = exp_out.get_val('traj.phase0.timeseries.states:y')
lon_x = exp_out.get_val('traj.phase0.timeseries.states:x')

fig, ax = plt.subplots(1, 1)
ax.set_aspect('equal')
ax.plot(lon, lat, 'ro')
ax.plot(lon_x, lat_x, 'k-')
ax.text(0, -0.1, f'speed = {speed[0, 0]:6.4f}')
plt.show()
