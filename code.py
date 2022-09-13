# m4 and generic imports
import board
# import neopixel
import busio
import analogio
# Pimoroni EnviroPlusWing
import pimoroni_physical_feather_pins
import simpleio
from lib.pimoroni_envirowing import screen, gas
from lib.pimoroni_envirowing.screen import plotter
from adafruit_bme280 import basic as adafruit_bme280
from pimoroni_circuitpython_ltr559 import Pimoroni_LTR559
from adafruit_bme280.basic import Adafruit_BME280_I2C
# OLED Screen imports
# import adafruit_displayio_sh1107
# from adafruit_displayio_sh1107 import SH1107
# generic display imports
import displayio
import terminalio
from adafruit_display_text import label
# code flow imports
import time
# generic Midi Imports
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.pitch_bend import PitchBend
#  uncomment if using USB MIDI
import usb_midi
import array
import math

displayio.release_displays()

# MIDI_PLUGGED_IN: bool = True


# def setup_midi() -> adafruit_midi.MIDI:
#     #  USB MIDI:
#     #  midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)
#     #  UART MIDI:
#     uart = busio.UART(board.TX, board.RX, baudrate=31250, timeout=0.001)  # init UART
#     midi_in_channel = 1
#     midi_out_channel = 1
#     midi_io: adafruit_midi.MIDI = adafruit_midi.MIDI(
#         midi_in=uart,
#         midi_out=uart,
#         in_channel=(midi_in_channel - 1),
#         out_channel=(midi_out_channel - 1),
#         debug=False,
#     )
#     return midi_io


# def setup_neo_pixel() -> neopixel.NeoPixel:
#     m4pixel: neopixel.NeoPixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0)
#     m4pixel.fill((0, 0, 0))
#     return m4pixel


def setup_i2c_pim() -> busio.I2C:
    i2c_bus: busio.I2C = busio.I2C(board.SCL, board.SDA)
    return i2c_bus


def setup_i2c_s() -> busio.I2C:
    i2c_bus: busio.I2C = board.I2C()
    return i2c_bus


# def setup_oled_screen(i2c_bus: busio.I2C) -> SH1107:
#     display_bus: displayio.I2CDisplay = displayio.I2CDisplay(i2c_bus, device_address=0x3C)
#     width = 128
#     height = 64
#     display: SH1107 = adafruit_displayio_sh1107.SH1107(
#         display_bus, width=width, height=height, rotation=0)
#     return display


def setup_bme280(i2c_bus: busio.I2C) -> Adafruit_BME280_I2C:
    bme280sensor: Adafruit_BME280_I2C = adafruit_bme280.Adafruit_BME280_I2C(i2c_bus, address=0x76)
    bme280sensor.sea_level_pressure = 1013.25
    return bme280sensor


def mean(values):
    return sum(values) / len(values)


def normalized_rms(values):
    minbuf = int(mean(values))
    samples_sum = sum(
        float(sample - minbuf) * (sample - minbuf)
        for sample in values
    )

    return math.sqrt(samples_sum / len(values))


# def send_midi_panic():
#     print("All MIDI notes off")
#     for x in range(128):
#         midi.send(NoteOff(x, 0))


# from https://stackoverflow.com/a/49955617
def human_format(num, round_to=0):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num = round(num / 1000.0, round_to)
    return '{:.{}f}{}'.format(round(num, round_to), round_to, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])


# colours for the plotter are defined as rgb values in hex, with 2 bytes for each colour
red = 0xFF0000
green = 0x00FF00
blue = 0x0000FF


def setup_gas_plotter(displayscreen):
    # Set up the gas screen plotter
    # the max value is set to 3.3 as its the max voltage the feather can read
    gas_splotter = plotter.ScreenPlotter([red, green, blue], max_value=3.3, min_value=0.5, top_space=10, display=displayscreen)

    # add a colour coded text label for each reading
    gas_splotter.group.append(label.Label(terminalio.FONT, text="OX: {:.0f}", color=red, x=0, y=5))
    gas_splotter.group.append(label.Label(terminalio.FONT, text="RED: {:.0f}", color=green, x=50, y=5))
    gas_splotter.group.append(label.Label(terminalio.FONT, text="NH3: {:.0f}", color=blue, x=110, y=5))
    return gas_splotter


pim_interval = 540
# interval = 540  # full screen of reading spans 24hrs
# interval = 1  # uncomment for 1 reading per second
# interval = 60  # uncomment for 1 reading per minute
# interval = 3600  # uncomment for 1 reading per hour
last_reading = time.monotonic()


