

module reg_en (
    input wire clk,
    input wire rst,
    input wire en,
    input wire [31:0] d,
    output wire [31:0] q
);

    logic [31:0] q;

    always @(posedge clk) begin
        if (rst) begin
            q <= 32'h0;
        end else if (en) begin
            q <= d;
        end
    end
    
endmodule


// Parent module with a miter with different inputs
module miter (
    input wire clk
    , output wire [31:0] qA
    , output wire [31:0] qB
);


    reg_en A (
        .clk(clk)
        , .q(qA)
    );

    reg_en B (
        .clk(clk)
        , .q(qB)
    );
        
endmodule