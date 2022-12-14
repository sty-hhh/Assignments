# Clock signal
set_property PACKAGE_PIN W5 [get_ports clk]							
	set_property IOSTANDARD LVCMOS33 [get_ports clk]
	create_clock -add -name sys_clk_pin -period 10.00 -waveform {0 5} [get_ports clk]
# Addr
set_property PACKAGE_PIN V17 [get_ports {ra_addr[0]}]					
        set_property IOSTANDARD LVCMOS33 [get_ports {ra_addr[0]}]	
set_property PACKAGE_PIN V16 [get_ports {ra_addr[1]}]					
        set_property IOSTANDARD LVCMOS33 [get_ports {ra_addr[1]}]	
set_property PACKAGE_PIN W16 [get_ports {ra_addr[2]}]					
        set_property IOSTANDARD LVCMOS33 [get_ports {ra_addr[2]}]	
set_property PACKAGE_PIN W17 [get_ports {ra_addr[3]}]					
        set_property IOSTANDARD LVCMOS33 [get_ports {ra_addr[3]}]
set_property PACKAGE_PIN W15 [get_ports {rb_addr[0]}]					
        set_property IOSTANDARD LVCMOS33 [get_ports {rb_addr[0]}]          
set_property PACKAGE_PIN V15 [get_ports {rb_addr[1]}]					
        set_property IOSTANDARD LVCMOS33 [get_ports {rb_addr[1]}]
set_property PACKAGE_PIN W14 [get_ports {rb_addr[2]}]					
        set_property IOSTANDARD LVCMOS33 [get_ports {rb_addr[2]}]
set_property PACKAGE_PIN W13 [get_ports {rb_addr[3]}]                    
        set_property IOSTANDARD LVCMOS33 [get_ports {rb_addr[3]}]
set_property PACKAGE_PIN V2 [get_ports {rd_addr[0]}]                    
        set_property IOSTANDARD LVCMOS33 [get_ports {rd_addr[0]}]
set_property PACKAGE_PIN T3 [get_ports {rd_addr[1]}]                    
        set_property IOSTANDARD LVCMOS33 [get_ports {rd_addr[1]}]          
set_property PACKAGE_PIN T2 [get_ports {rd_addr[2]}]                    
        set_property IOSTANDARD LVCMOS33 [get_ports {rd_addr[2]}]
set_property PACKAGE_PIN R3 [get_ports {rd_addr[3]}]                    
        set_property IOSTANDARD LVCMOS33 [get_ports {rd_addr[3]}] 
# sel        
set_property PACKAGE_PIN R2 [get_ports {sel}]                    
                set_property IOSTANDARD LVCMOS33 [get_ports {sel}]
# memtoreg              
set_property PACKAGE_PIN T1 [get_ports {memtoreg}]                    
                set_property IOSTANDARD LVCMOS33 [get_ports {memtoreg}]                                                             
# seg
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
# ans
set_property PACKAGE_PIN U2 [get_ports {ans[0]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {ans[0]}]
set_property PACKAGE_PIN U4 [get_ports {ans[1]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {ans[1]}]
set_property PACKAGE_PIN V4 [get_ports {ans[2]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {ans[2]}]
set_property PACKAGE_PIN W4 [get_ports {ans[3]}]					
	set_property IOSTANDARD LVCMOS33 [get_ports {ans[3]}]
# Buttons
set_property PACKAGE_PIN U18 [get_ports rst]						
        set_property IOSTANDARD LVCMOS33 [get_ports rst]
