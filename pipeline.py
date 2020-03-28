# -*- coding: utf-8 -*-
"""
Apache Beam pipeline for the London cycle hire data set.


@author: Oliver
"""

import os

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText


# The PipelineOptions() method is a command line parser for reading any option
# passed the following way:     --<option>=<value>
p = beam.Pipeline(options=PipelineOptions())

data_path = "Trips.csv"
data_filename = os.path.join(os.getcwd(), data_path)


# Reading file into pipeline:
data_from_source = (p | 'ReadMyFile' >> ReadFromText(data_filename))


# Test beam with a printer f'n:
def printer(data_item):
    """Print stuff."""
    print(data_item)


class TypeOf(beam.DoFn):
    def process(self, data_item):
        print(type(data_item))


#def discard_incomplete(record):
#    """Filters out incomplete records."""
#    if 'geolocation' in record and 'year' in record:
#        yield record


data_from_source = (p
                    | 'ReadMyFile' >> ReadFromText(data_filename)
                    | 'Split using beam.Map' >> beam.Map(lambda record: (record.split(","))[8])
                    | 'Print the data' >> beam.ParDo(printer)
#                    | 'Check data type' >> beam.ParDo(TypeOf())
                    | 'Map record to 1' >> beam.Map(lambda record: (record, 1))
                    | 'GroupBy' >> beam.GroupByKey()
                    | 'Sum' >> beam.Map(lambda record: (record[0],
                                                        sum(record[1])))
                    )


result = p.run()