def process_pim_pulse(gas_splotter):

    gas_reading = gas.read_all()
    # update the line graph
    # the value plotted on the graph is the voltage drop over each sensor, not the resistance, as it graphs nicer

    oxidizing = gas_reading._OX.value * (gas_reading._OX.reference_voltage / 65535)
    reducing = gas_reading._RED.value * (gas_reading._RED.reference_voltage / 65535)
    nh3 = gas_reading._NH3.value * (gas_reading._NH3.reference_voltage / 65535)

    print(f"oxi:{oxidizing} red:{reducing} nh3:{nh3}")


    gas_splotter.update(
        oxidizing,
        reducing,
        nh3,
        draw=False
    )

    # update the labels
    gas_splotter.group[1].text = "OX:{}".format(oxidizing)
    gas_splotter.group[2].text = "RED:{}".format(reducing)
    gas_splotter.group[3].text = "NH3:{}".format(nh3)

    gas_splotter.draw()

    print(str(oxidizing) + " " + str(reducing) + " " + str(nh3))


# # Open-G tuning G4 D3 G3 B3 D4
# banjo_string_tuning_1 = 79  # "G4"  # 79?
# banjo_string_tuning_2 = 62  # "D3"  # 62?
# banjo_string_tuning_3 = 67  # "G3"  # 67?
# banjo_string_tuning_4 = 71  # "B3"  # 71?
# banjo_string_tuning_5 = 74  # "D4"  # 74?

# banjo_string_current_1 = banjo_string_tuning_1
# banjo_string_current_2 = banjo_string_tuning_2
# banjo_string_current_3 = banjo_string_tuning_3
# banjo_string_current_4 = banjo_string_tuning_4
# banjo_string_current_5 = banjo_string_tuning_5

# note_queue = []


# def add_roll():
#     v = 90
#     # string1
#     # print(nanoseconds_per_tick)
#     # print(nanoseconds_per_tick/100)
#     # print(10000000)
#     # delay = 10000000  # nanoseconds_per_tick / 100
#     delay = nanoseconds_per_tick / 10
#     note_queue.append({'time_stamp': stamp, 'midi_note': banjo_string_current_3, 'velocity': int(v)})
#     # note_queue.append({'time_stamp': stamp + note_duration + delay, 'midi_note': banjo_string_current_3, 'velocity': 0})

#     note_queue.append({'time_stamp': stamp + delay, 'midi_note': banjo_string_current_4, 'velocity': v})
#     # note_queue.append({'time_stamp': stamp + note_duration + delay, 'midi_note': banjo_string_current_4, 'velocity': 0})

#     note_queue.append({'time_stamp': stamp + delay * 2, 'midi_note': banjo_string_current_2, 'velocity': v})
#     # note_queue.append({'time_stamp': stamp + note_duration + (delay * 2), 'midi_note': banjo_string_current_2, 'velocity': 0})

#     note_queue.append({'time_stamp': stamp + delay * 3, 'midi_note': banjo_string_current_5, 'velocity': v})
#     # note_queue.append({'time_stamp': stamp + note_duration + (delay * 3), 'midi_note': banjo_string_current_5, 'velocity': 0})

#     note_queue.append({'time_stamp': stamp, 'midi_note': banjo_string_current_1, 'velocity': int(v/2)})
#     # note_queue.append({'time_stamp': stamp + note_duration + (delay * 2), 'midi_note': banjo_string_current_1, 'velocity': 0})
#     pass


# def add_strum():
#     v = 90
#     # string1
#     # print(nanoseconds_per_tick)
#     # print(nanoseconds_per_tick/100)
#     # print(10000000)
#     # delay = 10000000  # nanoseconds_per_tick / 100
#     delay = nanoseconds_per_tick / 500
#     note_queue.append({'time_stamp': stamp, 'midi_note': banjo_string_current_1, 'velocity': int(v/2)})
#     note_queue.append({'time_stamp': stamp + note_duration + delay*2, 'midi_note': banjo_string_current_1, 'velocity': 0})

#     note_queue.append({'time_stamp': stamp + delay, 'midi_note': banjo_string_current_2, 'velocity': v})
#     note_queue.append({'time_stamp': stamp + note_duration + delay, 'midi_note': banjo_string_current_2, 'velocity': 0})

#     note_queue.append({'time_stamp': stamp + delay*2, 'midi_note': banjo_string_current_3, 'velocity': v})
#     note_queue.append({'time_stamp': stamp + note_duration + (delay*2), 'midi_note': banjo_string_current_3, 'velocity': 0})

