const std = @import("std");
const rl = @import("raylib");
const rg = @import("raygui");
const gui = @import("./gui.zig");
const Menu = @import("./menu.zig");
const Experiments = @import("./experiments.zig");
const Flagoscope = @import("./flagoscope.zig");
const Detector = @import("./detector.zig");
const license = @import("./license.zig");
const State = @import("./state.zig").State;
const flags = @import("./flags.zig");

const emscripten = std.os.emscripten;

var shader: rl.Shader = undefined;
var target: rl.RenderTexture = undefined;
var time_loc_index: i32 = 0;
var state: State = State.menu;
var changedState = true;
var detector: Detector = undefined;
var experiments: Experiments = undefined;
var flagoscope: Flagoscope = undefined;
var menu: Menu = undefined;

var resolutionLocIndex: i32 = -1;
pub fn main() anyerror!void {
    rl.setConfigFlags(.{ .msaa_4x_hint = true, .window_maximized = true, .window_resizable = true });

    rl.initWindow(40, 40, "LabOps Synergy 365 Executive");

    defer rl.closeWindow();

    gui.loadStyle();

    shader = try rl.loadShader("resources/scan.vert", "resources/scan.frag");
    defer shader.unload();

    time_loc_index = rl.getShaderLocation(shader, "time");
    resolutionLocIndex = rl.getShaderLocation(shader, "resolution");

    rl.setShaderValue(
        shader,
        resolutionLocIndex,
        &rl.Vector2.init(gui.width(), gui.height()),
        rl.ShaderUniformDataType.vec2,
    );

    target = try rl.loadRenderTexture(@intFromFloat(gui.width()), @intFromFloat(gui.height()));
    defer target.unload();

    try license.load();
    try flags.refreshFlags();

    // load views
    experiments = try .init(&flags.gold_flag, license.LicenseEdition.Gold);
    defer experiments.deinit();

    flagoscope = try .init(&flags.bronze_flag, license.LicenseEdition.Bronze);
    defer flagoscope.deinit();

    detector = try .init(&flags.silver_flag, license.LicenseEdition.Silver);
    defer detector.deinit();

    menu = try .init();
    defer menu.deinit();

    defer flags.bronze_flag.deinit(std.heap.c_allocator);
    defer flags.silver_flag.deinit(std.heap.c_allocator);
    defer flags.gold_flag.deinit(std.heap.c_allocator);

    emscripten.emscripten_set_main_loop(updateDrawFrame, 0, 1);
}

fn reloadShaders() !void {
    target.unload();
    target = try rl.loadRenderTexture(@intFromFloat(gui.width()), @intFromFloat(gui.height()));

    rl.setShaderValue(
        shader,
        resolutionLocIndex,
        &rl.Vector2.init(gui.width(), gui.height()),
        rl.ShaderUniformDataType.vec2,
    );
}

var lastSize = rl.Vector2.init(-1, -1);

export fn updateDrawFrame() void {
    rl.maximizeWindow();

    if (!std.math.approxEqRel(f32, lastSize.x, gui.width(), 0.01) or !std.math.approxEqRel(f32, lastSize.y, gui.height(), 0.01)) {
        lastSize.x = gui.width();
        lastSize.y = gui.height();

        reloadShaders() catch |err| std.log.err("reloadShaders() error: {any}", .{err});
        flagoscope.onResized() catch |err| std.log.err("flagoscope resize error: {any}", .{err});
    }

    target.begin();
    {
        const next_state_err = switch (state) {
            State.menu => menu.draw(changedState),
            State.experiments => experiments.draw(changedState),
            State.flagoscope => flagoscope.draw(changedState),
            State.detector => detector.draw(changedState),
        };

        if (next_state_err) |next_state| {
            if (next_state) |n| {
                state = n;
                changedState = true;
            } else {
                changedState = false;
            }
        } else |err| {
            std.log.err("drawer() error: {any}", .{err});
        }
    }
    target.end();

    rl.beginDrawing();
    {
        const time: f32 = @floatCast(rl.getTime());
        rl.setShaderValue(shader, time_loc_index, &time, rl.ShaderUniformDataType.float);
        shader.activate();
        target.texture.drawRec(.init(0, 0, gui.width(), -gui.height()), .init(0, 0), rl.Color.white);
        shader.deactivate();
    }
    rl.endDrawing();
}
