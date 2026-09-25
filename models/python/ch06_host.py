#!/usr/bin/env python3
"""CH06 candidate host/register behavior and analytic throughput; no real SPI/DMA."""

import argparse
import csv
import hashlib
import json
import math
import struct
from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'specs/system/CH06_HOST_CONTRACT.json'
CH04 = ROOT / 'reports/subsystem/CH04_DATAFLOW_SUMMARY.json'
CH02 = ROOT / 'specs/system/CH02_MODE_ASSUMPTIONS.json'
REPORT = ROOT / 'reports/subsystem/CH06_HOST_SUMMARY.json'
REVIEW = ROOT / 'docs/interfaces/CH06_REGISTER_PROTOCOL.md'
HEADER = struct.Struct('<HBBHHIIQI')
CRC = struct.Struct('<I')
PHYSICAL = {'approved_host_part_revision_and_errata_policy',
            'verified_spi_pins_mode_max_sck_and_mcu_firmware',
            'measured_payload_goodput_wake_cs_dma_retry_and_power',
            'approved_asic_sram_dma_and_cdc_implementation',
            'approved_product_modes_frame_loss_and_retention_policy',
            'reviewed_security_and_body_drive_authorization_policy',
            'qualified_timebase_and_host_epoch_semantics'}
REQUIREMENTS = {'HIF-0001', 'HIF-0002', 'HIF-0003', 'MEM-0001', 'MEM-0002',
                'TIM-0001', 'TIM-0004', 'SEC-0003', 'SEC-0004'}
UNITS = {'protocol_major': 'version', 'header_bytes': 'B', 'crc_bytes': 'B',
         'max_payload_bytes': 'B', 'queue_capacity_bytes': 'B',
         'illustrative_wire_utilization': 'ratio', 'capacity_guard': 'ratio'}
TYPES = {'DATA': 1, 'GAP': 2, 'STATUS': 3, 'READ': 16, 'WRITE': 17,
         'ACK': 18, 'REPLY': 19, 'ERROR': 20}
FLAGS = {'TIME_VALID': 1, 'GAP_PRESENT': 2}
STATUS_BITS = {'READY': 0, 'OVERFLOW': 1, 'CRC_ERROR': 2,
               'BAD_COMMAND': 3, 'TIME_INVALID': 4, 'SESSION_BREAK': 5}
REGISTER_NAMES = ('DEVICE_ID', 'ABI_VERSION', 'STATUS', 'IRQ_ENABLE', 'IRQ_PENDING',
                  'TIME_SNAPSHOT', 'TIME_LO', 'TIME_HI', 'TIME_SEQ', 'FIFO_BYTES',
                  'LOSS_COUNT', 'BOOT_EPOCH')
FIELDS = [('magic', 16), ('major', 8), ('type', 8), ('flags', 16),
          ('payload_len', 16), ('seq', 32), ('boot_epoch', 32),
          ('sample_time_us', 64), ('reserved', 32)]
MASK32 = (1 << 32) - 1
MASK64 = (1 << 64) - 1


class ProtocolError(ValueError):
    """Malformed frame, unapproved assumption or illegal software access."""


def meta(obj, unit):
    if not isinstance(obj, dict) or set(obj) != {'value', 'unit', 'evidence', 'source', 'conditions', 'range'}:
        raise ProtocolError('Missing source and bounds for parameter')
    if obj['unit'] != unit or obj['evidence'] != 'assumed' or any(
            not isinstance(obj[k], str) or not obj[k].strip() for k in ('source', 'conditions')):
        raise ProtocolError('Unknown units or evidence class')
    v, bounds = obj['value'], obj['range']
    if (type(v) not in (int, float) or not math.isfinite(v) or type(bounds) is not list or
            len(bounds) != 2 or any(type(x) not in (int, float) or not math.isfinite(x) for x in bounds) or
            not bounds[0] <= v <= bounds[1]):
        raise ProtocolError('Invalid parameter range')
    if unit != 'ratio' and (type(v) is not int or any(type(x) is not int for x in bounds)):
        raise ProtocolError('Nonintegral field')
    return v


