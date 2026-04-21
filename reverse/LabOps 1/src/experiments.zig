const State = @import("./state.zig").State;
const rl = @import("raylib");
const rg = @import("raygui");
const gui = @import("./gui.zig");
const license = @import("./license.zig");
const std = @import("std");

const emscripten = std.os.emscripten;

const Experiment = struct {
    name: [:0]const u8,
    author: [:0]const u8,
    text: []const u8,
    premium: bool,
};

const flag_token = "<FLAG>";
const experiments = [_]Experiment{
    .{
        .name = "Spiciest Pepper",
        .author = "Dr. Pepper",
        .text =
        \\Objective: Determine the upper limit of capsaicin concentration achievable through selective cultivation.
        \\Method: Cross-breeding, controlled stress exposure, and repeated Scoville testing.
        \\Result: Specimens exceeded expected tolerance thresholds; handling now requires protective equipment.
        \\Conclusion: Flavor perception breaks down before biological limits are reached.
        ,
        .premium = false,
    },
    .{
        .name = "Perpetual Motion Apparatus",
        .author = "Einert Albstein",
        .text =
        \\Objective: Construct a self-sustaining mechanical system with zero external energy input.
        \\Method: Iterative redesign of coupled flywheels, magnetic biasing, and friction minimization.
        \\Result: Apparatus maintained motion only under idealized assumptions; real-world losses dominated.
        \\Conclusion: Conservation laws remain undefeated despite creative engineering.
        ,
        .premium = false,
    },
    .{
        .name = "Flaggiest Seed",
        .author = "Dr. Flagsalot",
        .text = 
        \\Objective: Observe emergent patterns in genetically unstable seeds.
        \\Method: Iterative growth cycles with deliberate mutation triggers.
        \\Result: Repeating symbolic structures appeared in leaf venation and growth rings.
        \\Conclusion: The signal is consistent, intentional, and reproducible.
        \\Note to self:
        \\  We should make sure to keep track of all the flags we have grown.
        \\  Until now, we've seen a couple, like
    ++ " " ++ flag_token,
    .premium = true,
    },
};

report_experiment: ?*const Experiment = null,
ad_colors: [4]rl.Color = .{ rl.Color.red, rl.Color.green, rl.Color.yellow, rl.Color.blue },
flag: *const std.ArrayList(u8),
required_license: license.LicenseEdition,

pub fn init(flag: *const std.ArrayList(u8), required_license: license.LicenseEdition) !@This() {
    return .{ .flag = flag, .required_license = required_license };
}

pub fn deinit(self: *@This()) void {
    _ = self;
}

pub fn draw(self: *@This(), _: bool) !?State {
    rl.clearBackground(gui.getBackgroundColor());

    if (gui.backButton()) {
        return State.menu;
    }

    var bounds = rl.Rectangle.init(50, gui.iconButtonSize() + 80, gui.widthPercent(0.2), gui.heightPercent(0.2));
    for (&experiments) |*experiment| {
        _ = rg.panel(bounds, experiment.name);

        gui.relTextSize(11);
        rg.setStyle(.default, .{ .control = .text_alignment }, @intFromEnum(rg.TextAlignment.right));
        defer gui.loadStyle();

        const text_size: f32 = @floatFromInt(rg.getStyle(.default, .{ .default = .text_size }));
        const status_bar_height: f32 = @floatFromInt(rg.getStyle(.statusbar, .{ .control = .border_width }));

        const premium_text = try std.fmt.allocPrintSentinel(
            std.heap.c_allocator,
            "Author: {s}\nPremium report: {}",
            .{ experiment.author, experiment.premium },
            0,
        );
        defer std.heap.c_allocator.free(premium_text);

        _ = rg.label(.init(bounds.x + 10, bounds.y + status_bar_height, bounds.width - 20, bounds.height), premium_text);

        const button_text = "Show report";
        const button_width = @as(f32, @floatFromInt(rg.getTextWidth(button_text))) * 1.2;
        if (rg.button(.init(
            bounds.x + bounds.width - button_width - 5,
            bounds.y + bounds.height - text_size - 5,
            button_width,
            text_size,
        ), button_text)) {
            self.report_experiment = experiment;
        }

        bounds.y += bounds.height + gui.heightPercent(0.025);
    }

    if (self.report_experiment) |experiment| {
        try self.showReport(experiment);
    }

    return null;
}

