// FPGA时钟路由和分布代码示例
// 展示各种时钟缓冲器的使用方法和配置

module fpga_clock_distribution_example (
    input  wire        sys_clk_p,        // 系统时钟输入
    input  wire        sys_clk_n,        // 系统时钟差分输入
    input  wire        reset_n,          // 异步复位
    output wire        led_out,          // LED输出
    output wire        uart_tx,          // UART发送
    input  wire        uart_rx,          // UART接收
    output wire        ddr_clk,          // DDR时钟
    output wire        ddr_clk_n,        // DDR差分时钟
    output wire        ddr_cke           // DDR时钟使能
);

// ============================================================================
// 全局时钟缓冲器 (BUFG) 示例
// ============================================================================

// 全局时钟输入缓冲器
IBUFGDS sys_clk_ibufgds (
    .I(sys_clk_p),
    .IB(sys_clk_n),
    .O(sys_clk)
);

// 全局时钟缓冲器
BUFG sys_clk_bufg (
    .I(sys_clk),
    .O(sys_clk_buf)
);

// 全局时钟使能控制
BUFGCE sys_clk_enable (
    .CE(sys_clk_en),
    .I(sys_clk_buf),
    .O(sys_clk_gated)
);

// ============================================================================
// 区域时钟缓冲器 (BUFH) 示例
// ============================================================================