def prepare(config, ch04=None, ch02=None):
    if config.get('schema_version') != 1 or config.get('evidence_class') != 'candidate_synthetic_contract':
        raise ProtocolError('Unexpected protocol schema/evidence')
    if set(config.get('physical_inputs', {})) != PHYSICAL or any(
            v is not None for v in config['physical_inputs'].values()):
        raise ProtocolError('Physical data need revised schema and independent gate')
    if not isinstance(config.get('source'), str) or not config['source'].strip():
        raise ProtocolError('Missing contract provenance')
    if set(config.get('parameters', {})) != set(UNITS):
        raise ProtocolError('Missing or unexpected protocol parameter')
    p = {key: meta(config['parameters'][key], unit) for key, unit in UNITS.items()}
    if (p['protocol_major'] != 1 or p['header_bytes'] != HEADER.size or p['crc_bytes'] != CRC.size or
            p['max_payload_bytes'] <= 0 or p['queue_capacity_bytes'] < p['max_payload_bytes'] or
            not 0 < p['illustrative_wire_utilization'] <= 1 or p['capacity_guard'] < 1):
        raise ProtocolError('Unsafe or incompatible contract parameters')
    frame = config.get('frame', {})
    if (frame.get('byte_order') != 'little' or frame.get('types') != TYPES or
            frame.get('flags') != FLAGS or frame.get('crc') !=
            'CRC-32c/Castagnoli; reflected 0x82F63B78; init 0xffffffff; final xor 0xffffffff; append little-endian u32' or
            frame.get('header_fields') != [{'name': name, 'bits': bits} for name, bits in FIELDS] or
            meta(frame.get('magic'), 'u16') != 0xC35A or config.get('status_bits') != STATUS_BITS):
        raise ProtocolError('Wire field definition differs from parser')
    regs = config.get('registers')
    if not isinstance(regs, list) or [r.get('name') for r in regs] != list(REGISTER_NAMES):
        raise ProtocolError('Missing register/duplicate name')
    for idx, r in enumerate(regs):
        if (set(r) != {'name', 'offset', 'access', 'reset', 'mask'} or
                type(r['offset']) is not int or r['offset'] != 4 * idx or
                r['access'] not in ('RO', 'WO', 'RW', 'RW1C') or
                any(type(r[key]) is not int or not 0 <= r[key] <= MASK32 for key in ('reset', 'mask')) or
                (r['reset'] & ~r['mask']) != 0):
            raise ProtocolError('Register overlap, invalid reset or undefined mask')
    expected_access = ('RO', 'RO', 'RO', 'RW', 'RW1C', 'WO', 'RO', 'RO', 'RO', 'RO', 'RO', 'RO')
    if ([r['access'] for r in regs] != list(expected_access) or
            [r['mask'] for r in regs[2:6]] != [63, 63, 63, 1] or
            regs[0]['reset'] != 0x484D4231 or regs[1]['reset'] != 0x00010000):
        raise ProtocolError('Candidate register semantics silently changed')
    desc = config.get('descriptor', {})
    if (desc.get('evidence') != 'assumed' or not desc.get('source') or
            desc.get('fields') != ['payload_bytes', 'sequence', 'sample_time_us', 'boot_epoch', 'owner'] or
            desc.get('states') != ['FREE', 'READY', 'HOST_VIEW', 'FREE_AFTER_ACK']):
        raise ProtocolError('Unreviewed DMA descriptor semantics')
    with (ROOT / 'state/REQUIREMENTS_TRACEABILITY.csv').open(newline='') as fh:
        ids = {row['Req_ID'] for row in csv.DictReader(fh)}
    if not REQUIREMENTS <= ids:
        raise ProtocolError('Unlinked contract requirement')
    ch04 = ch04 if ch04 is not None else json.loads(CH04.read_text())
    ch02 = ch02 if ch02 is not None else json.loads(CH02.read_text())
    if (ch04.get('schema_version') != 1 or
            ch04.get('gate', {}).get('model') != 'MODEL_PASS_IF_REGRESSION_PASSES' or
            ch04.get('gate', {}).get('physical') != 'FEASIBILITY_HOLD' or
            ch02.get('schema_version') != 1 or
            sorted(ch04['mode_rates']) != sorted(m['id'] for m in ch02['modes']) or
            ch04.get('ch02_input_sha256') != hashlib.sha256(CH02.read_bytes()).hexdigest()):
        raise ProtocolError('CH02/CH04 source mismatch')
    return p


