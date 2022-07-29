from pymavlink import DFReader as DF
import polars as pl

class DataFlash:
    def __init__(self) -> None:
        pass

    # main function which will initialize the function
    def initialize(self, filename):
        self.filename = filename
        self.DFDict = {}
        self.DFcolumn_unit = {}
        self.DFcolumn_multiplier = {}
        self.DFcolumn_list = {}

        # dict to set datatype of each column in flight data type. [It will extract FMT]
        dtypes = {
            "a": pl.Utf8,
            "b": pl.Int64,
            "B": pl.Int64,
            "h": pl.Int64,
            "H": pl.Int64,
            "i": pl.Int64,
            "I": pl.Int64,
            "f": pl.Float64,
            "n": pl.Utf8,
            "N": pl.Utf8,
            "Z": pl.Utf8,
            "c": pl.Float64,
            "C": pl.Float64,
            "e": pl.Float64,
            "E": pl.Float64,
            "L": pl.Float64,
            "d": pl.Float64,
            "M": pl.Int64,
            "q": pl.Int64,
            "Q": pl.Int64
        }

        # dict of units of each column [Extract from FMTU]
        dunits = {
            '-': "" ,              # no units e.g. Pi, or a string
            '?': "UNKNOWN" ,       # Units which haven't been worked out yet....
            'A': "A" ,             # Ampere
            'a': "Ah" ,            # Ampere hours
            'd': "deg" ,           # of the angular variety, -180 to 180
            'b': "B" ,             # bytes
            'k': "deg/s" ,         # degrees per second. Degrees are NOT SI, but is some situations more user-friendly than radians
            'D': "deglatitude" ,   # degrees of latitude
            'e': "deg/s/s" ,       # degrees per second per second. Degrees are NOT SI, but is some situations more user-friendly than radians
            'E': "rad/s" ,         # radians per second
            'G': "Gauss" ,         # Gauss is not an SI unit, but 1 tesla = 10000 gauss so a simple replacement is not possible here
            'h': "degheading" ,    # 0.? to 359.?
            'i': "A.s" ,           # Ampere second
            'J': "W.s" ,           # Joule (Watt second)
            #  'l': "l" ,          # litres
            'L': "rad/s/s" ,       # radians per second per second
            'm': "m" ,             # metres
            'n': "m/s" ,           # metres per second
            #  'N', "N" ,          # Newton
            'o': "m/s/s" ,         # metres per second per second
            'O': "degC" ,          # degrees Celsius. Not SI, but Kelvin is too cumbersome for most users
            '%': "%" ,             # percent
            'S': "satellites" ,    # number of satellites
            's': "sec" ,             # seconds
            'q': "rpm" ,           # rounds per minute. Not SI, but sometimes more intuitive than Hertz
            'r': "rad" ,           # radians
            'U': "deglongitude" ,  # degrees of longitude
            'u': "ppm" ,           # pulses per minute
            'v': "V" ,             # Volt
            'P': "Pa" ,            # Pascal
            'w': "Ohm" ,           # Ohm
            'W': "Watt" ,          # Watt
            'X': "W.h" ,           # Watt hour
            'Y': "us" ,            # pulse width modulation in microseconds
            'z': "Hz" ,            # Hertz
            '#': "instance"        # (e.g.)Sensor instance number
        }
        # dict of multiplier of each column [Extract from FMTU]  
        dmultiplier = {
            '-': 0 ,       # no multiplier e.g. a string
            '?': 1 ,       # multipliers which haven't been worked out yet....
        # <leave a gap here, just in case....>
            '2': 1e2 ,
            '1': 1e1 ,
            '0': 1e0 ,
            'A': 1e-1 ,
            'B': 1e-2 ,
            'C': 1e-3 ,
            'D': 1e-4 ,
            'E': 1e-5 ,
            'F': 1e-6 ,
            'G': 1e-7 ,
            'I': 1e-9 ,
        # <leave a gap here, just in case....>
            '!': 3.6 , # (ampere*second => milliampere*hour) and (km/h => m/s)
            '/': 3600 , # (ampere*second => ampere*hour)
        }

        # Initialize the bin file
        self.DFdecode = DF.DFReader_binary(filename, zero_time_base=True)
        while 1:
            # extracting FMT and FMTU for initialize the dataframe 
            DFmsg = self.DFdecode.recv_match(type=['FMT', 'FMTU'])
            if DFmsg is None:
                self.DFdecode.rewind()
                break
            # convert DF msg to Dict
            DFdict = DFmsg.to_dict()
            if DFdict['mavpackettype'] == 'FMT':
                # Initializing DataFrame with FMT message
                DFcolumns_init = [pl.Series(column, dtype= dtypes[dtype]) for column, dtype in zip(DFdict['Columns'].split(','), list(DFdict['Format']))]
                self.DFDict[DFdict['Name']] = pl.DataFrame(DFcolumns_init)
                self.DFcolumn_list[DFdict['Name']]= [column for column in DFdict['Columns'].split(',')]
            elif DFdict['mavpackettype'] == 'FMTU':
                # Exctracting Units and mutliplier for columns
                self.DFcolumn_unit[self.DFdecode.id_to_name[DFdict['FmtType']]] = {column: dunits[unit] 
                                            for column, unit in zip(self.DFcolumn_list[self.DFdecode.id_to_name[DFdict['FmtType']]], DFdict['UnitIds'])}
                self.DFcolumn_multiplier[self.DFdecode.id_to_name[DFdict['FmtType']]] = {column: dmultiplier[multiplier] 
                                            for column, multiplier in zip(self.DFcolumn_list[self.DFdecode.id_to_name[DFdict['FmtType']]], DFdict['MultIds'])}
     
    def DFextract(self, dtype):
        DFlist = []
        while 1:
            # extract the data type
            DFmsg = self.DFdecode.recv_match(type=dtype)
            if DFmsg is None:
                self.DFdecode.rewind()
                break
            DFdict = DFmsg.to_dict()
            if 'TimeUS' not in DFdict: break
            elif 'mavpackettype' in DFdict: del DFdict['mavpackettype']
            # list append of DFmsg
            DFlist.append(DFdict)
        if len(DFlist) != 0:
            # updating dataframe from DF list
            self.DFDict[dtype] = pl.concat([self.DFDict[dtype], pl.DataFrame(DFlist, columns= self.DFDict[dtype].columns)])
        else:
            return False

    def DFcheckmulti(self, dtype):
            Dnum = []
            for i in range(6):
                DFmsg = self.DFdecode.recv_match(type=dtype)
                if DFmsg is None:
                    self.DFdecode.rewind()
                    break
                DFdict = DFmsg.to_dict()
                if isinstance(DFdict['I'], int) ==  True:
                    Dnum.append(DFdict['I'])
            self.DFdecode.rewind()
            return list(set(Dnum))

    def DFcsvexport(self, dtype):
        DFdictlist = []
        while 1:
            DFmsg = self.DFdecode.recv_match(type=dtype)
            if DFmsg is None:
                self.DFdecode.rewind()
                break
            DFdict = DFmsg.to_dict()
            if 'mavpackettype' in DFdict: del DFdict['mavpackettype']
            DFdictlist.append(DFdict)
        return pl.DataFrame(DFdictlist)