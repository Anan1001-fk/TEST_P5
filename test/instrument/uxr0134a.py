import pyvisa
import time


class Uxr0134a(object):
    def __init__(self, res_name="TCPIP0::169.254.184.140::inst0::INSTR", res_type="TCPIP"):
        rm = pyvisa.ResourceManager()
        self.uxr_id = rm.open_resource(res_name)
        self.uxr_id.write_termination = "\n"
        self.uxr_id.read_termination = "\n"
        self.uxr_id.timeout = 20000

    def get_id(self, query="*IDN?"):
        """Returns the instrument identification code to check whether the remote communication is normal
        """
        cmd = "*IDN?"
        return self.uxr_id.query(cmd)

    def close(self):
        """release the corresponding resource
        """
        self.uxr_id.close()

    def default_setup(self):
        """Sets the uxr0134a to default mode
        """
        cmd = "*RST"
        self.uxr_id.write(cmd)
        time.sleep(5)
        cmd = ":SYSTem:PRESet"
        self.uxr_id.write(cmd)
        time.sleep(6)

    def auto_scale(self):
        """Sets the uxr0134a to default mode
        """
        cmd = ":AUToscale"
        self.uxr_id.write(cmd)
        time.sleep(8)

    def auto_verticalscale(self, chan_num):
        self.uxr_id.write(":AUToscale:VERTical CHANnel%d" % chan_num)
        time.sleep(4)

    def clear_all_meas(self):
        """clears the measurement results from the screen and disables all previously enabled measurements.
        """
        cmd = ":MEASure:CLEar"
        self.uxr_id.write(cmd)

    def clear_display(self):
        """Clear the display.just like the oscilloscope's front panel [Clear Display] key.
        """
        self.uxr_id.write(":CDISplay")
        time.sleep(0.3)

    def set_out_state(self, chan_num, state="OFF"):
        """sets the channel display On or Off
        :param chan_num: 1,2,3,4
        :param state: "OFF" or "ON"
        """
        cmd = ":CHAN%d:DISP %s" % (chan_num, state)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_all_out_state(self, *args):
        """  sets the channel display On or Off
        """
        for i_idx in range(0, len(args), 2):
            self.set_out_state(args[i_idx], args[i_idx + 1])

    def get_ber(self, chan_num):
        """
        Args:
            chan_num:

        Returns:
        """
        try:
            cmd = ":MEASure:BER? CHAN%d" % chan_num
            ber = self.uxr_id.query(cmd)
            time.sleep(0.5)
            return float(ber.strip())
        except:
            for i_try in range(3):
                time.sleep(0.2)
                try:
                    cmd = ":MEASure:BER? CHAN%d" % chan_num
                    ber = self.uxr_id.query(cmd)
                    time.sleep(0.5)
                    return float(ber.strip())
                except:
                    continue

    def get_freq(self, chan_num):
        """
        Args:
            chan_num:

        Returns:
        """
        cmd = ":MEASure:BER? CHAN%d" % chan_num
        ber = self.uxr_id.query(cmd)
        time.sleep(0.5)
        return ber.strip()

    # :MEASure: BER? CHAN3


    def get_freq_jitter(self, chan_num):
        """
        Args:
            chan_num:

        Returns:
        """
        cmd = ":MEASure:BER? CHAN%d" % chan_num
        ber = self.uxr_id.query(cmd)
        time.sleep(0.5)
        return ber.strip()

    def set_hor_scale(self, hor_scale=20):
        """sets horizontal scale HorScaleValue
        :param hor_scale: unit: ns
        example: "HORizontal:MODE:SCAle 50.0000E-9"
        """
        hor_scale = hor_scale * 1e-9
        cmd = ":TIMEBASE:SCALE %.12f" % hor_scale
        self.uxr_id.write(cmd)
        time.sleep(0.3)

    def set_ver_offset(self, chan_num=1, offset=0.1):
        """sets the vertical offset for the specified channel
        :param chan_num:
        :param offset:
        """
        cmd = "CHAN%d:OFFSet %e" % (chan_num, offset)
        self.uxr_id.write(cmd)
        time.sleep(0.5)

    def set_threshold_hysteresis(self, chan_num, hysteresis, threshold):
        self.set_general_threshold_method(threshold_method="HYSTeresis")
        cmd = ":MEASure:THResholds:GENeral:HYSTeresis CHANnel%d,%f,%f" % (chan_num, hysteresis, threshold)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_general_threshold_method(self, chan_num=1, threshold_method="PERCent"):
        """
        This is used to switch the threshold application across all channels or a single channel,
        and method is also specified

        @param chan_num  ALL | 1 | 2 | 3 | 4
        @param threshold_method ABSolute | PERCent| HYSTeresis | PAMCustom | PAMAutomatic | T2080 | T9010
        """
        if chan_num == "ALL":
            cmd = ":MEASure:THResholds:GENeral:METHod %s,%s" % (chan_num, threshold_method)
        else:
            cmd = ":MEASure:THResholds:GENeral:METHod CHANnel%d,%s" % (chan_num, threshold_method)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_auto_threshold(self, chan_num, threshold_method):
        """
        This is used to switch the threshold application across all channels or a single channel,
        and method is also specified

        @param chan_num  ALL | 1 | 2 | 3 | 4
        @param threshold_method ABSolute | PERCent| HYSTeresis
        """
        self.set_general_threshold_method(chan_num, threshold_method=threshold_method)
        cmd = ":MEASure:THResholds:GENAUTO CHANnel%d" % chan_num
        self.uxr_id.write(cmd)
        time.sleep(3)

    def set_threshold_precent_all_type(self, chan_num, percent_type, type='', upper_pct=90, middle_pct=50,
                                       lower_pct=10):
        """
        @param type  :GENeral | :RFALl | :SERial | “” (“” means all type)
        @param percent_type : "T1090" "T2080"
        @param chan_num  ALL | 1 | 2 | 3 | 4
        """
        if chan_num == "ALL":
            self.uxr_id.write(f":MEASure:THResholds{type}:METHod {chan_num},{percent_type}")
        else:
            self.uxr_id.write(f":MEASure:THResholds{type}:METHod CHANnel{chan_num},{percent_type}")  # 可以直接用来表示预设档位

    def set_threshold_precent_all(self, chan_num=1, upper_pct=90, middle_pct=50, lower_pct=10, type='', ):
        """
        @param type  :GENeral | :RFALl | :SERial | “” (“” means all type)
        @param chan_num  | 1 | 2 | 3 | 4
        """
        self.uxr_id.write(
            f":MEASure:THResholds{type}:METHod CHANnel%s,PERCent" % chan_num)
        self.uxr_id.write(
            f":MEASure:THResholds{type}:PERCent CHANnel%s,%f,%f,%f" % (chan_num, upper_pct, middle_pct, lower_pct))

    def set_ref_percent(self, chan_num=1, percent_type="T1090"):
        """These threshold settings are used for rise/fall measurements
        ":MEASure:THResholds:RFALl:METHod CHANnel1,HYSTeresis"
        percent_type: "T1090", "T2080"
        """
        cmd = ":MEASure:THResholds:RFALl:METHod CHANnel%d, %s" % (chan_num, percent_type)
        self.uxr_id.write(cmd)
        time.sleep(0.3)

    def set_ver_scale(self, chan_num=1, ver_scale=1.0, mode="manual"):
        """sets the vertical scale value
        :param chan_num: 1,2,3,4
        :param ver_scale: unit V
        """
        if mode.lower().strip() == "manual":
            if ver_scale > 1:
                print("1V is the maximum value")
            cmd = "CHAN%d:SCAle %f" % (chan_num, ver_scale)
            if ver_scale < 0.02:
                cmd = "CHAN%d:SCAle %f" % (chan_num, 0.02)
            self.uxr_id.write(cmd)
            time.sleep(0.2)
        else:
            self.uxr_id.write(":AUToscale:VERTical CHANnel%d" % chan_num)
            time.sleep(4)

    def set_all_ver_scale(self, *args):
        """sets the vertical scale value
        :param ver_scale3:
        :param chan_num: 1,2,3,4
        :param ver_scale: unit V
        """
        for i_idx in range(0, len(args), 2):
            self.set_ver_scale(args[i_idx], args[i_idx + 1])

    def set_trig_mode(self, trig_mode):
        """this command selects the trigger mode.
        :TRIGger: MODE {EDGE | GLITch | PWIDth | PATTern | STATe | RUNT | SHOLd
         | TRANsition | DELay | TIMeout | WINDow | OR | EBURst | SEQuence
         | SBUS < N > | IFMagn}
         """
        cmd = ":TRIGger:MODE %s" % (trig_mode)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_trig_level(self, chan_num, trig_level):
        """:TRIGger:LEVel {{CHANnel<N> | AUX},<level>}"""
        cmd1 = ":TRIGger:EDGE:SOURce CHANnel%d" % (chan_num)
        cmd = ":TRIGger:LEVel CHANnel%d,%f" % (chan_num, trig_level)
        self.uxr_id.write(cmd1)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_edge_trig_para(self, chan_num=1, slope="POSitive", trig_level=0.5):
        """
        :TRIGger:EDGE[{1 | 2}]:SLOPe {POSitive | NEGative | EITHer | ALTernate}
        """
        self.set_trig_mode("EDGE")
        cmd = ":TRIGger:EDGE1:SLOPe %s" % slope.upper()
        self.uxr_id.write(cmd)
        time.sleep(0.2)
        cmd = ":TRIGger:EDGE1:SOURce CHANnel%d" % chan_num
        self.uxr_id.write(cmd)
        time.sleep(0.2)
        self.set_trig_level(chan_num, trig_level)

        # def set_trig_para(self, trig_chan=1, trig_type="EDGE", trig_slope="RISe", trig_level=0.5):

    #     """sets the Trig Ch,type,slope and level TrigLevV: unit V
    #     :param trig_chan: 1,2,3,4
    #     :param trig_type: TRIGger:A:TYPe
    #     EDGE|RUNT|TRANsition|PATtern|GLItch|SETHold|UNDEFINED|
    #     WIDth|TIMEOut|WINdow|STATE|DDRRead|DDRWrite|DDRREADWrite
    #     :param trig_slope: RISe|FALL|EITher
    #     :param trig_level: unit: V
    #     example: "TRIGger:A:TYPe EDGE" "TRIGger:A:EDGE:SOUrce CH3"
    #     """
    #     if trig_type == "EDGE":
    #         cmd = "TRIGger:A:EDGE:SOUrce CH%d" % trig_chan
    #         self.uxr_id.write(cmd)
    #         time.sleep(0.3)
    #         cmd = "TRIGger:A:EDGE:SLOpe %s" % trig_slope
    #         self.uxr_id.write(cmd)
    #         time.sleep(0.3)
    #
    #     cmd = "TRIGger:A:TYPe %s" % trig_type
    #     self.uxr_id.write(cmd)
    #     time.sleep(0.3)
    #     cmd = ":TRIGger:LEVel CHANnel%d, %e" % (trig_chan, trig_level)
    #
    #     print("-----------------------set_trig_para", id(self))
    #     self.uxr_id.write(cmd)
    #     time.sleep(0.3)

    def set_glitch_para(self, chan=1, search_num=1, type="GLItch", width=2, level=-0.2, mode=10):
        """
        :param chan: the corresponding chan
        :param search_num: the serial number of search
        :param type: {EDGE|RUNT|TRANsition|PATtern|GLItch|SETHold|UNDEFINED|
        WIDth|TIMEOut|WINdow|STATE|DDRRead|DDRWrite|DDRREADWrite}
        SEARCH:SEARCH<x>:TRIGger:A:TYPe?
        :param width: unit ns
        :param level: unit: V
        :param mode: {EITher|NEGAtive|POSITIVe}
        """
        self.set_search_type_chan(search_num, type, chan)
        self.set_search_glitch_width(search_num, width)
        self.set_search_trig_level(search_num, type, level)
        self.set_search_state(search_num, "ON")
        self.set_search_glitch_polarity(search_num, mode)

    def set_search_mode(self, mode="OFF"):
        """sets or queries the stop of acquisitions when a search finds an event.
        SEARCH:STOP {<NR1>|OFF|ON|1|0}
        ON: stops the acquisition if event found"""

        cmd = "SEARCH:STOP %s" % mode
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def measure_window_source(self, type, meas_n):
        """
        :param type：ZOOM | CGRade | {MAIN | ALL}
        :param meas_n: Can be an integer from 1 – 40.
        """
        if meas_n is None:
            self.uxr_id.write(':MEASure:WINDow %s' % type)
        else:
            self.uxr_id.write(':MEASure:WINDow %s,MEAS%d' % (type, meas_n))

    def set_search_type_chan(self, search_num=1, type="EDGE", chan=1):
        """
        :param type:
        SEARCH:SEARCH<x>:TRIGger:A:TYPe
        {EDGE|RUNT|TRANsition|PATtern|GLItch|SETHold|UNDEFINED|
        WIDth|TIMEOut|WINdow|STATE|DDRRead|DDRWrite|DDRREADWrite}
        SEARCH:SEARCH<x>:TRIGger:A:TYPe?
        :param chan:
        """
        cmd = "SEARCH:SEARCH%d:TRIGger:A:TYPe %s" % (search_num, type)
        self.uxr_id.write(cmd)
        time.sleep(0.2)
        if type.upper() == "EDGE":
            cmd = "SEARCH:SEARCH%d:TRIGGER:A:EDGE:SOURCE CH%d" % (search_num, chan)
        elif type.upper() == "GLITCH":
            cmd = "SEARCH:SEARCH%d:TRIGger:A:PULse:SOUrce CH%d" % (search_num, chan)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_search_glitch_width(self, search_num, width):
        """
        :param search_num:
        :param width: unit ns
        "SEARCH:SEARCH1:TRIGGER:A:GLITCH:WIDTH 1e-9" 1ns
        """
        width = width
        cmd = "SEARCH:SEARCH%d:TRIGger:A:GLItch:WIDth %.2fE-9" % (search_num, width)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_search_edge_slope(self, search_num, mode):
        """
        :param search_num:
        :param mode:
        SEARCH:SEARCH<x>:TRIGger:A:EDGE:SLOpe:CH<x>{RISe|FALL|EITher}
        SEARCH:SEARCH1:TRIGGER:A:EDGE:SLOPE:CH2 RISE sets the Channel 2 slope for search 1 to rise.
        """
        chan = self.uxr_id.query("SEARCH:SEARCH%d:TRIGger:A:EDGE:SOUrce?" % search_num).replace("\n", "")
        if not isinstance(mode, str):
            if mode > 0:
                slope = "RISe"
            elif mode < 0:
                slope = "FALL"
            else:
                slope = "EITher"
        else:
            slope = mode
        cmd = "SEARCH:SEARCH%d:TRIGger:A:EDGE:SLOpe:%s %s" % (search_num, chan, slope)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_search_glitch_polarity(self, search_num, mode):
        """
        :param search_num:
        :param mode: >0: POSITIVe <0: NEGAtive 0: EITher
        SEARCH:SEARCH<x>:TRIGger:A:GLItch:POLarity:CH<x> {EITher|NEGAtive|POSITIVe}
        """
        chan = self.uxr_id.query("SEARCH:SEARCH%d:TRIGger:A:PULse:SOUrce?" % search_num).replace("\n", "")
        if not isinstance(mode, str):
            if mode > 0:
                polarity = "POSITIVe"
            elif mode < 0:
                polarity = "NEGAtive"
            else:
                polarity = "EITher"
        else:
            polarity = mode
        cmd = "SEARCH:SEARCH%d:TRIGger:A:GLItch:POLarity:%s %s" % (search_num, chan, polarity)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_search_trig_level(self, search_num, type, level):
        """
        :param search_num:
        :param level: unit: V
        "SEARCH:SEARCH1:TRIGger:A:LEVel:CH1 2.15"
        """
        if type.upper() == "GLITCH":
            chan = self.uxr_id.query("SEARCH:SEARCH%d:TRIGger:A:PULse:SOUrce?" % search_num).replace("\n", "")
        elif type.upper() == "EDGE":
            chan = self.uxr_id.query("SEARCH:SEARCH%d:TRIGger:A:EDGE:SOUrce?" % search_num).replace("\n", "")
        cmd = "SEARCH:SEARCH%d:TRIGger:A:LEVel:%s %f" % (search_num, chan, level)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_search_state(self, search_num, state="OFF"):
        """
        SEARCH:SEARCH<x>:STATE
        """
        cmd = "SEARCH:SEARCH%d:STATE %s" % (search_num, state)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def get_search_stop(self):
        """
        uxr.uxr_id.query("SEARCH:STOP?")
        SEARCH:STOP? might return :SEARCH:STOP 1, indicating that a search found
        an event and stops acquisition
        1 stops the acquisition.
        0 continues the acquisition.
        """
        cmd = "SEARCH:STOP?"
        result = int(self.uxr_id.query(cmd).replace("\n", ""))
        time.sleep(0.2)
        return result

    def get_search_count(self, search_num):
        """
        uxr.uxr_id.query("SEARCH:STOP?")
        SEARCH:SEARCH<x>:TOTAL? might return the searched count

        """
        cmd = "SEARCH:SEARCH%d:TOTAL?" % search_num
        result = int(self.uxr_id.query(cmd).replace("\n", ""))
        time.sleep(0.2)
        return result

    def set_single(self):
        """is equivalent to pressing the single button on the front panel
        ACQuire:STOPAfter {RUNSTop|SEQuence}
        ACQuire:STOPAfter?
        if you want to clear the waveforms, measurement and acquisitions, you should execute the clear method
        """
        cmd = "ACQuire:STOPAfter SEQuence"  # it will set the trigger mode as "normal" at the same time
        self.uxr_id.write(cmd)
        time.sleep(0.2)
        self.clear_all()
        time.sleep(0.5)

    def set_trigger_mode(self, mode="AUTO"):
        """is equivalent toselecting Mode from the Trig menu and then choosing the desired Trigger Mode.
        TRIGger:A:MODe {AUTO|NORMal}
        """
        self.clear_all()
        time.sleep(1)
        cmd = "TRIGger:A:MODe %s" % mode  # it will set the trigger mode as "normal" at the same time
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_term(self, chan_num, term):
        """sets channel input termination

        :param chan_num: 1,2,3,4
        :param term: 50 or 1e6, if TermVal <= 50,sets it to 50, else 1e6

        example: "CH4:TERmination 50"
        """
        cmd = "CH%d:TERmination %d" % (chan_num, term)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_display_mode(self, display_mode="OFF"):
        """sets the persistence aspect of the display
        :param display_mode: 'OFF', 'INFPersist' or VARpersist
        INFPersist mode let the new waveform overlay on the old ones
        example: DISplay:PERSistence {OFF|INFPersist|VARpersist}
        """
        cmd = "DISplay:PERSistence %s" % display_mode
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    # def set_display_var_value(self, value):
    #     """if the persistence mode is VARpersist, set the value, it means, after the time set by value, the data will be
    #     refreshed.the persistence decay time and ranges should be from 0.5 to 100
    #     example: "DISPLAY:VARPERSIST 5" sets the persistence decay time to 5s."""
    #
    #     cmd = "DISplay:VARpersist %f" % value
    #     self.uxr_id.write(cmd)
    #     time.sleep(0.2)
    # def set_200m_real_time_eye(self, chan_num, state="OFF"):
    #     self.set_hor_scale(20)
    #     if state.strip().upper() == "OFF":
    #         self.set_real_time_eye_state(chan_num, state)
    #     else:
    #         self.set_real_time_eye_state(chan_num, state="ON")
    #         self.set_general_threshold_method(chan_num, "HYSTeresis")
    #         self.set_threshold_hysteresis(chan_num, hysteresis=0.04, threshold=0.45)
    #         self.set_clock_recovery_ojtf(method="SOPLL", data_rate=200e6, loop_bandwidth=120e3, damping_fact=0.707)
    #         self.set_mem_depth(10e6)
    #         time.sleep(1)
    #     self.set_eye_para(chan_num)
    #     self.set_recovery_clock_state(chan_num, "OFF")

    def set_100m_200m_real_time_eye(self, chan_num, state="OFF", mode="200m"):
        self.set_hor_scale(20)
        if state.strip().upper() == "OFF":
            self.set_real_time_eye_state(chan_num, state)
        else:
            self.set_real_time_eye_state(chan_num, state="ON")
            self.set_general_threshold_method(chan_num, "HYSTeresis")
            self.set_threshold_hysteresis(chan_num, hysteresis=0.04, threshold=0.45)
            if "200" in mode:
                self.set_clock_recovery_ojtf(method="SOPLL", data_rate=200e6, loop_bandwidth=120e3, damping_fact=0.707)
            elif "100" in mode:
                self.set_clock_recovery_ojtf(method="SOPLL", data_rate=100e6, loop_bandwidth=60e3, damping_fact=0.707)

            self.set_mem_depth(10e6)
            time.sleep(1)
        self.set_eye_para(chan_num)
        self.set_recovery_clock_state(chan_num, "OFF")

    def set_4g_real_time_eye(self, chan_num, data_rate, state="OFF"):
        if state.strip().upper() == "OFF":
            self.set_real_time_eye_state(chan_num, state)
        else:
            self.set_real_time_eye_state(chan_num, state="ON")
            self.set_general_threshold_method(chan_num, "HYSTeresis")
            self.set_threshold_hysteresis(chan_num, hysteresis=0.02, threshold=0)
            self.set_clock_recovery_ojtf(method="SOPLL", data_rate=data_rate, loop_bandwidth=(data_rate / 1667),
                                         damping_fact=0.707)
            self.set_mem_depth(6e6)
            time.sleep(1)
        self.set_eye_para(chan_num)
        self.set_recovery_clock_state(chan_num, "OFF")

    def set_real_time_eye_state(self, chan_num=1, state="OFF"):
        """command enables (ON) or disables (OFF) the display of the real-time eye.
        uxr_x.uxr_id.write(":MTESt:FOLDing ON, CHANnel1")"""
        cmd = ":MTESt:FOLDing %s, CHANnel%d" % (state, chan_num)
        self.uxr_id.write(cmd)
        time.sleep(0.4)

    def color_grade(self, chan_num=1, state="OFF"):
        """sets the color grade persistence on or off
        :DISPlay:CGRade {{ON | 1} | {OFF | 0}}[,<source>]
        """
        cmd = "DISPlay:CGRade %s, CHANnel%d" % (state, chan_num)
        self.uxr_id.write(cmd)
        cmd = "DISPlay:CGRade:LEGend OFF"
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_eye_para(self, chan_num=1, unit="SECond"):
        """
        :MEASure:CGRade:EWIDth <algorithm>[,<source>[,<threshold>[,<units>]]]
        chan_num:
        unit:
        MEASure:CGRade:EWIDth:THReshold {AUTomatic | SPECified}[, <source>]
        """
        self.color_grade(chan_num, "ON")
        cmd = "MEASure:CGRade:EWIDth:THReshold AUTomatic, CHANnel%d" % chan_num
        self.uxr_id.write(cmd)
        time.sleep(0.4)
        # height_cmd = ":MEASure:CGRade:EHEight MEASured, CHANnel%d" % chan_num
        # self.uxr_id.write(height_cmd)
        # time.sleep(0.4)
        # width_cmd = ":MEASure:CGRade:EWIDth MEASured, CHANnel%d" % chan_num
        # # width_cmd = ":MEASure:CGRade:EWIDth EXTRapolated, CHANnel%d, %s" % (chan_num, unit)
        # self.uxr_id.write(width_cmd)
        # time.sleep(0.4)

    def get_eye_para(self, chan_num=1, unit="SECond"):
        """
        :MEASure:CGRade:EWIDth <algorithm>[,<source>[,<threshold>[,<units>]]]
        chan_num:
        unit:
        """
        self.color_grade(chan_num, "ON")
        height_cmd = ":MEASure:CGRade:EHEight? EXTRapolated, CHANnel%d" % chan_num
        eye_height = round(float(self.uxr_id.query(height_cmd)), 3)
        time.sleep(0.4)
        width_cmd = ":MEASure:CGRade:EWIDth? EXTRapolated, CHANnel%d" % chan_num
        eye_width = round(float(self.uxr_id.query(width_cmd)) * 1e12, 3)
        time.sleep(0.4)
        eye_para = dict(eye_height=eye_height, eye_width=eye_width)
        time.sleep(0.4)
        return eye_para

    def get_eye_jitter_ps(self, chan_num=1, format="PP", unit="SECond"):
        self.color_grade(chan_num, "ON")
        cmd = ":MEASure:CGRade:JITTer? %s, CHANnel%d, %s" % (format, chan_num, unit)
        eye_jitter = round(float(self.uxr_id.query(cmd)) * 1e12, 3)
        time.sleep(0.4)
        return eye_jitter

    def enable_jitter(self, state, units, edge):
        """
        @param state {ON | OFF}
        @param units "{SECond | UNITinterval}"
        @param edge {RISing | FALLing | BOTH}

        """
        self.uxr_id.write(f":MEASure:RJDJ:STATe {state}")
        self.uxr_id.write(f":MEASure:RJDJ:UNITs {units}")
        self.uxr_id.write(f":MEASure:RJDJ:EDGE {edge}")
        time.sleep(0.6)

    def get_tj(self):
        cmd = ":MEASure:RJDJ:ALL?"
        a = self.uxr_id.query(cmd)
        jitter_result = a.split(",")
        TJ = jitter_result[0:3]

        RJ_rms = jitter_result[3:6]

        DJ_dd = jitter_result[6:9]

        PJ_rms = jitter_result[9:12]

        PJ_dd = jitter_result[12:15]

        DDJ_dd = jitter_result[15:18]

        DCD = jitter_result[18:21]

        ISIpp = jitter_result[21:24]

        Transitions = jitter_result[24:27]

        UTJ = jitter_result[27:30]

        UDJ_dd = jitter_result[30:33]

        DDPWS = jitter_result[33:36]

        F2 = jitter_result[36:39]

        pattern_length = self.uxr_id.query(":MEASure:RJDJ:APLength?")

        return [TJ[1], RJ_rms[1], DJ_dd[1], PJ_rms[1], PJ_dd[1], DDJ_dd[1], DCD[1], ISIpp[1], UTJ[1], UDJ_dd[1],
                pattern_length]

    def set_eye_jitter(self, chan_num=1, format="PP", unit="SECond"):
        """measures the jitter at the eye diagram crossing point
        chan_num:
        format: {PP | RMS}
        unit: {SECond | UNITinterval}
        example: ":MEASure: CGRade:JITTer < format > [, < source > [, < units >]]"
        ":MEASure:CGRade:JITTer RMS, CHANnel1, SECond"
        """
        self.color_grade(chan_num, "ON")
        cmd = ":MEASure:CGRade:JITTer %s, CHANnel%d, %s" % (format, chan_num, unit)
        self.uxr_id.write(cmd)
        time.sleep(0.6)

    def add_meas(self, chan_num, meas_type="FREQ"):
        """sets the measure number, the channel you want to measure and the measure type
        :param chan_num: 1,2,3,4
        :param meas_num: 1,2,3,4,5,6,7,8
        :param meas_type:
        "FREQuency|VPP|VRMS|VAMPlitude|DUTYcycle|PERiod|RISetime|FALLtime|BER|PLENgth|Datarate"
        MEASure:PERiod CHANnel1"
        """
        cmd = "MEASure:%s CHANnel%d" % (meas_type, chan_num)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def measure_eye(self, chan_num, eye_type):
        """
        :param eye_type: EHEight | EWIDth
        """
        #  :MEASure: CGRade:EWIDth < algorithm > [, < source > [, < threshold > [, < units >]]]
        # algorithm: MEASured | EXTRapolated
        cmd = ":MEASure:CGRade:%s MEASured,CHANnel%d" % (eye_type, chan_num)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def get_eye_value(self, eye_type):
        cmd = ":MEASure:CGRade:%s?" % eye_type
        value = self.uxr_id.query(cmd)
        return float(value)

    def get_eh_value_mv(self):
        eye_height = round(self.get_eye_value("EHEight") * 1000, 3)
        return eye_height

    def get_ew_value_ps(self):
        eye_width = round(self.get_eye_value("EWIDth") * 1e12, 3)
        return eye_width

    def get_slew_rate_ps(self, chan_num):
        rl = []
        rise_time = round(self.get_meas_val(chan_num, meas_type="RISetime", meas_statistic="MEAN") * 1e12, 3)
        fall_time = round(self.get_meas_val(chan_num, meas_type="FALLtime", meas_statistic="MEAN") * 1e12, 3)
        rl.append(rise_time)
        rl.append(fall_time)
        return rl

    def set_meas_type(self, chan_num, meas_num, meas_type="FREQ", meas_sour=1):
        """sets the measure number, the channel you want to measure and the measure type
        :param chan_num: 1,2,3,4
        :param meas_num: 1,2,3,4,5,6,7,8
        :param meas_type:
         MEASUrement:MEAS<x>:TYPe {AMPlitude|AREa|
        BURst|CARea|CMEan|CRMs|DELay|DISTDUty|
        EXTINCTDB|EXTINCTPCT|EXTINCTRATIO|EYEHeight|
        EYEWIdth|FALL|FREQuency|HIGH|HITs|LOW|
        MAXimum|MEAN|MEDian|MINImum|NCROss|NDUty|
        NOVershoot|NWIdth|PBASe|PCROss|PCTCROss|PDUty|
        PEAKHits|PERIod|PHAse|PK2Pk|PKPKJitter|
        PKPKNoise|POVershoot|PTOP|PWIdth|QFACtor|
        RISe|RMS|RMSJitter|RMSNoise|SIGMA1|SIGMA2|
        SIGMA3|SIXSigmajit|SNRatio|STDdev|UNDEFINED| WAVEFORMS}
        MEASUrement:MEAS<x>:TYPe?
        :param measure_sour: 1,2 Source2 measurements apply only to phase and delay measurement
         types,which require both a target (Source1) and reference (Source2) source.
         example: 'MEASUrement:MEAS1:SOUrce1 CH4'
         'MEASUrement:MEAS2:TYPe MEAN'
        """
        cmd = "MEASUrement:MEAS%d:SOUrce%d CH%d" % (meas_num, meas_sour, chan_num)
        self.uxr_id.write(cmd)
        time.sleep(0.2)
        cmd = "MEASUrement:MEAS%d:TYPe %s" % (meas_num, meas_type)
        self.uxr_id.write(cmd)
        time.sleep(0.2)
        cmd = "MEASUrement:MEAS%d:STATE ON" % meas_num
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_delay_para(self, meas_num, sour1_chan=1, sour2_chan=2, edge1_type="RISe", edge2_type="RISe",
                       direction="FORWards"):
        """The MidPercent command affects the results of delay measurements.
        """
        self.uxr_id.write("MEASUrement:MEAS%d:DELay:DIREction %s" % (meas_num, direction))
        time.sleep(0.1)
        self.uxr_id.write("MEASUrement:MEAS%d:DELay:EDGE1 %s" % (meas_num, edge1_type))
        time.sleep(0.1)
        self.uxr_id.write("MEASUrement:MEAS%d:DELay:EDGE2 %s" % (meas_num, edge2_type))
        time.sleep(0.1)
        self.uxr_id.write("MEASUrement:MEAS%d:SOUrce1 CH%d" % (meas_num, sour1_chan))
        time.sleep(0.1)
        self.uxr_id.write("MEASUrement:MEAS%d:SOUrce2 CH%d" % (meas_num, sour2_chan))
        time.sleep(0.1)

    def set_ref_absolute(self, meas_num, high_ref, mid_ref, low_ref):
        """sets the reference level, and is the Absolute reference level
        :param meas_num:
        :param high_ref:
        :param mid_ref:
        :param low_ref:
        """
        cmd = "MEASUrement:MEAS%d:REFLevel:METHod ABSolute" % meas_num
        self.uxr_id.write(cmd)
        time.sleep(0.1)
        cmd = "MEASUrement:MEAS%d:REFLevel:ABSolute:HIGH %e" % (meas_num, high_ref)
        self.uxr_id.write(cmd)
        time.sleep(0.1)
        cmd = "MEASUrement:MEAS%d:REFLevel:ABSolute:MID %e" % (meas_num, mid_ref)
        self.uxr_id.write(cmd)
        time.sleep(0.1)
        cmd = "MEASUrement:MEAS%d:REFLevel:ABSolute:LOW %e" % (meas_num, low_ref)
        self.uxr_id.write(cmd)
        time.sleep(0.1)

    def set_meas_state(self, meas_num, meas_state="ON"):
        """sets meas_num state: on or off
        example: 'MEASUrement:MEAS1:STATE ON'
        """
        cmd = "MEASUrement:MEAS%d:STATE %s" % (meas_num, meas_state)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_global_bandwidth(self, bandwidth):
        """
        set global bandwidth limit
        @param bandwidth: AUTO | MAX | a real number (eg:1e9)
        """
        self.uxr_id.write(f':ACQuire:BANDwidth {bandwidth}')

    def set_channel_bandwidth(self, chan_num, type, bandwidth):
        """
        @param type: WALL | BESSEL4 | BUTTerworth
        """
        self.set_global_bandwidth('AUTO')
        self.uxr_id.write(f':CHANnel{chan_num}:ISIM:BWLimit ON')
        self.uxr_id.write(f':CHANnel{chan_num}:ISIM:BWLimit:TYPE {type}')
        self.uxr_id.write(f':CHANnel{chan_num}:ISIM:BANDwidth {bandwidth}')

    def set_channel_bandpass(self, chan_num, CFRequency):
        self.set_global_bandwidth('AUTO')
        self.uxr_id.write(f':CHANnel{chan_num}:ISIM:BWLimit ON')
        self.uxr_id.write(f':CHANnel{chan_num}:ISIM:BWLimit:TYPE BANDpass')
        # self.uxr_id.write(f':CHANnel{chan_num}:ISIM:BANDwidth {bandwidth}')
        self.uxr_id.write(f':CHANnel{chan_num}:ISIM:BPASs:{CFRequency}')

    def clear_all(self):
        """clears all acquisitions, measurements, and waveforms.
        """
        cmd = "CLEAR ALL"
        self.uxr_id.write(cmd)
        time.sleep(1.5)

    def set_acq_state(self, acq_state="ON"):
        """starts or stops acquisitions, equivalent to pressing the Run/Stop button
        :param acq_state: "ON" or "OFF", "RUN" or "STOP"
        """
        cmd = "ACQuire:STATE %s" % acq_state
        self.uxr_id.write(cmd)
        time.sleep(0.3)

    def set_annotation_state(self, meas_num):
        """starts or stops acquisitions, equivalent to pressing the Run/Stop button
        :param acq_state: "ON" or "OFF", "RUN" or "STOP"
        """
        cmd = "MEASUrement:ANNOTation:STATE MEAS%d" % meas_num
        self.uxr_id.write(cmd)
        time.sleep(0.3)

    def get_acq_state(self):
        """get the acq_state
        0, indicating that the acquisition is stopped.
        1, singling or no action
        """
        cmd = "ACQuire:STATE?"
        acq_state = self.uxr_id.query(cmd)
        time.sleep(0.2)
        return acq_state[0:-1]

    def set_clock_recovery_source(self, recovery_source=1):
        ":ANALyze: CLOCk:METHod: SOURce{ALL | < source >}"
        cmd = ":ANALyze:CLOCk:METHod:SOURce CHAN%d" % recovery_source
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_clock_recovery_method(self, chan_num=1, method="SOPLL"):

        """
          {FIXed,{AUTO | {SEMI[,<data_rate>]} | <data_rate>}}
          | {TOPLL[,<data_rate>[,<natural_frequency>[,<pole_frequency>[,
              <damping_factor>[,<PLL_settling_time>]]]]]}
          | {EXPlicit,<source>,{RISing | FALLing | BOTH}[,
              <multiplier>[,<clock_freq>]]}
          | {EXPTOPLL,<source>,{RISing | FALLing | BOTH},
              <multiplier>,<clock_freq>,<natural_frequency>,
              <pole_frequency>,<damping_factor>}
          | {EQTOPLL[,<data_rate>[,<natural_frequency>[,<pole_frequency>[,
              <damping_factor>[,<PLL_settling_time>]]]]]}
          | {FC,{FC1063 | FC2125 | FC425}}
          | {FLEXR,<baud_rate>}
          | {FLEXT,<baud_rate>}
          | {PWM}
          | {CPHY[,<symbol_rate>[,<setup_UI>]]}
          | {BMC}
          | {LFPS}
          | {PCIE5,{PCIE8 | PCIE16 | PCIE32}
          | {PCIE6,{PCIE8 | PCIE16 | PCIE32 | PCIE64}}

        FIXed (Constant Frequency)

        TOPLL (Third Order PLL)

        EXPlicit (Explicit Clock)

        EXPTOPLL (Explicit Third Order PLL)

        EQTOPLL (Equalized Third Order PLL)

        FC (Fibre Channel)

        FLEXR (FlexRay Receiver)

        """
        cmd = ":ANALyze:CLOCk OFF,CHANnel%d" % chan_num
        self.uxr_id.write(cmd)
        time.sleep(0.2)
        cmd = ":ANALyze:CLOCk:METHod %s" % method
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_clock_recovery_ojtf(self, method="FOPLL", data_rate=4e9, loop_bandwidth=2.5e6, damping_fact=0.707):
        """[:MEASure:CLOCk:METHod:OJTF]
        {FOPLL,<data_rate>,<ojtf_loop_bandwidth>}
      | {EQFOPLL,<data_rate>,<ojtf_loop_bandwidth>}
      | {SOPLL,<data_rate>,<ojtf_loop_bandwidth>,<damping_factor>}
      | {EQSOPLL,<data_rate>,<ojtf_loop_bandwidth>,<damping_factor>}
      | {EXPFOPLL <source>,{RISing | FALLing | BOTH},
          <multiplier>,<clock_freq>,<ojtf_loop_bandwidth>}
      | {EXPSOPLL <source>,{RISing | FALLing | BOTH},
          <multiplier>,<clock_freq>,<ojtf_loop_bandwidth>,<damping_fact>}"""
        # cmd = ":MEASure:CLOCk:METHod:OJTF SOPLL, 1e9, 2.5e6,damping_fact 0.707"
        self.set_clock_recovery_method(method="SOPLL")
        cmd = ":MEASure:CLOCk:METHod:OJTF %s, %f, %f, %f" % (method, data_rate, loop_bandwidth, damping_fact)
        self.uxr_id.write(cmd)
        time.sleep(2)

    def set_recovery_clock_state(self, chan_num=1, state="OFF"):
        """The :ANALyze:CLOCk command turns the recovered clock display on or off and sets the clock recovery channel source."""
        if state.strip().lower() == "off":
            cmd = ":ANALyze:CLOCk OFF"
        else:
            cmd = ":ANALyze:CLOCk ON,CHAN%d" % (state, chan_num)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_nrz_ber_signal(self, chan_num, file_name=None, invert_state="OFF"):
        self.set_signal_type(chan_num, "NRZ")
        if file_name is not None:
            self.set_signal_load_pattern(chan_num, file_name)
        else:
            self.set_signal_pattern_length(1, "AUTO")

    def set_meas_4g_ber_para(self, chan_num, file_name, invert_state="OFF"):
        self.set_hor_scale(1)
        self.set_nrz_ber_signal(chan_num, file_name, invert_state)
        self.set_clock_recovery_source(recovery_source=chan_num)
        self.set_clock_recovery_ojtf(method="SOPLL", data_rate=4e9, loop_bandwidth=2.5e6, damping_fact=0.707)
        self.set_general_threshold_method(chan_num, "HYSTeresis")
        self.set_mem_depth(5e6)
        self.set_threshold_hysteresis(1, hysteresis=0.02, threshold=0)
        self.add_meas(1, "BER")
        self.add_meas(1, "PLENgth")
        self.set_recovery_clock_state(chan_num, "OFF")

    def set_meas_100m_200m_ber_para(self, chan_num, file_name=None, mode="200m", invert_state="OFF"):
        self.set_hor_scale(20)
        if file_name is not None:
            self.set_signal_pattern_length(1, "AUTO")
        else:
            self.set_nrz_ber_signal(chan_num, file_name, invert_state)
        self.set_clock_recovery_source(recovery_source=chan_num)
        if "200m" in mode:
            self.set_clock_recovery_ojtf(method="SOPLL", data_rate=200e6, loop_bandwidth=120e3, damping_fact=0.707)
        elif "100m" in mode:
            self.set_clock_recovery_ojtf(method="SOPLL", data_rate=100e6, loop_bandwidth=60e3, damping_fact=0.707)
        self.set_general_threshold_method(chan_num, "HYSTeresis")
        self.set_mem_depth(10e6)
        self.set_threshold_hysteresis(1, hysteresis=0.04, threshold=0.3)
        self.add_meas(1, "BER")
        self.add_meas(1, "PLENgth")
        self.set_recovery_clock_state(chan_num, "OFF")

    def set_sample_rate(self, sample_rate=5.0000E+10):
        """set the sample rate in the Horiz/Acq
        :ACQuire:SRATe[:ANALog] {AUTO | MAX | <rate>}
        """
        cmd = ":ACQuire:SRATe:ANALog %s" % sample_rate
        self.uxr_id.write(cmd)
        time.sleep(0.5)

    def set_mem_depth(self, mem_depth=1.0E+6, mode="manual"):
        """set the mode record length rate in the Horiz/Acq
        """
        if mode.lower().strip() == "manual":
            cmd = ":ACQuire:POINts:ANALog %s" % mem_depth
        else:
            cmd = ":ACQuire:POINts:ANALog AUTO"
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def get_mode_record_length(self):
        """set the mode record length rate in the Horiz/Acq
        """
        cmd = "HORizontal:MODE:RECOrdlength?"
        record_length = self.uxr_id.query(cmd)
        time.sleep(0.1)
        return record_length

    def get_mode_sample_rate(self):
        """get the sample rate in the Horiz/Acq
        """
        cmd = "HORIZONTAL:MODE:SAMPLERATE?"
        sample_rate = self.uxr_id.query(cmd)
        time.sleep(0.1)
        return sample_rate

    def clear_single_meas(self, meas_num):
        cmd = ":MEASurement%d:CLEar" % meas_num
        self.uxr_id.write(cmd)

    def get_uxr_value(self, cmd):
        result = float(self.uxr_id.query(cmd))
        time.sleep(0.2)
        return result

    def get_meas_val(self, chan_num, meas_type="FREQ", meas_statistic="Max"):
        """
        measure the corresponding type and get the specified statistic value
        Args:
            chan_num: 1, 2, 3, s4
            meas_type: RISetime|FALLtime|FREQuency|VPP|PLENgth|Datarate|VAMPlitude
            meas_statistic:CURR|MEAN|MAX|RANGE|STDD|COUNT
        Returns: value
        """
        if meas_statistic.lower() == "range":
            self.uxr_id.write(":MEASure:STATistics MAX")
            time.sleep(0.3)
            max_value = self.get_uxr_value(":MEASure:%s? CHANnel%d" % (meas_type, chan_num))
            self.uxr_id.write(":MEASure:STATistics MIN")
            time.sleep(0.3)
            min_value = self.get_uxr_value(":MEASure:%s? CHANnel%d" % (meas_type, chan_num))
            time.sleep(0.3)
            return max_value - min_value
        else:
            self.uxr_id.write(":MEASure:STATistics %s" % meas_statistic)
            time.sleep(0.3)
            meas_value = self.get_uxr_value(":MEASure:%s? CHANnel%d" % (meas_type, chan_num))
            time.sleep(0.3)
            return float(meas_value)

    def get_hor_scale(self):
        """get horizontal scale
        """
        cmd = "HORizontal:MODE:SCAle?"
        hor_scale = self.uxr_id.query(cmd)
        time.sleep(0.2)
        return hor_scale * 1e9

    def set_math_function(self, math_num, math_function):
        """
        :param math_num: the math number
        :param math_function: a quoted string argument is the mathematical expression that defines the waveform
        """
        cmd = 'MATH%d:DEFine "%s"' % (math_num, math_function)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_math_label(self, math_num, label_name):
        """
        This command sets the label string, which is used for annotating the math waveform on the screen.
        :param math_num: the math number
        :param label_name: specifies the label to annotate the math waveform
        """
        cmd = "MATH%d:LABel:NAMe %s" % (math_num, label_name)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_math_ver_pos_grid(self, math_num, math_ver_pos_grid):
        """This command sets the vertical position of the specified Math waveform.
        :param math_num: the math number
        :param math_ver_pos_grid: top to bottom : 5 to -5 unit: grid
        """
        cmd = "MATH%d:VERTical:POSition %f" % (math_num, math_ver_pos_grid)
        self.uxr_id.write(cmd)
        time.sleep(2)

    def set_math_ver_scale(self, math_num, math_ver_scale):
        """This command sets the vertical scale of the specified math waveform..
        :param math_num: the math number
        :param math_ver_scale: unit V
        """
        cmd = "MATH%d:VERTical:SCAle %f" % (math_num, round(math_ver_scale, 1))
        self.uxr_id.write(cmd)
        time.sleep(2)

    def set_math_meas_type(self, meas_num, math_num, math_meas_type):
        """set the measure type of the math channle
        :param math_num: the math number
        :param math_meas_type: same as set_meas_type method
        """
        cmd = "MEASUrement:MEAS%d:SOUrce%d MATH%d" % (meas_num, 1, math_num)
        self.uxr_id.write(cmd)
        time.sleep(0.2)
        cmd = "MEASUrement:MEAS%d:TYPe %s" % (meas_num, math_meas_type)
        self.uxr_id.write(cmd)
        time.sleep(0.2)
        cmd = "MEASUrement:MEAS%d:STATE ON" % meas_num
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_math_out_state(self, math_num=1, math_state="OFF"):
        cmd = "SELECT:MATH%d %s" % (math_num, math_state)
        self.uxr_id.write(cmd)
        time.sleep(3)

    def set_cursor_chan(self, source=1, chan=1):
        """sets or queries the source(s) for the currently selected cursor type
        The cursor is specified by x, which can be 1 or 2. If the cursor is not specified,it defaults to cursor 1.
        :param source: specify which cursor
        :param chan: channel number
        CURSor: SOUrce < x > {CH1|CH2|CH3|CH4|MATH1|MATH2|MATH3|MATH4|REF1|REF1|REF3|REF4}
        CURSOR:SOURCE 1 CH2 sets the Cursor1 source to Channel 2.
        """
        if isinstance(chan, int):
            cmd = "CURSOR:SOURCE%d CH%d" % (source, chan)
        else:
            cmd = "CURSOR:SOURCE%d %s" % (source, chan)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_ver_cursor_position(self, cursor_num=1, postion: float = 0):
        """
        CURSor:VBArs:POS<x> <NR3>
        :param cursor_num:
        :param postion:
        :return:
        """
        cmd = "CURSor:VBArs:POS%d %s" % (cursor_num, postion)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def get_ver_cursor_position(self, cursor_num=1):
        """
        CURSor:VBArs:POS<x> <NR3>
        :param cursor_num:
        :param postion:
        :return:
        """
        cmd = "CURSor:VBArs:POS%d?" % cursor_num
        result = self.uxr_id.query(cmd)
        time.sleep(0.2)
        return float(result.replace("\n", ""))

    def set_cursor_state(self, state="ON"):
        """
        CURSor:STATE {<NR1>|ON|OFF}
        """
        cmd = "CURSor:STATE %s" % state
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_meas_gating_type(self, gating_type="OFF"):
        """
        MEASUrement:GATing {ON|OFF|<NR1>|ZOOM<x>|CURSor}
        """
        cmd = "MEASUrement:GATing %s" % gating_type
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def get_data(self, data_chan, start_point, stop_point):
        cmd = "WFMOutpre: ENCdg ASCii"
        self.uxr_id.write(cmd)
        time.sleep(0.2)
        cmd = "DATa:SOUrce %s" % data_chan
        self.uxr_id.write(cmd)
        time.sleep(0.2)
        cmd = "DATa:STARt %d" % start_point
        self.uxr_id.write(cmd)
        time.sleep(0.2)
        cmd = "DATa:STOP %d" % stop_point
        self.uxr_id.write(cmd)
        time.sleep(0.2)
        wf_data = self.uxr_id.query("WAVFrm?")
        time.sleep(1)
        return wf_data

    def save_picture(self, file_path, file_name):
        """capture the picture and save it
        :param file_path: example"C:\TekScope"
        :param file_name: example"1.PNG"
        """
        cmd = r":EXPORT:FILENAME " + '"' + file_path + "\\" + file_name + '"' + \
              "; FORMAT PNG; IMAGE NORMAL; PALETTE COLOR; VIEW FULLSCREEN"
        self.uxr_id.write(cmd)
        # file = file_path + "\\" + file_name + r".png"
        # cmd = "EXPort: FORMat PNG";  self.uxr_id.write(cmd); time.sleep(0.2) # {BMP | JPEG | PCX | PNG | TIFF}
        # cmd = 'EXPort: FILEName "%s"' % file; self.uxr_id.write(cmd); time.sleep(0.2)
        # cmd = "EXPort: VIEW FULLSCREEN"; self.uxr_id.write(cmd); time.sleep(0.2)      #  {FULLSCREEN | GRAticule | FULLNOmenu}
        # cmd = 'EXPort STARt'
        # self.uxr_id.write(cmd)
        # time.sleep(2)

    def save_screen_image(self, filename):
        cmd = ":DISK:SAVE:IMAGe '%s'" % filename
        self.uxr_id.write(cmd)
        print(f"Save Image to {filename}")
        time.sleep(2)

    def set_signal_load_pattern(self, chan_num, file_name, path=r"c:\Users\Public\Documents\Infiniium\Patterns\PRBS"):
        """:ANALyze:SIGNal:PATTern:LOAD <source>,"<pattern_file_path>"""
        file = path + "\\" + file_name + ".ptrn"
        # cmd = ':ANALyze:SIGNal:PATTern:LOAD CHAN%d,"%s"' % (chan_num, r"C:/Users/Public/Documents/Infiniium/Patterns/PRBS/PRBS7_7-8_bit.ptrn")
        cmd = ':ANALyze:SIGNal:PATTern:LOAD CHAN%d,"%s"' % (chan_num, file)
        # cmd = ':ANALyze:SIGNal:PATTern:LOAD CHAN1,"%s"' % (chan_num, file) "PRBS7_7-8_bit.ptrn
        self.uxr_id.write(cmd)
        time.sleep(0.2)
        # path = r"C:\Users\Public\Documents\Infiniium\Patterns\PRBS\PRBS7_7-8_bit.ptrn"
        # file = path + "\\" + "PRBS7_7-8_bit.ptrn"

    def set_signal_invert_state(self, state="OFF"):
        """:ANALyze:SIGNal:PATTern:INVert {{0 | OFF} | {1 | ON}}"""
        cmd = ":ANALyze:SIGNal:PATTern:INVert %s" % state
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_signal_reverse(self, state="OFF"):
        """:ANALyze:SIGNal:PATTern:REVerse {{0 | OFF} | {1 | ON}}"""
        cmd = ":ANALyze:SIGNal:PATTern:REVerse %s" % state
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_signal_clear_pattern(self, chan_num):
        cmd = ':ANALyze:SIGNal:PATTern:CLEar CHAN%d' % chan_num
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_signal_type(self, chan_num=1, data_type="NRZ"):
        data_type = data_type.strip().upper()
        cmd = ":ANALyze:SIGNal:TYPE CHAN%d, %s" % (chan_num, data_type)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_signal_pattern_length(self, chan_num=1, pattern_length="AUTO"):
        cmd = ":ANALyze:SIGNal:PATTern:PLENgth CHAN%d,%s" % (chan_num, pattern_length)
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    # def add_ber(self, chan_num=1):
    #     """:ANALyze:SIGNal:TYPE <source>,{UNSPecified | NRZ | PAM4 | PAM3 | PAM6
    #     | PAM8 | CPHY, <source_B-C>, <source_C-A> | FEXTension | SPECtral}"""
    #     cmd = ":MEASure:BER CHAN%d" % chan_num
    #     uxr_x.uxr_id.write(cmd)
    #     time.sleep(0.2)

    def add_meas_ber(self, chan_num=1, data_type="NRZ"):
        self.set_signal_type(chan_num, data_type)
        self.add_meas(chan_num=1, meas_type="BER")

    def set_uxr_state(self, state):
        # stat ["STOP"|"RUN"]
        self.uxr_id.write(f":{state.upper()}")

    def set_jitter_pattern_arbitrary(self):
        cmd='SYSTem:CONTrol "JitRandomPatternLength -1 parnLenRand"'
        self.uxr_id.write(cmd)
        time.sleep(0.2)

    def set_jitter_pattern_periodic(self):
        cmd = 'SYSTem:CONTrol "JitRandomPatternLength -1 patnLenPer"'
        self.uxr_id.write(cmd)
        time.sleep(0.2)
if __name__ == "__main__":
    uxr = Uxr0134a("TCPIP0::192.168.1.11::inst0::INSTR", "TCPIP")