def crc32c(data):
    crc = MASK32
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0x82F63B78 if crc & 1 else 0)
    return crc ^ MASK32


@dataclass(frozen=True)
class Frame:
    kind: int
    seq: int
    boot_epoch: int
    sample_time_us: int
    payload: bytes
    flags: int = 0


def validate_frame(frame, p):
    if (frame.kind not in TYPES.values() or
            any(type(x) is not int or not 0 <= x <= limit for x, limit in
                [(frame.seq, MASK32), (frame.boot_epoch, MASK32),
                 (frame.sample_time_us, MASK64), (frame.flags, 0xFFFF)]) or
            type(frame.payload) is not bytes or len(frame.payload) > p['max_payload_bytes'] or
            frame.flags & ~3):
        raise ProtocolError('Invalid frame dimensions or reserved flags')
    if frame.kind == TYPES['DATA']:
        if frame.flags not in (0, FLAGS['TIME_VALID']):
            raise ProtocolError('DATA may contain only time-valid flag')
        if not frame.flags & FLAGS['TIME_VALID'] and frame.sample_time_us != 0:
            raise ProtocolError('Invalid time must be zero, never fabricated')
    elif frame.kind == TYPES['GAP']:
        if (frame.flags != FLAGS['GAP_PRESENT'] or frame.sample_time_us != 0 or
                len(frame.payload) != 4 or struct.unpack('<I', frame.payload)[0] == 0):
            raise ProtocolError('A gap needs a nonzero loss count')
    else:
        if frame.flags or frame.sample_time_us:
            raise ProtocolError('Control frame may not claim a sensor timestamp')
        sizes = {TYPES['STATUS']: 0, TYPES['READ']: 4, TYPES['WRITE']: 8,
                 TYPES['ACK']: 4, TYPES['REPLY']: 8, TYPES['ERROR']: 8}
        if len(frame.payload) != sizes[frame.kind]:
            raise ProtocolError('Wrong command payload length')


def encode(frame, p):
    validate_frame(frame, p)
    head = HEADER.pack(0xC35A, p['protocol_major'], frame.kind, frame.flags,
                       len(frame.payload), frame.seq, frame.boot_epoch,
                       frame.sample_time_us, 0)
    content = head + frame.payload
    return content + CRC.pack(crc32c(content))


def decode(raw, p):
    if type(raw) is not bytes or len(raw) < HEADER.size + CRC.size:
        raise ProtocolError('Truncated frame')
    magic, major, kind, flags, length, seq, boot, time_us, reserved = HEADER.unpack_from(raw)
    if magic != 0xC35A or major != p['protocol_major'] or reserved or length > p['max_payload_bytes']:
        raise ProtocolError('Magic/version/reserved/length mismatch')
    if len(raw) != HEADER.size + length + CRC.size:
        raise ProtocolError('Extra/truncated frame bytes')
    expected = CRC.unpack_from(raw, len(raw) - CRC.size)[0]
    if crc32c(raw[:-CRC.size]) != expected:
        raise ProtocolError('CRC-32c mismatch')
    frame = Frame(kind, seq, boot, time_us, raw[HEADER.size:-CRC.size], flags)
    validate_frame(frame, p)
    return frame


