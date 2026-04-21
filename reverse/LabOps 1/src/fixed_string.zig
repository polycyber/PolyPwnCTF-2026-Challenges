const std = @import("std");

pub const FixedStringError = error{
    StringTooLong,
    StringTooShort,
};

pub fn FixedString(comptime bufferSize: usize) type {
    return struct {
        buffer: [bufferSize]u8 = undefined,
        length: usize = 0,

        pub fn string(self: *const @This()) []const u8 {
            return self.buffer[0..self.length];
        }

        pub noinline fn push(self: *@This(), value: u8) FixedStringError!void {
            if (self.length >= bufferSize) {
                return FixedStringError.StringTooLong;
            }

            self.buffer[self.length] = value;
            self.length += 1;
        }

        pub noinline fn push_front(self: *@This(), value: u8) FixedStringError!void {
            if (self.length >= bufferSize) {
                return FixedStringError.StringTooLong;
            }

            @memmove(self.buffer[1 .. self.length + 1], self.buffer[0..self.length]);

            self.buffer[0] = value;
            self.length += 1;
        }

        pub noinline fn pop(self: *@This()) FixedStringError!u8 {
            if (self.length == 0) {
                return FixedStringError.StringTooShort;
            }

            self.length -= 1;
            return self.buffer[self.length];
        }
    };
}
