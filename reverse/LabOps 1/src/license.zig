const rl = @import("raylib");
const rg = @import("raygui");
const gui = @import("./gui.zig");
const std = @import("std");
const fixed_string = @import("./fixed_string.zig");
const license_base = @import("./license_base.zig");
const flags = @import("./flags.zig");

const emscripten = std.os.emscripten;

pub const LicenseEdition = license_base.LicenseEdition;

pub var in_upgrade_popup = false;
var error_message: ?[]const u8 = null;
pub var license_manager = license_base.LicenseManager.init();

const local_storage_key = "license";

pub noinline fn maybeShowUpgradePopup() !void {
    if (!in_upgrade_popup) {
        return;
    }

    const popup_dimensions = rl.Vector2.init(gui.widthPercent(0.5), gui.heightPercent(0.7));
    const full_popup_bounds = rl.Rectangle.init(
        gui.centerStart(0, gui.width(), popup_dimensions.x),
        gui.centerStart(0, gui.height(), popup_dimensions.y),
        popup_dimensions.x,
        popup_dimensions.y,
    );

    _ = rg.panel(full_popup_bounds, null);

    const popup_bounds = gui.pad(full_popup_bounds, 20);

    {
        gui.relTextSize(24);
        gui.alignText(.left, .top);
        defer gui.loadStyle();

        _ = rg.label(popup_bounds, "Upgrade");
    }

    if (rg.button(
        .init(popup_bounds.x + popup_bounds.width - gui.iconButtonSize(), popup_bounds.y, gui.iconButtonSize(), gui.iconButtonSize()),
        gui.iconText(.cross),
    )) {
        in_upgrade_popup = false;
    }

    const key_pressed = @intFromEnum(rl.getKeyPressed());
    if (@intFromEnum(rl.KeyboardKey.a) <= key_pressed and key_pressed <= @intFromEnum(rl.KeyboardKey.z)) {
        const key_char: u8 = @intCast(key_pressed - @intFromEnum(rl.KeyboardKey.a) + 'A');

        license_manager.advance(key_char);
    } else if (@intFromEnum(rl.KeyboardKey.backspace) == key_pressed) {
        license_manager.revert();
    }

    const license_key = license_manager.license_key.string();
    for (0..license_manager.license_key.buffer.len) |i| {
        const entries_per_line = license_manager.license_key.buffer.len / 2;
        const text_size = gui.heightPercent(0.08);
        const entry_width = popup_bounds.width / @as(f32, @floatFromInt(entries_per_line));

        const position = rl.Vector2
            .init(@floatFromInt(i % entries_per_line), @floatFromInt(i / entries_per_line))
            .multiply(.init(entry_width, text_size))
            .add(.init(popup_bounds.x, popup_bounds.y + popup_bounds.height / 3));

        rl.drawLineV(position.add(.init(entry_width / 20, 0)), position.add(.init(entry_width - entry_width * 2 / 20, 0)), rl.Color.white);

        if (i >= license_key.len) {
            continue;
        }

        const font = try rl.getFontDefault();
        rl.drawTextCodepoint(font, license_key[i], position.add(.init(0, -text_size)), text_size, rl.Color.white);
    }

    if (error_message) |msg| {
        rg.setStyle(.default, .{ .control = .text_color_normal }, @bitCast(rl.Color.red.toInt()));
        defer gui.loadStyle();

        const error_label = try std.fmt.allocPrintSentinel(std.heap.c_allocator, "Error: {s}!", .{msg}, 0);
        defer std.heap.c_allocator.free(error_label);

        _ = rg.label(.init(popup_bounds.x + 10, popup_bounds.y + popup_bounds.height / 2 + 30, popup_bounds.width - 10, 30), error_label);

        const dismiss_text = "Dismiss";
        const dismiss_text_width = @as(f32, @floatFromInt(rg.getTextWidth(dismiss_text))) * 1.5;
        if (rg.button(
            .init(popup_bounds.x + 10, popup_bounds.y + popup_bounds.height / 2 + 60, dismiss_text_width, 40),
            dismiss_text,
        )) {
            error_message = null;
        }
    }

    const validate_text = "Validate";
    const validate_text_width = @as(f32, @floatFromInt(rg.getTextWidth(validate_text))) * 1.5;
    if (rg.button(
        .init(popup_bounds.x + popup_bounds.width - validate_text_width, popup_bounds.y + popup_bounds.height - 30, validate_text_width, 40),
        validate_text,
    )) {
        if (license_manager.validate()) |_| {
            in_upgrade_popup = false;
            error_message = null;
        } else |err| {
            error_message = switch (err) {
                license_base.LicenseError.LicenseTooShort => "License key too short",
                license_base.LicenseError.LicenseInvalid => "License key invalid",
            };
        }

        try flags.refreshFlags();
        _ = save() catch null;
    }
}

pub noinline fn load() !void {
    const loaded_license = @as(?[*:0]u8, emscripten.emscripten_run_script_string(
        std.fmt.comptimePrint("localStorage.getItem('{s}')", .{local_storage_key}),
    )) orelse return;

    license_manager.load(std.mem.span(loaded_license));
}

noinline fn save() !void {
    const license_key = license_manager.license_key.string();

    var encoded: std.ArrayList(u8) = .empty;
    defer encoded.deinit(std.heap.c_allocator);

    try std.base64.standard.Encoder.encodeWriter(encoded.writer(std.heap.c_allocator), license_key);

    const script = try std.fmt.allocPrintSentinel(
        std.heap.c_allocator,
        "localStorage.setItem('{s}', atob('{s}'))",
        .{ local_storage_key, encoded.items },
        0,
    );
    defer std.heap.c_allocator.free(script);

    emscripten.emscripten_run_script(script);
}
