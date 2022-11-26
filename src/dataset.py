import math
import pandas as pd


class Dataset:
    """
    Class for parsing csv datasets with provided countries lists and their corresponding latitude and longitude.
    This class using build method, creates so-called distance matrix, represented as a dictionary to provide from-to
    (country) information. This structure contains precomputed distances between each place or country.
    """
    def __init__(self, csv_data_path, number_of_rows=None, random_pick_dataset=False, choose_my_route=False,
                 selected_places=None
                 ):
        self.df = pd.read_csv(csv_data_path)
        self.distance_coords_dict = {}
        self.countries = []
        self.n_of_rows = number_of_rows
        self.random_pick = random_pick_dataset
        self.selected_places = selected_places
        self.choose_my_route = choose_my_route

    def __build__(self):
        """
        :return: Distance matrix between each pair of points.
        """

        # if selected then only the given specific route will be processed
        if self.choose_my_route:
            self.df = self.df[self.df['place'].isin(self.selected_places)].reset_index()

        # no specific route is provided, but the subset of places will be selected (e.g. do not consider whole dataset)
        elif self.n_of_rows is not None:
            # pick random places
            if self.random_pick:
                self.df = self.df.sample(n=self.n_of_rows, ignore_index=True)
            # pick first n_of_rows data samples
            else:
                self.df = self.df.head(self.n_of_rows)

        # compute modified distance matrix represented as distance_coords_dict
        for idx1, row1 in self.df.iterrows():
            self.countries.append(row1.place)
            for idx2, row2 in self.df.iterrows():
                distance = self.get_distance_from_lat_lon_in_km(row1.lat, row1.lng,
                                                                row2.lat, row2.lng)
                self.distance_coords_dict[row1.place + "-" + row2.place] = \
                    [distance, [row1.lat, row1.lng, row2.lat, row2.lng]]

    @staticmethod
    def get_distance_from_lat_lon_in_km(lat1, lon1, lat2, lon2):
        """
        Method computes formally well-known formula to get distance in km, based on latitude and longitude values.
        https://www.movable-type.co.uk/scripts/latlong.html
        """
        radius = 6371
        d_lat = (lat2 - lat1) * (math.pi / 180)
        d_lon = (lon2 - lon1) * (math.pi / 180)

        a = math.sin(d_lat / 2) * math.sin(d_lat / 2) + math.cos(lat1 * (math.pi / 180)) * math.cos(
            lat2 * (math.pi / 180)) * math.sin(d_lon / 2) * math.sin(d_lon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        dist = radius * c
        return dist
