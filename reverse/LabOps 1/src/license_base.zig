const std = @import("std");
const fixed_string = @import("./fixed_string.zig");

inline fn join(high: u16, low: u16) u32 {
    return (@as(u32, high) << 16) | @as(u32, low);
}

// see https://plzin.github.io/mba/ | x + y | 2, 39, 3
inline fn add(a: u32, b: u32, aux0: u32, aux1: u32) u32 {
    return 4076773752 +% 468869379 *% (((a | aux0) ^ b) & (a ^ aux0 ^ b ^ aux0)) +% 4261080673 *% ~(a ^ ~aux1) +% 628961007 *% a +% 1990130147 *% ~aux0 +% 3735313126 *% ~(aux0 ^ b ^ b) +% 2842166303 *% ~aux1 +% 2085383833 *% (~(aux0 ^ b) & b & aux1 & b & aux1) +% 3461902540 *% aux1 +% 3826097917 *% ((aux0 | a | (b & aux1)) ^ ((aux1 ^ aux1) | b)) +% 4277214516 *% ~~~b +% 3494541587 *% ~((aux1 ^ aux0) & (a | aux0)) +% 2122408675 *% ~~a +% 4255656203 *% ~(~b ^ (aux1 | a)) +% 1737900177 *% (((aux1 & aux0) | b) ^ ~aux1) +% 1775055127 *% (aux1 ^ ~aux1) +% 1843792216 *% ((aux1 | b | aux0 | aux0) & aux0) +% 3325120253 *% ((a & ~aux1) ^ ~aux0) +% 1802470846 *% ((aux0 & b & (aux0 | a)) ^ ~aux0) +% 4172200552 *% ~((aux0 | a) & (b ^ b)) +% 3864939961 *% (a ^ aux0 ^ a ^ b) +% 3237307586 *% (~(b ^ b) | ((b | aux0) & b)) +% 2042690541 *% ((~b | aux0) ^ (aux0 | ~b)) +% 1470824707 *% ((aux1 | aux0) & aux0 & a & aux0) +% 2108172555 *% (a ^ (aux1 & (b | b))) +% 1434855757 *% (a & aux1 & a & (a | (b & b))) +% 3753367835 *% (aux1 | aux0 | (a & a) | ~b) +% 390247193 *% ~(a ^ b | ~a) +% 4101913946 *% b +% 2160159942 *% (((aux1 ^ aux1) & (aux1 | b)) ^ aux0) +% 2833743029 *% (a ^ aux1) +% 3748925298 *% ~b +% 1294897717 *% (((b | (aux1 ^ b)) ^ aux0)) +% 1139268377 *% (~a | ~aux1 | (aux1 ^ aux0)) +% 3010009172 *% ~(aux1 ^ aux0 | (aux0 & b)) +% 3058185892 *% ~((aux1 ^ aux1) & b & a) +% 4222237214 *% (~(aux1 | aux0) & (b ^ a | ~b));
}

inline fn xor(x: u32, y: u32, aux0: u32, aux1: u32, aux2: u32, aux3: u32, aux4: u32, aux5: u32, aux6: u32) u32 {
    return 668484673 +% 1040599749 *% aux3 +% 1530857391 *% ~(((x ^ (aux3 & y & aux4 & aux5 & (aux3 ^ aux4) & ~(aux0 ^ x ^ (y | aux3)))) & aux2) | ~(((x | aux3) ^ (aux1 & aux2) ^ aux2 ^ aux1 ^ (aux3 | y)) & ~aux5 & ((y | aux3) ^ (aux3 | y))) | ~aux0) +% 2788997953 *% aux6 +% 3307173635 *% ~x +% 4294967295 *% y +% 2788997953 *% ~aux6 +% 180046005 *% (~(aux6 ^ aux4 ^ (~aux0 | ~~~aux6)) & ~~(((aux3 ^ aux5 ^ aux4 ^ aux2) & aux2 & y & (aux2 | aux2)) | (~aux6 & ~aux3) ^ ~~aux3) & x & ~x) +% 3307173636 *% x +% 2286199674 *% aux5 +% 3254367547 *% (aux3 | aux3) +% 3162247677 *% (aux3 | ~(((aux3 ^ aux0 | aux4 ^ aux0) & (aux3 | x) & ~aux0) | ~((aux4 ^ aux1) & (aux2 | aux1))) | ~(~~y & aux5) | (aux5 & (aux4 | aux0)) | x | ~aux0 | ~y) +% 793411341 *% (((~~aux5 | (~(~aux5 & ~~aux2) ^ aux0)) & ~(~~(aux3 ^ aux0) | ~(~aux5 & aux5)) & (aux3 | aux5)) | aux1) +% 2 *% (~x & y) +% 2008767622 *% ~~aux5 +% 3501555955 *% aux1;
}

