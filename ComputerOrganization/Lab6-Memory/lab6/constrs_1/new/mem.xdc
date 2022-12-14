set_property PACKAGE_PIN W5 [get_ports clk]							
	set_property IOSTANDARD LVCMOS33 [get_ports clk]
	create_clock -add -name sys_clk_pin -period 10.00 -waveform {0 5} [get_ports clk]

set_property PACKAGE_PIN V17 [get_ports {addr[0]}]					
        set_property IOSTANDARD LVCMOS33 [get_ports {addr[0]}]	
set_property PACKAGE_PIN V16 [get_ports {addr[1]}]					
        set_property IOSTANDARD LVCMOS33 [get_ports {addr[1]}]	
set_property PACKAGE_PIN W16 [get_ports {addr[2]}]					
        set_property IOSTANDARD LVCMOS33 [get_ports {addr[2]}]	
set_property PACKAGE_PIN W17 [get_ports {addr[3]}]					
        set_property IOSTANDARD LVCMOS33 [get_ports {addr[3]}]
set_property PACKAGE_PIN W15 [get_ports {addr[4]}]					
        set_property IOSTANDARD LVCMOS33 [get_ports {addr[4]}]          
set_property PACKAGE_PIN V15 [get_ports {addr[5]}]					
        set_property IOSTANDARD LVCMOS33 [get_ports {addr[5]}]
set_property PACKAGE_PIN W14 [get_ports {addr[6]}]					
        set_property IOSTANDARD LVCMOS33 [get_ports {addr[6]}]
set_property PACKAGE_PIN W13 [get_ports {addr[7]}]                    
        set_property IOSTANDARD LVCMOS33 [get_ports {addr[7]}]
         	
#7 segment display
set_property PACKAGE_PIN W7 [get_ports {seg[6]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {seg[6]}]
set_property PACKAGE_PIN W6 [get_ports {seg[5]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {seg[5]}]
set_property PACKAGE_PIN U8 [get_ports {seg[4]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {seg[4]}]
set_property PACKAGE_PIN V8 [get_ports {seg[3]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {seg[3]}]
set_property PACKAGE_PIN U5 [get_ports {seg[2]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {seg[2]}]
set_property PACKAGE_PIN V5 [get_ports {seg[1]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {seg[1]}]
set_property PACKAGE_PIN U7 [get_ports {seg[0]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {seg[0]}]

set_property PACKAGE_PIN U2 [get_ports {ans[0]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {ans[0]}]
set_property PACKAGE_PIN U4 [get_ports {ans[1]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {ans[1]}]
set_property PACKAGE_PIN V4 [get_ports {ans[2]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {ans[2]}]
set_property PACKAGE_PIN W4 [get_ports {ans[3]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {ans[3]}]
##Buttons
set_property PACKAGE_PIN U18 [get_ports rst]						
        set_property IOSTANDARD LVCMOS33 [get_ports rst]
 