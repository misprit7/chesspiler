module fn(
  input  wire [31:0] a, b, c, d, e, f, g, h,
  input  wire [31:0] k, w,
  output wire [31:0] a_out, b_out, c_out, d_out, e_out, f_out, g_out, h_out
);
  // SHA-256 round function
  // S1 = (e rightrotate 6) xor (e rightrotate 11) xor (e rightrotate 25)
  wire [31:0] s1;
  assign s1 = ((e >> 6) | (e << 26)) ^ ((e >> 11) | (e << 21)) ^ ((e >> 25) | (e << 7));
  
  // ch = (e and f) xor ((not e) and g)
  wire [31:0] ch;
  assign ch = (e & f) ^ (~e & g);
  
  // temp1 = h + S1 + ch + k + w
  wire [31:0] temp1;
  assign temp1 = h + s1 + ch + k + w;
  
  // S0 = (a rightrotate 2) xor (a rightrotate 13) xor (a rightrotate 22)
  wire [31:0] s0;
  assign s0 = ((a >> 2) | (a << 30)) ^ ((a >> 13) | (a << 19)) ^ ((a >> 22) | (a << 10));
  
  // maj = (a and b) xor (a and c) xor (b and c)
  wire [31:0] maj;
  assign maj = (a & b) ^ (a & c) ^ (b & c);
  
  // temp2 = S0 + maj
  wire [31:0] temp2;
  assign temp2 = s0 + maj;
  
  // Update registers for next round
  assign h_out = g;
  assign g_out = f;
  assign f_out = e;
  assign e_out = d + temp1;
  assign d_out = c;
  assign c_out = b;
  assign b_out = a;
  assign a_out = temp1 + temp2;
endmodule 