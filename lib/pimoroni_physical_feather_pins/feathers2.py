from . import pin_error
#import board
import microcontroller

def pin3():
    raise NotImplementedError

def pin5():
    return microcontroller.pin.GPIO18

def pin6():
    return microcontroller.pin.GPIO17

def pin7():
    return microcontroller.pin.GPIO16

def pin8():
    return microcontroller.pin.GPIO15

def pin9():
    return microcontroller.pin.GPIO14

def pin10():
    return microcontroller.pin.GPIO8

def pin11():
    return microcontroller.pin.GPIO36

def pin12():
    return microcontroller.pin.GPIO35

def pin13():
    return microcontroller.pin.GPIO37

def pin14():
    return microcontroller.pin.GPIO38

def pin15():
    return microcontroller.pin.GPIO39

def pin16():
#   This is 3V3 LDO 2 OUTPUT
    raise NotImplementedError

def pin17():
    return microcontroller.pin.GPIO3

def pin18():
    return microcontroller.pin.GPIO4

def pin19():
    return microcontroller.pin.GPIO5

def pin20():
    return microcontroller.pin.GPIO6

def pin21():
    return microcontroller.pin.GPIO9

def pin22():
    return microcontroller.pin.GPIO10

def pin23():
    return microcontroller.pin.GPIO11

def pin24():
    return microcontroller.pin.GPIO12

def pin25():
    return microcontroller.pin.GPIO13

def init(scope):
    """Pull the pin definitions into the main module namespace"""
    for key in globals().keys():
        if key.startswith('pin'):
            scope[key] = globals()[key]
