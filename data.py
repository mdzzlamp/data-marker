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
        self.image_loader = self.loads()
        self.csv_file = open(self.csv_path(), 'a', newline='')
        self.csv_writer = csv.writer(self.csv_file)

    def loads(self):
        unmarked_dir_path = os.path.join(self.dataset_path, 'unmarked')
        for x in os.listdir(unmarked_dir_path):
            yield os.path.abspath(os.path.join(unmarked_dir_path, x))

    def close(self):
        self.csv_file.close()

    def next_img(self):
        return next(self.image_loader)

    def csv_path(self):
        csv_path = os.path.join(self.dataset_path, 'data.csv')
        return csv_path

    def marked_dir(self):
        marked_dir_path = os.path.join(self.dataset_path, 'marked')
        if not os.path.isdir(marked_dir_path):
            os.mkdir(marked_dir_path)
        return marked_dir_path

    def save_sample(self, img_path, coordinates, category_id):
        filename = os.path.basename(img_path)
        self.csv_writer.writerow([filename.split('.')[0]] + coordinates + [category_id])
        os.rename(img_path, os.path.join(self.marked_dir(), filename))
