"""CH06 negative contract tests; does not verify physical SPI, DMA, or security."""

import copy
import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'models/python'))
import ch06_host as host  # noqa: E402


class HostContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(host.CONFIG.read_text())
        cls.p = host.prepare(cls.config)

    def device(self):
        return host.CandidateDevice(self.config, self.p)

    def test_crc32c_known_check_vector(self):
        self.assertEqual(host.crc32c(b'123456789'), 0xE3069283)
        self.assertNotEqual(host.crc32c(b'123456788'), 0xE3069283)

    def test_golden_header_and_payload_bytes(self):
        f = host.Frame(host.TYPES['DATA'], 0, 1, (1 << 32) + 7, b'hello', 1)
        raw = host.encode(f, self.p)
        self.assertEqual(raw.hex(),
                         '5ac3010101000500000000000100000007000000010000000000000068656c6c6f1fa06cee')
        self.assertEqual(host.decode(raw, self.p), f)

    def test_corrupted_payload_or_header_fails_crc(self):
        raw = bytearray(host.encode(host.Frame(1, 0, 1, 7, b'one', 1), self.p))
        for idx in (6, host.HEADER.size):
            with self.subTest(index=idx):
                altered = raw.copy()
                altered[idx] ^= 1
                with self.assertRaises(host.ProtocolError):
                    host.decode(bytes(altered), self.p)

    def test_unknown_version_reserved_flags_and_type_rejected(self):
        raw = host.encode(host.Frame(1, 0, 1, 7, b'x', 1), self.p)
        for idx, value in ((2, 2), (24, 1), (4, 4), (3, 127)):
            with self.subTest(index=idx), self.assertRaises(host.ProtocolError):
                b = bytearray(raw)
                b[idx] = value
                # Recompute CRC to isolate semantic checks from corruption detection.
                b[-4:] = struct.pack('<I', host.crc32c(b[:-4]))
                host.decode(bytes(b), self.p)

    def test_length_oversize_and_trailing_bytes_fail(self):
        raw = bytearray(host.encode(host.Frame(1, 0, 1, 0, b'd', 0), self.p))
        with self.assertRaisesRegex(host.ProtocolError, 'Extra/truncated'):
            host.decode(bytes(raw + b'x'), self.p)
        struct.pack_into('<H', raw, 6, self.p['max_payload_bytes'] + 1)
        with self.assertRaises(host.ProtocolError):
            host.decode(bytes(raw), self.p)

    def test_missing_timestamp_is_explicit_zero(self):
        valid = host.Frame(1, 0, 1, 0, b'payload', 0)
        self.assertEqual(host.decode(host.encode(valid, self.p), self.p).sample_time_us, 0)
        with self.assertRaises(host.ProtocolError):
            host.encode(host.Frame(1, 0, 1, 123, b'payload', 0), self.p)
        with self.assertRaises(host.ProtocolError):
            host.encode(host.Frame(1, 0, 1, 0, b'payload', host.FLAGS['GAP_PRESENT']), self.p)

    def test_gap_requires_count_and_no_sample_time(self):
        with self.assertRaises(host.ProtocolError):
            host.encode(host.Frame(2, 1, 1, 0, b'\0'*4, 2), self.p)
        with self.assertRaises(host.ProtocolError):
            host.encode(host.Frame(2, 1, 1, 10, struct.pack('<I', 1), 2), self.p)

    def test_parser_partial_chunks_and_chip_select_boundary(self):
        raw = host.encode(host.Frame(1, 0, 1, 3, b'abcdef', 1), self.p)
        parser = host.IncrementalParser(self.p)
        self.assertEqual(parser.feed(raw[:1]), [])
        self.assertEqual(parser.feed(raw[1:10]), [])
        self.assertEqual(parser.feed(raw[10:]), [host.decode(raw, self.p)])
        parser.feed(raw[:8])
        parser.end_chip_select()
        self.assertEqual(parser.errors, 1)
        self.assertEqual(parser.feed(raw[8:]), [])  # no cross-CS completion

    def test_parser_recovers_after_bad_crc_and_noise(self):
        raw = host.encode(host.Frame(1, 0, 1, 3, b'valid', 1), self.p)
        bad = bytearray(raw)
        bad[-1] ^= 0x80
        parser = host.IncrementalParser(self.p)
        out = parser.feed(b'noise' + bytes(bad) + raw)
        self.assertEqual(out, [host.decode(raw, self.p)])
        self.assertGreater(parser.errors, 0)
        with self.assertRaises(host.ProtocolError):
            parser.feed(b'A' * (1 << 20 + 1))

    def test_sequence_wrap_duplicate_reordered_and_reset_epoch(self):
        tracker = host.SequenceTracker()
        tracker.negotiate(9)
        last = host.encode(host.Frame(1, host.MASK32, 9, 0, b'a'), self.p)
        zero = host.encode(host.Frame(1, 0, 9, 0, b'b'), self.p)
        self.assertEqual(tracker.accept(last, self.p)[0], 'NEW')
        self.assertEqual(tracker.accept(last, self.p)[0], 'DUPLICATE')
        self.assertEqual(tracker.accept(zero, self.p)[0], 'NEW')
        with self.assertRaises(host.ProtocolError):
            tracker.accept(host.encode(host.Frame(1, 2, 9, 0, b'gap'), self.p), self.p)
        with self.assertRaises(host.ProtocolError):
            tracker.accept(host.encode(host.Frame(1, 1, 10, 0, b'newboot'), self.p), self.p)

    def test_same_sequence_different_bytes_rejected(self):
        tracker = host.SequenceTracker()
        tracker.negotiate(1)
        tracker.accept(host.encode(host.Frame(1, 3, 1, 0, b'a'), self.p), self.p)
        with self.assertRaises(host.ProtocolError):
            tracker.accept(host.encode(host.Frame(1, 3, 1, 0, b'b'), self.p), self.p)

    def test_time_snapshot_stays_coherent_until_next_command(self):
        d = self.device()
        d.set_time((1 << 32) - 1)
        d.write(20, 1)
        lo = d.read(24)
        d.set_time((1 << 32) + 13)
        self.assertEqual((d.read(28), lo, d.read(32)), (0, host.MASK32, 1))
        d.write(20, 1)
        self.assertEqual((d.read(28), d.read(24), d.read(32)), (1, 13, 2))

    def test_ro_wo_unmapped_and_reserved_bits_fail(self):
        d = self.device()
        for op in (lambda: d.write(0, 0), lambda: d.read(20), lambda: d.read(5),
                   lambda: d.write(12, 1 << 15), lambda: d.write(20, 0)):
            with self.assertRaises(host.ProtocolError):
                op()

    def test_interrupt_w1c_hardware_set_wins(self):
        d = self.device()
        d.write(12, 0x3F)
        d.event('OVERFLOW')
        self.assertTrue(d.irq_asserted)
        d.write(16, 2, concurrent_event=2)
        self.assertEqual(d.read(16) & 2, 2)
        d.write(16, 2)
        self.assertEqual(d.read(16) & 2, 0)
        self.assertEqual(d.read(8) & 2, 2)  # sticky status not magically cleared

    def test_credit_and_ack_own_frame_until_successful_commit(self):
        d = self.device()
        d.enqueue(b'hello', sample_time_us=1)
        self.assertIsNone(d.request(36))
        self.assertEqual(d.read(36), 5)
        raw = d.request(37)
        self.assertEqual(raw, d.request(37))
        for seq, boot in ((1, 1), (0, 2)):
            with self.assertRaises(host.ProtocolError):
                d.acknowledge(seq, boot)
        self.assertEqual(d.acknowledge(0, 1), raw)
        self.assertEqual(d.read(36), 0)

    def test_wire_command_reply_retry_is_idempotent(self):
        d = self.device()
        def cmd(kind, seq, payload):
            return host.encode(host.Frame(kind, seq, 1, 0, payload), self.p)
        read = cmd(host.TYPES['READ'], 0, struct.pack('<I', 0))
        reply = d.command(read)
        decoded = host.decode(reply, self.p)
        self.assertEqual((decoded.kind, decoded.seq, decoded.boot_epoch),
                         (host.TYPES['REPLY'], 0, 1))
        self.assertEqual(struct.unpack('<II', decoded.payload), (0, 0x484D4231))
        self.assertEqual(d.command(read), reply)
        d.set_time(7)
        snapshot = cmd(host.TYPES['WRITE'], 1, struct.pack('<II', 20, 1))
        self.assertEqual(host.decode(d.command(snapshot), self.p).kind, host.TYPES['REPLY'])
        self.assertEqual(d.read(32), 1)
        d.set_time(8)
        self.assertEqual(host.decode(d.command(snapshot), self.p).payload, struct.pack('<II', 0, 0))
        self.assertEqual((d.read(32), d.read(24)), (1, 7))
        with self.assertRaisesRegex(host.ProtocolError, 'reordered'):
            d.command(read)  # Only the immediately previous command may be retried.

    def test_wire_command_error_crc_reset_and_ack_replay(self):
        d = self.device()
        def cmd(kind, seq, payload, epoch=1):
            return host.encode(host.Frame(kind, seq, epoch, 0, payload), self.p)
        illegal = cmd(host.TYPES['WRITE'], 0, struct.pack('<II', 0, 1))
        error = d.command(illegal)
        self.assertEqual((host.decode(error, self.p).kind,
                          struct.unpack('<II', host.decode(error, self.p).payload)),
                         (host.TYPES['ERROR'], (1, 0)))
        self.assertEqual(d.command(illegal), error)
        self.assertTrue(d.read(8) & (1 << host.STATUS_BITS['BAD_COMMAND']))
        corrupted = bytearray(cmd(host.TYPES['WRITE'], 1, struct.pack('<II', 12, 3)))
        corrupted[-1] ^= 0x80
        with self.assertRaisesRegex(host.ProtocolError, 'CRC'):
            d.command(bytes(corrupted))
        self.assertTrue(d.read(8) & (1 << host.STATUS_BITS['CRC_ERROR']))
        self.assertEqual(d.read(12), 0)
        d.enqueue(b'a', sample_time_us=2)
        d.request(33)
        ack = cmd(host.TYPES['ACK'], 1, struct.pack('<I', 0))
        response = d.command(ack)
        self.assertEqual(struct.unpack('<II', host.decode(response, self.p).payload), (0, 33))
        self.assertEqual(d.read(36), 0)
        self.assertEqual(d.command(ack), response)  # No second consume.
        d.reset()
        with self.assertRaisesRegex(host.ProtocolError, 'epoch'):
            d.command(ack)
        next_boot = cmd(host.TYPES['READ'], 0, struct.pack('<I', 44), epoch=2)
        self.assertEqual(struct.unpack('<II', host.decode(d.command(next_boot), self.p).payload), (0, 2))

    def test_overflow_emits_counted_gap_when_space_returns(self):
        conf = copy.deepcopy(self.config)
        conf['parameters']['queue_capacity_bytes']['value'] = 1024
        p = host.prepare(conf)
        d = host.CandidateDevice(conf, p)
        self.assertTrue(d.enqueue(b'X'*1024, sample_time_us=0))
        self.assertFalse(d.enqueue(b'lost', sample_time_us=1))
        self.assertEqual(d.read(40), 1)
        raw = d.request(1024 + 32)
        d.acknowledge(0, 1)
        self.assertTrue(d.enqueue(b'next', sample_time_us=2))
        gap = host.decode(d.request(36), p)
        self.assertEqual(gap.kind, host.TYPES['GAP'])
        self.assertEqual(struct.unpack('<I', gap.payload)[0], 1)
        d.acknowledge(gap.seq, 1)
        data = host.decode(d.request(36), p)
        self.assertEqual(data.payload, b'next')
        self.assertEqual(d.read(36), 4)

    def test_soft_reset_marks_session_break_and_invalidates_ack(self):
        d = self.device()
        d.enqueue(b'a', sample_time_us=1)
        d.request(33)
        d.reset()
        self.assertEqual(d.read(44), 2)
        self.assertEqual(d.read(8) & (1 << 5), 1 << 5)
        with self.assertRaises(host.ProtocolError):
            d.acknowledge(0, 1)

    def test_register_and_protocol_security_surface_has_no_actuator_enable(self):
        self.assertFalse(any('DRIVE' in r['name'] or 'LED_EN' in r['name']
                             for r in self.config['registers']))
        with self.assertRaises(host.ProtocolError):
            self.device().write(0x100, 1)

    def test_throughput_reconciles_group_bytes_without_double_header(self):
        report = host.generate(self.config)
        research = report['modes']['research_raw']
        self.assertEqual(research['sample_group_bytes_per_s'], 1_548_240)
        self.assertEqual(research['new_ch06_wire_bytes_per_s'], 1_597_552)
        self.assertEqual(research['whole_group_frames_per_s'], 1541)
        self.assertEqual(research['min_illustrative_sck_hz_with_guard'], 21_909_285)
        self.assertEqual(research['probes_at_70pct_full_duty']['16000000'], 'AVERAGE_DEFICIT')
        self.assertEqual(research['probes_at_70pct_full_duty']['32000000'], 'AVERAGE_ONLY')
        fast = report['modes']['research_fast_stress']
        self.assertEqual(fast['probes_at_70pct_full_duty']['64000000'], 'AVERAGE_DEFICIT')

    def test_reject_invalid_units_registers_sources_and_physical_values(self):
        for mutate in (lambda c: c['parameters']['header_bytes'].update(unit='bit'),
                       lambda c: c['registers'][2].update(offset=4),
                       lambda c: c['registers'][5].update(access='RW'),
                       lambda c: c['frame']['types'].update(DATA=42),
                       lambda c: c['physical_inputs'].update(verified_spi_pins_mode_max_sck_and_mcu_firmware='assumed')):
            c = copy.deepcopy(self.config)
            mutate(c)
            with self.assertRaises(host.ProtocolError):
                host.prepare(c)

    def test_changed_ch04_source_fails_reconciliation(self):
        source = json.loads(host.CH04.read_text())
        source['ch02_input_sha256'] = '0' * 64
        with self.assertRaises(host.ProtocolError):
            host.prepare(self.config, ch04=source)


if __name__ == '__main__':
    unittest.main()
