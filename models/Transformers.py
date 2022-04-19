from __future__ import division
from itertools import count
from lib.MatrixBuilder import MatrixBuilder
from models.Branches import TX_LARGE_G, TX_LARGE_B
from models.Buses import _all_bus_key
import math
from models.shared import stamp_line


class Transformers:
    _ids = count(0)

    def __init__(self,
                 from_bus,
                 to_bus,
                 r,
                 x,
                 status,
                 tr,
                 ang,
                 Gsh_raw,
                 Bsh_raw,
                 rating):
        """Initialize a transformer instance

        Args:
            from_bus (int): the primary or sending end bus of the transformer.
            to_bus (int): the secondary or receiving end bus of the transformer
            r (float): the line resitance of the transformer in
            x (float): the line reactance of the transformer
            status (int): indicates if the transformer is active or not
            tr (float): transformer turns ratio
            ang (float): the phase shift angle of the transformer
            Gsh_raw (float): the shunt conductance of the transformer
            Bsh_raw (float): the shunt admittance of the transformer
            rating (float): the rating in MVA of the transformer
        """
        self.id = self._ids.__next__()

        self.from_bus = _all_bus_key[from_bus]
        self.to_bus = _all_bus_key[to_bus]

        self.r = r
        self.x = x

        self.tr = tr
        self.ang_rad = ang * math.pi / 180.

        self.G_loss = r / (r ** 2 + x ** 2)
        self.B_loss = x / (r ** 2 + x ** 2) #source of error

        self.status = status

    def assign_nodes(self, node_index):
        self.node_primary_Ir = node_index.__next__()
        self.node_primary_Ii = node_index.__next__()
        self.node_secondary_Vr = node_index.__next__()
        self.node_secondary_Vi = node_index.__next__()

    def stamp_primal_linear(self, Y: MatrixBuilder, J, tx_factor):
        if not self.status:
            return

        scaled_tr = self.tr + (1 - self.tr) * tx_factor 
        scaled_angle = self.ang_rad - self.ang_rad * tx_factor
        scaled_G = self.G_loss + TX_LARGE_G * self.G_loss * tx_factor
        scaled_B = self.B_loss + TX_LARGE_B * self.B_loss * tx_factor

        ###Primary Winding Current

        #Real
        Y.stamp(self.from_bus.node_Vr, self.node_primary_Ir, 1)

        #Imaginary
        Y.stamp(self.from_bus.node_Vi, self.node_primary_Ii, 1)

        ###Primary Winding Voltage

        #Real
        Y.stamp(self.node_primary_Ir, self.from_bus.node_Vr, 1)
        Y.stamp(self.node_primary_Ir, self.node_secondary_Vr, -scaled_tr * math.cos(scaled_angle))
        Y.stamp(self.node_primary_Ir, self.node_secondary_Vi, scaled_tr * math.sin(scaled_angle))


        #Imaginary
        Y.stamp(self.node_primary_Ii, self.from_bus.node_Vi, 1)
        Y.stamp(self.node_primary_Ii, self.node_secondary_Vr, -scaled_tr * math.sin(scaled_angle))
        Y.stamp(self.node_primary_Ii, self.node_secondary_Vi, -scaled_tr * math.cos(scaled_angle))

        ###Secondary Winding Current

        #Real
        Y.stamp(self.node_secondary_Vr, self.node_primary_Ir, -scaled_tr * math.cos(scaled_angle))
        Y.stamp(self.node_secondary_Vr, self.node_primary_Ii, -scaled_tr * math.sin(scaled_angle))

        #Imaginary
        Y.stamp(self.node_secondary_Vi, self.node_primary_Ii, -scaled_tr * math.cos(scaled_angle))
        Y.stamp(self.node_secondary_Vi, self.node_primary_Ir, scaled_tr * math.sin(scaled_angle))

        ###Secondary Losses

        Vr_from = self.node_secondary_Vr
        Vi_from = self.node_secondary_Vi
        Vr_to = self.to_bus.node_Vr
        Vi_to = self.to_bus.node_Vi

        stamp_line(Y, Vr_from, Vr_to, Vi_from, Vi_to, scaled_G, scaled_B)

    def stamp_dual_linear(self, Y: MatrixBuilder, J, tx_factor):
        pass