// 水平时钟缓冲器 - 用于同一行的多个模块
BUFH clk_div2_bufh (
    .I(clk_div2),
    .CE(1'b1),
    .CLR(1'b0),
    .O(clk_div2_h)
);

// 区域时钟缓冲器 - 用于特定区域
BUFR clk_div4_bufr (
    .I(clk_div2),
    .CE(1'b1),
    .CLR(1'b0),
    .O(clk_div4_r)
);

// ============================================================================
// I/O时钟缓冲器 (BUFIO) 示例
// ============================================================================

// DDR接口时钟缓冲器
BUFIO ddr_clk_bufio (
    .I(ddr_clk_in),
    .O(ddr_clk_io)
);

// DDR控制时钟缓冲器
BUFG ddr_ctrl_clk_bufg (
    .I(ddr_clk_in),
    .O(ddr_ctrl_clk)
);

// ============================================================================
// 多区域时钟缓冲器 (BUFMR) 示例
// ============================================================================

// 多区域时钟缓冲器 - 跨越多个时钟区域
BUFMR ddr_clk_bufmr (
    .I(ddr_clk_in),
    .O(ddr_clk_region[0]),
    .O(ddr_clk_region[1])
);

// ============================================================================
// 时钟分频器示例
// ============================================================================

// 使用BUFR进行可编程分频
reg [7:0] clk_div_counter;
wire clk_div2;
wire clk_div4;
wire clk_div8;

always @(posedge sys_clk_buf or posedge reset_n) begin
    if (!reset_n)
        clk_div_counter <= 8'h00;
    else
        clk_div_counter <= clk_div_counter + 1;
end

assign clk_div2 = clk_div_counter[0];
assign clk_div4 = clk_div_counter[1];
assign clk_div8 = clk_div_counter[2];

// ============================================================================
// PLL/MMCM时钟管理示例
// ============================================================================

// MMCM时钟管理单元
MMCME2_BASE #(
    .BANDWIDTH("OPTIMIZED"),
    .CLKFBOUT_MULT_F(8.0),
    .CLKFBOUT_PHASE(0.0),
    .CLKIN1_PERIOD(10.0),
    .DIVCLK_DIVIDE(1),
    .CLKOUT0_DIVIDE_F(4.0),
    .CLKOUT0_PHASE(0.0),
    .CLKOUT0_DUTY_CYCLE(0.5),
    .CLKOUT1_DIVIDE(8),
    .CLKOUT1_PHASE(0.0),
    .CLKOUT1_DUTY_CYCLE(0.5),
    .CLKOUT2_DIVIDE(16),
    .CLKOUT2_PHASE(0.0),
    .CLKOUT2_DUTY_CYCLE(0.5),
    .CLKOUT3_DIVIDE(32),
    .CLKOUT3_PHASE(0.0),
    .CLKOUT3_DUTY_CYCLE(0.5)
) mmcm_inst (
    .CLKIN1(sys_clk),
    .CLKFBIN(clk_feedback),
    .RST(1'b0),
    .PWRDWN(1'b0),
    .CLKOUT0(mmcm_clk0),
    .CLKOUT0B(),
    .CLKOUT1(mmcm_clk1),
    .CLKOUT1B(),
    .CLKOUT2(mmcm_clk2),
    .CLKOUT2B(),
    .CLKOUT3(mmcm_clk3),
    .CLKOUT3B(),
    .CLKOUT4(),
    .CLKOUT5(),
    .CLKOUT6(),
    .CLKFBOUT(clk_feedback),
    .CLKFBOUTB()
);

// MMCM输出缓冲器
BUFG mmcm_clk0_bufg (.I(mmcm_clk0), .O(mmcm_clk0_buf));
BUFG mmcm_clk1_bufg (.I(mmcm_clk1), .O(mmcm_clk1_buf));
BUFG mmcm_clk2_bufg (.I(mmcm_clk2), .O(mmcm_clk2_buf));
BUFG mmcm_clk3_bufg (.I(mmcm_clk3), .O(mmcm_clk3_buf));

// ============================================================================
// DDR接口时钟生成示例
// ============================================================================

// DDR时钟输出
ODDR ddr_clk_oddr (
    .Q(ddr_clk),
    .C(ddr_clk_io),
    .CE(1'b1),
    .D1(1'b1),
    .D2(1'b0),
    .R(1'b0),
    .S(1'b0)
);

ODDR ddr_clk_n_oddr (
    .Q(ddr_clk_n),
    .C(ddr_clk_io),
    .CE(1'b1),
    .D1(1'b0),
    .D2(1'b1),
    .R(1'b0),
    .S(1'b0)
);

// DDR时钟使能
ODDR ddr_cke_oddr (
    .Q(ddr_cke),
    .C(sys_clk_buf),
    .CE(1'b1),
    .D1(ddr_cke_reg),
    .D2(ddr_cke_reg),
    .R(1'b0),
    .S(1'b0)
);

// ============================================================================
// UART接口时钟示例
// ============================================================================

// UART波特率时钟生成
reg [15:0] uart_divider;
reg uart_clk;
wire uart_clk_en;

always @(posedge sys_clk_buf or posedge reset_n) begin
    if (!reset_n) begin
        uart_divider <= 16'h0000;
        uart_clk <= 1'b0;
    end else begin
        if (uart_divider == BAUD_DIVIDER-1) begin
            uart_divider <= 16'h0000;
            uart_clk <= ~uart_clk;
        end else begin
            uart_divider <= uart_divider + 1;
        end
    end
end

assign uart_clk_en = (uart_divider == 16'h0000);

// UART发送器
reg [7:0] uart_tx_data;
reg uart_tx_en;
reg uart_tx_state;
reg [3:0] uart_tx_bit_count;
reg uart_tx_bit;

always @(posedge uart_clk or posedge reset_n) begin
    if (!reset_n) begin
        uart_tx_data <= 8'h00;
        uart_tx_en <= 1'b0;
        uart_tx_state <= 1'b0;
        uart_tx_bit_count <= 4'h0;
        uart_tx_bit <= 1'b1;
    end else begin
        case (uart_tx_state)
            1'b0: begin  // 空闲状态
                if (uart_tx_en) begin
                    uart_tx_state <= 1'b1;
                    uart_tx_bit_count <= 4'h0;
                end
                uart_tx_bit <= 1'b1;
            end
            1'b1: begin  // 发送数据
                if (uart_tx_bit_count < 4'd10) begin
                    case (uart_tx_bit_count)
                        4'd0: uart_tx_bit <= 1'b0;        // 起始位
                        4'd1: uart_tx_bit <= uart_tx_data[0];
                        4'd2: uart_tx_bit <= uart_tx_data[1];
                        4'd3: uart_tx_bit <= uart_tx_data[2];
                        4'd4: uart_tx_bit <= uart_tx_data[3];
                        4'd5: uart_tx_bit <= uart_tx_data[4];
                        4'd6: uart_tx_bit <= uart_tx_data[5];
                        4'd7: uart_tx_bit <= uart_tx_data[6];
                        4'd8: uart_tx_bit <= uart_tx_data[7];
                        4'd9: uart_tx_bit <= 1'b1;        // 停止位
                    endcase
                    uart_tx_bit_count <= uart_tx_bit_count + 1;
                end else begin
                    uart_tx_state <= 1'b0;
                    uart_tx_en <= 1'b0;
                end
            end
        endcase
    end
end

assign uart_tx = uart_tx_bit;

// ============================================================================
// LED闪烁控制示例
// ============================================================================

// LED闪烁计数器
reg [23:0] led_counter;
reg led_state;

always @(posedge sys_clk_buf or posedge reset_n) begin
    if (!reset_n) begin
        led_counter <= 24'h000000;
        led_state <= 1'b0;
    end else begin
        led_counter <= led_counter + 1;
        if (led_counter == 24'hFFFFFF) begin
            led_state <= ~led_state;
        end
    end
end

assign led_out = led_state;

// ============================================================================
// 时钟门控信号生成
// ============================================================================

// 系统时钟使能
reg sys_clk_en_reg;
always @(posedge sys_clk_buf or posedge reset_n) begin
    if (!reset_n)
        sys_clk_en_reg <= 1'b1;
    else
        sys_clk_en_reg <= 1'b1;  // 始终使能，可根据需要修改
end

assign sys_clk_en = sys_clk_en_reg;

// DDR时钟使能
reg ddr_cke_reg;
always @(posedge sys_clk_buf or posedge reset_n) begin
    if (!reset_n)
        ddr_cke_reg <= 1'b0;
    else
        ddr_cke_reg <= 1'b1;  // DDR初始化完成后使能
end

// ============================================================================
// 时钟域交叉处理
// ============================================================================

// 异步复位同步器
reg reset_sync_1;
reg reset_sync_2;
reg reset_sync_3;

always @(posedge sys_clk_buf or posedge reset_n) begin
    if (!reset_n) begin
        reset_sync_1 <= 1'b0;
        reset_sync_2 <= 1'b0;
        reset_sync_3 <= 1'b0;
    end else begin
        reset_sync_1 <= 1'b1;
        reset_sync_2 <= reset_sync_1;
        reset_sync_3 <= reset_sync_2;
    end
end

wire sys_reset = reset_sync_3;

// 跨时钟域数据同步
reg [7:0] data_sync_1;
reg [7:0] data_sync_2;
reg [7:0] data_sync_3;

always @(posedge mmcm_clk0_buf or posedge sys_reset) begin
    if (sys_reset) begin
        data_sync_1 <= 8'h00;
        data_sync_2 <= 8'h00;
        data_sync_3 <= 8'h00;
    end else begin
        data_sync_1 <= uart_tx_data;
        data_sync_2 <= data_sync_1;
        data_sync_3 <= data_sync_2;
    end
end

// ============================================================================
// 时钟约束示例 (UCF格式)
// ============================================================================

# 全局时钟约束
NET "sys_clk" TNM_NET = "sys_clk";
TIMESPEC TS_sys_clk = PERIOD "sys_clk" 10 ns HIGH 50%;

# 时钟组约束
NET "mmcm_clk0" TNM_NET = "mmcm_clk0";
NET "mmcm_clk1" TNM_NET = "mmcm_clk1";
TIMESPEC TS_mmcm_clk0 = PERIOD "mmcm_clk0" 2.5 ns HIGH 50%;
TIMESPEC TS_mmcm_clk1 = PERIOD "mmcm_clk1" 5 ns HIGH 50%;

# 异步时钟组
NET "uart_clk" TNM_NET = "uart_clk";
TIMESPEC TS_uart_clk = PERIOD "uart_clk" 104.167 ns HIGH 50%;

# 时钟偏斜约束
NET "sys_clk" MAXSKEW = 0.5 ns;
NET "ddr_clk" MAXSKEW = 0.25 ns;

# 时钟使能约束
NET "sys_clk_en" TIG;
NET "ddr_cke" TIG;

endmodule

// ============================================================================
// 时钟缓冲器使用指南
// ============================================================================

/*
1. BUFG (全局时钟缓冲器)
   - 用于系统主时钟
   - 提供最低偏斜和抖动
   - 驱动能力最强
   - 建议用于: 全局时钟、PLL输出、MMCM输出

2. BUFH (水平时钟缓冲器)
   - 用于同一行的多个模块
   - 水平方向时钟分布
   - 功耗较低
   - 建议用于: 行内时钟分配、模块级时钟

3. BUFR (区域时钟缓冲器)
   - 用于特定区域
   - 可编程分频
   - 灵活的区域控制
   - 建议用于: 局部时钟、I/O接口时钟

4. BUFIO (I/O时钟缓冲器)
   - 专用I/O时钟网络
   - 极低抖动
   - 高速I/O支持
   - 建议用于: DDR接口、高速串行接口

5. BUFMR (多区域时钟缓冲器)
   - 跨越多个时钟区域
   - 资源共享
   - 灵活连接
   - 建议用于: 跨区域时钟分配、大型设计

设计注意事项:
- 合理选择时钟缓冲器类型
- 最小化时钟域数量
- 优化时钟网络负载
- 控制时钟偏斜
- 考虑功耗优化
- 使用时钟门控技术
*/