noinline fn showReport(self: *@This(), experiment: *const Experiment) !void {
    const gpa = std.heap.c_allocator;
    const height = gui.heightPercent(0.8);
    const bounds = rl.Rectangle.init(gui.widthPercent(0.4), gui.centerStart(0, gui.height(), height), gui.widthPercent(0.55), height);

    _ = rg.panel(bounds, null);

    // title
    {
        rg.setStyle(.default, .{ .control = .text_alignment }, @intFromEnum(rg.TextAlignment.center));
        defer gui.loadStyle();

        const text = try std.fmt.allocPrintSentinel(
            std.heap.c_allocator,
            "Experiment: {s}\nBy: {s}",
            .{ experiment.name, experiment.author },
            0,
        );

        defer std.heap.c_allocator.free(text);

        _ = rg.label(.init(bounds.x, bounds.y + 50, bounds.width, 16), text);
    }

    // contents
    {
        gui.relTextSize(11);
        rg.setStyle(.default, .{ .default = .text_alignment_vertical }, @intFromEnum(rg.TextAlignmentVertical.top));
        rg.setStyle(.default, .{ .default = .text_wrap_mode }, @intFromEnum(rg.TextWrapMode.word));
        defer gui.loadStyle();

        const replacement = if (license.license_manager.isEdition(self.required_license)) self.flag.items else "POLYCYB...";
        const experiment_text = try std.mem.replaceOwned(u8, gpa, experiment.text, flag_token, replacement);
        defer gpa.free(experiment_text);

        const experiment_text_c = try gpa.dupeZ(u8, experiment_text);
        defer gpa.free(experiment_text_c);

        _ = rg.textBox(
            .init(bounds.x + 10, bounds.y + 100, bounds.width - 20, bounds.height - 110),
            @constCast(experiment_text_c),
            @intCast(experiment_text_c.len),
            false,
        );
    }

    if (experiment.premium and !license.license_manager.isEdition(self.required_license)) {
        const font = try rl.getFontDefault();

        rl.beginScissorMode(
            @intFromFloat(bounds.x),
            @intFromFloat(bounds.y),
            @intFromFloat(bounds.width),
            @intFromFloat(bounds.height),
        );

        for (0..100) |line| {
            for (0..100) |col| {
                _ = rl.drawTextPro(
                    font,
                    "<DEMO>",
                    .init(bounds.x + @as(f32, @floatFromInt(col * 150)), bounds.y + @as(f32, @floatFromInt(line * 60))),
                    .init(0, 0),
                    -30,
                    50,
                    @floatFromInt(rg.getStyle(.default, .{ .default = .text_spacing })),
                    rl.Color.white.alpha(0.5),
                );
            }
        }

        rl.endScissorMode();

        const rectangle_size = rl.Vector2.init(bounds.width / 1.5, bounds.height / 3);
        const rectangle_bounds = rl.Rectangle.init(
            gui.centerStart(bounds.x, bounds.width, rectangle_size.x),
            gui.centerStart(bounds.y + bounds.height / 2, bounds.height / 2, rectangle_size.y),
            rectangle_size.x,
            rectangle_size.y,
        );

        rl.drawRectangleGradientEx(
            rectangle_bounds,
            self.ad_colors[0],
            self.ad_colors[1],
            self.ad_colors[2],
            self.ad_colors[3],
        );

        for (&self.ad_colors) |*color| {
            const hsv = color.toHSV();
            color.* = rl.Color.fromHSV(@mod(hsv.x + 1, 360), hsv.y, hsv.z);
        }

        {
            rg.setStyle(.default, .{ .control = .text_color_normal }, @bitCast(rl.Color.white.toInt()));
            gui.relTextSize(22);
            rg.setStyle(.default, .{ .default = .text_alignment_vertical }, @intFromEnum(rg.TextAlignmentVertical.top));
            rg.setStyle(.default, .{ .default = .text_wrap_mode }, @intFromEnum(rg.TextWrapMode.word));
            defer gui.loadStyle();

            const text = try std.fmt.allocPrintSentinel(
                gpa,
                "You need a {s} license to view premium experiments. Click to upgrade",
                .{@tagName(self.required_license)},
                0,
            );
            defer gpa.free(text);

            _ = rg.label(rectangle_bounds, text);
        }

        if (rl.isMouseButtonPressed(rl.MouseButton.left) and rl.checkCollisionPointRec(rl.getMousePosition(), rectangle_bounds)) {
            license.in_upgrade_popup = true;
        }
    }

    try license.maybeShowUpgradePopup();
}
