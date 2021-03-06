from minibus_generator import MinibusGenerator
from minibus_stops import closest_stop
import logging
from minibus_routes import MinibusRoutes
from collections import defaultdict

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class MinibusTracker(object):

    def __init__(self, tracked_route, debug=False):
        self.minibus_generator = MinibusGenerator(debug=debug)

        self.route_id, self.route_data = tracked_route, MinibusRoutes()[tracked_route]

        self.tracked_minibuses = {}

        self.lost_minibuses = defaultdict(int)

    def refresh_minibuses(self):
        current_time, non_tracked_buses = self.minibus_generator.get_minibuses(route_number=self.route_id.route_number)

        non_tracked_buses = {car_id: minibus
                             for car_id, minibus in non_tracked_buses.items()
                             if minibus.route_number == self.route_id.route_number
                             }

        for car_id, minibus in non_tracked_buses.items():
            if car_id in self.tracked_minibuses or self.at_first_stop(minibus=minibus):
                if self.at_last_stop(minibus=minibus):
                    logger.debug('{} drove to last stop'.format(car_id))
                    del self.tracked_minibuses[car_id]
                    continue

                if car_id not in self.tracked_minibuses:
                    logger.debug('{} tracking started'.format(car_id))

                # fixme: these could probably just be calculated when needed...?
                minibus.stop_index, minibus.stop = closest_stop(minibus=minibus, stops=self.route_data.stops)

                minibus.departure = self.route_data.timetable.closest_departure(current_time=current_time,
                                                                                closest_stop_index=minibus.stop_index)

                self.tracked_minibuses[car_id] = minibus

        # minibuses sometimes can not appear in gps data intermittently for a few reading, make sure not to lose them
        for car_id in list(self.tracked_minibuses.keys()):
            if car_id not in non_tracked_buses.keys():
                times_missing = self.lost_minibuses[car_id] = self.lost_minibuses[car_id] + 1
                logger.debug('{} is missing for {}'.format(car_id, times_missing))
                if times_missing > 5:
                    del self.tracked_minibuses[car_id]
                    del self.lost_minibuses[car_id]

    def at_first_stop(self, minibus):
        return minibus.location - self.route_data.stops[0].location < 100

    def at_last_stop(self, minibus):
        return minibus.location - self.route_data.stops[-1].location < 100
