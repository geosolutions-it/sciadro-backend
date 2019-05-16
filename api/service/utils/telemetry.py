import struct
from dataclasses import dataclass
from typing import List
from typing import BinaryIO

ATT = 'ATT'
POS = 'POS'

DECODERS = {
    ATT: struct.Struct('<Iffffff'),
    POS: struct.Struct('<Iiiii'),
}


@dataclass
class TelemetryAttributes:
    time: int
    roll: float
    pitch: float
    yaw: float
    roll_speed: float
    pitch_speed: float
    yaw_speed: float


@dataclass
class TelemetryPosition:
    time: int
    latitude: float
    longitude: float
    altitude: float
    relative_altitude: float


@dataclass
class Telemetry:
    attributes: List[TelemetryAttributes]
    positions: List[TelemetryPosition]


def _parse_telemetry_data(file: BinaryIO, file_name: str = None) -> Telemetry:
    telemetry = Telemetry([], [])
    start_time = None
    while True:
        code = file.read(3).decode('utf-8')

        if not code:
            break

        if code not in DECODERS:
            raise ValueError(f'Invalid code: {code}')
        else:
            decoder = DECODERS[code]
            chunk = file.read(decoder.size)

            if not chunk:
                break

            if len(chunk) < decoder.size:
                raise ValueError(f'{file_name} is corrupted. {decoder.size - len(chunk)} byte(s) missing')

            values = decoder.unpack(chunk)

            if start_time is None:
                start_time = values[0]

            if code == ATT:
                values = (values[0] - start_time,) + values[1:]
                telemetry.attributes.append(TelemetryAttributes(*values))
            else:
                values = (values[0] - start_time, values[1] / 10000000, values[2] / 10000000, values[3] / 1000,
                          values[4] / 1000)
                telemetry.positions.append(TelemetryPosition(*values))
    return telemetry


def parse_telemetry_data(file):
    return _parse_telemetry_data(file, 'telemetry_file')

# def parse_telemetry_data(file_name: str) -> Telemetry:
    # with open(file_name, "rb") as file:
    #     return _parse_telemetry_data(file, file_name)