#     note_queue.append({'time_stamp': stamp + delay*3, 'midi_note': banjo_string_current_4, 'velocity': v})
#     note_queue.append({'time_stamp': stamp + note_duration + (delay*3), 'midi_note': banjo_string_current_4, 'velocity': 0})

#     note_queue.append({'time_stamp': stamp + delay*4, 'midi_note': banjo_string_current_1, 'velocity': v})
#     note_queue.append({'time_stamp': stamp + note_duration + (delay*4), 'midi_note': banjo_string_current_4, 'velocity': 0})
#     pass


# pixel: neopixel.NeoPixel = setup_neo_pixel()


# if MIDI_PLUGGED_IN:
#     midi: adafruit_midi.MIDI = setup_midi()
#     midiMessage = ""
#     msg = midi.receive()

#     root_notes = (48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59)  # used during config
#     note_numbers = (48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
#                     60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
#                     72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83)
#     note_names = ("C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2",
#                   "C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", "A#3", "B3",
#                   "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",)

#     root_picked = True  # state of root selection
#     mode_picked = True  # state of mode selection
#     mode_choice = 0

#     major = (0, 2, 4, 5, 7, 9, 11)
#     minor = (0, 2, 3, 5, 7, 8, 10)
#     dorian = (0, 2, 3, 5, 7, 9, 10)
#     phrygian = (0, 1, 3, 5, 7, 8, 10)
#     lydian = (0, 2, 4, 6, 7, 9, 11)
#     mixolydian = (0, 2, 4, 5, 7, 9, 10)
#     locrian = (0, 1, 3, 5, 6, 8, 10)

#     modes = [major, minor, dorian, phrygian, lydian, mixolydian, locrian]
#     mode_names = ("Major/Ionian",
#                   "Minor/Aeolian",
#                   "Dorian",
#                   "Phrygian",
#                   "Lydian",
#                   "Mixolydian",
#                   "Locrian")

#     intervals = list(major)
#     scale_root = root_notes[7]  # default G2 if nothing is picked

#     scale = []  # create the base scale
#     for i in range(7):
#         scale.append(scale_root + intervals[i])

#     midi_notes = []  # build the list with three octaves


#     for m in range(7):
#         midi_notes.append(scale[m])
#     for l in range(7):
#         midi_notes.append(scale[l] + 12)
#     for k in range(7):
#         midi_notes.append(scale[k] + 24)

#     send_midi_panic()



PIM_PLUGGED_IN = False

i2cP: busio.I2C = setup_i2c_pim()
bme280: Adafruit_BME280_I2C = setup_bme280(i2cP)
ltr559 = Pimoroni_LTR559(i2cP)
gas_reading = gas.read_all()
mic: analogio.AnalogIn = analogio.AnalogIn(pimoroni_physical_feather_pins.pin8())
displayscreen = screen.Screen()
PIM_PLUGGED_IN = True


OLED_PLUGGED_IN = False
# try:
#     i2c: busio.I2C = setup_i2c_s()
#     displayscreen: SH1107 = setup_oled_screen(i2c)
#     OLED_PLUGGED_IN = True
# except Exception:
#     OLED_PLUGGED_IN = False


print("start screen")

splash: displayio.Group = displayio.Group()
displayscreen.show(splash)
test_text = "Hello World"
test_text_area = label.Label(
    terminalio.FONT, text=test_text, color=0xFFFFFF, x=4, y=6
)
splash.append(test_text_area)

# micmin = 65535
# micmax = 0
# samples = array.array('H', [0] * 160)

# PIM_PLUGGED_IN = False

current_step = 0

pix_brightness = .5
mic_current = 0

# pulse = True
# bpm = 60  # beat per minute
# tpb = 1  # ticks per beat

# ticks_per_minute = bpm * tpb
# ticks_per_second = ticks_per_minute / 60
# seconds_per_tick = 1/ticks_per_second
# nanoseconds_per_tick = seconds_per_tick * 1000000000


# print(nanoseconds_per_tick)

# stamp = time.monotonic_ns()
# next_tick = stamp + nanoseconds_per_tick
# current_step = -1

# tick_pattern = (-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1)
# # tick_pattern = (0, 7, 0, 7, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0)
# note_duration = nanoseconds_per_tick * .7
# note_off_queue = []

