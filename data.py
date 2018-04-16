import csv
import os


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DataManager(metaclass=Singleton):
    def __init__(self, directory='./dataset'):
        self.dataset_path = directory
        self.check_csv_existence()

        self.image_loader = self.loads()
        #
        # self.writer = csv.writer()
        # self.reader = csv.reader()

    def loads(self):
        for x in os.listdir(os.path.join(self.dataset_path, 'images')):
            yield os.path.abspath(os.path.join(self.dataset_path, 'images', x))

    def next_img(self):
        return next(self.image_loader)

    def check_csv_existence(self):
        csv_path = os.path.join(self.dataset_path, 'data.csv')
        if not os.path.isfile(csv_path):
            os.system('touch {0}'.format(csv_path))

    def save_sample(self, img, coordinates, category_id):
        filename = os.path.basename(img)

