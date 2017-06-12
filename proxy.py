####################################################################################
#
#    NeuroMaC: Neuronal Morphologies & Circuits
#    Copyright (C) 2013-2017 Okinawa Institute of Science and Technology Graduate
#    University, Japan.
#
#    See the file AUTHORS for details.
#    This file is part of NeuroMaC.
#
#    NeuroMaC is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 3,
#    as published by the Free Software Foundation.
#
#    NeuroMaC is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

# import zmq
# context = zmq.Context(1)
# # set up the proxy, for all-to-all capabilities
# proxy_sub = context.socket(zmq.XSUB)
# #proxy_sub.setsockopt(zmq.SUBSCRIBE, "")
# proxy_sub.bind("tcp://*:%s"%5559)
# proxy_pub = context.socket(zmq.XPUB)
# proxy_pub.bind("tcp://*:%s"%5560)
# zmq.device(zmq.PROXY,proxy_sub,proxy_pub)

import zmq

def main():
    try:
        context = zmq.Context(1)
        # Socket facing clients
        frontend = context.socket(zmq.SUB)
        frontend.bind("tcp://*:5559")
        frontend.setsockopt(zmq.SUBSCRIBE, "")
        # Socket facing services
        backend = context.socket(zmq.PUB)
        backend.bind("tcp://*:5560")
        zmq.device(zmq.FORWARDER, frontend, backend)
    except Exception, e:
        print (e)
        print ("bringing down zmq device")
    finally:
        pass
        frontend.close()
        backend.close()
        context.term()

if __name__ == "__main__":
    main()
