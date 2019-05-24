from django.test import TestCase
from io import BytesIO
from ..utils.asset import parse_asset_data
from ..utils.asset import Root
from ..utils.asset import Source
from ..utils.asset import Frame
from ..utils.asset import Id
from ..utils.asset import Position
from ..utils.asset import Size
from ..utils.asset import Anomaly
from ..utils.asset import Status
from ..utils.asset import Box
from xml.etree.ElementTree import ParseError


class AssetFileParsing(TestCase):
    def setUp(self) -> None:
        self.file = BytesIO()

    def tearDown(self) -> None:
        self.file.close()

    def test_basic_functionality(self) -> None:
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
                <powerline>
                    <source>
                        <filename>Colibri_lun_nov_5_15_38_48_2018_GMT.avi</filename>
                        <path>D:/Dati Utente/s.nardi/Commesse/SCIADRO/OR6_GEOSOLUTIONS/Dati</path>
                    </source>
                    <frame>
                        <pose>
                            <latitude>43.6525</latitude>
                            <longitude>10.4374</longitude>
                        </pose>
                        <id>
                            <index>36</index>
                            <database>Unknown</database>
                        </id>
                        <size>
                            <width>1024</width>
                            <height>768</height>
                            <depth>3</depth>
                        </size>
                        <objects>
                            <object>
                                <type>insulator</type>
                                <status>
                                    <class>Unknown</class>
                                    <confidence>0</confidence>
                                </status>
                                <id>1</id>
                                <box>
                                    <xmin>475</xmin>
                                    <ymin>42</ymin>
                                    <xmax>518</xmax>
                                    <ymax>233</ymax>
                                </box>
                            </object>
                        </objects>
                    </frame>
                </powerline>'''
        asset_data = Root(
            type='powerline',
            source=Source(
                file_name='Colibri_lun_nov_5_15_38_48_2018_GMT.avi',
                path='D:/Dati Utente/s.nardi/Commesse/SCIADRO/OR6_GEOSOLUTIONS/Dati'
            ),
            frames=[
                Frame(
                    id=Id(
                        index=36,
                        database='Unknown'
                    ),
                    position=Position(
                        longitude=10.4374,
                        latitude=43.6525
                    ),
                    size=Size(
                        width=1024,
                        height=768,
                        depth=3
                    ),
                    anomalies=[
                        Anomaly(
                            id=1,
                            type='insulator',
                            status=Status(
                                class_='Unknown',
                                confidence=0
                            ),
                            box=Box(
                                x_min=475,
                                y_min=42,
                                x_max=518,
                                y_max=233
                            )
                        )
                    ]
                )
            ]
        )
        self.file.write(xml.encode('utf-8'))
        self.file.seek(0)
        result = parse_asset_data(self.file)
        self.assertEqual(result, asset_data)

    def test_empty_file(self) -> None:
        self.assertRaises(ParseError, lambda: parse_asset_data(self.file))