class IncrementalParser:
    """Byte chunks within one chip-select transaction; CS reset discards incomplete data."""

    def __init__(self, p):
        self.p = p
        self.buf = bytearray()
        self.errors = 0

    def feed(self, data):
        if type(data) is not bytes:
            raise ProtocolError('Parser needs bytes')
        if len(data) + len(self.buf) > 1 << 20:
            raise ProtocolError('Unbounded parser input')
        self.buf.extend(data)
        frames = []
        magic = struct.pack('<H', 0xC35A)
        while len(self.buf) >= 2:
            idx = self.buf.find(magic)
            if idx < 0:
                self.buf[:] = self.buf[-1:] if self.buf[-1:] == magic[:1] else b''
                break
            if idx:
                del self.buf[:idx]
            if len(self.buf) < HEADER.size:
                break
            _, _, _, _, length, _, _, _, _ = HEADER.unpack_from(self.buf)
            if length > self.p['max_payload_bytes']:
                self.errors += 1
                del self.buf[0]
                continue
            size = HEADER.size + length + CRC.size
            if len(self.buf) < size:
                break
            candidate = bytes(self.buf[:size])
            try:
                frames.append(decode(candidate, self.p))
                del self.buf[:size]
            except ProtocolError:
                self.errors += 1
                del self.buf[0]
        return frames

    def end_chip_select(self):
        if self.buf:
            self.errors += 1
        self.buf.clear()


class SequenceTracker:
    def __init__(self):
        self.boot = None
        self.last_seq = None
        self.last_bytes = None

    def negotiate(self, boot_epoch):
        if type(boot_epoch) is not int or not 0 <= boot_epoch <= MASK32:
            raise ProtocolError('Invalid boot epoch')
        self.boot, self.last_seq, self.last_bytes = boot_epoch, None, None

    def accept(self, raw, p):
        frame = decode(raw, p)
        if self.boot is None or frame.boot_epoch != self.boot:
            raise ProtocolError('Boot epoch unnegotiated or changed')
        if self.last_seq is not None:
            diff = (frame.seq - self.last_seq) & MASK32
            if diff == 0:
                if raw != self.last_bytes:
                    raise ProtocolError('Same sequence with different bytes')
                return 'DUPLICATE', frame
            if diff != 1:
                raise ProtocolError('Missing or reordered sequence')
        self.last_seq, self.last_bytes = frame.seq, raw
        return 'NEW', frame