test "obfuscated action" {
    try std.testing.expectEqual(13 + 14, add(13, 14, 283, 2383));
    try std.testing.expectEqual(13 ^ 14, xor(13, 14, 283, 2383, 2, 344, 2243, 222, 444));
}

noinline fn validateDemoLicense(_: []const u8, _: u64, checksum: u35) bool {
    return checksum == 0;
}

noinline fn validateBronzeLicense(name: []const u8, expiration: u64, checksum: u35) bool {
    var computed_checksum: u35 = 0x28ac91b93;

    for (0.., name) |i, char| {
        computed_checksum ^= std.math.rotl(u35, char, i * 7) ^ char;
    }

    computed_checksum +%= @as(u10, @truncate(expiration));
    computed_checksum -%= @as(u13, @truncate(expiration >> 10));
    computed_checksum *%= @as(u20, @truncate(expiration >> 23));
    computed_checksum +%= @as(u21, @truncate(expiration >> 43));

    return computed_checksum == checksum;
}

noinline fn validateSilverLicense(name: []const u8, expiration: u64, checksum: u35) bool {
    // var computed_checksum: u35 = 0x13371337;

    // computed_checksum ^= @as(u35, @truncate(expiration));
    // computed_checksum ^= @as(u35, @truncate(expiration >> 35));

    // for (0.., name) |i, char| {
    //     computed_checksum ^= @as(u35, char) << ((char *% i) % 28);
    // }

    // return computed_checksum == checksum;

    var checked_checksum = checksum;

    var it = std.mem.reverseIterator(name);
    while (it.next()) |char| {
        checked_checksum ^= @as(u35, char) << @as(u6, @truncate(char *% it.index));
    }

    checked_checksum ^= @as(u35, @truncate(expiration >> 35));
    checked_checksum ^= @as(u35, @truncate(expiration));

    return checked_checksum == 0x13371337;
}

const gold_cycles = 512;
fn generateGoldLicense(name: []const u8, expiration: u64) u35 {
    const modified_expiration = expiration ^ 0xbf10a0b58afbac17;
    var state = [_]u7{
        @truncate(modified_expiration >> 7),
        @truncate(modified_expiration >> 28),
        @truncate(modified_expiration >> 14),
        @truncate(modified_expiration >> 21),
        @truncate(modified_expiration),
    };

    for (0..gold_cycles) |i| {
        state[4] ^= state[3];
        state[3] -%= std.math.rotl(u7, state[2], 1 + i % 4) ^ 0x7f;
        state[2] +%= state[1];
        state[1] ^= state[0];
        state[0] = state[0] ^ @as(u7, @truncate(name[i % name.len]));
    }

    return @as(u35, state[0]) << 28 |
        @as(u35, state[1]) << 21 |
        @as(u35, state[2]) << 14 |
        @as(u35, state[3]) << 7 |
        @as(u35, state[4]);
}

noinline fn validateGoldLicense(name: []const u8, expiration: u64, checksum: u35) bool {
    var state = [_]u7{
        @truncate(checksum >> 28),
        @truncate(checksum >> 21),
        @truncate(checksum >> 14),
        @truncate(checksum >> 7),
        @truncate(checksum),
    };

    for (0..gold_cycles) |raw_i| {
        const i = gold_cycles - 1 - raw_i;

        state[0] = state[0] ^ @as(u7, @truncate(name[i % name.len]));
        state[1] = @truncate(xor(state[0], state[1], state[2], state[3], state[4], 2838, @truncate(i), state[0] *% 2, state[1] << 1));
        state[2] = @truncate(add(state[2], 0 -% @as(u32, state[1]), state[1], state[0]));
        state[3] = @truncate(add(std.math.rotl(u7, state[2], 1 + i % 4) ^ 0x7f, state[3], state[4], state[1]));
        state[4] ^= state[3];
    }

    const modified_expiration = expiration ^ 0xbf10a0b58afbac17;
    return (state[0] == @as(u7, @truncate(modified_expiration >> 7)) and
        state[1] == @as(u7, @truncate(modified_expiration >> 28)) and
        state[2] == @as(u7, @truncate(modified_expiration >> 14)) and
        state[3] == @as(u7, @truncate(modified_expiration >> 21)) and
        state[4] == @as(u7, @truncate(modified_expiration)));
}