gas_splotter = setup_gas_plotter(displayscreen)
last_pim_reading = time.monotonic()
print("start loop")
while True:
    # begin loop

    # pulse = False
    # stamp = time.monotonic_ns()
    # if stamp > next_tick:
    #     next_tick = stamp + nanoseconds_per_tick
    #     pulse = True

    # if pulse:
    #     current_step = (current_step + 1) % tpb
    #     # add_strum()
    #     # add_roll()
    #     # Note On
    #     if tick_pattern[current_step] > -1:
    #         temp_note = midi_notes[tick_pattern[current_step]]
    #         note_off_queue.append({'TStamp': stamp+note_duration, 'Note': temp_note})
    #         midi.send(NoteOn(temp_note, 120))
    #     # print("MIDI NoteOn:", note_names[note_numbers.index(midi_notes[current_step])])
    #     # print(temp_note)

    # # Process note_queue
    # # note_queue.append({'time_stamp': stamp, 'midi_note': banjo_string_current_1, 'velocity': v})

    # for q in note_queue:
    #     if q["time_stamp"] < stamp:
    #         midi.send(NoteOn(q["midi_note"], q["velocity"]))
    #         if q["velocity"] > 0:
    #             print("MIDI NoteOn:", note_names[note_numbers.index(q["midi_note"])], q["velocity"])
    #         note_queue.remove(q)

    # for z in note_off_queue:
    #     # print(z["TStamp"])
    #     if z["TStamp"] < stamp:
    #         midi.send(NoteOn(z["Note"], 0))
    #         note_off_queue.remove(z)

    # print(len(note_off_queue))

    # if PIM_PLUGGED_IN and last_pim_reading + pim_interval < time.monotonic():
    last_pim_reading = time.monotonic()
    lux = ltr559.get_lux()
    prox = ltr559.get_proximity()

    process_pim_pulse(gas_splotter)

    # ox = gas_reading._OX.value * (gas_reading._OX.reference_voltage / 65535)
    # red = gas_reading._RED.value * (gas_reading._RED.reference_voltage / 65535)
    # nh3 = gas_reading._NH3.value * (gas_reading._NH3.reference_voltage / 65535)

    temp = bme280.temperature
    pres = bme280.pressure
    hum = bme280.humidity
    alt = bme280.altitude
    # sample = abs(mic.value - 32768)

    print(f"temp:{temp} pres:{pres} hum:{hum} alt:{alt}")

        # mic_current = mic.value

        # if mic_current > micmax:
        #     micmax = mic.value
        # elif mic_current < micmin:
        #     micmin = mic_current
        # mic_range = micmax - micmin
        # micdec = simpleio.map_range(mic_current, micmin, micmax, 0, 1)

        # pix_brightness = micdec

        # print(str(ox) + " " + str(red) + " " + str(nh3))
        # test_text_area.text = str(midiMessage)

    # if MIDI_PLUGGED_IN:
    #     msg = midi.receive()

    #     if msg is not None:
    #         #  if a NoteOn message...
    #         if isinstance(msg, NoteOn):
    #             string_msg = 'NoteOn'
    #             #  get note number
    #             string_val = str(msg.note)
    #             msg_out = msg
    #             msg_out.note = msg_out.note
    #             print(lux*200)
    #             pitch_weird = PitchBend(int(lux*200), channel=msg_out.channel)
    #             midi.send(pitch_weird)
    #         #  if a NoteOff message...
    #         if isinstance(msg, NoteOff):
    #             string_msg = 'NoteOff'
    #             #  get note number
    #             string_val = str(msg.note)
    #             msg_out = msg
    #         #  if a PitchBend message...
    #         if isinstance(msg, PitchBend):
    #             string_msg = 'PitchBend'
    #             #  get value of pitchbend
    #             string_val = str(msg.pitch_bend)
    #             msg_out = msg
    #         #  if a CC message...
    #         if isinstance(msg, ControlChange):
    #             string_msg = 'ControlChange'
    #             #  get CC message number
    #             string_val = str(msg.control)
    #             msg_out = msg
    #         #  update text area with message type and value of message as strings
    #         test_text_area.text = (string_msg + " " + string_val)
    #         print(string_msg + " " + string_val)
    #         midi.send(msg_out)

    #     # i = 0
    #     # midi.send(NoteOn(midi_notes[i], 120))
    #     # print("MIDI NoteOn:", note_names[note_numbers.index(midi_notes[i])])
    #     # time.sleep(0.15)
    #     # midi.send(NoteOn(midi_notes[i], 0))


    # # m4neopixel
    # pixel.fill((1, 1, 50))
    # pixel.brightness = pix_brightness

    time.sleep(3)  # a little delay here helps avoid debounce annoyances
    # end loop
    pass