class CandidateDevice:
    """An ASIC-facing contract model, not a host firmware or DMA implementation."""

    def __init__(self, config, p):
        self.p = p
        self.regs = {r['name']: r for r in config['registers']}
        self.offsets = {r['offset']: r['name'] for r in config['registers']}
        self.irq_enable = self.pending = 0
        self.status = 1 << STATUS_BITS['READY']
        self.boot_epoch = 1
        self.snapshot = self.snapshot_seq = 0
        self.now_us = 0
        self.loss_count = self.pending_gap = 0
        self.seq = 0
        self.queue = deque()
        self.queued_payload_bytes = 0
        self.commands = SequenceTracker()
        self.commands.negotiate(self.boot_epoch)
        self.last_response = None

    def _reg(self, offset):
        if type(offset) is not int or offset not in self.offsets:
            raise ProtocolError('Unmapped or unaligned register')
        return self.regs[self.offsets[offset]]

    def set_time(self, now_us):
        if type(now_us) is not int or not self.now_us <= now_us <= MASK64:
            raise ProtocolError('Time may not step backwards or overflow')
        self.now_us = now_us

    def read(self, offset):
        r = self._reg(offset)
        if r['access'] == 'WO':
            raise ProtocolError('Write-only register')
        value = {'STATUS': self.status, 'IRQ_ENABLE': self.irq_enable,
                 'IRQ_PENDING': self.pending, 'TIME_LO': self.snapshot & MASK32,
                 'TIME_HI': self.snapshot >> 32, 'TIME_SEQ': self.snapshot_seq,
                 'FIFO_BYTES': self.queued_payload_bytes,
                 'LOSS_COUNT': self.loss_count, 'BOOT_EPOCH': self.boot_epoch}.get(r['name'], r['reset'])
        return value

    def write(self, offset, value, *, concurrent_event=0):
        r = self._reg(offset)
        if (type(value) is not int or not 0 <= value <= MASK32 or value & ~r['mask'] or
                type(concurrent_event) is not int or concurrent_event & ~63 or concurrent_event < 0):
            raise ProtocolError('Reserved bits or invalid register value')
        if r['access'] == 'RO':
            raise ProtocolError('Read-only register')
        if concurrent_event and r['name'] != 'IRQ_PENDING':
            raise ProtocolError('Concurrent IRQ injection only applies to pending register')
        if r['name'] == 'IRQ_ENABLE':
            self.irq_enable = value
        elif r['name'] == 'IRQ_PENDING':
            self.pending = (self.pending & ~value) | concurrent_event  # HW set wins.
        elif r['name'] == 'TIME_SNAPSHOT':
            if value != 1:
                raise ProtocolError('Snapshot command must be one')
            self.snapshot = self.now_us
            self.snapshot_seq = (self.snapshot_seq + 1) & MASK32
        else:
            raise ProtocolError('Unimplemented write semantics')

    @property
    def irq_asserted(self):
        return bool(self.pending & self.irq_enable)

    def event(self, name):
        if name not in STATUS_BITS:
            raise ProtocolError('Unknown event')
        bit = 1 << STATUS_BITS[name]
        self.status |= bit
        self.pending |= bit

    def reset(self):
        # Only a modeled retained SOFT reset. Power-loss epoch uniqueness is unproven.
        self.boot_epoch = (self.boot_epoch + 1) & MASK32
        if self.boot_epoch == 0:
            raise ProtocolError('Boot epoch wrapped; require new host identity')
        self.queue.clear()
        self.queued_payload_bytes = 0
        self.pending_gap = self.loss_count = 0
        self.snapshot = self.snapshot_seq = 0
        self.now_us = 0
        self.seq = 0
        self.irq_enable = self.pending = 0
        self.status = (1 << STATUS_BITS['READY']) | (1 << STATUS_BITS['SESSION_BREAK'])
        self.commands.negotiate(self.boot_epoch)
        self.last_response = None

    def _append(self, kind, payload, *, time_us=0, flags=0):
        frame = Frame(kind, self.seq, self.boot_epoch, time_us, payload, flags)
        raw = encode(frame, self.p)
        self.queue.append({'raw': raw, 'payload_bytes': len(payload), 'owner': 'READY', 'seq': self.seq})
        self.queued_payload_bytes += len(payload)
        self.seq = (self.seq + 1) & MASK32
        return raw

    def enqueue(self, payload, sample_time_us=None):
        if type(payload) is not bytes or not payload or len(payload) > self.p['max_payload_bytes']:
            raise ProtocolError('Empty, oversized or non-byte record')
        gap_size = 4 if self.pending_gap else 0
        if self.queued_payload_bytes + gap_size + len(payload) > self.p['queue_capacity_bytes']:
            self.loss_count = min(MASK32, self.loss_count + 1)
            self.pending_gap = min(MASK32, self.pending_gap + 1)
            self.event('OVERFLOW')
            return False
        if self.pending_gap:
            self._append(TYPES['GAP'], struct.pack('<I', self.pending_gap), flags=FLAGS['GAP_PRESENT'])
            self.pending_gap = 0
        if sample_time_us is None:
            self.event('TIME_INVALID')
            self._append(TYPES['DATA'], payload)
        else:
            if type(sample_time_us) is not int or not 0 <= sample_time_us <= MASK64:
                raise ProtocolError('Invalid sample timestamp')
            self._append(TYPES['DATA'], payload, time_us=sample_time_us, flags=FLAGS['TIME_VALID'])
        return True

    def request(self, credit_bytes):
        if type(credit_bytes) is not int or credit_bytes < 0:
            raise ProtocolError('Invalid host credit')
        if not self.queue or len(self.queue[0]['raw']) > credit_bytes:
            return None
        self.queue[0]['owner'] = 'HOST_VIEW'
        return self.queue[0]['raw']  # Retry yields identical bytes until valid ACK.

    def acknowledge(self, seq, boot_epoch):
        if (type(seq) is not int or type(boot_epoch) is not int or
                not self.queue or self.queue[0]['owner'] != 'HOST_VIEW' or
                self.queue[0]['seq'] != seq or self.boot_epoch != boot_epoch):
            raise ProtocolError('ACK without matching committed host view')
        item = self.queue.popleft()
        self.queued_payload_bytes -= item['payload_bytes']
        return item['raw']

    def command(self, raw):
        """Idempotent immediately previous command in one modeled boot session.

        REPLY carries (status=0, read value or ACKed wire bytes); ERROR carries
        (code=1, value=0). Corrupt/unnegotiated frames get no response.
        """
        try:
            verdict, cmd = self.commands.accept(raw, self.p)
        except ProtocolError as exc:
            self.event('CRC_ERROR' if 'CRC' in str(exc) else 'BAD_COMMAND')
            raise
        if verdict == 'DUPLICATE':
            return self.last_response
        try:
            if cmd.kind == TYPES['READ']:
                result = self.read(struct.unpack('<I', cmd.payload)[0])
            elif cmd.kind == TYPES['WRITE']:
                offset, value = struct.unpack('<II', cmd.payload)
                self.write(offset, value)
                result = 0
            elif cmd.kind == TYPES['ACK']:
                seq = struct.unpack('<I', cmd.payload)[0]
                result = len(self.acknowledge(seq, cmd.boot_epoch))
            else:
                raise ProtocolError('Unknown host command type')
            reply_kind, reply_body = TYPES['REPLY'], struct.pack('<II', 0, result)
        except ProtocolError:
            self.event('BAD_COMMAND')
            reply_kind, reply_body = TYPES['ERROR'], struct.pack('<II', 1, 0)
        self.last_response = encode(Frame(reply_kind, cmd.seq, self.boot_epoch, 0,
                                          reply_body), self.p)
        return self.last_response


