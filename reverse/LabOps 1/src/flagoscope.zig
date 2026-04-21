const State = @import("./state.zig").State;
const rl = @import("raylib");
const rg = @import("raygui");
const gui = @import("./gui.zig");
const std = @import("std");
const license = @import("./license.zig");

const FlagoscopeShader = struct {
    shader: rl.Shader,
    waviness_loc_index: i32,
    noise_loc_index: i32,
    time_loc_index: i32,
    stitchiness_loc_index: i32,

    fn init() !@This() {
        const s = try rl.loadShader("resources/flagoscope.vert", "resources/flagoscope.frag");

        return .{
            .shader = s,
            .waviness_loc_index = rl.getShaderLocation(s, "waviness"),
            .noise_loc_index = rl.getShaderLocation(s, "noise"),
            .time_loc_index = rl.getShaderLocation(s, "time"),
            .stitchiness_loc_index = rl.getShaderLocation(s, "stitchiness"),
        };
    }

    fn deinit(self: *const @This()) void {
        self.shader.unload();
    }

    fn set_waviness(self: *const @This(), new_value: f32) void {
        rl.setShaderValue(
            self.shader,
            self.waviness_loc_index,
            &new_value,
            rl.ShaderUniformDataType.float,
        );
    }

    fn set_noise(self: *const @This(), new_value: f32) void {
        rl.setShaderValue(
            self.shader,
            self.noise_loc_index,
            &new_value,
            rl.ShaderUniformDataType.float,
        );
    }

    fn set_stitchiness(self: *const @This(), new_value: f32) void {
        rl.setShaderValue(
            self.shader,
            self.stitchiness_loc_index,
            &new_value,
            rl.ShaderUniformDataType.float,
        );
    }

    fn update_time(self: *const @This()) void {
        const time: f32 = @floatCast(rl.getTime());
        rl.setShaderValue(self.shader, self.time_loc_index, &time, rl.ShaderUniformDataType.float);
    }
};

const TextBox = enum { Waviness, Noise, Stitchiness };

shader: FlagoscopeShader,
target: ?rl.RenderTexture2D = null,
is_help_shown: bool = false,
is_error_shown: bool = false,

waviness: f32 = 1.0,
waviness_text_buffer: std.ArrayList(u8) = .empty,
noise: f32 = 1.0,
noise_text_buffer: std.ArrayList(u8) = .empty,
stitchiness: f32 = 1.0,
stitchiness_text_buffer: std.ArrayList(u8) = .empty,

required_license: license.LicenseEdition,
flag: *const std.ArrayList(u8),
flag_index: usize = 0,
active_text_box: ?TextBox = null,

fn radius() f32 {
    return @min(gui.width(), gui.height()) * 0.75 / 2;
}

fn inner_radius() f32 {
    return radius() * 0.85;
}

pub fn init(flag: *const std.ArrayList(u8), required_license: license.LicenseEdition) !@This() {
    const shader = try FlagoscopeShader.init();
    errdefer shader.deinit();

    var self: @This() = .{
        .shader = shader,
        .flag = flag,
        .required_license = required_license,
    };

    try self.loadRenderTexture();

    self.shader.set_waviness(self.waviness);
    self.shader.set_noise(self.noise);
    self.shader.set_stitchiness(self.stitchiness);

    return self;
}

pub fn deinit(self: *@This()) void {
    self.shader.deinit();

    if (self.target) |t| {
        t.unload();
    }
}

fn loadRenderTexture(self: *@This()) !void {
    if (self.target) |t| {
        t.unload();
    }

    self.target = try rl.loadRenderTexture(@intFromFloat(inner_radius() * 2), @intFromFloat(inner_radius() * 2));
    errdefer self.target.?.unload();

    rl.genTextureMipmaps(&self.target.?.texture);
    rl.setTextureFilter(self.target.?.texture, rl.TextureFilter.anisotropic_16x);
}

