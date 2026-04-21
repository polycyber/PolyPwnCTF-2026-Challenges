pub fn mantissa(value: f32) u32 {
    return @as(u23, @truncate(@as(u32, @bitCast(value))));
}

pub fn exponent(value: f32) i8 {
    return @intCast(@as(i16, @intCast(@as(u16, @truncate(@as(u32, @bitCast(value)) >> 23)))) - 127);
}
