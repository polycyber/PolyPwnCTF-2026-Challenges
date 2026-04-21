const State = @import("./state.zig").State;
const license = @import("./license.zig");
const gui = @import("./gui.zig");
const std = @import("std");
const rl = @import("raylib");
const rg = @import("raygui");

const Selection = struct {
    item: usize,
    selection_time: std.time.Instant,
};

const detection_time_seconds = 5;
const food_texture_resolution = 16;

food_texture: rl.Texture,
food_texture_len: usize,
flag_texture: rl.Texture,
selection: ?Selection = null,
flag: *const std.ArrayList(u8),
required_license: license.LicenseEdition,

pub fn init(flag: *const std.ArrayList(u8), required_license: license.LicenseEdition) !@This() {
    const food_texture = try rl.loadTexture("resources/food.png");
    errdefer food_texture.unload();

    const flag_texture = try rl.loadTexture("resources/flag.png");
    errdefer flag_texture.unload();

    const food_texture_len = try std.math.divExact(usize, @intCast(food_texture.width), food_texture_resolution);

    return .{
        .flag_texture = flag_texture,
        .food_texture = food_texture,
        .food_texture_len = food_texture_len,
        .flag = flag,
        .required_license = required_license,
    };
}

pub fn deinit(self: *@This()) void {
    self.flag_texture.unload();
    self.food_texture.unload();
}

pub fn draw(self: *@This(), _: bool) !?State {
    rl.clearBackground(gui.getBackgroundColor());

    if (gui.backButton()) {
        return State.menu;
    }

    try self.drawItems();
    try self.drawDetector();

    return null;
}

var scroll = rl.Vector2.init(0, 0);
var view = rl.Rectangle.init(0, 0, 0, 0);
fn drawItems(self: *@This()) !void {
    const width = gui.width() / 3;
    const columns = 5;
    const spacing = width / columns;

    const content = rl.Rectangle.init(
        0,
        0,
        width,
        @as(f32, @floatFromInt(try std.math.divCeil(usize, self.food_texture_len, columns))) * spacing,
    );

    const control = rg.ScrollBarProperty.scroll_slider_size;
    const scrollbar_width = rg.getStyle(.scrollbar, .{ .control = @as(*const rg.ControlProperty, @ptrCast(&control)).* });
    const scroll_rec = rl.Rectangle.init(
        50,
        gui.iconButtonSize() + 60,
        content.width + @as(f32, @floatFromInt(scrollbar_width)),
        gui.height() - gui.iconButtonSize() - 90,
    );

    // see https://github.com/raysan5/raygui/blob/master/examples/scroll_panel/scroll_panel.c
    _ = rg.scrollPanel(
        scroll_rec,
        null,
        content,
        &scroll,
        &view,
    );

    var mouse_cell: rl.Vector2 = undefined;
    {
        rl.beginScissorMode(@intFromFloat(view.x), @intFromFloat(view.y), @intFromFloat(view.width), @intFromFloat(view.height));
        defer rl.endScissorMode();

        _ = rg.grid(
            .init(scroll_rec.x, scroll_rec.y + scroll.y, content.width, content.height),
            "",
            content.width / columns,
            1,
            &mouse_cell,
        );

        for (0..self.food_texture_len + 1) |i| {
            const coord = rl.Vector2.init(@floatFromInt(i % columns), @floatFromInt(i / columns));
            const target = rl.Rectangle.init(
                scroll_rec.x + spacing * coord.x,
                scroll_rec.y + scroll.y + coord.y * spacing,
                spacing,
                spacing,
            );

            self.drawItem(i, gui.pad(target, 5), rl.Color.white);
        }
    }

    if (rl.isMouseButtonPressed(rl.MouseButton.left) and mouse_cell.x >= 0 and mouse_cell.y >= 0) {
        try self.setSelection(@as(usize, @intFromFloat(mouse_cell.x)) + @as(usize, @intFromFloat(mouse_cell.y)) * columns);
    }
}

