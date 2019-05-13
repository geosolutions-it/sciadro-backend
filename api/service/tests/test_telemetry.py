from django.test import TestCase
from ..utils.telemetry import ATT
from ..utils.telemetry import POS
from ..utils.telemetry import TelemetryAttributes
from ..utils.telemetry import TelemetryPosition
from ..utils.telemetry import Telemetry
from io import BytesIO
from ..utils.telemetry import _parse_telemetry_data
from ..utils.telemetry import DECODERS
from dataclasses import astuple


ATT_BINARY = ATT.encode('utf-8')
POS_BINARY = POS.encode('utf-8')


def attributes_to_binary(attributes: TelemetryAttributes) -> bytes:
    return DECODERS[ATT].pack(*astuple(attributes))


def position_to_binary(position: TelemetryPosition) -> bytes:
    values = list(astuple(position))
    values[1] = int(values[1] * 10000000)
    values[2] = int(values[2] * 10000000)
    values[3] = int(values[3] * 1000)
    values[4] = int(values[4] * 1000)
    return DECODERS[POS].pack(*values)


class TelemetryFileParsing(TestCase):
    def setUp(self) -> None:
        self.file = BytesIO()

    def tearDown(self) -> None:
        self.file.close()

    def test_basic_functionality(self) -> None:
        # WARNING: time value needs to be always 0 because of the parsing algorithm
        attributes = TelemetryAttributes(0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
        position = TelemetryPosition(0, 7.0, 8.0, 9.0, 10.0)
        telemetry = Telemetry([attributes], [position])

        self.file.write(ATT_BINARY)
        self.file.write(attributes_to_binary(attributes))
        self.file.write(POS_BINARY)
        self.file.write(position_to_binary(position))
        self.file.seek(0)

        result = _parse_telemetry_data(self.file, 'Test')

        self.assertEqual(result, telemetry)

    def test_empty_file(self) -> None:
        self.assertEqual(_parse_telemetry_data(self.file), Telemetry([], []))

    def test_invalid_code(self) -> None:
        self.file.write('RANDOM'.encode('utf-8'))
        self.file.seek(0)
        self.assertRaisesMessage(ValueError, "Invalid code: RAN", lambda: _parse_telemetry_data(self.file))

    def test_file_is_corrupted(self) -> None:
        self.file.write(ATT_BINARY)
        self.file.write(ATT_BINARY)
        self.file.seek(0)
        self.assertRaisesMessage(ValueError, "None is corrupted. 25 byte(s) missing", lambda: _parse_telemetry_data(self.file))
