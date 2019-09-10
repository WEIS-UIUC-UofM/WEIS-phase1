# Copyright 2019 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import numpy as np
from ccblade import CCAirfoil, CCBlade
from scipy import interpolate, gradient

from WTC_toolbox import turbine as wtc_turbine

turbine = wtc_turbine.Turbine()

# Some useful constants
pi = np.pi
r2d = 180/pi         # radians to degrees
d2r = pi/180         # degrees to radians


class Controller():
    """
    Class controller can be used to read in / write out controller param files
    And update tunings
    """

    def __init__(self):
        """
        Maybe just initialize the internal variables
        This also lists what will need to be defined
        """
        pass

    def read_param_file(self, param_file):
        """
        Load the parameter files directly from a FAST input deck
        """
        # Pitch Controller Parameters
        self.PC_zeta = param_file.PC_zeta            # Pitch controller damping ratio (-)
        self.PC_omega = param_file.PC_omega                # Pitch controller natural frequency (rad/s)
        
        # Torque Controller Parameters
        self.VS_zeta = param_file.VS_zeta            # Torque controller damping ratio (-)
        self.VS_omega = param_file.VS_omega                # Torque controller natural frequency (rad/s)
        
        # Setpoint Smoother Parameters
        self.Kss_PC = param_file.Kss_PC              # Pitch controller reference gain bias 
        self.Kss_VS = param_file.Kss_VS              # Torque controller reference gain bias
        self.Vmin = turbine.VS_Vmin                  # Cut-in wind speed (m/s)
        self.Vrat = turbine.PC_Vrated                # Rated wind speed (m/s)
        self.Vmax = turbine.PC_Vmax                  # Cut-out wind speed (m/s), -- Does not need to be exact


    def write_param_file(self, param_file):
        """
        Load the parameter files directly from a FAST input deck
        """

    def tune_controller(self, turbine):
        """
        Given a turbine model, tune the controller parameters
        """
        # -------------Load Parameters ------------- #
        # Re-define Turbine Parameters for shorthand
        J = turbine.J                           # Total rotor inertial (kg-m^2) 
        rho = turbine.rho                       # Air density (kg/m^3)
        R = turbine.RotorRad                    # Rotor radius (m)
        Ar = np.pi*R**2                         # Rotor area (m^2)
        Ng = turbine.Ng                         # Gearbox ratio (-)
        RRspeed = turbine.RRspeed               # Rated rotor speed (rad/s)
        
        # Cp Surface and related
        CP = turbine.CP                         # Turbine CP surface
        cp_interp = turbine.cp_interp           # Interpolation function for Cp surface values
        ct_interp = turbine.ct_interp           # Interpolation function for Ct surface values
        cq_interp = turbine.cq_interp           # Interpolation function for Cq surface values


        # Load controller parameters 
        #   - should be self.read_param_file() eventually, hard coded for now
        self.controller_params()

        # Re-define controller tuning parameters for shorthand
        PC_zeta = self.PC_zeta                  # Pitch controller damping ratio
        PC_omega = self.PC_omega                # Pitch controller natural frequency (rad/s)
        VS_zeta = self.VS_zeta                  # Torque controller damping ratio (-)
        VS_omega = self.VS_omega                # Torque controller natural frequency (rad/s)
        Vrat = self.Vrat                        # Rated wind speed (m/s)
        Vmin = turbine.Vmin                     # Cut in wind speed (m/s)
        Vmax = turbine.Vmax                     # Cut out wind speed (m/s)
 
        # -------------Define Operation Points ------------- #
        TSR_rated = RRspeed*R/Vrat  # TSR at rated

        # separate wind speeds by operation regions
        v_br = np.arange(Vmin,Vrat,0.1)             # below rated
        v_ar = np.arange(Vrat,Vmax,0.1)             # above rated
        v = np.concatenate((v_br, v_ar))

        # separate TSRs by operations regions
        TSR_br = np.ones(len(v_br))*turbine.TSR_opt # below rated     
        TSR_ar = RRspeed*R/v_ar                     # above rated
        TSR_op = np.concatenate((TSR_br, TSR_ar))   # operational TSRs

        # Find Operational CP values
        CP_above_rated = turbine.cp_interp(0,TSR_ar[0])            # Cp during rated operation (not optimal). Assumes cut-in bld pitch to be 0
        CP_op_br = np.ones(len(v_br)) * turbine.CP_max  # below rated
        CP_op_ar = CP_above_rated * (TSR_ar/TSR_rated)**3          # above rated
        CP_lin = np.concatenate((CP_op_br, CP_op_ar))   # operational CPs to linearize around
        pitch_initial_rad = turbine.pitch_initial_rad
        TSR_initial = turbine.TSR_initial

        pitch_op = np.zeros(len(TSR_op))
        CP_op = np.zeros(len(TSR_op))
        # ------------- Find Linearized State Matrices ------------- #

        # Find gradients
        CP_grad_TSR, CP_grad_pitch = gradient(turbine.CP)
        dCPdBeta_interp = interpolate.interp2d(pitch_initial_rad, TSR_initial, CP_grad_pitch, kind='cubic')
        dCPdTSR_interp = interpolate.interp2d(pitch_initial_rad, TSR_initial, CP_grad_TSR, kind='cubic')

        for i in range(len(TSR_op)):
            tsr = TSR_op[i]

            # Find pitch angle as a function of linearized operating CP for each TSR
            self.CP_TSR = np.ndarray.flatten(turbine.cp_interp(turbine.pitch_initial_rad, tsr))
            CP_lin[i] = np.maximum( np.minimum(CP_lin[i], np.max(self.CP_TSR)), np.min(self.CP_TSR))
            f_cp_pitch = interpolate.interp1d(self.CP_TSR,pitch_initial_rad) 
            pitch_op[i] = f_cp_pitch(CP_lin[i])
            
        
            # Find "operational" CP and derivatives 
            CP_op = turbine.cp_interp(pitch_op[i],tsr) 
                        

        # Store some variables
        self.v = v          # Wind speed (m/s)
        self.CP_lin = CP_lin     # Operational power coefficients
        self.CP_op = CP_op
        self.pitch_op = pitch_op
        self.TSR_op = TSR_op
