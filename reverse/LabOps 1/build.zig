const std = @import("std");
const rlz = @import("raylib_zig");

fn buildClient(b: *std.Build) !*std.Build.Step {
    const target = b.resolveTargetQuery(.{
        .cpu_arch = .wasm32,
        .os_tag = .emscripten,
    });

    const optimize = std.builtin.OptimizeMode.ReleaseFast;

    const raylib_dep = b.dependency("raylib_zig", .{
        .target = target,
        .optimize = optimize,
    });

    const raylib = raylib_dep.module("raylib");
    const raygui = raylib_dep.module("raygui");
    const raylib_artifact = raylib_dep.artifact("raylib");

    const exe_mod = b.createModule(.{
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
        .strip = false,
    });

    exe_mod.addImport("raylib", raylib);
    exe_mod.addImport("raygui", raygui);

    // start emsdk stuff
    const emsdk = rlz.emsdk;
    const wasm = b.addLibrary(.{
        .name = "client",
        .root_module = exe_mod,
    });

    const install_dir: std.Build.InstallDir = .{ .custom = "web" };
    var emcc_flags = emsdk.emccDefaultFlags(b.allocator, .{ .optimize = optimize });
    try emcc_flags.put("-g2", {});

    var key_iter = emcc_flags.keyIterator();
    while (key_iter.next()) |key| {
        if (std.mem.startsWith(u8, key.*, "-O")) {
            _ = emcc_flags.remove(key.*);
        }
    }

    try emcc_flags.put("-O0", {});

    var emcc_settings = emsdk.emccDefaultSettings(b.allocator, .{ .optimize = optimize });
    try emcc_settings.put("INLINING_LIMIT", "1");
    try emcc_settings.put("MAX_WEBGL_VERSION", "2");

    const emcc_step = emsdk.emccStep(b, raylib_artifact, wasm, .{
        .optimize = optimize,
        .flags = emcc_flags,
        .settings = emcc_settings,
        .shell_file_path = raylib_dep.builder.dependency("raylib", .{}).path("src/minshell.html"),
        .install_dir = install_dir,
        .embed_paths = &.{.{ .src_path = "resources/" }},
    });

    b.getInstallStep().dependOn(emcc_step);

    return emcc_step;
}

pub fn build(b: *std.Build) !void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const client_step = try buildClient(b);

    const httpz = b.dependency("httpz", .{
        .target = target,
        .optimize = optimize,
    });

    const server = b.addExecutable(.{
        .name = "server",
        .root_module = b.createModule(.{
            .root_source_file = b.path("src/server.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    server.step.dependOn(client_step);

    server.root_module.addAnonymousImport("client.html", .{ .root_source_file = b.path("zig-out/web/client.html") });
    server.root_module.addAnonymousImport("client.wasm", .{ .root_source_file = b.path("zig-out/web/client.wasm") });
    server.root_module.addAnonymousImport("client.js", .{ .root_source_file = b.path("zig-out/web/client.js") });
    server.root_module.addImport("httpz", httpz.module("httpz"));

    b.installArtifact(server);

    const run_server = b.addRunArtifact(server);
    const run_step = b.step("run", "Run the app");
    run_step.dependOn(&run_server.step);
}
