`timescale 10ns / 10ns

module tb();

reg clk = 0;

always #10 clk = ~clk;

reg up = 1;

initial begin
	
	#50000; 

	up = 0;
	
	#500000;

	$finish();
end

top dut(
	.clk8(clk),
	.lcd_fmark(1),
	.keypad_up(up)
);



// Dump waves
  initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, tb);
  end

endmodule


module TRELLIS_IO(
	inout B,
	input I,
	input T,
	output O
);
	parameter DIR = "INPUT";
	reg T_pd;
	always @(*) if (T === 1'bz) T_pd <= 1'b0; else T_pd <= T;

	generate
		if (DIR == "INPUT") begin
			assign B = 1'bz;
			assign O = B;
		end else if (DIR == "OUTPUT") begin
			assign B = T_pd ? 1'bz : I;
			assign O = 1'bx;
		end else if (DIR == "BIDIR") begin
			assign B = T_pd ? 1'bz : I;
			assign O = B;
		end else begin
			ERROR_UNKNOWN_IO_MODE error();
		end
	endgenerate

endmodule



module ODDRX1F
(
  output wire Q,     // 1-bit DDR output
  input wire SCLK,   // 1-bit clock input
  input wire D0,     // 1-bit data input (positive edge)
  input wire D1,     // 1-bit data input (negative edge)
  input wire RST     // 1-bit reset
);

	reg D1_f;
	reg D1_ff;
	reg D1_fff;
	reg D0_f;
	reg D0_ff;

    reg Qn, Qp;
	
	always @(posedge SCLK) begin
		Qp <= D0_ff;
		
		D0_f <= D0;
		D0_ff <= D0_f;
		
		D1_f <= D1;
		D1_ff <= D1_f;
		D1_fff <= D1_ff;
	end

	always @(negedge SCLK) 
		Qn <= D1_fff;


    assign Q = SCLK ? Qp : Qn;

endmodule