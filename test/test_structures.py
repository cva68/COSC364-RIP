"""
    RIP Packet Structure / Entry Structure unit tests.
    MIT License. Copyright © 2025 Connor Varney, Kahu Jones
"""

import unittest

from test.context import (
    PacketCommands,
    RIPPacket,
    RIPEntry,
    PacketParseError,
    PacketCommandError,
    PacketVersionError
)

HEADER_LENGTH = 4
ENTRY_LENGTH = 20
ADDRESS_FAMILY = 2
VERSION = 2


class RIPEntryTestSuite(unittest.TestCase):
    """
        RIP Entry test suite.
    """
    def test_initialisation(self):
        """
            Test the initialisation of a RIP entry.
        """
        entry = RIPEntry(id=1, metric=1)
        self.assertEqual(entry.id, 1)
        self.assertEqual(entry.metric, 1)

    def test_packet_formation(self):
        """
            Test the formation of a RIP *entry* packet.
        """
        entry = RIPEntry(id=1, metric=1)
        packet = entry.as_packet()
        self.assertEqual(len(packet), 20)  # 20 bytes
        self.assertEqual(packet[0], 0)     # LSB should be 0
        self.assertEqual(packet[1], ADDRESS_FAMILY)  # AFI should be 2
        self.assertEqual(packet[2], 0)     # Reserved
        self.assertEqual(packet[3], 0)     # Reserved
        self.assertEqual(packet[4:8], bytes([0, 0, 0, 1]))  # ID
        self.assertEqual(packet[8:16], bytes([0] * 8))  # Reserved
        self.assertEqual(
            packet[16:20],
            (1).to_bytes(4, byteorder='big')
        )  # Metric should be 1, big endian


class RIPPacketTestSuite(unittest.TestCase):
    """
        RIP Packet test suite.
    """
    def test_initialisation(self):
        """
            Test the initialisation of a RIP packet, verifying the header
            length.
        """
        packet = RIPPacket.construct(
            router_id=1,
            command=PacketCommands.REQUEST,
            entries=[],
            version=VERSION
        )

        self.assertIsNotNone(packet)
        self.assertEqual(len(packet), 4)  # 4B header, no entries

    def test_packet_parsing(self):
        """
            Construct a packet, then parse it back into its components.
            Verify the components match the original packet.
        """
        entry1 = RIPEntry(id=2, metric=1)
        entry2 = RIPEntry(id=3, metric=1)

        packet = RIPPacket.construct(
            router_id=1,
            command=PacketCommands.RESPONSE,
            entries=[entry1, entry2],
            version=VERSION
        )

        self.assertEqual(len(packet), 44)  # 4B header, 2 entries

        command, router_id, entries = RIPPacket.parse(packet)
        self.assertEqual(command, PacketCommands.RESPONSE)
        self.assertEqual(router_id, 1)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].id, entry1.id)
        self.assertEqual(entries[0].metric, entry1.metric)
        self.assertEqual(entries[1].id, entry2.id)
        self.assertEqual(entries[1].metric, entry2.metric)

    def test_parse_invalid_packet(self):
        """
            Test the parsing of an invalid packet.
            This should raise an exception.
        """
        # Try an empty packet
        invalid_packet = bytearray(0)
        self.assertRaises(
            PacketParseError,
            RIPPacket.parse,
            invalid_packet
        )

        # Try a packet with an invalid command
        invalid_packet = bytearray(10)
        invalid_packet[0] = 99
        invalid_packet[1] = VERSION
        self.assertRaises(
            PacketCommandError,
            RIPPacket.parse,
            invalid_packet
        )

        # Try a packet with an invalid version
        invalid_packet[0] = PacketCommands.REQUEST
        invalid_packet[1] = 99
        self.assertRaises(
            PacketVersionError,
            RIPPacket.parse,
            invalid_packet
        )


if __name__ == '__main__':
    unittest.main()