fn drawDetector(self: *@This()) !void {
    const panel_bounds = rl.Rectangle.init(
        gui.width() / 2,
        90,
        gui.width() / 2 - 30,
        gui.height() - 130,
    );

    _ = rg.panel(panel_bounds, null);

    if (self.selection) |s| {
        const item_size = panel_bounds.height / 2 - 10;
        const item_bounds = rl.Rectangle.init(panel_bounds.x + (panel_bounds.width - item_size) / 2, panel_bounds.y + 5, item_size, item_size);
        _ = rg.panel(item_bounds, null);

        const elapsed_time = @as(f32, @floatFromInt((try std.time.Instant.now()).since(s.selection_time))) / std.time.ns_per_s;
        const is_scanning = elapsed_time < detection_time_seconds;

        var tint = rl.Color.white;
        if (is_scanning) {
            tint = tint.alpha(0.75 + std.math.sin(elapsed_time * 2) / 4);
        }

        self.drawItem(s.item, gui.pad(item_bounds, 5), tint);

        const content_bounds = rl.Rectangle.init(
            panel_bounds.x,
            panel_bounds.y + panel_bounds.height / 2,
            panel_bounds.width,
            panel_bounds.height / 2,
        );

        const gpa = std.heap.c_allocator;
        var text = std.ArrayList(u8).empty;
        defer text.deinit(gpa);

        rg.setStyle(.default, .{ .default = .text_wrap_mode }, @intFromEnum(rg.TextWrapMode.word));
        if (is_scanning) {
            gui.alignText(.center, .middle);
            gui.relTextSize(24);

            try text.appendSlice(gpa, "Scanning");

            const dots: usize = @intFromFloat((elapsed_time - std.math.floor(elapsed_time)) * 4);
            for (0..dots) |_| {
                try text.appendSlice(gpa, " .");
            }

            try text.append(gpa, 0);

            _ = rg.label(content_bounds, @ptrCast(text.items));
        } else {
            gui.alignText(.center, .top);
            gui.relTextSize(16);

            if (s.item == self.food_texture_len) {
                try text.appendSlice(gpa, "FLAG\n(100% certainty)\nDetails: ");

                if (license.license_manager.isEdition(self.required_license)) {
                    try text.appendSlice(gpa, self.flag.items);
                } else {
                    try text.print(gpa, "A {s} license is required to view this item's details", .{@tagName(self.required_license)});
                }
            } else {
                var rng = std.Random.DefaultPrng.init(s.item);
                const details = [_][]const u8{
                    "Smells nice",
                    "Tastes good",
                    "Spoiled",
                    "Antioxidant",
                };

                try text.print(
                    gpa,
                    "NOT FLAG\n({d}% certainty)\nDetails: {s}",
                    .{
                        rng.random().intRangeAtMost(u8, 50, 100),
                        details[rng.random().uintLessThan(usize, details.len)],
                    },
                );
            }

            try text.append(gpa, 0);
        }

        _ = rg.label(content_bounds, @ptrCast(text.items));
        gui.loadStyle();
    } else {
        gui.alignText(.center, .middle);
        gui.relTextSize(24);
        defer gui.loadStyle();

        _ = rg.label(panel_bounds, "No item selected");
    }
}

fn setSelection(self: *@This(), value: ?usize) !void {
    self.selection = if (value) |v| .{ .item = v, .selection_time = try std.time.Instant.now() } else null;
}

fn drawItem(self: *const @This(), index: usize, dest: rl.Rectangle, tint: rl.Color) void {
    const TextureInfo = struct {
        texture: rl.Texture2D,
        source_rect: rl.Rectangle,
    };

    const texture_info: TextureInfo = if (index < self.food_texture_len) .{
        .texture = self.food_texture,
        .source_rect = .init(@floatFromInt(index * food_texture_resolution), 0, food_texture_resolution, food_texture_resolution),
    } else .{
        .texture = self.flag_texture,
        .source_rect = .init(0, 0, @floatFromInt(self.flag_texture.width), @floatFromInt(self.flag_texture.height)),
    };

    texture_info.texture.drawPro(
        texture_info.source_rect,
        dest,
        .init(0, 0),
        0,
        tint,
    );
}
