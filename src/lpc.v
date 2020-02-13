/*
 * iCEstick LPC TPM Sniffer (lpc.v)
 * 
 * LPC decoder
 * by Alexander Couzens (lynxis)
 * with TPM-specific modifications by Denis Andzakovic
 */

module lpc(
	input wire reset,
	input wire lpc_clk,
	input wire lpc_reset,
	input wire [3:0] lpc_ad,
	input wire lpc_frame,
	output wire [3:0] out_cyctype_dir,
	output wire [31:0] out_addr,
	output wire [7:0] out_data,
	output reg out_sync_timeout,
	output reg out_clk_enable);

	// type and direction. same as in LPC Spec 1.1
	// addr & data written or read

	// registers
	reg [3:0] counter;                      // counter
	reg [3:0] cyctype_dir;                  // mode & direction, same as in LPC Spec 1.1
	reg [31:0] addr;                        // 32 bit address
	reg [7:0] data;                         // 8 bit data

    // combinatorial logic
	assign out_cyctype_dir = cyctype_dir;
	assign out_data = data;
	assign out_addr = addr;

	// state machine
	localparam[3:0] STATE_IDLE = 4'd0;
    localparam[3:0] STATE_START = 4'd1;
    localparam[3:0] STATE_CYCLE_DIR = 4'd2;
    localparam[3:0] STATE_ADDRESS = 4'd3;
    localparam[3:0] STATE_TAR = 4'd4;
    localparam[3:0] STATE_SYNC = 4'd5;
    localparam[3:0] STATE_READ_DATA = 4'd6;
    localparam[3:0] STATE_ABORT = 4'd7;
	reg [3:0] state = STATE_IDLE;

    // synchronous logic
	always @(posedge lpc_clk or negedge lpc_reset)
    begin
		if (~lpc_reset)
        begin
			state <= STATE_IDLE;
			counter <= 4'd1;
		end else
        begin
			if (~lpc_frame)
            begin
				counter <= 4'd1;

                // TPM-specific modification to only log messages with the start
                // field b0101 (5) 
				if (lpc_ad == 4'b0101)                  // start condition
					state <= STATE_CYCLE_DIR;
				else
					state <= STATE_IDLE;                // abort
            end else
            begin
                // decrement counter
                counter <= counter - 1'd1;

                // 
                case (state)
                    STATE_CYCLE_DIR:
                        cyctype_dir <= lpc_ad;

                    STATE_ADDRESS:
                    begin
                        addr[31:4] <= addr[27:0];
                        addr[3:0] <= lpc_ad;
                    end

                    STATE_READ_DATA:
                    begin
                        data[7:4] <= lpc_ad;
                        data[3:0] <= data[7:4];
                    end

                    STATE_SYNC:
                    begin
                        if (lpc_ad == 4'b0000)
                            if (cyctype_dir[3] == 1'b0)
                            begin                       // I/O or memory
                                data <= 8'd0;
                                counter <= 4'd2;
                                state <= STATE_READ_DATA;
                            end else
                                state <= STATE_IDLE;   // unsupported DMA or reserved
                    end
                endcase

                if (counter == 1)
                begin
                    case (state)
                        STATE_CYCLE_DIR:
                        begin
                            out_clk_enable <= 1'b0;
                            out_sync_timeout <= 1'b0;

                            if (lpc_ad[3:2] == 2'b00)
                            begin                       // I/O
                                counter <= 4'd4;
                                addr <= 32'd0;
                                state <= STATE_ADDRESS;
                            end
                            else                        // don't care about anything other than I/O
                                state <= STATE_IDLE;
                        end

                        STATE_ADDRESS:
                        begin
                            if (cyctype_dir[1])         // write memory or I/O
                                state <= STATE_READ_DATA;
                            else                        // read memory or I/O
                                counter <= 4'd2;
                                state <= STATE_TAR;
                        end

                        STATE_TAR:
                        begin
                            counter <= 4'd1;
                            state <= STATE_SYNC;
                        end

                        STATE_SYNC:
                        begin
                            if (lpc_ad == 4'b1111)
                            begin
                                // TPM-specific modification
                                // only log data from address 0x24 (36)
                                if (addr == 32'h24)
                                begin 
                                    out_sync_timeout <= 1;
                                    out_clk_enable <= 1;
                                end

                                state <= STATE_IDLE;
                            end
                        end

                        STATE_READ_DATA:
                        begin
                            // TPM-specific modification
                            // only log data from address 0x24 (36)
                            if (addr == 32'h24)
                                out_clk_enable <= 1;

                            state <= STATE_IDLE;
                        end

                        // TODO: Missing TAR after READ_DATA
                        // 
                        STATE_ABORT:
                            counter <= 4'd2;
					endcase
				end
			end
		end
	end

endmodule
