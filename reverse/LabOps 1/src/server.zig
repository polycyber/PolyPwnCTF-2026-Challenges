const std = @import("std");
const httpz = @import("httpz");
const Allocator = std.mem.Allocator;
const license = @import("./license_base.zig");

const PORT = 80;
const COOLDOWN_NS = 300 * std.time.ns_per_ms;

var server_instance: ?*httpz.Server(*Handler) = null;

const fakeFlag = "POLYCYBER{an_inv4l1D_l1c3n5e_wOnT_g1Ve_u_a_fl4g}";
const flags = [_][]const u8{
    "POLYCYBER{4n_3mBedD3d_k3YG3n}",
    "POLYCYBER{qu1ck_1nvers1on}",
    "POLYCYBER{h4nD_r0ll3d_h4SH}",
};

pub fn main() !void {
    if (comptime @import("builtin").os.tag == .windows) {
        return error.PlatformNotSupported;
    }

    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    const allocator = gpa.allocator();

    std.posix.sigaction(std.posix.SIG.INT, &.{ .handler = .{ .handler = shutdown }, .mask = std.posix.sigemptyset(), .flags = 0 }, null);
    std.posix.sigaction(std.posix.SIG.TERM, &.{ .handler = .{ .handler = shutdown }, .mask = std.posix.sigemptyset(), .flags = 0 }, null);

    var handler = Handler.init(allocator);
    defer handler.deinit();

    var server = try httpz.Server(*Handler).init(
        allocator,
        .{
            .address = "0.0.0.0",
            .port = PORT,
        },
        &handler,
    );
    defer server.deinit();

    var router = try server.router(.{});

    router.get("/", staticFileHandler("client.html"), .{});
    inline for (.{ "client.html", "client.js", "client.wasm" }) |r| {
        router.get("/" ++ r, staticFileHandler(r), .{});
    }

    router.get("/flags", flagsHandler, .{});

    std.debug.print("listening http://0.0.0.0:{d}/\n", .{PORT});

    server_instance = &server;
    try server.listen();
}

fn shutdown(_: c_int) callconv(.c) void {
    if (server_instance) |server| {
        server_instance = null;
        server.stop();
    }
}

const Handler = struct {
    last_seen: std.AutoHashMap(u128, std.time.Instant),

    pub fn init(allocator: Allocator) @This() {
        return .{ .last_seen = .init(allocator) };
    }

    pub fn deinit(self: *@This()) void {
        self.last_seen.deinit();
    }

    pub fn registerClient(self: *@This(), client: std.net.Address) !void {
        const addr = switch (client.any.family) {
            std.posix.AF.INET => 0xffff00000000 | @as(u128, client.in.sa.addr),
            std.posix.AF.INET6 => std.mem.readInt(u128, &client.in6.sa.addr, .big),
            else => unreachable,
        };

        if (self.last_seen.get(addr)) |instant| {
            const now = try std.time.Instant.now();
            if (now.since(instant) < COOLDOWN_NS) {
                std.log.info("client {f} is sending requests too fast", .{client});
                std.Thread.sleep(COOLDOWN_NS);
            }
        }

        try self.last_seen.put(addr, try std.time.Instant.now());
    }

    pub fn notFound(_: *Handler, _: *httpz.Request, res: *httpz.Response) !void {
        res.status = 404;
        res.body = "this is not a web challenge :) nothing to see here";
    }

    pub fn uncaughtError(_: *Handler, req: *httpz.Request, res: *httpz.Response, err: anyerror) void {
        std.debug.print("uncaught http error at {s}: {}\n", .{ req.url.path, err });

        res.headers.add("content-type", "text/html; charset=utf-8");

        res.status = 500;
        res.body = "oops!";
    }
};

fn staticFileHandler(path: []const u8) fn (handler: *Handler, req: *httpz.Request, res: *httpz.Response) anyerror!void {
    const gen = struct {
        fn handler(_: *Handler, _: *httpz.Request, res: *httpz.Response) anyerror!void {
            res.content_type = comptime httpz.ContentType.forFile(path);
            res.body = @embedFile(path);
        }
    };
    return gen.handler;
}

fn flagsHandler(handler: *Handler, req: *httpz.Request, res: *httpz.Response) anyerror!void {
    try handler.registerClient(req.conn.address);

    const query = try req.query();
    const license_key = query.get("lk") orelse "";

    var license_manager = license.LicenseManager.init();

    license_manager.load(license_key);

    res.status = 200;
    try res.json(.{
        .bronze_flag = if (license_manager.isEdition(license.LicenseEdition.Bronze)) flags[0] else fakeFlag,
        .silver_flag = if (license_manager.isEdition(license.LicenseEdition.Silver)) flags[1] else fakeFlag,
        .gold_flag = if (license_manager.isEdition(license.LicenseEdition.Gold)) flags[2] else fakeFlag,
    }, .{});
}