def mode_rates(p, ch04, clocks):
    rows = {}
    util = Fraction(str(p['illustrative_wire_utilization']))
    guard = Fraction(str(p['capacity_guard']))
    for name, data in sorted(ch04['mode_rates'].items()):
        raw = data['raw']
        group_bytes = raw['sample_group_bytes_per_s']
        frames = 0
        for stream in raw['stream_detail']:
            group_size, group_count = stream['group_bytes'], stream['groups_per_s']
            if group_size <= 0 or group_size > p['max_payload_bytes'] or group_count < 0:
                raise ProtocolError('Cannot preserve CH04 whole sample group')
            frames += math.ceil(group_count / (p['max_payload_bytes'] // group_size))
        if sum(s['group_bytes'] * s['groups_per_s'] for s in raw['stream_detail']) != group_bytes:
            raise ProtocolError('CH04 bytes and whole group counts disagree')
        wire_bytes = group_bytes + frames * (HEADER.size + CRC.size)
        min_clock = math.ceil(Fraction(8 * wire_bytes) * guard / util) if wire_bytes else 0
        rows[name] = {'class': data['class'], 'sample_group_bytes_per_s': group_bytes,
                      'whole_group_frames_per_s': frames, 'new_ch06_wire_bytes_per_s': wire_bytes,
                      'ch04_alternative_framed_bytes_per_s': raw['framed_bytes_per_s'],
                      'min_illustrative_sck_hz_with_guard': min_clock,
                      'probes_at_70pct_full_duty': {str(c): 'AVERAGE_ONLY' if c >= min_clock else 'AVERAGE_DEFICIT'
                                                    for c in clocks}}
    return rows


def generate(config):
    ch04, ch02 = json.loads(CH04.read_text()), json.loads(CH02.read_text())
    p = prepare(config, ch04, ch02)
    clocks = ch02['format_assumptions']['illustrative_single_data_line_clocks_hz']
    if clocks != [8_000_000, 16_000_000, 32_000_000, 64_000_000]:
        raise ProtocolError('Unreviewed CH02 illustrative clock list')
    device = CandidateDevice(config, p)
    device.set_time((1 << 32) + 7)
    device.write(20, 1)
    probe = {'time_lo': device.read(24), 'time_hi': device.read(28),
             'time_seq': device.read(32)}
    one = device.enqueue(b'hello', sample_time_us=device.now_us)
    raw = device.request(HEADER.size + 5 + CRC.size)
    probe['frame_hex'] = raw.hex() if raw else None
    probe['retry_identical'] = raw == device.request(len(raw)) if raw else False
    probe['crc32c_check_vector'] = hex(crc32c(b'123456789'))
    probe['queued_before_ack'] = device.read(36)
    if one and raw:
        device.acknowledge(decode(raw, p).seq, device.boot_epoch)
    probe['queued_after_ack'] = device.read(36)
    return {'schema_version': 1, 'evidence_class': 'candidate_synthetic_contract',
            'gate': 'MODEL_PASS_ABI_PHYSICAL_HOLD',
            'config_sha256': hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
            'ch04_sha256': hashlib.sha256(CH04.read_bytes()).hexdigest(),
            'header_bytes': HEADER.size, 'crc_bytes': CRC.size,
            'max_payload_bytes': p['max_payload_bytes'],
            'registers': config['registers'], 'frame_types': TYPES,
            'fields': config['frame']['header_fields'], 'status_bits': STATUS_BITS,
            'example': probe, 'modes': mode_rates(p, ch04, clocks),
            'physical_inputs_missing': sorted(PHYSICAL)}


def render(report):
    regrows = '\n'.join(f"| `{r['name']}` | `0x{r['offset']:03X}` | {r['access']} | `0x{r['reset']:08X}` | `0x{r['mask']:08X}` |"
                        for r in report['registers'])
    rows = '\n'.join(f"| `{name}` | {d['sample_group_bytes_per_s']} | {d['whole_group_frames_per_s']} | "
                     f"{d['new_ch06_wire_bytes_per_s']} | {d['min_illustrative_sck_hz_with_guard']} | "
                     f"{d['probes_at_70pct_full_duty']['16000000']} / {d['probes_at_70pct_full_duty']['32000000']} |"
                     for name, d in report['modes'].items())
    return f"""# CH06 candidate register and host protocol contract

Generate with `python3 models/python/ch06_host.py --write`; verify `--check`. Input `specs/system/CH06_HOST_CONTRACT.json` SHA-256 `{report['config_sha256']}` and CH04 report SHA-256 `{report['ch04_sha256']}`. The [CH06 host survey](../literature/host_interface/2026-09-25_STATE_OF_ART_REVIEW.md) was merged before model work. **Proposed ABI, not frozen hardware/firmware.** All address, size, clock and frame choices are candidate fixtures.

## Byte-exact packet candidate

Frame = 28-byte little-endian header, 0–1024 B payload, then 4-byte CRC-32c. Ordered fields: magic `0xC35A` (u16), major (u8=1), type (u8), flags (u16: bit0 time-valid, bit1 gap), payload length (u16), sequence (u32), modeled boot epoch (u32), sample time in µs (u64), reserved zero (u32). CRC-32c reflected polynomial `0x82F63B78`, init/final XOR `0xFFFFFFFF`; covers header+payload; append little-endian. Check vector `123456789` → `{report['example']['crc32c_check_vector']}`. Types: DATA=1, GAP=2 (u32 nonzero lost record count), STATUS=3, READ=16 (u32 aligned offset), WRITE=17 (u32 offset+u32 value), ACK=18 (u32 sequence), REPLY=19 (u32 status 0 + u32 result), ERROR=20 (u32 code 1 + u32 zero). REPLY/ERROR echo the command sequence and epoch. Unknown version/type/flags/reserved, illegal lengths, bad CRC and truncated frames fail. Parser may receive byte chunks **within one chip select**; an unfinished frame at CS end is discarded. CRC detects corruption but cannot authenticate a command; there is no body-drive enable in this map.

Frame sequence increments modulo 2³² **per emitted frame**. Host negotiates boot epoch before accepting frame sequence; duplicate sequence must contain identical bytes, a gap or reordering is reported. Data events lost before a frame is made are represented by the next GAP marker with a count. A soft-reset discontinuity starts a new modeled boot epoch; uniqueness through full power loss is unresolved. An unacknowledged frame remains in FIFO and a retry returns identical bytes. FIFO data is consumed only by ACK of the head sequence and matching epoch. A CRC-successful transfer alone is **not** a commit. Credit counts total wire bytes, including header/CRC.

Host commands have their own per-epoch sequence space and receive byte-identical replies for a retry of the **immediately previous** identical command; side effects execute once. A malformed command or changed epoch gets no reply, whereas a valid but illegal access gets ERROR and sets BAD_COMMAND. READ returns the register value; WRITE returns zero; ACK returns the acknowledged frame wire-byte count. An older replay, authenticated origin, clocking of full-duplex reply and long-term command history remain unresolved. REPLY/ERROR are control frames and cannot carry sensor time.

## Candidate 32-bit register map

| Register | Offset | Access | Reset | Valid mask |
|---|---:|---|---:|---:|
{regrows}

All reads/writes are one aligned 32-bit word. Unmapped/unaligned, reserved-bit, illegal access or unsupported command fails. `STATUS`: READY, OVERFLOW, CRC_ERROR, BAD_COMMAND, TIME_INVALID, SESSION_BREAK bits 0–5; sticky until modeled reset. `IRQ_ENABLE` masks `IRQ_PENDING`. `IRQ_PENDING` is write-one-to-clear, with a simultaneous hardware set winning over software clear. Writing exactly 1 to `TIME_SNAPSHOT` latches the 64-bit time and increments `TIME_SEQ`; reading LO and HI afterward cannot tear until the next snapshot. A host can bracket LO/HI with SEQ and retry if another software actor snapshots concurrently. Dynamic FIFO_BYTES counts payload only, distinct from wire credits or SRAM capacity. No external wake/reset/IRQ electrical timing or actuator permission is approved.

## Average throughput sensitivities

Reframe each CH04 *unframed whole sample group* per stream into ≤1024-byte payloads without splitting a group; aggregate counts over one second. CH04's alternative framed rate already has its **own** header/CRC and is not added again. Illustrative SCK bound = `ceil(8 × CH06 wire B/s × 1.2 / 0.7)`, with invented full-duty availability and no separate measured CS or wake cost. `AVERAGE_ONLY` is no timed-queue or physical pass.

| CH02 mode | Group B/s | Whole-group frames/s | New CH06 wire B/s | Minimum SCK Hz (synthetic) | 16/32 MHz probe |
|---|---:|---:|---:|---:|---|
{rows}

Latency, burst peaks, BLE, contention, silicon clock power, SRAM and DMA energy remain unverified; see CH04 timed queue and `OI-013`. Nordic engineering-B host errata require **part/build-specific** qualification before implementation. No selected SPI mode, pin, safe SCK or software ABI is approved. [CH06 gate](../reviews/CH06_GATE.md): MODEL_PASS / ABI_AND_PHYSICAL_HOLD.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = generate(json.loads(CONFIG.read_text()))
    js = json.dumps(report, indent=2, sort_keys=True) + '\n'
    md = render(report)
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REVIEW.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(js)
        REVIEW.write_text(md)
        print('CH06 candidate register/packet reports written; physical ABI HOLD')
    else:
        if REPORT.read_text() != js or REVIEW.read_text() != md:
            raise SystemExit('CH06 report stale: run --write and review changes')
        print('CH06 reports match candidate source/model; physical ABI HOLD')


if __name__ == '__main__':
    main()
