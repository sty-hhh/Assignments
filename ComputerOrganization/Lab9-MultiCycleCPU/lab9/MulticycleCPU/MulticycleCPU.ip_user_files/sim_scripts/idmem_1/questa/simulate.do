onbreak {quit -f}
onerror {quit -f}

vsim -t 1ps -lib xil_defaultlib idmem_opt

do {wave.do}

view wave
view structure
view signals

do {idmem.udo}

run -all

quit -force