test "gold" {
    const Params = struct {
        name: []const u8,
        expiration: u64,
    };

    const params = [_]Params{
        .{ .name = "BOB", .expiration = 2938382 },
        .{ .name = "TEST", .expiration = 388473 },
        .{ .name = "HELLO", .expiration = 29383821282 },
        .{ .name = "OTHER", .expiration = 28382 },
    };

    for (params) |p| {
        const checksum = generateGoldLicense(p.name, p.expiration);

        try std.testing.expect(validateGoldLicense(p.name, p.expiration, checksum));
        try std.testing.expect(!validateGoldLicense(p.name, p.expiration, checksum - 1));
    }
}

pub const LicenseError = error{ LicenseTooShort, LicenseInvalid };
pub const LicenseEdition = enum(u2) { Demo, Bronze, Silver, Gold };
pub const LicensePayload = struct {
    name: fixed_string.FixedString(10),
    expiration_secs: u64,
    edition: LicenseEdition,

    pub fn deinit(self: *@This()) void {
        self.name.deinit();
    }
};

const EncodedLicensePayload = packed struct {
    name_value: u48,
    edition: LicenseEdition,
    checksum: u35,
    expiry: u15,
    extra: u12,
};

comptime {
    std.debug.assert(@bitSizeOf(EncodedLicensePayload) == 112);
}

pub const LicenseManager = struct {
    license_key: fixed_string.FixedString(24),
    payload: ?LicensePayload,

    pub noinline fn init() @This() {
        return .{ .license_key = .{}, .payload = null };
    }

    pub noinline fn advance(self: *@This(), value: u8) void {
        _ = self.license_key.push(value) catch null;
    }

    pub noinline fn revert(self: *@This()) void {
        _ = self.license_key.pop() catch null;
    }

    pub noinline fn load(self: *@This(), data: []const u8) void {
        for (data) |c| self.advance(c);

        self.validate() catch return;
    }

    pub noinline fn validate(self: *@This()) LicenseError!void {
        self.payload = null;

        if (self.license_key.length != self.license_key.buffer.len) {
            return LicenseError.LicenseTooShort;
        }

        const license_value = @as(u112, @truncate(parseUnsignedBase26(u120, self.license_key.string()) catch unreachable));
        const encoded_payload = @as(EncodedLicensePayload, @bitCast(license_value));

        var decoded_payload: LicensePayload = .{
            .name = .{},
            .expiration_secs = license_epoch + @as(u64, @intCast(encoded_payload.expiry)) * std.time.s_per_day,
            .edition = encoded_payload.edition,
        };

        {
            var remaining_name_value = encoded_payload.name_value;
            while (remaining_name_value != 0) {
                const letter: u8 = @intCast(remaining_name_value % 27);
                remaining_name_value = remaining_name_value / 27;

                decoded_payload.name.push_front(if (letter == 26) ' ' else 'A' + letter) catch unreachable;
            }
        }

        const checksum_checker = switch (decoded_payload.edition) {
            LicenseEdition.Demo => &validateDemoLicense,
            LicenseEdition.Bronze => &validateBronzeLicense,
            LicenseEdition.Silver => &validateSilverLicense,
            LicenseEdition.Gold => &validateGoldLicense,
        };

        if (!checksum_checker(decoded_payload.name.string(), decoded_payload.expiration_secs, encoded_payload.checksum)) {
            return LicenseError.LicenseInvalid;
        }

        self.payload = decoded_payload;
    }

    pub noinline fn isEdition(self: *const @This(), edition: LicenseEdition) bool {
        const payload = self.payload orelse return false;

        return edition == payload.edition;
    }
};

noinline fn parseUnsignedBase26(comptime T: type, buf: []const u8) std.fmt.ParseIntError!T {
    var value: T = 0;

    for (0..buf.len) |i| {
        if (value != 0) {
            value = try std.math.mul(T, value, 26);
        }

        const char = buf[i];
        const char_value = switch (char) {
            'A'...'Z' => char - 'A',
            'a'...'z' => char - 'a',
            else => return error.InvalidCharacter,
        };

        value = try std.math.add(T, value, char_value);
    }

    return value;
}

const license_epoch = blk: {
    var days = 0;

    for (1970..2020) |year| {
        days += std.time.epoch.getDaysInYear(year);
    }

    break :blk days * std.time.s_per_day;
};
