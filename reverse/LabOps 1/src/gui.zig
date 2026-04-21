const rl = @import("raylib");
const rg = @import("raygui");
const std = @import("std");

pub fn iconButtonSize() f32 {
    return heightPercent(0.075);
}

pub fn width() f32 {
    return @floatFromInt(rl.getScreenWidth());
}

pub fn height() f32 {
    return @floatFromInt(rl.getScreenHeight());
}

pub fn widthPercent(percent: f32) f32 {
    return width() * percent;
}

pub fn heightPercent(percent: f32) f32 {
    return height() * percent;
}

pub fn maximize() void {}

pub fn centerStart(base_pos: f32, container_size: f32, inner_size: f32) f32 {
    return base_pos + (container_size - inner_size) / 2;
}

pub fn relTextSize(size: u32) void {
    const percent = @as(f32, @floatFromInt(size)) / 400;
    rg.setStyle(.default, .{ .default = .text_size }, @intFromFloat(heightPercent(percent)));
    rg.setStyle(.default, .{ .default = .text_line_spacing }, @intFromFloat(heightPercent(percent) * 1.2));
}

pub fn loadStyle() void {
    rg.loadStyleDefault();

    rg.setStyle(.default, .{ .control = .border_color_normal }, 0x1c8d00ff);
    rg.setStyle(.default, .{ .control = .base_color_normal }, 0x161313ff);
    rg.setStyle(.default, .{ .control = .text_color_normal }, 0x38f620ff);
    rg.setStyle(.default, .{ .control = .border_color_focused }, @bitCast(@as(u32, 0xc3fbc6ff)));
    rg.setStyle(.default, .{ .control = .base_color_focused }, 0x43bf2eff);
    rg.setStyle(.default, .{ .control = .text_color_focused }, @bitCast(@as(u32, 0xdcfadcff)));
    rg.setStyle(.default, .{ .control = .border_color_pressed }, 0x1f5b19ff);
    rg.setStyle(.default, .{ .control = .base_color_pressed }, 0x43ff28ff);
    rg.setStyle(.default, .{ .control = .text_color_pressed }, 0x1e6f15ff);
    rg.setStyle(.default, .{ .control = .border_color_disabled }, 0x223b22ff);
    rg.setStyle(.default, .{ .control = .base_color_disabled }, 0x182c18ff);
    rg.setStyle(.default, .{ .control = .text_color_disabled }, 0x244125ff);
    relTextSize(16);
    // rg.setStyle(.default, .{ .default = .text_spacing }, 0x00000000);
    rg.setStyle(.default, .{ .default = .line_color }, @bitCast(@as(u32, 0xe6fce3ff)));
    rg.setStyle(.default, .{ .default = .background_color }, 0x0c1505ff);
    rg.setStyle(rg.Control.default, .{ .default = .text_wrap_mode }, @intFromEnum(rg.TextWrapMode.none));
}

pub fn getBackgroundColor() rl.Color {
    const raw_color = rg.getStyle(.default, .{ .default = .background_color });

    return .fromInt(@bitCast(raw_color));
}

pub fn backButton() bool {
    return rg.button(.init(30, 30, iconButtonSize(), iconButtonSize()), iconText(rg.IconName.arrow_left));
}

pub fn iconText(comptime icon: rg.IconName) *const [5:0]u8 {
    return comptime std.fmt.comptimePrint("#{}#", .{@intFromEnum(icon)});
}

pub fn sliderEdit(
    bounds: rl.Rectangle,
    text: [:0]const u8,
    value_buffer: *std.ArrayList(u8),
    gpa: std.mem.Allocator,
    value: *f32,
    min_value: f32,
    max_value: f32,
    edit_mode: bool,
) !i32 {
    var result: i32 = 0;

    if (rg.slider(
        .init(bounds.x, bounds.y + bounds.height / 2, bounds.width, bounds.height / 2),
        "",
        "",
        value,
        min_value,
        max_value,
    ) != 0) {
        result = 1;
    }

    _ = rg.label(.init(bounds.x, bounds.y, bounds.width, bounds.height / 2), text);

    const labelWidth = @as(f32, @floatFromInt(rg.getTextWidth(text)));

    if (!std.mem.endsWith(u8, value_buffer.items, &[_]u8{ 0, 0 })) {
        try value_buffer.appendNTimes(gpa, 0, 2);
    }

    if (rg.textBox(
        .init(bounds.x + labelWidth, bounds.y, bounds.width - labelWidth, bounds.height / 2),
        @ptrCast(value_buffer.items),
        @as(i32, @intCast(value_buffer.items.len)),
        edit_mode,
    )) {
        value_buffer.items.len = std.mem.len(@as([*:0]const u8, @ptrCast(value_buffer.items)));

        if (std.fmt.parseFloat(f32, value_buffer.items) catch null) |parsed_value| {
            if (min_value <= parsed_value and parsed_value <= max_value) {
                value.* = parsed_value;
            }
        }

        result = 1;
    }

    if (!edit_mode) {
        value_buffer.items.len = 0;
        try value_buffer.print(gpa, "{d}", .{value.*});
    }

    return result;
}

pub fn pad(rect: rl.Rectangle, padding: f32) rl.Rectangle {
    return .init(rect.x + padding, rect.y + padding, rect.width - padding * 2, rect.height - padding * 2);
}

pub fn alignText(horizontal: rg.TextAlignment, vertical: rg.TextAlignmentVertical) void {
    rg.setStyle(.default, .{ .control = .text_alignment }, @intFromEnum(horizontal));
    rg.setStyle(.default, .{ .default = .text_alignment_vertical }, @intFromEnum(vertical));
}
