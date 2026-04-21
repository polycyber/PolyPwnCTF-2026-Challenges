const std = @import("std");
const license = @import("./license.zig");

const emscripten = std.os.emscripten;

pub var bronze_flag = std.ArrayList(u8).empty;
pub var silver_flag = std.ArrayList(u8).empty;
pub var gold_flag = std.ArrayList(u8).empty;

pub fn refreshFlags() !void {
    const url = try std.fmt.allocPrintSentinel(std.heap.c_allocator, "/flags?lk={s}", .{license.license_manager.license_key.string()}, 0);
    defer std.heap.c_allocator.free(url);

    var raw_buffer: ?[*]u8 = null;
    var size: i32 = -1;
    var err: i32 = 0;
    emscripten.emscripten_wget_data(url, @ptrCast(&raw_buffer), &size, &err);

    if (err != 0 or raw_buffer == null) {
        const data = "failed to fetch flags";
        bronze_flag.items.len = 0;
        try bronze_flag.appendSlice(std.heap.c_allocator, data);
        silver_flag.items.len = 0;
        try silver_flag.appendSlice(std.heap.c_allocator, data);
        gold_flag.items.len = 0;
        try gold_flag.appendSlice(std.heap.c_allocator, data);

        return;
    }

    const buffer = raw_buffer.?[0..@as(usize, @intCast(size))];
    defer std.heap.raw_c_allocator.free(buffer);

    const Response = struct {
        bronze_flag: []const u8,
        silver_flag: []const u8,
        gold_flag: []const u8,
    };

    const parsed = try std.json.parseFromSlice(Response, std.heap.c_allocator, buffer, .{});
    defer parsed.deinit();

    const response = parsed.value;

    bronze_flag.items.len = 0;
    try bronze_flag.appendSlice(std.heap.c_allocator, response.bronze_flag);
    silver_flag.items.len = 0;
    try silver_flag.appendSlice(std.heap.c_allocator, response.silver_flag);
    gold_flag.items.len = 0;
    try gold_flag.appendSlice(std.heap.c_allocator, response.gold_flag);
}
