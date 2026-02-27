from __future__ import annotations
import numpy as np


class Sample:
    '''
    This modules defined a sample

    Parameters
    ----------
    name : str
        Name of the sample.
    mass : float, optional
        Mass of the sample, unit is mg.
    '''
    def __init__(self, name: str,
                 mass: float | None = None):
        self.name = name
        self.mass = mass  # milligram
        self._measurements = []
    
    def add_measurement(self, m):
        if m not in self._measurements:
            print(f'{m} (added)')
            self._measurements.append(m)
            m.sample = self  # double-linked with the measurement
        else:
            print(f'The Measurment [{m}] \n'
                  f'is already exist in sample [{self}] ')


class Measurement():
    def __init__(self, 
                 sample: "Sample", 
                 filepath: str | None = None):
        self.filepath = filepath
        self.sample = sample
        self.raw_dataframe, self.dataframe = self.load_data()
        self.mode = ''

    @property
    def sample_name(self):
        return self.sample.name if self.sample else "Unknown Sample"

    def load_data(self):
        assert self.filepath is not None
        try:
            with open(file=self.filepath, encoding='utf-8', errors="strict") as f:
                content = f.readlines()
        except UnicodeDecodeError:
            with open(file=self.filepath, encoding='iso-8859-1') as f:
                content = f.readlines()

        # Data start after the Line [Data].
        data_start_line = content.index('[Data]\n') + 1
        lines = content[data_start_line:]
        headers = lines[0].strip().split(',')
        rows = [l.strip().split(',') for l in lines[1:]]

        raw_data = {h: [] for h in headers}

        for row in rows:
            for h, v in zip(headers, row):
                raw_data[h].append(v)

        processed_data = self.process_data(raw_data)

        return raw_data, processed_data

    def process_data(self, raw_data):      

        import re

        keep_pattern = (
            r'^Temperature \(|'
            r'Magnetic Field \(|'
            r'Moment \(|'
            r'M. Std. Err. \('
        )

        processed = {}

        for key, values in raw_data.items():
            if re.search(keep_pattern, key):

                nums = []
                for v in values:
                    try:
                        nums.append(float(v))
                    except:
                        nums.append(float('nan'))

                if key.startswith('Moment'):
                    nums = [v / self.sample.mass if self.sample.mass else v for v in nums]

                processed[key] = nums

        return processed



