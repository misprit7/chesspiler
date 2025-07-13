module fn(
  input  wire [1:0] in,
  output wire [1:0] out
);
  assign out = in + 2'b01;
endmodule