pub fn draw(self: *@This(), _: bool) !?State {
    rl.clearBackground(gui.getBackgroundColor());

    if (gui.backButton()) {
        return State.menu;
    }

    // sliders
    {
        gui.relTextSize(11);
        var bounds = rl.Rectangle.init(60, (gui.height() - 30) / 2, gui.widthPercent(0.15), gui.heightPercent(0.1));

        // waviness
        if (gui.sliderEdit(
            bounds,
            "Waviness :",
            &self.waviness_text_buffer,
            std.heap.c_allocator,
            &self.waviness,
            0,
            1,
            self.active_text_box == TextBox.Waviness,
        ) catch 0 != 0) { //----
            self.active_text_box = null;

            if (self.waviness < 0.5 and !license.license_manager.isEdition(self.required_license)) {
                self.is_error_shown = true;
                self.waviness = 1.0;
            }

            self.shader.set_waviness(self.waviness);
        }

        if (rl.isMouseButtonPressed(rl.MouseButton.left) and rl.checkCollisionPointRec(rl.getMousePosition(), bounds)) {
            self.active_text_box = TextBox.Waviness;
        }

        // noise
        bounds.y += 10 + bounds.height;

        if (gui.sliderEdit(
            bounds,
            "Noise :",
            &self.noise_text_buffer,
            std.heap.c_allocator,
            &self.noise,
            0,
            1,
            self.active_text_box == TextBox.Noise,
        ) catch 0 != 0) {
            self.active_text_box = null;

            if (self.noise < 0.4 and !license.license_manager.isEdition(self.required_license)) {
                self.is_error_shown = true;
                self.noise = 1.0;
            }

            self.shader.set_noise(self.noise);
        }

        if (rl.isMouseButtonPressed(rl.MouseButton.left) and rl.checkCollisionPointRec(rl.getMousePosition(), bounds)) {
            self.active_text_box = TextBox.Noise;
        }

        // sitchiness
        bounds.y += 10 + bounds.height;

        if (gui.sliderEdit(
            bounds,
            "Stitchiness :",
            &self.stitchiness_text_buffer,
            std.heap.c_allocator,
            &self.stitchiness,
            0,
            1,
            self.active_text_box == TextBox.Stitchiness,
        ) catch 0 != 0) {
            self.active_text_box = null;

            if (self.stitchiness < 0.15 and !license.license_manager.isEdition(self.required_license)) {
                self.is_error_shown = true;
                self.stitchiness = 1.0;
            }

            self.shader.set_stitchiness(self.stitchiness);
        }

        if (rl.isMouseButtonPressed(rl.MouseButton.left) and rl.checkCollisionPointRec(rl.getMousePosition(), bounds)) {
            self.active_text_box = TextBox.Stitchiness;
        }

        gui.loadStyle();
    }

    self.drawCircle();

    // buttons
    {
        var bounds = rl.Rectangle.init(
            gui.width() / 2 - gui.iconButtonSize() - 5,
            gui.height() - gui.iconButtonSize() * 2,
            gui.iconButtonSize(),
            gui.iconButtonSize(),
        );

        if (rg.button(bounds, gui.iconText(rg.IconName.player_play_back))) {
            self.flag_index = @intCast(@mod(@as(isize, @intCast(self.flag_index)) - 1, @as(isize, @intCast(self.flag.items.len))));
        }

        bounds.x += 10 + gui.iconButtonSize();

        if (rg.button(bounds, gui.iconText(rg.IconName.player_play))) {
            self.flag_index = (self.flag_index + 1) % self.flag.items.len;
        }
    }

    if (self.is_error_shown) {
        try self.drawError();
    }

    return null;
}

fn drawError(self: *@This()) !void {
    const size = rl.Vector2.init(gui.widthPercent(0.3), gui.heightPercent(0.5));
    var bounds = rl.Rectangle.init(
        gui.centerStart(0, gui.width(), size.x),
        gui.centerStart(0, gui.height(), size.y),
        size.x,
        size.y,
    );

    if (rg.windowBox(bounds, "Error") != 0) {
        self.is_error_shown = false;
    }

    bounds.x += 5;
    bounds.width -= 5;
    bounds.height -= 24;
    bounds.y += 24;

    gui.relTextSize(20);
    rg.setStyle(rg.Control.default, .{ .default = .text_alignment_vertical }, @intFromEnum(rg.TextAlignmentVertical.top));
    rg.setStyle(rg.Control.default, .{ .default = .text_wrap_mode }, @intFromEnum(rg.TextWrapMode.word));
    defer gui.loadStyle();

    const gpa = std.heap.c_allocator;
    const text = try std.fmt.allocPrintSentinel(
        gpa,
        "The value is invalid and only available to {s} subscribers",
        .{@tagName(self.required_license)},
        0,
    );
    defer gpa.free(text);

    _ = rg.label(bounds, text);
}

fn drawCircle(self: *@This()) void {
    const anchor = rl.Vector2.init(
        gui.centerStart(0, gui.width(), inner_radius() * 2),
        gui.centerStart(0, gui.height(), inner_radius() * 2),
    );

    {
        self.target.?.begin();
        defer self.target.?.end();

        rl.clearBackground(rl.Color.blank);

        rg.setStyle(.default, .{ .control = .text_color_normal }, rl.Color.red.toInt());
        rg.setStyle(.default, .{ .default = .text_size }, @intFromFloat(inner_radius() * 2));
        gui.alignText(.center, .middle);
        defer gui.loadStyle();

        const flag_letter = [_:0]u8{self.flag.items[self.flag_index]};
        _ = rg.label(.init(0, 0, inner_radius() * 2, inner_radius() * 2), &flag_letter);
    }

    self.shader.update_time();
    self.shader.shader.activate();
    self.target.?.texture.drawRec(.init(0, 0, inner_radius() * 2, -inner_radius() * 2), anchor, rl.Color.white);
    self.shader.shader.deactivate();

    const foreground_color = rl.Color.fromInt(@bitCast(rg.getStyle(.default, .{ .default = .line_color })));
    rl.drawRing(
        .init(gui.width() / 2, gui.height() / 2),
        inner_radius() - 1,
        radius(),
        0,
        360,
        360,
        foreground_color,
    );
}

pub fn onResized(self: *@This()) !void {
    try self.loadRenderTexture();
}
