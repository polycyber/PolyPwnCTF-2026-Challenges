const State = @import("./state.zig").State;
const rl = @import("raylib");
const rg = @import("raygui");
const gui = @import("./gui.zig");
const license = @import("./license.zig");
const std = @import("std");

progress: f32 = 0.0,

pub fn init() !@This() {
    return .{};
}

pub fn deinit(self: *@This()) void {
    _ = self;
}

pub fn draw(self: *@This(), _: bool) !?State {
    rl.clearBackground(gui.getBackgroundColor());

    _ = rg.label(.init(30, 30, gui.width(), 60), "LabOps Synergy 365 Executive");

    if (self.progress < 1.0) {
        const progressBarWidth = gui.widthPercent(0.8);
        const progressBarHeight = gui.widthPercent(0.1);
        _ = rg.progressBar(
            .init(
                gui.centerStart(0, gui.width(), progressBarWidth),
                gui.centerStart(0, gui.height(), progressBarHeight),
                progressBarWidth,
                progressBarHeight,
            ),
            "",
            "",
            &self.progress,
            0,
            1,
        );
        self.progress += 0.01;

        return null;
    }

    const separation = gui.heightPercent(0.125);
    const buttonWidth = @as(f32, @floatFromInt(rg.getTextWidth("Experiments"))) * 1.5;
    var buttonBounds = rl.Rectangle.init(gui.width() - buttonWidth - separation, separation, buttonWidth, gui.heightPercent(0.15));

    if (rg.button(buttonBounds, "Experiments")) {
        return State.experiments;
    }

    buttonBounds.y += separation + buttonBounds.height;

    if (rg.button(buttonBounds, "Flagoscope")) {
        return State.flagoscope;
    }

    buttonBounds.y += separation + buttonBounds.height;

    if (rg.button(buttonBounds, "Detector")) {
        return State.detector;
    }

    const license_box = rl.Rectangle.init(
        50,
        120,
        gui.widthPercent(0.5),
        gui.height() - 180,
    );

    _ = rg.groupBox(license_box, "License information");

    if (rg.button(.init(license_box.x + 5, license_box.y + license_box.height / 2 - 25, 50, 50), gui.iconText(rg.IconName.key))) {
        license.in_upgrade_popup = true;
    }

    const text = if (license.license_manager.payload) |*payload| blk: {
        const expiry = std.time.epoch.EpochSeconds.getEpochDay(.{ .secs = payload.expiration_secs }).calculateYearDay();
        const expiry_month = expiry.calculateMonthDay();

        break :blk try std.fmt.allocPrintSentinel(
            std.heap.c_allocator,
            "Licensed to: {s}\nExpires: {}-{}-{}\nEdition: {s}",
            .{
                payload.name.string(),
                expiry.year,
                expiry_month.month.numeric(),
                @as(u8, expiry_month.day_index) + 1,
                @tagName(payload.edition),
            },
            0,
        );
    } else try std.fmt.allocPrintSentinel(std.heap.c_allocator, "No license data found", .{}, 0);

    defer std.heap.c_allocator.free(text);

    {
        gui.relTextSize(21);
        rg.setStyle(.default, .{ .default = .text_alignment_vertical }, @intFromEnum(rg.TextAlignmentVertical.top));
        defer gui.loadStyle();

        _ = rg.label(
            .init(license_box.x + 60, license_box.y + 15, license_box.width - 60, license_box.height - 15),
            text,
        );
    }

    try license.maybeShowUpgradePopup();

    return null;
}
