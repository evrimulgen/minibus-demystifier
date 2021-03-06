import hashlib
from minibus_generator import MinibusGenerator
from minibus_routes import MinibusRoutes
from minibus_routes import RouteID
from minibus_stops import closest_stop
from timetable import TimetableIndex
from timetable import decode_data
from nose.tools import assert_equal
from unittest import TestCase


class TestClass(TestCase):
    @classmethod
    def setup_class(cls):
        minibus_routes = MinibusRoutes()
        cls.route = minibus_routes[RouteID(route_number='246', type='a1-b')]

    def test_decoding(self):
        encoded_data_test = ['17728', '12', '17726']
        days_test = 79

        decoded_data = decode_data(encoded_data_test, days_test)
        assert_equal(len(decoded_data), days_test)

        correct_decode_data = ['17728', '17728', '17728', '17728', '17728', '17728', '17728', '17728', '17728', '17728',
                               '17728', '17728', '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726',
                               '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726',
                               '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726',
                               '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726',
                               '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726',
                               '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726',
                               '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726', '17726']

        assert_equal(decoded_data, correct_decode_data)

    def test_timetable(self):
        timetable = self.route.timetable

        time_at_stop = timetable[TimetableIndex(departure=12, stop=0)]

        hash_object = hashlib.md5(str(timetable.timetable).encode('utf-8'))
        digest = hash_object.hexdigest()
        expected_digest = 'a8e5f7272a07115e3205d5fed667f2ec'

        assert_equal(time_at_stop, 563)
        assert_equal(digest, expected_digest)

    def test_closest_departure(self):
        minibus_generator = MinibusGenerator(debug=True)

        current_time, minibuses = minibus_generator.get_minibuses('246')

        stops = self.route.stops

        minibus = [minibus
                   for minibus in minibuses.values()
                   if minibus.route_number == '246'][0]

        stop_index, _ = closest_stop(minibus, stops)

        timetable = self.route.timetable

        closest_departure = timetable.closest_departure(current_time, stop_index)

        assert_equal(31, closest_departure)

    def test_time_difference(self):
        timetable = self.route.timetable

        difference = timetable.time_to_stop(28, 6, 11)
        assert_equal(difference, 9)

        difference = timetable.time_to_stop(0, 0, 6)
        assert_equal(difference, 10)