# % Linearized operation points
# [CpGrad_Beta,CpGrad_TSR] = gradient(Cpmat,1);

# Cp(toi) = interp2(Betavec,TSRvec,Cpmat,Beta_op(toi),tsr);
# dCpdB(toi) = interp2(Betavec,TSRvec,CpGrad_Beta,Beta_op(toi),tsr)./Beta_del;
# dCpdTSR(toi) = interp2(Betavec,TSRvec,CpGrad_TSR,Beta_op(toi),tsr)./TSR_del;

# %% Final derivatives and system "matrices"
# dtdb(toi) = Ng/2*rho*Ar*R*(1/tsr_sat(toi))*dCpdB(toi)*vv(toi)^2;
# dtdl = Ng/(2)*rho*Ar*R*vv(toi)^2*(1/tsr_sat(toi)^2)* (dCpdTSR(toi)*tsr_sat(toi) - Cp(toi)); % assume operating at optimal
# dldo = R/vv(toi)/Ng;
# dtdo = dtdl*dldo;

# A(toi) = dtdo/J;            % Plant pole
# B_t = -Ng^2/J;              % Torque input gain 
# Bb(toi) = dtdb(toi)/J;     % BldPitch input gain

# %% Wind Disturbance Input gain
# % dldv = -tsr/vv(toi); 
# % dtdv = dtdl*dldv;
# % B_v = dtdv/J;

# end

# Beta_del = Betavec(2) - Betavec(1);
# TSR_del = TSRvec(2) - TSRvec(1);
            
    def controller_params(self):
    # Hard coded controller parameters for turbine. Using this until read_param_file is good to go
    #           - Coded for NREL 5MW 

        # Pitch Controller Parameters
        self.PC_zeta = 0.7                      # Pitch controller damping ratio (-)
        self.PC_omega = 0.6                     # Pitch controller natural frequency (rad/s)
        
        # Torque Controller Parameters
        self.VS_zeta = 0.7                      # Torque controller damping ratio (-)
        self.VS_omega = 0.3                     # Torque controller natural frequency (rad/s)
        
        # Other basic parameters
        self.Vrat = 11.4                        # Rated wind speed (m/s)
